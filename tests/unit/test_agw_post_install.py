#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from unittest.mock import Mock, PropertyMock, call, mock_open, patch

from magma_access_gateway_post_install.agw_post_install import (
    AGWCloudCheckinError,
    AGWConfigurationError,
    AGWControlProxyConfigFileMissingError,
    AGWControlProxyConfigurationError,
    AGWPackagesMissingError,
    AGWPostInstallChecks,
    AGWRootCertificateMissingError,
    AGWServicesNotRunningError,
)


class TestAGWPostInstallChecks(unittest.TestCase):

    TEST_MAGMA_AGW_INTERFACES = ["iface1", "iface2", "iface3"]
    TEST_MAGMA_AGW_SERVICES = ["magma@service1", "magma@service2", "magma@service3"]
    TEST_NON_MAGMA_SERVICES = ["service1", "service2", "service3"]
    TEST_TIMEOUT_WAITING_FOR_SERVICE = 1
    TEST_WAIT_FOR_SERVICE_INTERVAL = 1
    TEST_REQUIRED_PACKAGES = ["package1", "package2", "package3"]

    def setUp(self) -> None:
        self.agw_post_install = AGWPostInstallChecks("/test/root/ca/pem/path")

    @patch("magma_access_gateway_post_install.agw_post_install.check_call")
    def test_given_installed_magma_agw_when_prepare_system_for_post_install_checks_then_relevant_actions_on_services_and_interfaces_are_executed(  # noqa: E501
        self, mocked_check_call
    ):
        expected_calls = [
            call(["service", "magma@*", "stop"]),
            call(["ifdown", "gtp_br0"]),
            call(["ifdown", "uplink_br0"]),
            call(["service", "openvswitch-switch", "restart"]),
            call(["ifup", "gtp_br0"]),
            call(["ifup", "uplink_br0"]),
        ]

        self.agw_post_install.prepare_system_for_post_install_checks()

        mocked_check_call.assert_has_calls(expected_calls)

    @patch("magma_access_gateway_post_install.agw_post_install.os.path.exists")
    @patch(
        "magma_access_gateway_post_install.agw_post_install.AGWPostInstallChecks.MAGMA_AGW_INTERFACES",  # noqa: E501
        new_callable=PropertyMock,
    )
    @patch(
        "magma_access_gateway_post_install.agw_post_install.open",
        new_callable=mock_open,
        read_data="up",
    )
    def test_given_some_agw_interfaces_missing_operstate_when_check_whether_required_interfaces_are_configured_then_agwconfigurationerror_is_raised(  # noqa: E501
        self, _, mocked_magma_interfaces, mocked_path_exists
    ):
        mocked_magma_interfaces.return_value = self.TEST_MAGMA_AGW_INTERFACES
        mocked_path_exists.side_effect = [True, False, True]

        with self.assertRaises(AGWConfigurationError):
            self.agw_post_install.check_whether_required_interfaces_are_configured()

    @patch(
        "magma_access_gateway_post_install.agw_post_install.open",
        new_callable=mock_open(),
    )
    @patch(
        "magma_access_gateway_post_install.agw_post_install.os.path.exists",
        Mock(return_value=True),
    )
    @patch(
        "magma_access_gateway_post_install.agw_post_install.AGWPostInstallChecks.MAGMA_AGW_INTERFACES",  # noqa: E501
        new_callable=PropertyMock,
    )
    def test_given_some_agw_interfaces_in_down_state_when_check_whether_required_interfaces_are_configured_then_agwconfigurationerror_is_raised(  # noqa: E501
        self, mocked_agw_ifaces, mocked_open
    ):
        mocked_agw_ifaces.return_value = self.TEST_MAGMA_AGW_INTERFACES
        interfaces_states = ["up", "down", "up"]
        mocked_open.side_effect = [
            mock_open(read_data=content).return_value for content in interfaces_states
        ]

        with self.assertRaises(AGWConfigurationError):
            self.agw_post_install.check_whether_required_interfaces_are_configured()

    @patch(
        "magma_access_gateway_post_install.agw_post_install.ping",
        Mock(return_value=None),
    )
    def test_given_no_network_connectivity_on_eth0_when_check_eth0_internet_connectivity_then_agwconfigurationerror_is_raised(  # noqa: E501
        self,
    ):
        with self.assertRaises(AGWConfigurationError):
            self.agw_post_install.check_eth0_internet_connectivity()

    @patch("magma_access_gateway_post_install.agw_post_install.check_call")
    def test_given_magma_service_not_running_when_start_magma_service_then_magma_service_is_started(  # noqa: E501
        self, mocked_check_call
    ):
        self.agw_post_install.start_magma_service()

        mocked_check_call.assert_called_once_with(["service", "magma@magmad", "start"])

    @patch("magma_access_gateway_post_install.agw_post_install.call")
    @patch(
        "magma_access_gateway_post_install.agw_post_install.AGWPostInstallChecks.MAGMA_AGW_SERVICES",  # noqa: E501
        new_callable=PropertyMock,
    )
    @patch(
        "magma_access_gateway_post_install.agw_post_install.AGWPostInstallChecks.NON_MAGMA_SERVICES",  # noqa: E501
        new_callable=PropertyMock,
    )
    @patch(
        "magma_access_gateway_post_install.agw_post_install.AGWPostInstallChecks.TIMEOUT_WAITING_FOR_SERVICE",  # noqa: E501
        new_callable=PropertyMock,
    )
    @patch(
        "magma_access_gateway_post_install.agw_post_install.AGWPostInstallChecks.WAIT_FOR_SERVICE_INTERVAL",  # noqa: E501
        new_callable=PropertyMock,
    )
    def test_given_some_agw_services_not_running_when_check_whether_required_services_are_running_then_agwservicesnotrunningerror_is_raised(  # noqa: E501
        self,
        mocked_wait_for_service_interval,
        mocked_timeout_waiting_for_service,
        mocked_non_magma_services,
        mocked_magma_services,
        mocked_call,
    ):
        mocked_magma_services.return_value = self.TEST_MAGMA_AGW_SERVICES
        mocked_non_magma_services.return_value = self.TEST_NON_MAGMA_SERVICES
        mocked_timeout_waiting_for_service.return_value = self.TEST_TIMEOUT_WAITING_FOR_SERVICE
        mocked_wait_for_service_interval.return_value = self.TEST_WAIT_FOR_SERVICE_INTERVAL
        is_service_running_states = [False, True, True, False, False, True]

        mocked_call.side_effect = is_service_running_states

        with self.assertRaises(AGWServicesNotRunningError):
            self.agw_post_install.check_whether_required_services_are_running()

    @patch("magma_access_gateway_post_install.agw_post_install.call")
    @patch(
        "magma_access_gateway_post_install.agw_post_install.AGWPostInstallChecks.REQUIRED_PACKAGES",  # noqa: E501
        new_callable=PropertyMock,
    )
    def test_given_not_all_required_magma_packages_are_installed_when_check_whether_required_packages_are_installed_then_agwpackagesmissingerror_is_raised(  # noqa: E501
        self, mocked_required_packages, mocked_call
    ):
        mocked_required_packages.return_value = self.TEST_REQUIRED_PACKAGES
        package_is_installed_statuses = [True, False, True]

        mocked_call.side_effect = package_is_installed_statuses

        with self.assertRaises(AGWPackagesMissingError):
            self.agw_post_install.check_whether_required_packages_are_installed()

    @patch(
        "magma_access_gateway_post_install.agw_post_install.os.path.exists",
        Mock(return_value=False),
    )
    def test_given_invalid_root_ca_pem_path_when_check_whether_root_certificate_exists_then_agwrootcertificatemissingerror_is_raised(  # noqa: E501
        self,
    ):
        with self.assertRaises(AGWRootCertificateMissingError):
            self.agw_post_install.check_whether_root_certificate_exists()

    @patch(
        "magma_access_gateway_post_install.agw_post_install.os.path.exists",
        Mock(return_value=False),
    )
    def test_given_control_proxy_config_file_missing_when_check_control_proxy_then_agwcontrolproxyconfigfilemissingerror_is_raised(  # noqa: E501
        self,
    ):
        with self.assertRaises(AGWControlProxyConfigFileMissingError):
            self.agw_post_install.check_control_proxy()

    @patch("magma_access_gateway_installer.agw_network_configurator.yaml.safe_load")
    @patch("magma_access_gateway_post_install.agw_post_install.open", new_callable=mock_open())
    @patch(
        "magma_access_gateway_post_install.agw_post_install.os.path.exists",
        Mock(return_value=True),
    )
    def test_given_control_proxy_config_file_is_missing_required_keys_when_check_control_proxy_then_agwcontrolproxyconfigurationerror_is_raised(  # noqa: E501
        self, _, mocked_yaml_safe_load
    ):
        invalid_control_proxy_config_file = {
            "cloud_address": "controller.example.com",
            "cloud_port": 443,
            "bootstrap_address": "bootstrapper-controller.example.com",
            "fluentd_address": "fluentd.example.com",
            "fluentd_port": 24224,
            "rootca_cert": "/test/root/ca/pem/path",
        }
        mocked_yaml_safe_load.return_value = invalid_control_proxy_config_file

        with self.assertRaises(AGWControlProxyConfigurationError):
            self.agw_post_install.check_control_proxy()

    def test_given_journal_not_containing_cloud_checkin_logs_when_check_cloud_check_in_then_agwcloudcheckinerror_is_raised(  # noqa: E501
        self,
    ):
        with self.assertRaises(AGWCloudCheckinError):
            self.agw_post_install.check_cloud_check_in()
