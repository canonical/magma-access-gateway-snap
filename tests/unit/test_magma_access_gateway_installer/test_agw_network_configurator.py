#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from unittest.mock import Mock, PropertyMock, mock_open, patch

from magma_access_gateway_installer.agw_network_configurator import (
    AGWInstallerNetworkConfigurator,
)


class TestAGWInstallerNetworkConfigurator(unittest.TestCase):
    TEST_MAGMA_NETPLAN_CONFIG_FILE = "/this/is/test/netplan/config"
    DNS_TEST_NETWORK_CONFIG = {
        "dns_address": "1.2.3.4 5.6.7.8",
    }
    EMPTY_NETWORK_CONFIG = {
        "sgi_ipv4_address": None,
        "sgi_ipv4_gateway": None,
        "sgi_ipv6_address": None,
        "sgi_ipv6_gateway": None,
        "sgi_mac_address": None,
        "s1_mac_address": None,
        "dns_address": None,
    }
    DHCP_BASED_NETWORK_CONFIG = {
        "sgi_ipv4_address": None,
        "sgi_ipv4_gateway": None,
        "sgi_ipv6_address": None,
        "sgi_ipv6_gateway": None,
        "s1_ipv4_address": "10.9.8.7/24",
        "s1_ipv6_address": None,
        "sgi_mac_address": "aa:bb:cc:dd:ee:ff",
        "s1_mac_address": "ff:ee:dd:cc:bb:aa",
        "dns_address": None,
    }
    STATIC_IPv4_NETWORK_CONFIG = {
        "sgi_ipv4_address": "1.2.3.4/24",
        "sgi_ipv4_gateway": "5.6.7.8",
        "sgi_ipv6_address": None,
        "sgi_ipv6_gateway": None,
        "s1_ipv4_address": "10.9.8.7/24",
        "s1_ipv6_address": None,
        "sgi_mac_address": "aa:bb:cc:dd:ee:ff",
        "s1_mac_address": "ff:ee:dd:cc:bb:aa",
        "dns_address": None,
    }
    STATIC_DUALSTACK_NETWORK_CONFIG = {
        "sgi_ipv4_address": "1.2.3.4/24",
        "sgi_ipv4_gateway": "5.6.7.8",
        "sgi_ipv6_address": "aaaa:bbbb:cccc:dddd:1:2:3:4/64",
        "sgi_ipv6_gateway": "dddd:cccc:bbbb:aaaa:5:6:7:8",
        "s1_ipv4_address": "10.9.8.7/24",
        "s1_ipv6_address": "aaaa:bbbb:cccc:dddd:10:9:8:7/64",
        "sgi_mac_address": "aa:bb:cc:dd:ee:ff",
        "s1_mac_address": "ff:ee:dd:cc:bb:aa",
        "dns_address": None,
    }
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

    @patch(
        "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator.MAGMA_NETPLAN_CONFIG_FILE",  # noqa: E501
        new_callable=PropertyMock,
    )
    @patch("magma_access_gateway_installer.agw_network_configurator.open", new_callable=mock_open)
    @patch("magma_access_gateway_installer.agw_network_configurator.check_call", Mock())
    def test_given_dhcp_based_network_config_when_configure_network_interfaces_then_correct_netplan_config_is_created(  # noqa: E501
        self, mocked_open_file, mocked_magma_netplan_config_file
    ):
        exepected_magma_netplan_config = """# This is the network config written by magma-access-gateway snap
network:
  ethernets:
    eth0:
      dhcp4: true
      dhcp6: true
      match:
        macaddress: aa:bb:cc:dd:ee:ff
      set-name: eth0
    eth1:
      dhcp4: false
      dhcp6: false
      addresses:
        - 10.9.8.7/24
      match:
        macaddress: ff:ee:dd:cc:bb:aa
      set-name: eth1
  version: 2"""  # noqa: E501
        mocked_magma_netplan_config_file.return_value = self.TEST_MAGMA_NETPLAN_CONFIG_FILE
        agw_network_configurator = AGWInstallerNetworkConfigurator(self.DHCP_BASED_NETWORK_CONFIG)

        agw_network_configurator.configure_network_interfaces()

        mocked_open_file.assert_called_once_with(self.TEST_MAGMA_NETPLAN_CONFIG_FILE, "w")
        mocked_open_file().write.assert_called_once_with(exepected_magma_netplan_config)

    @patch(
        "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator.MAGMA_NETPLAN_CONFIG_FILE",  # noqa: E501
        new_callable=PropertyMock,
    )
    @patch("magma_access_gateway_installer.agw_network_configurator.open", new_callable=mock_open)
    @patch("magma_access_gateway_installer.agw_network_configurator.check_call", Mock())
    def test_given_static_ipv4_network_config_when_configure_network_interfaces_then_correct_netplan_config_is_created(  # noqa: E501
        self, mocked_open_file, mocked_magma_netplan_config_file
    ):
        exepected_magma_netplan_config = """# This is the network config written by magma-access-gateway snap
network:
  ethernets:
    eth0:
      dhcp4: false
      dhcp6: false
      addresses:
        - 1.2.3.4/24
      routes:
        - to: default
          via: 5.6.7.8
      match:
        macaddress: aa:bb:cc:dd:ee:ff
      set-name: eth0
    eth1:
      dhcp4: false
      dhcp6: false
      addresses:
        - 10.9.8.7/24
      match:
        macaddress: ff:ee:dd:cc:bb:aa
      set-name: eth1
  version: 2"""  # noqa: E501
        mocked_magma_netplan_config_file.return_value = self.TEST_MAGMA_NETPLAN_CONFIG_FILE
        agw_network_configurator = AGWInstallerNetworkConfigurator(self.STATIC_IPv4_NETWORK_CONFIG)

        agw_network_configurator.configure_network_interfaces()

        mocked_open_file.assert_called_once_with(self.TEST_MAGMA_NETPLAN_CONFIG_FILE, "w")
        mocked_open_file().write.assert_called_once_with(exepected_magma_netplan_config)

    @patch(
        "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator.MAGMA_NETPLAN_CONFIG_FILE",  # noqa: E501
        new_callable=PropertyMock,
    )
    @patch("magma_access_gateway_installer.agw_network_configurator.open", new_callable=mock_open)
    @patch("magma_access_gateway_installer.agw_network_configurator.check_call", Mock())
    def test_given_static_dualstack_network_config_when_configure_network_interfaces_then_correct_netplan_config_is_created(  # noqa: E501
        self, mocked_open_file, mocked_magma_netplan_config_file
    ):
        exepected_magma_netplan_config = """# This is the network config written by magma-access-gateway snap
network:
  ethernets:
    eth0:
      dhcp4: false
      dhcp6: false
      addresses:
        - 1.2.3.4/24
        - aaaa:bbbb:cccc:dddd:1:2:3:4/64
      routes:
        - to: default
          via: 5.6.7.8
          metric: 200
        - to: default
          via: dddd:cccc:bbbb:aaaa:5:6:7:8
          metric: 300
      match:
        macaddress: aa:bb:cc:dd:ee:ff
      set-name: eth0
    eth1:
      dhcp4: false
      dhcp6: false
      addresses:
        - 10.9.8.7/24
        - aaaa:bbbb:cccc:dddd:10:9:8:7/64
      match:
        macaddress: ff:ee:dd:cc:bb:aa
      set-name: eth1
  version: 2"""  # noqa: E501
        mocked_magma_netplan_config_file.return_value = self.TEST_MAGMA_NETPLAN_CONFIG_FILE
        agw_network_configurator = AGWInstallerNetworkConfigurator(
            self.STATIC_DUALSTACK_NETWORK_CONFIG
        )

        agw_network_configurator.configure_network_interfaces()

        mocked_open_file.assert_called_once_with(self.TEST_MAGMA_NETPLAN_CONFIG_FILE, "w")
        mocked_open_file().write.assert_called_once_with(exepected_magma_netplan_config)

    @patch(
        "magma_access_gateway_installer.agw_network_configurator.open",
        new_callable=mock_open,
        read_data=GOOD_DNS_CONFIG,
    )
    def test_given_dns_is_already_configured_when_configure_dns_then_no_config_is_written(
        self, mocked_open_file
    ):
        agw_network_configurator = AGWInstallerNetworkConfigurator(self.DNS_TEST_NETWORK_CONFIG)

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
        agw_network_configurator = AGWInstallerNetworkConfigurator(self.DNS_TEST_NETWORK_CONFIG)

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
        agw_network_configurator = AGWInstallerNetworkConfigurator(self.DNS_TEST_NETWORK_CONFIG)

        agw_network_configurator.configure_dns()

        mock_check_call.assert_called_once_with(["service", "systemd-resolved", "restart"])
