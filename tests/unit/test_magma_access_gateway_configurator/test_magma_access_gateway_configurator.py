#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from argparse import Namespace
from unittest.mock import Mock, patch

import magma_access_gateway_configurator


class TestAGWConfiguratorInit(unittest.TestCase):

    VALID_TEST_DOMAIN = "agw-test.com"
    INVALID_TEST_DOMAIN = "agw-test"

    @patch(
        "magma_access_gateway_configurator.os.path.exists",
        Mock(return_value=True),
    )
    def test_given_invalid_domain_cli_argument_is_passed_when_validate_args_then_validationfailure_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(domain=self.INVALID_TEST_DOMAIN, root_ca_path="whatever")

        with self.assertRaises(magma_access_gateway_configurator.AGWConfigurationError):
            magma_access_gateway_configurator.validate_args(test_args)

    @patch(
        "magma_access_gateway_configurator.os.path.exists",
        Mock(return_value=False),
    )
    def test_given_non_existent_root_ca_path_cli_argument_is_passed_when_validate_args_then_filenotfounderror_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(domain=self.VALID_TEST_DOMAIN, root_ca_path="whatever")

        with self.assertRaises(FileNotFoundError):
            magma_access_gateway_configurator.validate_args(test_args)

    @patch.object(
        magma_access_gateway_configurator.agw_configurator.AGWConfigurator,
        "cleanup_old_configs",
    )
    @patch("magma_access_gateway_configurator.agw_configurator.os.path.exists")
    @patch("builtins.input", Mock(return_value="Y"))
    @patch("magma_access_gateway_configurator.cli_arguments_parser", Mock())
    @patch("magma_access_gateway_configurator.validate_args", Mock())
    @patch("magma_access_gateway_configurator.load_public_key_to_base64der", Mock())
    @patch("magma_access_gateway_configurator.AGWConfigurator.copy_root_ca_pem", Mock())
    @patch("magma_access_gateway_configurator.AGWConfigurator.configure_control_proxy", Mock())
    @patch("magma_access_gateway_configurator.AGWConfigurator.restart_magma_services", Mock())
    def test_given_agw_config_files_exist_when_main_then_cleanup_old_configs_is_executed(
        self, mocked_path_exists, mocked_cleanup_old_configs
    ):
        mocked_path_exists.side_effect = [True, False, True, False, True]

        magma_access_gateway_configurator.main()

        self.assertTrue(mocked_cleanup_old_configs.called)

    @patch.object(
        magma_access_gateway_configurator.agw_configurator.AGWConfigurator,
        "cleanup_old_configs",
    )
    @patch("magma_access_gateway_configurator.agw_configurator.os.path.exists")
    @patch("magma_access_gateway_configurator.cli_arguments_parser", Mock())
    @patch("magma_access_gateway_configurator.validate_args", Mock())
    @patch("magma_access_gateway_configurator.load_public_key_to_base64der", Mock())
    @patch("magma_access_gateway_configurator.AGWConfigurator.copy_root_ca_pem", Mock())
    @patch("magma_access_gateway_configurator.AGWConfigurator.configure_control_proxy", Mock())
    @patch("magma_access_gateway_configurator.AGWConfigurator.restart_magma_services", Mock())
    def test_given_agw_config_files_do_not_exist_when_main_then_cleanup_old_configs_is_not_executed(  # noqa: E501
        self, mocked_path_exists, mocked_cleanup_old_configs
    ):
        mocked_path_exists.side_effect = [False, False, False, False, False]

        magma_access_gateway_configurator.main()

        self.assertFalse(mocked_cleanup_old_configs.called)

    @patch("magma_access_gateway_configurator.agw_configurator.os.path.exists")
    @patch("builtins.input", Mock(return_value="N"))
    @patch("magma_access_gateway_configurator.cli_arguments_parser", Mock())
    @patch("magma_access_gateway_configurator.validate_args", Mock())
    @patch("magma_access_gateway_configurator.load_public_key_to_base64der", Mock())
    @patch("magma_access_gateway_configurator.AGWConfigurator.copy_root_ca_pem", Mock())
    @patch("magma_access_gateway_configurator.AGWConfigurator.configure_control_proxy", Mock())
    @patch("magma_access_gateway_configurator.AGWConfigurator.restart_magma_services", Mock())
    def test_given_agw_config_files_exist_when_main_and_user_refuses_to_reconfigure_agw_then_configurator_exits_with_0_rc(  # noqa: E501
        self, mocked_path_exists
    ):
        mocked_path_exists.side_effect = [True, False, True, False, True]

        with self.assertRaises(SystemExit) as exit_code:
            magma_access_gateway_configurator.main()
        self.assertEqual(exit_code.exception.code, 0)
