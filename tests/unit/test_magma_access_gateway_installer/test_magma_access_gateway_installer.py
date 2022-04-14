#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from argparse import Namespace
from unittest.mock import MagicMock, Mock, patch

import magma_access_gateway_installer


class TestAGWInstallerInit(unittest.TestCase):

    VALID_TEST_IPv4_ADDRESS = "1.2.3.4/24"
    INVALID_TEST_IPv4_ADDRESS = "321.0.1.5/24"
    VALID_TEST_GW_IPv4_ADDRESS = "2.3.4.5"
    INVALID_TEST_GW_IPv4_ADDRESS = "321.3.4.5"
    VALID_TEST_IPv6_ADDRESS = "fd9c:0175:3d65:cfbd:1:2:3:4/64"
    VALID_TEST_GW_IPv6_ADDRESS = "fd9c:0175:3d65:cfbd:4:3:2:1"
    DNS_LIST_WITH_VALID_ADDRESS = ["1.2.3.4", "5.6.7.8"]
    DNS_LIST_WITH_INVALID_ADDRESS = ["1.2.3.4", "321.3.4.5", "5.6.7.8"]
    TEST_INTERFACES_LIST = ["lo", "bear", "rabbit", "eagle", "moose"]
    VALID_TEST_SGi_INTERFACE_NAME = "rabbit"
    INVALID_TEST_SGi_INTERFACE_NAME = "wolf"
    VALID_TEST_S1_INTERFACE_NAME = "moose"
    INVALID_TEST_S1_INTERFACE_NAME = "snake"
    TEST_SGi_MAC = "aa:bb:cc:dd:ee:ff"
    TEST_S1_MAC = "ff:ee:dd:cc:bb:aa"
    VALID_CLI_ARGUMENTS = Namespace(
        ipv4_address=VALID_TEST_IPv4_ADDRESS,
        gw_ipv4_address=VALID_TEST_GW_IPv4_ADDRESS,
        ipv6_address=VALID_TEST_IPv6_ADDRESS,
        gw_ipv6_address=VALID_TEST_GW_IPv6_ADDRESS,
        dns=DNS_LIST_WITH_VALID_ADDRESS,
        sgi=VALID_TEST_SGi_INTERFACE_NAME,
        s1=VALID_TEST_S1_INTERFACE_NAME,
    )
    APT_LIST_WITHOUT_MAGMA = b"""lua-cjson/focal,now 2.1.0+dfsg-2.1 amd64 [installed,automatic]\n
lvm2/focal,now 2.03.07-1ubuntu1 amd64 [installed,automatic]\n
lxd-agent-loader/focal,now 0.4 all [installed,automatic]\n
lz4/focal-updates,focal-security,now 1.9.2-2ubuntu0.20.04.1 amd64 [installed,automatic]\n
make/focal,now 4.2.1-1.2 amd64 [installed,automatic]\n
man-db/focal,now 2.9.1-1 amd64 [installed,automatic]\n
"""

    @patch("magma_access_gateway_installer.netifaces.interfaces", MagicMock())
    def test_given_only_ip_address_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(
            ipv4_address=self.VALID_TEST_IPv4_ADDRESS,
            gw_ipv4_address=None,
            ipv6_address=None,
            gw_ipv6_address=None,
        )

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args)

    @patch("magma_access_gateway_installer.netifaces.interfaces", MagicMock())
    def test_given_only_gw_ip_address_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(
            ipv4_address=None,
            gw_ipv4_address=self.VALID_TEST_GW_IPv4_ADDRESS,
            ipv6_address=None,
            gw_ipv6_address=None,
        )

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args)

    @patch("magma_access_gateway_installer.netifaces.interfaces", MagicMock())
    def test_given_invalid_gw_ip_address_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(
            ipv4_address=self.VALID_TEST_IPv4_ADDRESS,
            gw_ipv4_address=self.INVALID_TEST_GW_IPv4_ADDRESS,
            ipv6_address=None,
            gw_ipv6_address=None,
        )

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args)

    @patch("magma_access_gateway_installer.netifaces.interfaces", MagicMock())
    def test_given_invalid_ip_address_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(
            ipv4_address=self.INVALID_TEST_IPv4_ADDRESS,
            gw_ipv4_address=self.VALID_TEST_GW_IPv4_ADDRESS,
            ipv6_address=None,
            gw_ipv6_address=None,
        )

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args)

    @patch("magma_access_gateway_installer.netifaces.interfaces", MagicMock())
    def test_given_static_ipv6_addresses_without_ipv4_addresses_when_validate_args_then_value_error_is_raise(  # noqa: E501
        self,
    ):
        test_args = Namespace(
            ipv4_address=None,
            gw_ipv4_address=None,
            ipv6_address=self.VALID_TEST_IPv6_ADDRESS,
            gw_ipv6_address=self.VALID_TEST_GW_IPv6_ADDRESS,
        )

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args)

    @patch("magma_access_gateway_installer.netifaces.interfaces", MagicMock())
    def test_given_invalid_dns_ip_address_passed_when_validate_args_then_value_error_is_raised(
        self,
    ):
        test_args = Namespace(
            ipv4_address=None,
            gw_ipv4_address=None,
            ipv6_address=None,
            gw_ipv6_address=None,
            dns=self.DNS_LIST_WITH_INVALID_ADDRESS,
        )

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args)

    @patch("magma_access_gateway_installer.network_interfaces", TEST_INTERFACES_LIST)
    def test_given_invalid_sgi_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(
            ipv4_address=None,
            gw_ipv4_address=None,
            ipv6_address=None,
            gw_ipv6_address=None,
            dns=self.DNS_LIST_WITH_VALID_ADDRESS,
            sgi=self.INVALID_TEST_SGi_INTERFACE_NAME,
            s1=self.VALID_TEST_S1_INTERFACE_NAME,
        )

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args)

    @patch("magma_access_gateway_installer.network_interfaces", TEST_INTERFACES_LIST)
    def test_given_invalid_s1_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(
        self,
    ):
        test_args = Namespace(
            ipv4_address=None,
            gw_ipv4_address=None,
            ipv6_address=None,
            gw_ipv6_address=None,
            dns=self.DNS_LIST_WITH_VALID_ADDRESS,
            sgi=self.VALID_TEST_SGi_INTERFACE_NAME,
            s1=self.INVALID_TEST_S1_INTERFACE_NAME,
        )
        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args)

    @patch("magma_access_gateway_installer.network_interfaces", TEST_INTERFACES_LIST)
    def test_given_invalid_sgi_and_s1_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(
            ipv4_address=None,
            gw_ipv4_address=None,
            ipv6_address=None,
            gw_ipv6_address=None,
            dns=self.DNS_LIST_WITH_VALID_ADDRESS,
            sgi=self.INVALID_TEST_SGi_INTERFACE_NAME,
            s1=self.INVALID_TEST_S1_INTERFACE_NAME,
        )

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args)

    @patch("magma_access_gateway_installer.network_interfaces", TEST_INTERFACES_LIST)
    def test_given_valid_sgi_and_s1_cli_argument_is_passed_when_validate_args_then_no_errors_are_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(
            ipv4_address=None,
            gw_ipv4_address=None,
            ipv6_address=None,
            gw_ipv6_address=None,
            dns=self.DNS_LIST_WITH_VALID_ADDRESS,
            sgi=self.VALID_TEST_SGi_INTERFACE_NAME,
            s1=self.VALID_TEST_S1_INTERFACE_NAME,
        )

        self.assertEqual(magma_access_gateway_installer.validate_args(test_args), None)

    @patch("magma_access_gateway_installer.get_mac_address")
    def test_given_valid_cli_arguments_when_generate_network_config_then_correct_network_config_is_created(  # noqa: E501
        self, mocked_get_mac_address
    ):
        mocked_get_mac_address.side_effect = [self.TEST_SGi_MAC, self.TEST_S1_MAC]
        expected_network_config = {
            "sgi_ipv4_address": self.VALID_TEST_IPv4_ADDRESS,
            "sgi_ipv4_gateway": self.VALID_TEST_GW_IPv4_ADDRESS,
            "sgi_ipv6_address": self.VALID_TEST_IPv6_ADDRESS,
            "sgi_ipv6_gateway": self.VALID_TEST_GW_IPv6_ADDRESS,
            "sgi_mac_address": self.TEST_SGi_MAC,
            "s1_mac_address": self.TEST_S1_MAC,
            "dns_address": " ".join(self.DNS_LIST_WITH_VALID_ADDRESS),
        }

        self.assertEqual(
            magma_access_gateway_installer.generate_network_config(self.VALID_CLI_ARGUMENTS),
            expected_network_config,
        )

    @patch("magma_access_gateway_installer.os.system")
    @patch("magma_access_gateway_installer.generate_network_config", Mock())
    @patch("magma_access_gateway_installer.AGWInstallerNetworkConfigurator", Mock())
    @patch("magma_access_gateway_installer.AGWInstallerInstallationServiceCreator", Mock())
    @patch("magma_access_gateway_installer.time.sleep", Mock())
    def test_given_static_ip_configuration_when_configure_network_then_system_goes_for_reboot_once_network_config_is_done(  # noqa: E501
        self, mock_os_system
    ):
        test_args = Namespace(
            ipv4_address=self.VALID_TEST_IPv4_ADDRESS,
            gw_ipv4_address=self.VALID_TEST_GW_IPv4_ADDRESS,
            ipv6_address=None,
            gw_ipv6_address=None,
        )

        magma_access_gateway_installer.configure_network(test_args)

        mock_os_system.assert_called_once_with("reboot")

    @patch("magma_access_gateway_installer.os.system")
    @patch.object(
        magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator,
        "apply_netplan_configuration",
    )
    @patch("magma_access_gateway_installer.generate_network_config", Mock())
    @patch("magma_access_gateway_installer.AGWInstallerNetworkConfigurator.configure_dns", Mock())
    @patch(
        "magma_access_gateway_installer.AGWInstallerNetworkConfigurator.configure_network_interfaces",  # noqa: E501
        Mock(),
    )
    def test_given_dhcp_ip_configuration_when_configure_network_then_system_is_not_rebooted_and_netplan_config_is_applied_once_network_config_is_done(  # noqa: E501
        self, mocked_apply_netplan_configuration, mock_os_system
    ):
        test_args = Namespace(
            ipv4_address=None,
            gw_ipv4_address=None,
            ipv6_address=None,
            gw_ipv6_address=None,
        )

        magma_access_gateway_installer.configure_network(test_args)

        mock_os_system.assert_not_called()
        self.assertTrue(mocked_apply_netplan_configuration.called)

    @patch.object(magma_access_gateway_installer, "configure_network")
    @patch("sys.argv", ["test.py", "--skip-networking"])
    @patch("magma_access_gateway_installer.validate_args", Mock())
    @patch("magma_access_gateway_installer.AGWInstallerPreinstallChecks", Mock())
    @patch("magma_access_gateway_installer.AGWInstallerServiceUserCreator", Mock())
    @patch("magma_access_gateway_installer.AGWInstaller", Mock())
    def test_given_skip_networking_cli_argument_passed_when_main_then_configure_network_is_not_run(
        self, mocked_configure_network
    ):
        magma_access_gateway_installer.main()

        self.assertFalse(mocked_configure_network.called)

    @patch.object(magma_access_gateway_installer, "configure_network")
    @patch("sys.argv", ["test.py", "--sgi", "eth0", "--s1", "eth1"])
    @patch("magma_access_gateway_installer.validate_args", Mock())
    @patch("magma_access_gateway_installer.AGWInstallerPreinstallChecks", Mock())
    @patch("magma_access_gateway_installer.AGWInstallerServiceUserCreator", Mock())
    @patch("magma_access_gateway_installer.AGWInstaller", Mock())
    def test_given_skip_networking_cli_argument_not_passed_when_main_then_configure_network_is_run(
        self, mocked_configure_network
    ):
        magma_access_gateway_installer.main()

        self.assertTrue(mocked_configure_network.called)

    @patch("magma_access_gateway_installer.network_interfaces", TEST_INTERFACES_LIST)
    def test_given_not_specified_sgi_and_s1_and_no_eth_and_eth1_in_the_system_when_cli_arguments_parser_then_first_two_interfaces_are_assigned_as_sgi_and_s1(  # noqa: E501
        self,
    ):
        parsed_args = magma_access_gateway_installer.cli_arguments_parser([])

        self.assertEqual(parsed_args.sgi, self.TEST_INTERFACES_LIST[0])
        self.assertEqual(parsed_args.s1, self.TEST_INTERFACES_LIST[1])

    @patch("magma_access_gateway_installer.network_interfaces", ["abc", "eth0", "def", "eth1"])
    def test_given_not_specified_sgi_and_s1_and_eth_and_eth1_in_the_system_when_cli_arguments_parser_then_eth0_assigned_to_sgi_and_eth1_assigned_to_s1(  # noqa: E501
        self,
    ):
        parsed_args = magma_access_gateway_installer.cli_arguments_parser([])

        self.assertEqual(parsed_args.sgi, "eth0")
        self.assertEqual(parsed_args.s1, "eth1")
