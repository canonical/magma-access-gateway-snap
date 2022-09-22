#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from unittest.mock import Mock, PropertyMock, mock_open, patch

from magma_access_gateway_post_install.agw_post_install import (
    AGWConfigurationError,
    AGWControlProxyConfigFileMissingError,
    AGWControlProxyConfigurationError,
    AGWPackagesMissingError,
    AGWPostInstallChecks,
    AGWRootCertificateMissingError,
    AGWServicesNotRunningError,
    Orc8rConnectivityError,
)


class TestAGWPostInstallChecks(unittest.TestCase):

    TEST_MAGMA_AGW_INTERFACES = ["iface1", "iface2", "iface3"]
    TEST_MAGMA_AGW_SERVICES = ["magma@service1", "magma@service2", "magma@service3"]
    TEST_NON_MAGMA_SERVICES = ["service1", "service2", "service3"]
    TEST_TIMEOUT_WAITING_FOR_SERVICE = 1
    TEST_WAIT_FOR_SERVICE_INTERVAL = 1
    TEST_REQUIRED_PACKAGES = ["package1", "package2", "package3"]
    OVS_SHOW_OUTPUT_WITH_ERROR = (
        "128dc4f0-80f9-4584-be74-57747ac0a68f"
        '    Manager "ptcp:6640"'
        "    Bridge gtp_br0"
        '        Controller "tcp:127.0.0.1:6654"'
        "            is_connected: true"
        '        Controller "tcp:127.0.0.1:6633"'
        "            is_connected: true"
        "        fail_mode: secure"
        "        Port mtr0"
        "            Interface mtr0"
        "                type: internal"
        "        Port gtp0"
        "            Interface gtp0"
        "                type: gtpu"
        "                options: {key=flow, remote_ip=flow}"
        '                error: "could not add network device gtp0 to ofproto (Address family not supported by protocol)"'  # noqa: W505, E501
        "        Port ipfix0"
        "            Interface ipfix0"
        "                type: internal"
        "        Port g_20031fac"
        "            Interface g_20031fac"
        "                type: gtpu"
        '                options: {csum="false", key=flow, remote_ip="172.31.3.32"}'
        '                error: "could not add network device g_20031fac to ofproto (Address family not supported by protocol)"'  # noqa: W505, E501
        "        Port gtp_br0"
        "            Interface gtp_br0"
        "                type: internal"
        "        Port proxy_port"
        "            Interface proxy_port"
        "        Port li_port"
        "            Interface li_port"
        "                type: internal"
        "        Port patch-up"
        "            Interface patch-up"
        "                type: patch"
        "                options: {peer=patch-agw}"
        "    Bridge uplink_br0"
        "        Port uplink_br0"
        "            Interface uplink_br0"
        "                type: internal"
        "        Port patch-agw"
        "            Interface patch-agw"
        "                type: patch"
        "                options: {peer=patch-up}"
        "         Port dhcp0"
        "             Interface dhcp0"
        "                 type: internal"
        '    ovs_version: "2.15.4"'
    )

    def setUp(self) -> None:
        self.agw_post_install = AGWPostInstallChecks()

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
        "magma_access_gateway_post_install.agw_post_install.check_output",
        return_value=OVS_SHOW_OUTPUT_WITH_ERROR.encode("utf-8"),
    )
    def test_given_ovs_error_when_check_for_ovs_error_then_agwconfigurationerror_is_raised(  # noqa: E501
        self, _
    ):
        with self.assertRaises(AGWConfigurationError):
            self.agw_post_install.check_ovs_has_not_unsupported_gpt_error()

    @patch(
        "magma_access_gateway_post_install.agw_post_install.ping",
        Mock(return_value=None),
    )
    def test_given_no_network_connectivity_on_eth0_when_check_eth0_internet_connectivity_then_agwconfigurationerror_is_raised(  # noqa: E501
        self,
    ):
        with self.assertRaises(AGWConfigurationError):
            self.agw_post_install.check_eth0_internet_connectivity()

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

    @patch("magma_access_gateway_post_install.agw_post_install.yaml.safe_load")
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

    @patch("magma_access_gateway_post_install.agw_post_install.journal.Reader", new_callable=Mock)
    def test_given_journal_not_containing_cloud_checkin_logs_when_check_cloud_check_in_then_agwcloudcheckinerror_is_raised(  # noqa: E501
        self, mocked_journal_reader
    ):
        mocked_journal_reader.return_value = MockedJournalReader(False)

        with self.assertRaises(Orc8rConnectivityError):
            self.agw_post_install.check_connectivity_with_orc8r()


class MockedJournalReader:
    def __init__(self, agw_configured: bool):
        self.journal_logs = self._set_journal_logs(agw_configured)

    def __iter__(self):
        return iter(self.journal_logs)

    @staticmethod
    def _set_journal_logs(agw_configured):
        if agw_configured:
            return [
                {
                    "PRIORITY": 6,
                    "_HOSTNAME": "test-host",
                    "SYSLOG_IDENTIFIER": "magmad",
                    "_PID": 1111,
                    "MESSAGE": "[SyncRPC] Got heartBeat from cloud",
                },
                {
                    "PRIORITY": 6,
                    "_HOSTNAME": "test-host",
                    "SYSLOG_IDENTIFIER": "magmad",
                    "_PID": 1111,
                    "MESSAGE": "Just some random log message.",
                },
                {
                    "PRIORITY": 6,
                    "_HOSTNAME": "test-host",
                    "SYSLOG_IDENTIFIER": "magmad",
                    "_PID": 1111,
                    "MESSAGE": "Checkin Successful! Successfully sent states to the cloud!",
                },
            ]
        else:
            return [
                {
                    "PRIORITY": 6,
                    "_HOSTNAME": "test-host",
                    "SYSLOG_IDENTIFIER": "magmad",
                    "_PID": 1111,
                    "MESSAGE": "Test message without desired text.",
                },
                {
                    "PRIORITY": 6,
                    "_HOSTNAME": "test-host",
                    "SYSLOG_IDENTIFIER": "magmad",
                    "_PID": 1111,
                    "MESSAGE": "Another test message without desired text.",
                },
                {
                    "PRIORITY": 6,
                    "_HOSTNAME": "test-host",
                    "SYSLOG_IDENTIFIER": "magmad",
                    "_PID": 1111,
                    "MESSAGE": "One more test message without desired text.",
                },
            ]

    def log_level(self, _):
        pass

    def this_boot(self):
        pass

    def add_match(self, *args, **kwargs):
        pass
