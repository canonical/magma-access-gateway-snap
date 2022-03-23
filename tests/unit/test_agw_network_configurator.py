#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import copy
import unittest
from unittest.mock import Mock, call, mock_open, patch

from magma_access_gateway_installer.agw_network_configurator import (
    AGWInstallerNetworkConfigurator,
)


class TestAGWInstallerNetworkConfigurator(unittest.TestCase):
    TEST_DNS_LIST = ["1.2.3.4", "5.6.7.8"]
    CORRECT_NETWORK_INTERFACES = ["eth0", "eth1"]
    INCORRECT_NETWORK_INTERFACES = ["test_if_name", "test_if_name_2"]
    GOOD_DNS_CONFIG = """[Resolve]
DNS=1.2.3.4 5.6.7.8
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
    BAD_DNS_CONFIG = """[Resolve]
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
    CLOUD_INIT_CONTENT_2_INTERFACES_ONLY = {
        "network": {
            "ethernets": {
                "test_if_name": {
                    "dhcp4": True,
                    "dhcp6": False,
                    "match": {"macaddress": "02:45:b8:e6:23:c6"},
                    "set-name": "test_if_name",
                },
                "test_if_name_2": {
                    "dhcp4": True,
                    "dhcp6": False,
                    "match": {"macaddress": "02:45:b8:e6:c6:23"},
                    "set-name": "test_if_name_2",
                },
            },
            "version": 2,
        }
    }
    CLOUD_INIT_CONTENT_MORE_INTERFACES = {
        "network": {
            "ethernets": {
                "test_if_name": {
                    "dhcp4": True,
                    "dhcp6": False,
                    "match": {"macaddress": "02:45:b8:e6:23:c6"},
                    "set-name": "test_if_name",
                },
                "test_if_name_2": {
                    "dhcp4": True,
                    "dhcp6": False,
                    "match": {"macaddress": "02:45:b8:e6:c6:23"},
                    "set-name": "test_if_name_2",
                },
                "test_if_name_3": {
                    "dhcp4": True,
                    "dhcp6": False,
                    "match": {"macaddress": "02:45:23:e6:c6:b8"},
                    "set-name": "test_if_name_3",
                },
                "test_if_name_4": {
                    "dhcp4": True,
                    "dhcp6": False,
                    "match": {"macaddress": "02:23:b8:e6:c6:45"},
                    "set-name": "test_if_name_4",
                },
            },
            "version": 2,
        }
    }
    TEST_SGi_INTERFACE = "test_if_name_2"
    TEST_S1_INTERFACE = "test_if_name_4"
    APT_LIST_WITH_NETPLAN = """netcat-openbsd/focal,now 1.206-1ubuntu1 amd64 [installed,automatic]
netpbm/focal,now 2:10.0-15.3build1 amd64 [installed,automatic]
netplan.io/focal-updates,now 0.103-0ubuntu5~20.04.5 amd64 [installed,automatic]
network-manager-gnome/focal-updates,now 1.8.24-1ubuntu3 amd64 [installed,automatic]
network-manager-openvpn-gnome/focal,now 1.8.12-1 amd64 [installed]
"""
    APT_LIST_WITHOUT_NETPLAN = """netcat-openbsd/focal,now 1.206-1ubuntu1 amd64 [installed,automatic]
netpbm/focal,now 2:10.0-15.3build1 amd64 [installed,automatic]
network-manager-gnome/focal-updates,now 1.8.24-1ubuntu3 amd64 [installed,automatic]
network-manager-openvpn-gnome/focal,now 1.8.12-1 amd64 [installed]
"""
    NETWORKING_SERVICE_ENABLED = b"""multipath-tools.service                        enabled         enabled
multipathd.service                             enabled         enabled
networkd-dispatcher.service                    enabled         enabled
networking.service                             enabled         enabled
nghttpx.service                                enabled         enabled
ondemand.service                               enabled         enabled
"""  # noqa: E501
    NETWORKING_SERVICE_DISABLED = b"""multipath-tools.service                        enabled         enabled
multipathd.service                             enabled         enabled
networkd-dispatcher.service                    enabled         enabled
networking.service                             disabled        disabled
nghttpx.service                                enabled         enabled
ondemand.service                               enabled         enabled
"""  # noqa: E501

    @patch("magma_access_gateway_installer.agw_network_configurator.open")
    def test_given_interfaces_have_correct_names_when_update_interfaces_names_then_no_config_is_written(  # noqa: E501
        self, mocked_open_file
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.update_interfaces_names()

        mocked_open_file.assert_not_called()

    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    def test_given_interfaces_have_correct_names_when_update_interfaces_names_then_grub_mkconfig_is_not_called(  # noqa: E501
        self, mock_check_call
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.update_interfaces_names()

        mock_check_call.assert_not_called()

    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    def test_given_interfaces_have_correct_names_when_update_interfaces_names_then_reboot_is_not_needed(  # noqa: E501
        self, _
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.update_interfaces_names()

        self.assertFalse(agw_network_configurator.reboot_needed)

    @patch("magma_access_gateway_installer.agw_network_configurator.yaml.dump")
    @patch(
        "magma_access_gateway_installer.agw_network_configurator.yaml.safe_load",
        return_value=copy.deepcopy(CLOUD_INIT_CONTENT_2_INTERFACES_ONLY),
    )
    @patch("magma_access_gateway_installer.agw_network_configurator.open", new_callable=mock_open)
    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    def test_given_interfaces_dont_have_correct_names_when_update_interfaces_names_then_netplan_config_file_is_updated(  # noqa: E501
        self, _, __, ___, mock_yaml_dump
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.INCORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )
        expected_cloud_init_content = {
            "network": {
                "ethernets": {
                    "eth0": {
                        "dhcp4": True,
                        "dhcp6": False,
                        "match": {"macaddress": "02:45:b8:e6:23:c6"},
                        "set-name": "eth0",
                    },
                    "eth1": {
                        "dhcp4": True,
                        "dhcp6": False,
                        "match": {"macaddress": "02:45:b8:e6:c6:23"},
                        "set-name": "eth1",
                    },
                },
                "version": 2,
            }
        }

        agw_network_configurator.update_interfaces_names()

        args, kwargs = mock_yaml_dump.call_args
        self.assertEqual(args[0], expected_cloud_init_content)
        self.assertEqual(mock_yaml_dump.call_count, 1)

    @patch("magma_access_gateway_installer.agw_network_configurator.yaml.dump")
    @patch(
        "magma_access_gateway_installer.agw_network_configurator.yaml.safe_load",
        return_value=copy.deepcopy(CLOUD_INIT_CONTENT_MORE_INTERFACES),
    )
    @patch("magma_access_gateway_installer.agw_network_configurator.open", new_callable=mock_open)
    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    def test_given_custom_sgi_and_s1_interfaces_names_when_update_interfaces_names_then_netplan_config_file_is_updated(  # noqa: E501
        self, _, __, ___, mock_yaml_dump
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.INCORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
            sgi_interface=self.TEST_SGi_INTERFACE,
            s1_interface=self.TEST_S1_INTERFACE,
        )
        expected_cloud_init_content = {
            "network": {
                "ethernets": {
                    "test_if_name": {
                        "dhcp4": True,
                        "dhcp6": False,
                        "match": {"macaddress": "02:45:b8:e6:23:c6"},
                        "set-name": "test_if_name",
                    },
                    "eth0": {
                        "dhcp4": True,
                        "dhcp6": False,
                        "match": {"macaddress": "02:45:b8:e6:c6:23"},
                        "set-name": "eth0",
                    },
                    "test_if_name_3": {
                        "dhcp4": True,
                        "dhcp6": False,
                        "match": {"macaddress": "02:45:23:e6:c6:b8"},
                        "set-name": "test_if_name_3",
                    },
                    "eth1": {
                        "dhcp4": True,
                        "dhcp6": False,
                        "match": {"macaddress": "02:23:b8:e6:c6:45"},
                        "set-name": "eth1",
                    },
                },
                "version": 2,
            }
        }

        agw_network_configurator.update_interfaces_names()

        args, kwargs = mock_yaml_dump.call_args
        self.assertEqual(args[0], expected_cloud_init_content)
        self.assertEqual(mock_yaml_dump.call_count, 1)

    @patch(
        "magma_access_gateway_installer.agw_network_configurator.yaml.safe_load",
        return_value=copy.deepcopy(CLOUD_INIT_CONTENT_2_INTERFACES_ONLY),
    )
    @patch("magma_access_gateway_installer.agw_network_configurator.open")
    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    def test_given_interfaces_dont_have_correct_names_when_update_interfaces_names_then_reboot_is_needed(  # noqa: E501
        self, _, __, ___
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.INCORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.update_interfaces_names()

        self.assertTrue(agw_network_configurator.reboot_needed)

    @patch(
        "magma_access_gateway_installer.agw_network_configurator.yaml.safe_load",
        return_value=CLOUD_INIT_CONTENT_2_INTERFACES_ONLY,
    )
    @patch("magma_access_gateway_installer.agw_network_configurator.open")
    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    def test_given_interfaces_dont_have_correct_names_when_update_interfaces_names_then_mkconfig_is_called(  # noqa: E501
        self, mock_check_call, _, __
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.INCORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.update_interfaces_names()

        mock_check_call.assert_called_once_with(
            ["grub-mkconfig", "-o", agw_network_configurator.BOOT_GRUB_GRUB_CFG_PATH]
        )

    @patch(
        "magma_access_gateway_installer.agw_network_configurator.open",
        new_callable=mock_open,
        read_data=GOOD_DNS_CONFIG,
    )
    def test_given_dns_is_already_configured_when_configure_dns_then_no_config_is_written(
        self, mocked_open_file
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.configure_dns()

        mocked_open_file().writelines.assert_not_called()

    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    @patch(
        "magma_access_gateway_installer.agw_network_configurator.open",
        new_callable=mock_open,
        read_data=BAD_DNS_CONFIG,
    )
    @patch("os.symlink")
    def test_given_dns_is_not_correctly_configured_when_configure_dns_then_dns_config_is_written(
        self, patch_symlink, mocked_open_file, _
    ):
        patch_symlink.return_value = True
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.configure_dns()

        mocked_open_file().writelines.assert_called_once_with(
            [line + "\n" for line in self.GOOD_DNS_CONFIG.splitlines()]
        )

    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    @patch(
        "magma_access_gateway_installer.agw_network_configurator.open",
        new_callable=mock_open,
        read_data=BAD_DNS_CONFIG,
    )
    @patch("os.symlink")
    def test_given_dns_is_not_correctly_configured_when_configure_dns_then_dns_service_is_restarted(  # noqa: E501
        self, patch_symlink, _, mock_check_call
    ):
        patch_symlink.return_value = True
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.configure_dns()

        mock_check_call.assert_called_once_with(["service", "systemd-resolved", "restart"])

    @patch("os.path.exists", Mock(return_value=True))
    @patch("os.makedirs", new_callable=Mock)
    @patch(
        "magma_access_gateway_installer.agw_network_configurator.open",
        new_callable=mock_open,
    )
    def test_given_network_interfaces_config_files_exist_when_create_interfaces_config_files_then_configuration_dir_is_not_being_created(  # noqa: E501
        self, _, mock_makedirs
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.create_interfaces_config_files()

        mock_makedirs.assert_not_called()

    @patch("os.path.exists", Mock(return_value=True))
    @patch("os.makedirs", new_callable=Mock)
    @patch(
        "magma_access_gateway_installer.agw_network_configurator.open",
        new_callable=mock_open,
    )
    def test_given_network_interfaces_config_files_exist_when_create_interfaces_config_files_then_no_configurations_are_written_to_any_file(  # noqa: E501
        self, mock_open_file, _
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.create_interfaces_config_files()

        mock_open_file.assert_not_called()

    @patch("os.path.exists", Mock(return_value=True))
    @patch("os.makedirs", new_callable=Mock)
    @patch(
        "magma_access_gateway_installer.agw_network_configurator.open",
        new_callable=mock_open,
    )
    def test_given_network_interfaces_config_files_exist_when_create_interfaces_config_files_then_reboot_is_not_needed(  # noqa: E501
        self, _, __
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.create_interfaces_config_files()

        self.assertFalse(agw_network_configurator.reboot_needed)

    @patch("os.path.exists", Mock(return_value=False))
    @patch("os.makedirs", new_callable=Mock)
    @patch(
        "magma_access_gateway_installer.agw_network_configurator.open",
        new_callable=mock_open,
    )
    def test_given_network_interfaces_config_files_dont_exist_when_create_interfaces_config_files_then_configuration_dir_created(  # noqa: E501
        self, _, mock_makedirs
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.create_interfaces_config_files()

        mock_makedirs.assert_called_once_with(agw_network_configurator.INTERFACES_DIR)

    @patch("os.path.exists", Mock(return_value=False))
    @patch("os.makedirs", new_callable=Mock)
    @patch(
        "magma_access_gateway_installer.agw_network_configurator.open",
        new_callable=mock_open,
    )
    def test_given_network_interfaces_config_files_dont_exist_and_dhcp_is_used_when_create_interfaces_config_files_then_eth0_is_configured_correctly(  # noqa: E501
        self, mock_open_file, _
    ):
        expected_config = [
            "auto eth0\n",
            "iface eth0 inet dhcp\n",
        ]
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.create_interfaces_config_files()

        self.assertTrue(call("/etc/network/interfaces.d/eth0", "w") in mock_open_file.mock_calls)
        self.assertTrue(call.writelines(expected_config) in mock_open_file().mock_calls)

    @patch("os.path.exists", Mock(return_value=False))
    @patch("os.makedirs", new_callable=Mock)
    @patch(
        "magma_access_gateway_installer.agw_network_configurator.open",
        new_callable=mock_open,
    )
    def test_given_network_interfaces_config_files_dont_exist_and_static_addressing_is_used_when_create_interfaces_config_files_then_eth0_is_configured_correctly(  # noqa: E501
        self, mock_open_file, _
    ):
        test_static_ip_address = "1.2.3.4/24"
        test_static_gw_ip_address = "4.3.2.1"
        expected_config = [
            "auto eth0\n",
            "iface eth0 inet static\n",
            "address 1.2.3.4\n",
            "netmask 255.255.255.0\n",
            "gateway 4.3.2.1\n",
        ]
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
            test_static_ip_address,
            test_static_gw_ip_address,
        )

        agw_network_configurator.create_interfaces_config_files()

        self.assertTrue(call("/etc/network/interfaces.d/eth0", "w") in mock_open_file.mock_calls)
        self.assertTrue(call.writelines(expected_config) in mock_open_file().mock_calls)

    @patch("os.path.exists", Mock(return_value=False))
    @patch("os.makedirs", new_callable=Mock)
    @patch(
        "magma_access_gateway_installer.agw_network_configurator.open",
        new_callable=mock_open,
    )
    def test_given_network_interfaces_config_files_dont_exist_when_create_interfaces_config_files_then_eth1_is_configured_correctly(  # noqa: E501
        self, mock_open_file, _
    ):
        expected_config = [
            "auto eth1\n",
            "iface eth1 inet static\n",
            "address 10.0.2.1\n",
            "netmask 255.255.255.0\n",
        ]
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.create_interfaces_config_files()

        self.assertTrue(call("/etc/network/interfaces.d/eth1", "w") in mock_open_file.mock_calls)
        self.assertTrue(call.writelines(expected_config) in mock_open_file().mock_calls)

    @patch("os.path.exists", Mock(return_value=False))
    @patch("os.makedirs", new_callable=Mock)
    @patch(
        "magma_access_gateway_installer.agw_network_configurator.open",
        new_callable=mock_open,
    )
    def test_given_network_interfaces_config_files_dont_exist_when_create_interfaces_config_files_then_reboot_is_needed(  # noqa: E501
        self, _, __
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.create_interfaces_config_files()

        self.assertTrue(agw_network_configurator.reboot_needed)

    @patch(
        "magma_access_gateway_installer.agw_network_configurator.check_output",
        return_value=APT_LIST_WITHOUT_NETPLAN,
    )
    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    def test_given_netplan_is_not_installed_when_remove_netplan_then_no_commands_are_executed(
        self, mock_check_call, _
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.remove_netplan()

        mock_check_call.assert_not_called()

    @patch(
        "magma_access_gateway_installer.agw_network_configurator.check_output",
        return_value=APT_LIST_WITH_NETPLAN,
    )
    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    def test_given_netplan_is_installed_when_remove_netplan_then_apt_remove_command_is_executed(
        self, mock_check_call, _
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.remove_netplan()

        mock_check_call.assert_called_once_with(["apt", "remove", "-y", "--purge", "netplan.io"])

    @patch(
        "magma_access_gateway_installer.agw_network_configurator.check_output",
        return_value=NETWORKING_SERVICE_ENABLED,
    )
    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    def test_given_networking_service_enabled_when_enable_networking_service_then_no_commands_are_executed(  # noqa: E501
        self, mock_check_call, _
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.enable_networking_service()

        mock_check_call.assert_not_called()

    @patch(
        "magma_access_gateway_installer.agw_network_configurator.check_output",
        return_value=NETWORKING_SERVICE_DISABLED,
    )
    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    def test_given_networking_service_disabled_when_enable_networking_service_then_relevant_systemctl_commands_are_executed(  # noqa: E501
        self, mock_check_call, _
    ):
        expected_calls = [
            call(["systemctl", "unmask", "networking"]),
            call(["systemctl", "enable", "networking"]),
        ]
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            self.TEST_DNS_LIST,
        )

        agw_network_configurator.enable_networking_service()

        mock_check_call.assert_has_calls(expected_calls)
