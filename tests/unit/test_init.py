# #!/usr/bin/env python3
# # Copyright 2022 Canonical Ltd.
# # See LICENSE file for licensing details.
#
# import sys
# import unittest
# from argparse import Namespace
# from unittest.mock import MagicMock, Mock, patch
#
# import magma_access_gateway_installer
#
#
# class TestAGWInstallerInit(unittest.TestCase):
#
#     TEST_APP_NAME = "test_app"
#     VALID_TEST_IP_ADDRESS = "1.2.3.4/24"
#     INVALID_TEST_IP_ADDRESS = "321.0.1.5/24"
#     VALID_TEST_GW_IP_ADDRESS = "2.3.4.5"
#     INVALID_TEST_GW_IP_ADDRESS = "321.3.4.5"
#
#     @patch("magma_access_gateway_installer.AGWInstallerPreinstallChecks.preinstall_checks", Mock())
#     @patch(
#         "magma_access_gateway_installer.AGWInstallerPreinstallChecks.install_required_system_packages",  # noqa: E501
#         Mock(),
#     )
#     @patch(
#         "magma_access_gateway_installer.AGWInstallerNetworkConfigurator.configure_network_interfaces",  # noqa: E501
#         Mock(),
#     )
#     @patch(
#         "magma_access_gateway_installer.AGWInstallerServiceUserCreator.create_magma_service_user",
#         Mock(),
#     )
#     def test_given_agw_installer_init_when_only_ip_address_cli_argument_is_given_then_value_error_is_raised(  # noqa: E501
#         self,
#     ):
#         test_args = [
#             self.TEST_APP_NAME,
#             "--ip-address",
#             self.VALID_TEST_IP_ADDRESS,
#         ]
#         with patch.object(sys, "argv", test_args), self.assertRaises(ValueError):
#             magma_access_gateway_installer.main()
#
#     @patch("magma_access_gateway_installer.AGWInstallerPreinstallChecks.preinstall_checks", Mock())
#     @patch(
#         "magma_access_gateway_installer.AGWInstallerPreinstallChecks.install_required_system_packages",  # noqa: E501
#         Mock(),
#     )
#     @patch(
#         "magma_access_gateway_installer.AGWInstallerNetworkConfigurator.configure_network_interfaces",  # noqa: E501
#         Mock(),
#     )
#     @patch(
#         "magma_access_gateway_installer.AGWInstallerServiceUserCreator.create_magma_service_user",
#         Mock(),
#     )
#     def test_given_agw_installer_init_when_only_gw_ip_address_cli_argument_is_given_then_value_error_is_raised(  # noqa: E501
#         self,
#     ):
#         test_args = [
#             self.TEST_APP_NAME,
#             "--gw-ip-address",
#             self.VALID_TEST_GW_IP_ADDRESS,
#         ]
#         with patch.object(sys, "argv", test_args), self.assertRaises(ValueError):
#             magma_access_gateway_installer.main()
#
#     @patch("magma_access_gateway_installer.AGWInstallerPreinstallChecks.preinstall_checks", Mock())
#     @patch(
#         "magma_access_gateway_installer.AGWInstallerPreinstallChecks.install_required_system_packages",  # noqa: E501
#         Mock(),
#     )
#     @patch(
#         "magma_access_gateway_installer.AGWInstallerNetworkConfigurator.configure_network_interfaces",  # noqa: E501
#         Mock(),
#     )
#     @patch(
#         "magma_access_gateway_installer.AGWInstallerServiceUserCreator.create_magma_service_user",
#         Mock(),
#     )
#     def test_given_agw_installer_init_when_invalid_gw_ip_address_is_given_then_value_error_is_raised(  # noqa: E501
#         self,
#     ):
#         test_args = [
#             self.TEST_APP_NAME,
#             "--ip-address",
#             self.VALID_TEST_IP_ADDRESS,
#             "--gw-ip-address",
#             self.INVALID_TEST_GW_IP_ADDRESS,
#         ]
#         with patch.object(sys, "argv", test_args), self.assertRaises(ValueError):
#             magma_access_gateway_installer.main()
#
#     @patch("magma_access_gateway_installer.AGWInstallerPreinstallChecks.preinstall_checks", Mock())
#     @patch(
#         "magma_access_gateway_installer.AGWInstallerPreinstallChecks.install_required_system_packages",  # noqa: E501
#         Mock(),
#     )
#     @patch(
#         "magma_access_gateway_installer.AGWInstallerNetworkConfigurator.configure_network_interfaces",  # noqa: E501
#         Mock(),
#     )
#     @patch(
#         "magma_access_gateway_installer.AGWInstallerServiceUserCreator.create_magma_service_user",
#         Mock(),
#     )
#     def test_given_agw_installer_init_when_invalid_ip_address_is_given_then_value_error_is_raised(
#         self,
#     ):
#         test_args = [
#             self.TEST_APP_NAME,
#             "--ip-address",
#             self.INVALID_TEST_IP_ADDRESS,
#             "--gw-ip-address",
#             self.VALID_TEST_GW_IP_ADDRESS,
#         ]
#         with patch.object(sys, "argv", test_args), self.assertRaises(ValueError):
#             magma_access_gateway_installer.main()
#
#     def test_given_agw_installer_init_when_installer_started_without_arguments_then_installation_steps_are_called_correctly(  # noqa: E501
#         self,
#     ):
#         with patch(
#             "magma_access_gateway_installer._cli_arguments_parser",
#             MagicMock(return_value=Namespace(ip_address=None, gw_ip_address=None)),
#         ), patch(
#             "magma_access_gateway_installer.AGWInstallerPreinstallChecks.install_required_system_packages",  # noqa: E501
#             Mock(),
#         ) as install_required_system_packages, patch(
#             "magma_access_gateway_installer.AGWInstallerPreinstallChecks.preinstall_checks", Mock()
#         ) as preinstall_checks, patch(
#             "magma_access_gateway_installer.AGWInstallerNetworkConfigurator.configure_network_interfaces",  # noqa: E501
#             Mock(),
#         ) as configure_network_interfaces, patch(
#             "magma_access_gateway_installer.AGWInstallerServiceUserCreator.create_magma_service_user",  # noqa: E501
#             Mock(),
#         ) as create_magma_service_user:
#             magma_access_gateway_installer.main()
#         install_required_system_packages.assert_called_once()
#         preinstall_checks.assert_called_once()
#         configure_network_interfaces.assert_called_once()
#         create_magma_service_user.assert_called_once()
