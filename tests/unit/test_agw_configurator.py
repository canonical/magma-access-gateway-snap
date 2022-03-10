#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import os
import unittest
from unittest.mock import Mock, PropertyMock, call, patch

from magma_access_gateway_configurator.agw_configurator import AGWConfigurator


class TestAGWConfigurator(unittest.TestCase):

    TEST_DOMAIN = "test_domain.com"
    TEST_ROOT_CA_PEM_PATH = "/test/rootCA.pem"
    TEST_ROOT_CA_PEM_DESTINATION_DIR = "/test/root/ca/pem/dest/dir"
    TEST_ROOT_CA_PEM_FILE_NAME = "test_rootCA.pem"
    TEST_MAGMA_CONTROL_PROXY_CONFIG_DIR = "/test/magma/configs/dir"
    TEST_MAGMA_CONTROL_PROXY_CONFIG_FILE_NAME = "test_control_proxy.yml"

    def setUp(self) -> None:
        self.mocked_root_ca_pem_file_name = patch(
            "magma_access_gateway_configurator.agw_configurator.AGWConfigurator.ROOT_CA_PEM_FILE_NAME",  # noqa: E501
            new_callable=PropertyMock(return_value=self.TEST_ROOT_CA_PEM_FILE_NAME),
        )
        self.mocked_root_ca_pem_dest_dir = patch(
            "magma_access_gateway_configurator.agw_configurator.AGWConfigurator.ROOT_CA_PEM_DESTINATION_DIR",  # noqa: E501
            new_callable=PropertyMock(return_value=self.TEST_ROOT_CA_PEM_DESTINATION_DIR),
        )
        self.mocked_magma_control_proxy_config_dir = patch(
            "magma_access_gateway_configurator.agw_configurator.AGWConfigurator.MAGMA_CONTROL_PROXY_CONFIG_DIR",  # noqa: E501
            new_callable=PropertyMock(return_value=self.TEST_MAGMA_CONTROL_PROXY_CONFIG_DIR),
        )
        self.mocked_magma_control_proxy_config_file_name = patch(
            "magma_access_gateway_configurator.agw_configurator.AGWConfigurator.MAGMA_CONTROL_PROXY_CONFIG_FILE_NAME",  # noqa: E501
            new_callable=PropertyMock(return_value=self.TEST_MAGMA_CONTROL_PROXY_CONFIG_FILE_NAME),
        )
        self.agw_configurator = AGWConfigurator(self.TEST_DOMAIN, self.TEST_ROOT_CA_PEM_PATH)

    @patch("magma_access_gateway_configurator.agw_configurator.os.makedirs")
    @patch(
        "magma_access_gateway_configurator.agw_configurator.shutil.copy",
        Mock(),
    )
    def test_given_non_existent_root_ca_pem_destination_dir_when_copy_root_ca_pem_then_root_ca_pem_destination_dir_is_created(  # noqa: E501
        self, mocked_makedirs
    ):
        with self.mocked_root_ca_pem_dest_dir:
            self.agw_configurator.copy_root_ca_pem()

        mocked_makedirs.assert_called_once_with(self.TEST_ROOT_CA_PEM_DESTINATION_DIR)

    @patch("magma_access_gateway_configurator.agw_configurator.os.makedirs")
    @patch(
        "magma_access_gateway_configurator.agw_configurator.os.path.exists",
        Mock(return_value=True),
    )
    @patch(
        "magma_access_gateway_configurator.agw_configurator.shutil.copy",
        Mock(),
    )
    def test_given_existent_root_ca_pem_destination_dir_when_copy_root_ca_pem_then_root_ca_pem_destination_dir_is_not_created(  # noqa: E501
        self, mocked_makedirs
    ):
        with self.mocked_root_ca_pem_dest_dir:
            self.agw_configurator.copy_root_ca_pem()

        mocked_makedirs.assert_not_called()

    @patch("magma_access_gateway_configurator.agw_configurator.shutil.copy")
    @patch(
        "magma_access_gateway_configurator.agw_configurator.os.path.exists",
        Mock(return_value=True),
    )
    def test_given_existent_root_ca_pem_destination_dir_when_copy_root_ca_pem_then_root_ca_pem_is_copied_to_the_destination_dir(  # noqa: E501
        self, mocked_copy
    ):
        with self.mocked_root_ca_pem_dest_dir, self.mocked_root_ca_pem_file_name:
            self.agw_configurator.copy_root_ca_pem()

        mocked_copy.assert_called_once_with(
            self.TEST_ROOT_CA_PEM_PATH,
            os.path.join(self.TEST_ROOT_CA_PEM_DESTINATION_DIR, self.TEST_ROOT_CA_PEM_FILE_NAME),
        )

    @patch("magma_access_gateway_configurator.agw_configurator.os.makedirs")
    @patch("magma_access_gateway_configurator.agw_configurator.os.path.exists")
    def test_given_non_existent_control_proxy_conf_dir_when_configure_control_proxy_then_control_proxy_conf_dir_is_created(  # noqa: E501
        self, mocked_path_exists, mocked_makedirs
    ):
        mocked_path_exists.side_effect = [False, True]

        with self.mocked_magma_control_proxy_config_dir:
            self.agw_configurator.configure_control_proxy()

        mocked_makedirs.assert_called_once_with(self.TEST_MAGMA_CONTROL_PROXY_CONFIG_DIR)

    @patch("magma_access_gateway_configurator.agw_configurator.os.makedirs")
    @patch("magma_access_gateway_configurator.agw_configurator.os.path.exists")
    def test_given_existent_control_proxy_conf_dir_when_configure_control_proxy_then_control_proxy_conf_dir_is_not_created(  # noqa: E501
        self, mocked_path_exists, mocked_makedirs
    ):
        mocked_path_exists.side_effect = [True, True]

        with self.mocked_magma_control_proxy_config_dir:
            self.agw_configurator.configure_control_proxy()

        mocked_makedirs.assert_not_called()

    @patch("magma_access_gateway_installer.agw_network_configurator.yaml.dump")
    @patch("magma_access_gateway_configurator.agw_configurator.os.path.exists")
    @patch("magma_access_gateway_configurator.agw_configurator.open")
    def test_given_non_existent_control_proxy_config_file_when_configure_control_proxy_then_control_proxy_config_file_is_created_with_correct_content(  # noqa: E501
        self, mocked_open, mocked_path_exists, mocked_yaml_dump
    ):
        expected_control_proxy_config = f"""cloud_address: controller.{self.TEST_DOMAIN}
cloud_port: 443
bootstrap_address: bootstrapper-controller.{self.TEST_DOMAIN}
bootstrap_port: 443
fluentd_address: fluentd.{self.TEST_DOMAIN}
fluentd_port: 24224

sentry_url_python: ""

rootca_cert: {self.TEST_ROOT_CA_PEM_DESTINATION_DIR}/{self.TEST_ROOT_CA_PEM_FILE_NAME}"""
        mocked_path_exists.side_effect = [True, False]

        # fmt: off
        with self.mocked_root_ca_pem_dest_dir, \
                self.mocked_root_ca_pem_file_name, \
                self.mocked_magma_control_proxy_config_dir, \
                self.mocked_magma_control_proxy_config_file_name:
            self.agw_configurator.configure_control_proxy()
        # fmt: on

        args, kwargs = mocked_yaml_dump.call_args
        mocked_open.assert_called_once_with(
            os.path.join(
                self.TEST_MAGMA_CONTROL_PROXY_CONFIG_DIR,
                self.TEST_MAGMA_CONTROL_PROXY_CONFIG_FILE_NAME,
            ),
            "w",
        )
        self.assertEqual(args[0], expected_control_proxy_config)
        self.assertEqual(mocked_yaml_dump.call_count, 1)

    @patch("magma_access_gateway_configurator.agw_configurator.os.path.exists")
    @patch("magma_access_gateway_configurator.agw_configurator.open")
    def test_given_existent_control_proxy_config_file_when_configure_control_proxy_then_control_proxy_config_file_is_not_created(  # noqa: E501
        self, mocked_open, mocked_path_exists
    ):
        mocked_path_exists.side_effect = [True, True]

        self.agw_configurator.configure_control_proxy()

        mocked_open.assert_not_called()

    @patch("magma_access_gateway_configurator.agw_configurator.check_call")
    def test_given_magma_agw_configuration_done_when_restart_magma_services_then_relevant_commands_are_called(  # noqa: E501
        self, mocked_check_call
    ):
        expected_calls = [
            call(["service", "magma@*", "stop"]),
            call(["service", "magma@magmad", "restart"]),
        ]

        self.agw_configurator.restart_magma_services()

        mocked_check_call.assert_has_calls(expected_calls)
