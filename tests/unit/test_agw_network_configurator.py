#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import copy
import unittest
from unittest.mock import mock_open, patch

from magma_access_gateway_installer.agw_network_configurator import (
    AGWInstallerNetworkConfigurator,
)


class TestAGWInstallerNetworkConfigurator(unittest.TestCase):
    CORRECT_NETWORK_INTERFACES = ["eth0", "eth1"]
    INCORRECT_NETWORK_INTERFACES = ["abc", "def"]

    GOOD_DNS_CONFIG = """[Resolve]
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

    CLOUD_INIT_CONTENT = {
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

    @patch("magma_access_gateway_installer.agw_network_configurator.open", new_callable=mock_open, read_data=GOOD_DNS_CONFIG)
    def test_given_dns_is_already_configured_when_configure_dns_then_no_config_is_written(self, mocked_open_file):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            None,
            None,
        )

        agw_network_configurator.configure_dns()

        mocked_open_file().writelines.assert_not_called()

    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    @patch("magma_access_gateway_installer.agw_network_configurator.open", new_callable=mock_open, read_data=BAD_DNS_CONFIG)
    @patch("os.symlink")
    def test_given_dns_is_not_correctly_configured_when_configure_dns_then_dns_config_is_written(self, patch_symlink, mocked_open_file, mock_check_call):
        patch_symlink.return_value = True

        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            None,
            None,
        )

        agw_network_configurator.configure_dns()

        mocked_open_file().writelines.assert_called_once_with(
            [line + "\n" for line in self.GOOD_DNS_CONFIG.splitlines()]
        )

    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    @patch("magma_access_gateway_installer.agw_network_configurator.open", new_callable=mock_open, read_data=BAD_DNS_CONFIG)
    @patch("os.symlink")
    def test_given_dns_is_not_correctly_configured_when_configure_dns_then_dns_service_is_restarted(self, patch_symlink, mocked_open_file, mock_check_call):
        patch_symlink.return_value = True

        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            None,
            None,
        )

        agw_network_configurator.configure_dns()

        mock_check_call.assert_called_once_with(['service', 'systemd-resolved', 'restart'])

    @patch("magma_access_gateway_installer.agw_network_configurator.open")
    def test_given_interfaces_have_correct_names_when_update_names_then_no_config_is_written(self, mocked_open_file):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            None,
            None,
        )

        agw_network_configurator.update_names()

        mocked_open_file.assert_not_called()

    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    def test_given_interfaces_have_correct_names_when_update_names_then_grub_mkconfig_is_not_called(self, mock_check_call):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.CORRECT_NETWORK_INTERFACES,
            None,
            None,
        )

        agw_network_configurator.update_names()

        mock_check_call.assert_not_called()

    @patch("magma_access_gateway_installer.agw_network_configurator.yaml.dump")
    @patch("magma_access_gateway_installer.agw_network_configurator.yaml.safe_load", return_value=copy.deepcopy(CLOUD_INIT_CONTENT))
    @patch("magma_access_gateway_installer.agw_network_configurator.open", new_callable=mock_open)
    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    def test_given_interfaces_dont_have_correct_names_when_update_names_then_grub_configuration_file_is_updated(self, mock_check_call, mock_open, mock_yaml_safe_load, mock_yaml_dump):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.INCORRECT_NETWORK_INTERFACES,
            None,
            None,
        )
        expected_cloud_init_content = {
            'network': {
                'ethernets': {
                    'eth0': {
                        'dhcp4': True,
                        'dhcp6': False,
                        'match': {
                            'macaddress': '02:45:b8:e6:23:c6'
                        },
                        'set-name': 'eth0'
                    }},
                'version': 2
            }
        }

        agw_network_configurator.update_names()

        args, kwargs = mock_yaml_dump.call_args
        self.assertEqual(args[0], expected_cloud_init_content)
        self.assertEqual(mock_yaml_dump.call_count, 1)

    @patch("magma_access_gateway_installer.agw_network_configurator.yaml.safe_load", return_value=CLOUD_INIT_CONTENT)
    @patch("magma_access_gateway_installer.agw_network_configurator.open")
    @patch("magma_access_gateway_installer.agw_network_configurator.check_call")
    def test_given_interfaces_dont_have_correct_names_when_update_names_then_mkconfig_is_called(self, mock_check_call, mock_open, mock_safe_load):
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.INCORRECT_NETWORK_INTERFACES,
            None,
            None,
        )

        agw_network_configurator.update_names()

        mock_check_call.assert_called_once_with(
            ["grub-mkconfig", "-o", agw_network_configurator.BOOT_GRUB_GRUB_CFG_PATH]
        )
