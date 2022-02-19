#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from unittest.mock import Mock, PropertyMock, call, mock_open, patch

from magma_access_gateway_installer.agw_network_configurator import (
    AGWInstallerNetworkConfigurator,
)


class TestAGWInstallerNetworkConfigurator(unittest.TestCase):
    TEST_NETWORK_INTERFACES = ["eth0", "eth1"]

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open())
    def test_given_agw_installer_network_configurator_when_prepare_interfaces_configuration_dir_if_doesnt_exist_then_configuration_dir_gets_created_properly(  # noqa: E501
        self, _, mocked_makedirs
    ):
        network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES, None, None
        )
        network_configurator._prepare_interfaces_configuration_dir_if_doesnt_exist()
        mocked_makedirs.assert_called_once_with(network_configurator.INTERFACES_DIR)

    @patch("os.makedirs")
    @patch("builtins.open", new_callable=mock_open)
    def test_given_agw_installer_network_configurator_when_prepare_interfaces_configuration_dir_if_doesnt_exist_then_interfaces_configuration_dir_is_written_to_etc_network_interfaces_file(  # noqa: E501
        self, mocked_open_file, _
    ):
        network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES, None, None
        )
        network_configurator._prepare_interfaces_configuration_dir_if_doesnt_exist()
        mocked_open_file.assert_called_with("/etc/network/interfaces", "w")
        mocked_open_file().write.assert_called_once_with(
            f"source-directory {network_configurator.INTERFACES_DIR}"
        )

    def test_given_agw_installer_network_configurator_when_static_eth0_address_given_then_correct_eth0_configuration_is_returned(  # noqa: E501
        self,
    ):
        test_static_ip_address = "1.2.3.4/24"
        test_static_gw_ip_address = "4.3.2.1"
        expected_config = [
            "auto eth0",
            "iface eth0 inet static",
            "address 1.2.3.4",
            "netmask 255.255.255.0",
            "gateway 4.3.2.1",
        ]
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES,
            test_static_ip_address,
            test_static_gw_ip_address,
        )
        self.assertEqual(agw_network_configurator._eth0_config, expected_config)

    @patch(
        "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator.INTERFACES_DIR",  # noqa: E501
        ".tox/.tmp",
    )
    def test_given_agw_installer_network_configurator_when_static_eth0_address_given_then_correct_message_is_logged_while_creating_interface_config_file(  # noqa: E501
        self,
    ):
        test_static_ip_address = "1.2.3.4/24"
        test_static_gw_ip_address = "4.3.2.1"
        with self.assertLogs() as logs:
            AGWInstallerNetworkConfigurator(
                self.TEST_NETWORK_INTERFACES,
                test_static_ip_address,
                test_static_gw_ip_address,
            )._prepare_eth0_configuration()
        self.assertEqual(
            logs.records[0].getMessage(),
            "Preparing configuration for SGi interface (eth0)...",
        )
        self.assertEqual(
            logs.records[1].getMessage(),
            f"Using statically configured IP {test_static_ip_address} "
            f"and Gateway {test_static_gw_ip_address}...",
        )

    def test_given_agw_installer_network_configurator_when_no_static_eth0_address_given_then_correct_eth0_configuration_is_returned(  # noqa: E501
        self,
    ):
        expected_config = [
            "auto eth0",
            "iface eth0 inet dhcp",
        ]
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES,
            None,
            None,
        )
        self.assertEqual(agw_network_configurator._eth0_config, expected_config)

    @patch(
        "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator.INTERFACES_DIR",  # noqa: E501
        ".tox/.tmp",
    )
    def test_given_agw_installer_network_configurator_when_no_static_eth0_address_given_then_correct_message_is_logged_while_creating_interface_config_file(  # noqa: E501
        self,
    ):
        with self.assertLogs() as logs:
            AGWInstallerNetworkConfigurator(
                self.TEST_NETWORK_INTERFACES,
                None,
                None,
            )._prepare_eth0_configuration()
        self.assertEqual(
            logs.records[0].getMessage(),
            "Preparing configuration for SGi interface (eth0)...",
        )
        self.assertEqual(
            logs.records[1].getMessage(),
            "Using DHCP allocated addresses...",
        )

    def test_given_agw_installer_network_configurator_when_configuring_eth1_interface_then_correct_eth1_configuration_is_returned(  # noqa: E501
        self,
    ):
        expected_config = [
            "auto eth1",
            "iface eth1 inet static",
            "address 10.0.2.1",
            "netmask 255.255.255.0",
        ]
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES,
            None,
            None,
        )
        self.assertEqual(agw_network_configurator._eth1_config, expected_config)

    @patch(
        "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator.INTERFACES_DIR",  # noqa: E501
        ".tox/.tmp",
    )
    def test_given_agw_installer_network_configurator_when_configuring_eth1_interface_then_correct_message_is_logged_while_creating_interface_config_file(  # noqa: E501
        self,
    ):
        with self.assertLogs() as logs:
            AGWInstallerNetworkConfigurator(
                self.TEST_NETWORK_INTERFACES,
                None,
                None,
            )._prepare_eth1_configuration()
        self.assertEqual(
            logs.records[0].getMessage(),
            "Preparing configuration for S1 interface (eth1)...",
        )

    def test_given_agw_installer_network_configurator_when_interfaces_are_named_eth0_and_eth1_then__network_interfaces_are_named_eth0_and_eth1_is_true(  # noqa: E501
        self,
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES,
            None,
            None,
        )
        self.assertTrue(agw_network_configurator._network_interfaces_are_named_eth0_and_eth1)

    def test_given_agw_installer_network_configurator_when_interfaces_are_not_named_eth0_and_eth1_then_network_interfaces_are_named_eth0_and_eth1_is_false(  # noqa: E501
        self,
    ):
        incorrect_interfaces_names_sets = [
            ["eth0", "test1"],
            ["test1", "eth1"],
            ["test1", "test2"],
        ]
        for incorrect_interfaces_names_set in incorrect_interfaces_names_sets:
            agw_network_configurator = AGWInstallerNetworkConfigurator(
                incorrect_interfaces_names_set,
                None,
                None,
            )
            self.assertFalse(agw_network_configurator._network_interfaces_are_named_eth0_and_eth1)

    def test_given_agw_installer_network_configurator_when_update_interfaces_names_in_cloud_init_is_called_then_interfaces_names_in_cloud_init_file_are_updated_correctly(  # noqa: E501
        self,
    ):
        mocked_cloud_init_content = {
            "network": {
                "ethernets": {
                    "test_if_name": {
                        "dhcp4": True,
                        "dhcp6": False,
                        "match": {"macaddress": "02:45:b8:e6:23:c6"},
                        "set-name": "test_if_name",
                    }
                },
                "version": 2,
            }
        }
        expected_cloud_init_file_write_calls = [
            call("network"),
            call(":"),
            call("\n"),
            call("  "),
            call("ethernets"),
            call(":"),
            call("\n"),
            call("    "),
            call("eth0"),
            call(":"),
            call("\n"),
            call("      "),
            call("dhcp4"),
            call(":"),
            call(" "),
            call("true"),
            call("\n"),
            call("      "),
            call("dhcp6"),
            call(":"),
            call(" "),
            call("false"),
            call("\n"),
            call("      "),
            call("match"),
            call(":"),
            call("\n"),
            call("        "),
            call("macaddress"),
            call(":"),
            call(" "),
            call("02:45:b8:e6:23:c6"),
            call("\n"),
            call("      "),
            call("set-name"),
            call(":"),
            call(" "),
            call("eth0"),
            call("\n"),
            call("  "),
            call("version"),
            call(":"),
            call(" "),
            call("2"),
            call("\n"),
        ]
        with patch(
            "magma_access_gateway_installer.agw_network_configurator.open",
            mock_open(),
        ) as mocked_open_file, patch(
            "magma_access_gateway_installer.agw_network_configurator.yaml.safe_load",
            Mock(return_value=mocked_cloud_init_content),
        ):
            agw_network_configurator = AGWInstallerNetworkConfigurator(
                self.TEST_NETWORK_INTERFACES, None, None
            )
            agw_network_configurator._update_interfaces_names_in_cloud_init()
            mocked_open_file_calls = mocked_open_file.mock_calls
            self.assertTrue(
                call(agw_network_configurator.CLOUD_INIT_YAML_PATH, "r") in mocked_open_file_calls
            )
            self.assertTrue(
                call(agw_network_configurator.CLOUD_INIT_YAML_PATH, "w") in mocked_open_file_calls
            )
            mocked_open_file().write.assert_has_calls(expected_cloud_init_file_write_calls)

    def test_given_agw_installer_network_configurator_when_configure_grub_is_called_then_required_parameters_are_added_to_etc_default_grub(  # noqa: E501
        self,
    ):
        mocked_etc_default_grub_content = """GRUB_DEFAULT=0
GRUB_TIMEOUT_STYLE=hidden
GRUB_TIMEOUT=0
GRUB_DISTRIBUTOR=`lsb_release -i -s 2> /dev/null || echo Debian`
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
GRUB_CMDLINE_LINUX=""

# Uncomment to enable BadRAM filtering, modify to suit your needs
# This works with Linux (no patch required) and with any kernel that obtains
# the memory map information from GRUB (GNU Mach, kernel of FreeBSD ...)
#GRUB_BADRAM="0x01234567,0xfefefefe,0x89abcdef,0xefefefef"

# Uncomment to disable graphical terminal (grub-pc only)
GRUB_TERMINAL=console

# The resolution used on graphical terminal
# note that you can use only modes which your graphic card supports via VBE
# you can see them in real GRUB with the command `vbeinfo'
#GRUB_GFXMODE=640x480

# Uncomment if you don't want GRUB to pass "root=UUID=xxx" parameter to Linux
#GRUB_DISABLE_LINUX_UUID=true

# Uncomment to disable generation of recovery mode menu entries
#GRUB_DISABLE_RECOVERY="true"

# Uncomment to get a beep at grub start
#GRUB_INIT_TUNE="480 440 1"
"""
        expected_etc_default_grub_content = """GRUB_DEFAULT=0
GRUB_TIMEOUT_STYLE=hidden
GRUB_TIMEOUT=0
GRUB_DISTRIBUTOR=`lsb_release -i -s 2> /dev/null || echo Debian`
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
GRUB_CMDLINE_LINUX="net.ifnames=0 biosdevname=0"

# Uncomment to enable BadRAM filtering, modify to suit your needs
# This works with Linux (no patch required) and with any kernel that obtains
# the memory map information from GRUB (GNU Mach, kernel of FreeBSD ...)
#GRUB_BADRAM="0x01234567,0xfefefefe,0x89abcdef,0xefefefef"

# Uncomment to disable graphical terminal (grub-pc only)
GRUB_TERMINAL=console

# The resolution used on graphical terminal
# note that you can use only modes which your graphic card supports via VBE
# you can see them in real GRUB with the command `vbeinfo'
#GRUB_GFXMODE=640x480

# Uncomment if you don't want GRUB to pass "root=UUID=xxx" parameter to Linux
#GRUB_DISABLE_LINUX_UUID=true

# Uncomment to disable generation of recovery mode menu entries
#GRUB_DISABLE_RECOVERY="true"

# Uncomment to get a beep at grub start
#GRUB_INIT_TUNE="480 440 1"
"""
        with patch(
            "magma_access_gateway_installer.agw_network_configurator.open",
            new=mock_open(read_data=mocked_etc_default_grub_content),
        ) as mocked_open_file:
            agw_network_configurator = AGWInstallerNetworkConfigurator(
                self.TEST_NETWORK_INTERFACES, None, None
            )
            agw_network_configurator._configure_grub()
            mocked_open_file_calls = mocked_open_file.mock_calls
            self.assertTrue(
                call(agw_network_configurator.ETC_DEFAULT_GRUB_PATH, "r") in mocked_open_file_calls
            )
            self.assertTrue(
                call(agw_network_configurator.ETC_DEFAULT_GRUB_PATH, "w") in mocked_open_file_calls
            )
            mocked_open_file().writelines.assert_called_once_with(
                [line + "\n" for line in expected_etc_default_grub_content.splitlines()]
            )

    @patch("magma_access_gateway_installer.agw_network_configurator.os", Mock())
    @patch("magma_access_gateway_installer.agw_network_configurator.check_call", Mock())
    def test_given_agw_installer_network_configurator_when_configure_dns_is_called_then_correct_dns_address_is_written_to_etc_systemd_resolved_conf(  # noqa: E501
        self,
    ):
        mocked_etc_systemd_resolved_conf_content = """[Resolve]
#DNS=
#FallbackDNS=
#Domains=
#LLMNR=no
#MulticastDNS=no
#DNSSEC=no
#DNSOverTLS=no
#Cache=no-negative
#DNSStubListener=yes
#ReadEtcHosts=yes
"""
        expected_etc_systemd_resolved_conf_content = """[Resolve]
DNS=8.8.8.8 208.67.222.222
#FallbackDNS=
#Domains=
#LLMNR=no
#MulticastDNS=no
#DNSSEC=no
#DNSOverTLS=no
#Cache=no-negative
#DNSStubListener=yes
#ReadEtcHosts=yes
"""
        with patch(
            "magma_access_gateway_installer.agw_network_configurator.open",
            new=mock_open(read_data=mocked_etc_systemd_resolved_conf_content),
        ) as mocked_open_file:
            network_configurator = AGWInstallerNetworkConfigurator(
                self.TEST_NETWORK_INTERFACES, None, None
            )
            network_configurator._configure_dns()
            mocked_open_file_calls = mocked_open_file.mock_calls
            self.assertTrue(
                call(network_configurator.ETC_SYSTEMD_RESOLVED_CONF_PATH, "r")
                in mocked_open_file_calls
            )
            self.assertTrue(
                call(network_configurator.ETC_SYSTEMD_RESOLVED_CONF_PATH, "w")
                in mocked_open_file_calls
            )
            mocked_open_file().writelines.assert_called_once_with(
                [line + "\n" for line in expected_etc_systemd_resolved_conf_content.splitlines()]
            )

    @patch("magma_access_gateway_installer.agw_network_configurator.os", Mock())
    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    def test_given_agw_installer_network_configurator_when_configure_dns_is_called_then_systemd_resolved_service_is_restarted(  # noqa: E501
        self, mock_check_call
    ):
        with patch(
            "magma_access_gateway_installer.agw_network_configurator.open",
            new=mock_open(),
        ):
            AGWInstallerNetworkConfigurator(
                self.TEST_NETWORK_INTERFACES, None, None
            )._configure_dns()
            mock_check_call.assert_called_once_with(["service", "systemd-resolved", "restart"])

    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    def test_given_agw_installer_network_configurator_when_update_grub_cfg_is_called_then_grub_mkconfig_command_is_run(  # noqa: E501
        self, mock_check_call
    ):
        network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES, None, None
        )
        network_configurator._update_grub_cfg()
        mock_check_call.assert_called_once_with(
            ["grub-mkconfig", "-o", network_configurator.BOOT_GRUB_GRUB_CFG_PATH]
        )

    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    def test_given_agw_installer_network_configurator_when_enable_networking_service_then_relevant_systemctl_command_are_run(  # noqa: E501
        self, mock_check_call
    ):
        expected_commands_to_be_called = [
            call(["systemctl", "unmask", "networking"]),
            call(["systemctl", "enable", "networking"]),
        ]
        AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES, None, None
        )._enable_networking_service()
        mock_check_call.assert_has_calls(expected_commands_to_be_called)

    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    def test_given_agw_installer_network_configurator_when_remove_netplan_is_called_then_relevant_apt_command_is_run(  # noqa: E501
        self, mock_check_call
    ):
        AGWInstallerNetworkConfigurator(self.TEST_NETWORK_INTERFACES, None, None)._remove_netplan()
        mock_check_call.assert_called_once_with(["apt", "remove", "-y", "--purge", "netplan.io"])

    def test_given_agw_installer_network_configurator_when_configure_network_interfaces_is_called_and_no_configuration_has_been_done_yet_then_entire_network_configuration_flow_is_executed(  # noqa: E501
        self,
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES,
            None,
            None,
        )
        with patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._network_interfaces_are_named_eth0_and_eth1",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._dns_configured",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._network_interfaces_config_files_exist",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch.object(
            agw_network_configurator, "_update_interfaces_names_in_cloud_init"
        ) as update_interfaces_names_in_cloud_init, patch.object(
            agw_network_configurator, "_configure_grub"
        ) as configure_grub, patch.object(
            agw_network_configurator, "_update_grub_cfg"
        ) as update_grub_cfg, patch.object(
            agw_network_configurator, "_configure_dns"
        ) as configure_dns, patch.object(
            agw_network_configurator, "_create_interfaces_config_files"
        ) as create_interfaces_config_files, patch.object(
            agw_network_configurator, "_remove_netplan"
        ) as remove_netplan, patch.object(
            agw_network_configurator, "_enable_networking_service"
        ) as enable_networking_service:
            agw_network_configurator.configure_network_interfaces()
        update_interfaces_names_in_cloud_init.assert_called_once()
        configure_grub.assert_called_once()
        update_grub_cfg.assert_called_once()
        configure_dns.assert_called_once()
        create_interfaces_config_files.assert_called_once()
        remove_netplan.assert_called_once()
        enable_networking_service.assert_called_once()

    def test_given_agw_installer_network_configurator_when_configure_network_interfaces_is_called_and_interfaces_are_named_correctly_then_network_configuration_flow_is_executed_without_renaming_interfaces(  # noqa: E501
        self,
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES,
            None,
            None,
        )
        with patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._network_interfaces_are_named_eth0_and_eth1",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._dns_configured",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._network_interfaces_config_files_exist",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch.object(
            agw_network_configurator, "_update_interfaces_names_in_cloud_init"
        ) as update_interfaces_names_in_cloud_init, patch.object(
            agw_network_configurator, "_configure_grub"
        ) as configure_grub, patch.object(
            agw_network_configurator, "_update_grub_cfg"
        ) as update_grub_cfg, patch.object(
            agw_network_configurator, "_configure_dns"
        ) as configure_dns, patch.object(
            agw_network_configurator, "_create_interfaces_config_files"
        ) as create_interfaces_config_files, patch.object(
            agw_network_configurator, "_remove_netplan"
        ) as remove_netplan, patch.object(
            agw_network_configurator, "_enable_networking_service"
        ) as enable_networking_service:
            agw_network_configurator.configure_network_interfaces()
        update_interfaces_names_in_cloud_init.assert_not_called()
        configure_grub.assert_not_called()
        update_grub_cfg.assert_not_called()
        configure_dns.assert_called_once()
        create_interfaces_config_files.assert_called_once()
        remove_netplan.assert_called_once()
        enable_networking_service.assert_called_once()

    def test_given_agw_installer_network_configurator_when_configure_network_interfaces_is_called_and_dns_is_configured_then_network_configuration_flow_is_executed_without_dns_configuration(  # noqa: E501
        self,
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES,
            None,
            None,
        )
        with patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._network_interfaces_are_named_eth0_and_eth1",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._dns_configured",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._network_interfaces_config_files_exist",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch.object(
            agw_network_configurator, "_update_interfaces_names_in_cloud_init"
        ) as update_interfaces_names_in_cloud_init, patch.object(
            agw_network_configurator, "_configure_grub"
        ) as configure_grub, patch.object(
            agw_network_configurator, "_update_grub_cfg"
        ) as update_grub_cfg, patch.object(
            agw_network_configurator, "_configure_dns"
        ) as configure_dns, patch.object(
            agw_network_configurator, "_create_interfaces_config_files"
        ) as create_interfaces_config_files, patch.object(
            agw_network_configurator, "_remove_netplan"
        ) as remove_netplan, patch.object(
            agw_network_configurator, "_enable_networking_service"
        ) as enable_networking_service:
            agw_network_configurator.configure_network_interfaces()
        update_interfaces_names_in_cloud_init.assert_called_once()
        configure_grub.assert_called_once()
        update_grub_cfg.assert_called_once()
        configure_dns.assert_not_called()
        create_interfaces_config_files.assert_called_once()
        remove_netplan.assert_called_once()
        enable_networking_service.assert_called_once()

    def test_given_agw_installer_network_configurator_when_configure_network_interfaces_is_called_and_interfaces_config_files_exist_then_network_configuration_flow_is_executed_without_creation_of_interfaces_config_files(  # noqa: E501
        self,
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES,
            None,
            None,
        )
        with patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._network_interfaces_are_named_eth0_and_eth1",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._dns_configured",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._network_interfaces_config_files_exist",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch.object(
            agw_network_configurator, "_update_interfaces_names_in_cloud_init"
        ) as update_interfaces_names_in_cloud_init, patch.object(
            agw_network_configurator, "_configure_grub"
        ) as configure_grub, patch.object(
            agw_network_configurator, "_update_grub_cfg"
        ) as update_grub_cfg, patch.object(
            agw_network_configurator, "_configure_dns"
        ) as configure_dns, patch.object(
            agw_network_configurator, "_create_interfaces_config_files"
        ) as create_interfaces_config_files, patch.object(
            agw_network_configurator, "_remove_netplan"
        ) as remove_netplan, patch.object(
            agw_network_configurator, "_enable_networking_service"
        ) as enable_networking_service:
            agw_network_configurator.configure_network_interfaces()
        update_interfaces_names_in_cloud_init.assert_called_once()
        configure_grub.assert_called_once()
        update_grub_cfg.assert_called_once()
        configure_dns.assert_called_once()
        create_interfaces_config_files.assert_not_called()
        remove_netplan.assert_called_once()
        enable_networking_service.assert_called_once()

    def test_given_agw_installer_network_configurator_when_configure_network_interfaces_is_called_and_netplan_is_not_installed_then_network_configuration_flow_is_executed_without_netplan_uninstallation(  # noqa: E501
        self,
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES,
            None,
            None,
        )
        with patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._network_interfaces_are_named_eth0_and_eth1",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._dns_configured",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._network_interfaces_config_files_exist",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch.object(
            agw_network_configurator, "_update_interfaces_names_in_cloud_init"
        ) as update_interfaces_names_in_cloud_init, patch.object(
            agw_network_configurator, "_configure_grub"
        ) as configure_grub, patch.object(
            agw_network_configurator, "_update_grub_cfg"
        ) as update_grub_cfg, patch.object(
            agw_network_configurator, "_configure_dns"
        ) as configure_dns, patch.object(
            agw_network_configurator, "_create_interfaces_config_files"
        ) as create_interfaces_config_files, patch.object(
            agw_network_configurator, "_remove_netplan"
        ) as remove_netplan, patch.object(
            agw_network_configurator, "_enable_networking_service"
        ) as enable_networking_service:
            agw_network_configurator.configure_network_interfaces()
        update_interfaces_names_in_cloud_init.assert_called_once()
        configure_grub.assert_called_once()
        update_grub_cfg.assert_called_once()
        configure_dns.assert_called_once()
        create_interfaces_config_files.assert_called_once()
        remove_netplan.assert_not_called()
        enable_networking_service.assert_called_once()

    def test_given_agw_installer_network_configurator_when_configure_network_interfaces_is_called_and_networking_service_is_enabled_then_network_configuration_flow_is_executed_without_enabling_networking_service(  # noqa: E501
        self,
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES,
            None,
            None,
        )
        with patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._network_interfaces_are_named_eth0_and_eth1",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._dns_configured",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._network_interfaces_config_files_exist",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch.object(
            agw_network_configurator, "_update_interfaces_names_in_cloud_init"
        ) as update_interfaces_names_in_cloud_init, patch.object(
            agw_network_configurator, "_configure_grub"
        ) as configure_grub, patch.object(
            agw_network_configurator, "_update_grub_cfg"
        ) as update_grub_cfg, patch.object(
            agw_network_configurator, "_configure_dns"
        ) as configure_dns, patch.object(
            agw_network_configurator, "_create_interfaces_config_files"
        ) as create_interfaces_config_files, patch.object(
            agw_network_configurator, "_remove_netplan"
        ) as remove_netplan, patch.object(
            agw_network_configurator, "_enable_networking_service"
        ) as enable_networking_service:
            agw_network_configurator.configure_network_interfaces()
        update_interfaces_names_in_cloud_init.assert_called_once()
        configure_grub.assert_called_once()
        update_grub_cfg.assert_called_once()
        configure_dns.assert_called_once()
        create_interfaces_config_files.assert_called_once()
        remove_netplan.assert_called_once()
        enable_networking_service.assert_not_called()

    def test_given_agw_installer_network_configurator_when_configure_network_interfaces_is_called_and_no_steps_had_to_be_executed_then_reboot_needed_flag_is_set_to_false(  # noqa: E501
        self,
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES,
            None,
            None,
        )
        with patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._network_interfaces_are_named_eth0_and_eth1",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._dns_configured",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._network_interfaces_config_files_exist",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch.object(
            agw_network_configurator, "_update_interfaces_names_in_cloud_init"
        ), patch.object(
            agw_network_configurator, "_configure_grub"
        ), patch.object(
            agw_network_configurator, "_update_grub_cfg"
        ), patch.object(
            agw_network_configurator, "_configure_dns"
        ), patch.object(
            agw_network_configurator, "_create_interfaces_config_files"
        ), patch.object(
            agw_network_configurator, "_remove_netplan"
        ), patch.object(
            agw_network_configurator, "_enable_networking_service"
        ):
            agw_network_configurator.configure_network_interfaces()
        self.assertFalse(agw_network_configurator.reboot_needed)

    def test_given_agw_installer_network_configurator_when_update_interfaces_names_in_cloud_init_is_called_then_reboot_needed_is_set_to_true(  # noqa: E501
        self,
    ):
        mocked_cloud_init_content = {
            "network": {
                "ethernets": {
                    "test_if_name": {
                        "dhcp4": True,
                        "dhcp6": False,
                        "match": {"macaddress": "02:45:b8:e6:23:c6"},
                        "set-name": "test_if_name",
                    }
                },
                "version": 2,
            }
        }
        with patch(
            "magma_access_gateway_installer.agw_network_configurator.open",
            mock_open(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.yaml.safe_load",
            Mock(return_value=mocked_cloud_init_content),
        ):
            agw_network_configurator = AGWInstallerNetworkConfigurator(
                self.TEST_NETWORK_INTERFACES, None, None
            )
            agw_network_configurator._update_interfaces_names_in_cloud_init()
        self.assertTrue(agw_network_configurator.reboot_needed)

    @patch("magma_access_gateway_installer.agw_network_configurator.check_output")
    def test_given_agw_installer_network_configurator_when_netplan_is_installed_then_netplan_installed_returns_true(  # noqa: E501
        self, mock_check_output
    ):
        mock_check_output.return_value = """nano/focal,now 4.8-1ubuntu1 amd64 [installed,automatic]
ncurses-base/focal,now 6.2-0ubuntu2 all [installed]
ncurses-bin/focal,now 6.2-0ubuntu2 amd64 [installed]
ncurses-term/focal,now 6.2-0ubuntu2 all [installed]
netbase/focal,now 6.1 all [installed,automatic]
netcat-openbsd/focal,now 1.206-1ubuntu1 amd64 [installed,automatic]
netplan.io/now 0.103-0ubuntu5~20.04.3 amd64 [installed,upgradable to: 0.103-0ubuntu5~20.04.5]
networkd-dispatcher/focal-updates,now 2.1-2~ubuntu20.04.1 all [installed,automatic]
ntfs-3g/focal-updates,focal-security,now 1:2017.3.23AR.3-3ubuntu1.1 amd64 [installed,automatic]
open-iscsi/focal-updates,now 2.0.874-7.1ubuntu6.2 amd64 [installed,automatic]
open-vm-tools/focal,now 2:11.0.5-4 amd64 [installed,upgradable to: 2:11.3.0-2ubuntu0~ubuntu20.04.2]
openssh-client/now 1:8.2p1-4ubuntu0.3 amd64 [installed,upgradable to: 1:8.2p1-4ubuntu0.4]
openssh-server/now 1:8.2p1-4ubuntu0.3 amd64 [installed,upgradable to: 1:8.2p1-4ubuntu0.4]
openssh-sftp-server/now 1:8.2p1-4ubuntu0.3 amd64 [installed,upgradable to: 1:8.2p1-4ubuntu0.4]
openssl/now 1.1.1f-1ubuntu2.9 amd64 [installed,upgradable to: 1.1.1f-1ubuntu2.10]
"""
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES, None, None
        )
        self.assertTrue(agw_network_configurator._netplan_installed)

    @patch("magma_access_gateway_installer.agw_network_configurator.check_output")
    def test_given_agw_installer_network_configurator_when_netplan_is_not_installed_then_netplan_installed_returns_false(  # noqa: E501
        self, mock_check_output
    ):
        mock_check_output.return_value = """nano/focal,now 4.8-1ubuntu1 amd64 [installed,automatic]
ncurses-base/focal,now 6.2-0ubuntu2 all [installed]
ncurses-bin/focal,now 6.2-0ubuntu2 amd64 [installed]
ncurses-term/focal,now 6.2-0ubuntu2 all [installed]
netbase/focal,now 6.1 all [installed,automatic]
netcat-openbsd/focal,now 1.206-1ubuntu1 amd64 [installed,automatic]
networkd-dispatcher/focal-updates,now 2.1-2~ubuntu20.04.1 all [installed,automatic]
ntfs-3g/focal-updates,focal-security,now 1:2017.3.23AR.3-3ubuntu1.1 amd64 [installed,automatic]
open-iscsi/focal-updates,now 2.0.874-7.1ubuntu6.2 amd64 [installed,automatic]
open-vm-tools/focal,now 2:11.0.5-4 amd64 [installed,upgradable to: 2:11.3.0-2ubuntu0~ubuntu20.04.2]
openssh-client/now 1:8.2p1-4ubuntu0.3 amd64 [installed,upgradable to: 1:8.2p1-4ubuntu0.4]
openssh-server/now 1:8.2p1-4ubuntu0.3 amd64 [installed,upgradable to: 1:8.2p1-4ubuntu0.4]
openssh-sftp-server/now 1:8.2p1-4ubuntu0.3 amd64 [installed,upgradable to: 1:8.2p1-4ubuntu0.4]
openssl/now 1.1.1f-1ubuntu2.9 amd64 [installed,upgradable to: 1.1.1f-1ubuntu2.10]
"""
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES, None, None
        )
        self.assertFalse(agw_network_configurator._netplan_installed)

    @patch("magma_access_gateway_installer.agw_network_configurator.check_output")
    def test_given_agw_installer_network_configurator_when_networking_service_not_present_then_networking_service_enabled_returns_false(  # noqa: E501
        self, mock_check_output
    ):
        mock_check_output.return_value = """multi-user.target                              static          enabled  # noqa: E501
network-online.target                          static          enabled
paths.target                                   static          enabled
printer.target                                 static          enabled
reboot.target                                  disabled        enabled
remote-cryptsetup.target                       disabled        enabled
remote-fs.target                               enabled         enabled
rescue-ssh.target                              static          enabled
runlevel0.target                               disabled        enabled
runlevel1.target                               static          enabled
""".encode()
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES, None, None
        )
        self.assertFalse(agw_network_configurator._networking_service_enabled)

    @patch("magma_access_gateway_installer.agw_network_configurator.check_output")
    def test_given_agw_installer_network_configurator_when_networking_service_present_but_disabled_then_networking_service_enabled_returns_false(  # noqa: E501
        self, mock_check_output
    ):
        mock_check_output.return_value = """multi-user.target                              static          enabled  # noqa: E501
network-online.target                          static          enabled
paths.target                                   static          enabled
printer.target                                 static          enabled
reboot.target                                  disabled        enabled
remote-cryptsetup.target                       disabled        enabled
networking.service                             disabled        disabled
remote-fs.target                               enabled         enabled
rescue-ssh.target                              static          enabled
runlevel0.target                               disabled        enabled
runlevel1.target                               static          enabled
""".encode()
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES, None, None
        )
        self.assertFalse(agw_network_configurator._networking_service_enabled)

    @patch("magma_access_gateway_installer.agw_network_configurator.check_output")
    def test_given_agw_installer_network_configurator_when_networking_service_present_and_enabled_then_networking_service_enabled_returns_true(  # noqa: E501
        self, mock_check_output
    ):
        mock_check_output.return_value = """multi-user.target                              static          enabled  # noqa: E501
network-online.target                          static          enabled
paths.target                                   static          enabled
printer.target                                 static          enabled
reboot.target                                  disabled        enabled
remote-cryptsetup.target                       disabled        enabled
networking.service                             enabled         enabled
remote-fs.target                               enabled         enabled
rescue-ssh.target                              static          enabled
runlevel0.target                               disabled        enabled
runlevel1.target                               static          enabled
""".encode()
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES, None, None
        )
        self.assertTrue(agw_network_configurator._networking_service_enabled)

    def test_given_agw_installer_network_configurator_when_create_interfaces_config_files_is_called_then_config_dir_and_config_files_creation_methods_are_called(  # noqa: E501
        self,
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES,
            None,
            None,
        )
        with patch.object(
            agw_network_configurator, "_prepare_interfaces_configuration_dir_if_doesnt_exist"
        ) as prepare_interfaces_configuration_dir_if_doesnt_exist, patch.object(
            agw_network_configurator, "_prepare_eth0_configuration"
        ) as prepare_eth0_configuration, patch.object(
            agw_network_configurator, "_prepare_eth1_configuration"
        ) as prepare_eth1_configuration:
            agw_network_configurator._create_interfaces_config_files()
        prepare_interfaces_configuration_dir_if_doesnt_exist.assert_called_once()
        prepare_eth0_configuration.assert_called_once()
        prepare_eth1_configuration.assert_called_once()

    @patch(
        "magma_access_gateway_installer.agw_network_configurator.os.path.exists",
        Mock(return_value=False),
    )
    def test_given_agw_installer_network_configurator_when_network_interfaces_config_files_exist_is_called_and_paths_dont_exist_then_network_interfaces_config_files_exist_returns_false(  # noqa: E501
        self,
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES, None, None
        )
        self.assertFalse(agw_network_configurator._network_interfaces_config_files_exist)

    @patch(
        "magma_access_gateway_installer.agw_network_configurator.os.path.exists",
        Mock(return_value=True),
    )
    def test_given_agw_installer_network_configurator_when_network_interfaces_config_files_exist_is_called_and_paths_exist_then_network_interfaces_config_files_exist_returns_true(  # noqa: E501
        self,
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.TEST_NETWORK_INTERFACES, None, None
        )
        self.assertTrue(agw_network_configurator._network_interfaces_config_files_exist)

    def test_given_agw_installer_network_configurator_when_network_interfaces_config_files_exist_is_called_and_only_one_path_exists_then_network_interfaces_config_files_exist_returns_false(  # noqa: E501
        self,
    ):
        with patch(
            "magma_access_gateway_installer.agw_network_configurator.os.path.exists",
            self._mocked_os_path_exist,
        ):
            agw_network_configurator = AGWInstallerNetworkConfigurator(
                self.TEST_NETWORK_INTERFACES, None, None
            )
            self.assertFalse(agw_network_configurator._network_interfaces_config_files_exist)

    def test_given_agw_installer_network_configurator_when_dns_has_already_been_configured_then_dns_configured_returns_true(  # noqa: E501
        self,
    ):
        mocked_etc_systemd_resolved_conf = """[Resolve]
DNS=8.8.8.8 208.67.222.222
#FallbackDNS=
#Domains=
#LLMNR=no
#MulticastDNS=no
#DNSSEC=no
#DNSOverTLS=no
#Cache=no-negative
#DNSStubListener=yes
#ReadEtcHosts=yes
        """
        with patch(
            "magma_access_gateway_installer.agw_network_configurator.open",
            mock_open(read_data=mocked_etc_systemd_resolved_conf),
        ):
            agw_network_configurator = AGWInstallerNetworkConfigurator(
                self.TEST_NETWORK_INTERFACES, None, None
            )
            self.assertTrue(agw_network_configurator._dns_configured)

    def test_given_agw_installer_network_configurator_when_dns_has_not_been_configured_then_dns_configured_returns_false(  # noqa: E501
        self,
    ):
        mocked_etc_systemd_resolved_conf = """[Resolve]
#DNS=
#FallbackDNS=
#Domains=
#LLMNR=no
#MulticastDNS=no
#DNSSEC=no
#DNSOverTLS=no
#Cache=no-negative
#DNSStubListener=yes
#ReadEtcHosts=yes
        """
        with patch(
            "magma_access_gateway_installer.agw_network_configurator.open",
            mock_open(read_data=mocked_etc_systemd_resolved_conf),
        ):
            agw_network_configurator = AGWInstallerNetworkConfigurator(
                self.TEST_NETWORK_INTERFACES, None, None
            )
            self.assertFalse(agw_network_configurator._dns_configured)

    @staticmethod
    def _mocked_os_path_exist(path):
        return {
            "/etc/network/interfaces.d/eth0": True,
            "/etc/network/interfaces.d/eth1": False,
        }.get(path)
