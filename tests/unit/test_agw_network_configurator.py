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

    def test_given_agw_installer_network_configurator_when_configure_network_interfaces_is_called_and_no_steps_had_to_be_executed_then_reboot_is_not_needed(  # noqa: E501
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
        ):
            agw_network_configurator.configure_network_interfaces()
        self.assertFalse(agw_network_configurator.reboot_needed)

    def test_given_agw_installer_network_configurator_when_grub_config_needs_to_be_changed_then_reboot_is_needed(  # noqa: E501
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
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.check_call", Mock()
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.open", mock_open()
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.yaml.safe_load",
            Mock(return_value=mocked_cloud_init_content),
        ):
            agw_network_configurator.configure_network_interfaces()
        self.assertTrue(agw_network_configurator.reboot_needed)

    def test_given_agw_installer_network_configurator_when_dns_config_needs_to_be_changed_then_reboot_is_not_needed(  # noqa: E501
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
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.os", Mock()
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.check_call", Mock()
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.open", mock_open()
        ):
            agw_network_configurator.configure_network_interfaces()
        self.assertFalse(agw_network_configurator.reboot_needed)

    def test_given_agw_installer_network_configurator_when_network_interfaces_config_files_need_to_be_created_then_reboot_is_needed(  # noqa: E501
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
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._prepare_interfaces_configuration_dir_if_doesnt_exist",  # noqa: E501
            Mock(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._prepare_eth0_configuration",  # noqa: E501
            Mock(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._prepare_eth1_configuration",  # noqa: E501
            Mock(),
        ):
            agw_network_configurator.configure_network_interfaces()
        self.assertTrue(agw_network_configurator.reboot_needed)

    def test_given_agw_installer_network_configurator_when_netplan_needs_to_be_removed_then_reboot_is_not_needed(  # noqa: E501
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
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.check_call", Mock()
        ):
            agw_network_configurator.configure_network_interfaces()
        self.assertFalse(agw_network_configurator.reboot_needed)

    def test_given_agw_installer_network_configurator_when_networking_service_needs_to_be_enabled_then_reboot_is_not_needed(  # noqa: E501
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
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.check_call", Mock()
        ):
            agw_network_configurator.configure_network_interfaces()
        self.assertFalse(agw_network_configurator.reboot_needed)

    def test_given_agw_installer_network_configurator_when_network_interfaces_names_need_to_be_changed_then_interfaces_names_are_updated_in_cloud_init(  # noqa: E501
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
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._configure_grub",  # noqa: E501
            Mock(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._update_grub_cfg",  # noqa: E501
            Mock(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.open",
            mock_open(),
        ) as mocked_open_file, patch(
            "magma_access_gateway_installer.agw_network_configurator.yaml.safe_load",
            Mock(return_value=mocked_cloud_init_content),
        ):
            agw_network_configurator.configure_network_interfaces()
        mocked_open_file_calls = mocked_open_file.mock_calls
        self.assertTrue(
            call(agw_network_configurator.CLOUD_INIT_YAML_PATH, "r") in mocked_open_file_calls
        )
        self.assertTrue(
            call(agw_network_configurator.CLOUD_INIT_YAML_PATH, "w") in mocked_open_file_calls
        )
        mocked_open_file().write.assert_has_calls(expected_cloud_init_file_write_calls)

    def test_given_agw_installer_network_configurator_when_network_interfaces_names_need_to_be_changed_then_expected_parameters_are_added_to_etc_default_grub(  # noqa: E501
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
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._update_interfaces_names_in_cloud_init",  # noqa: E501
            Mock(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._update_grub_cfg",  # noqa: E501
            Mock(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.open",
            new=mock_open(read_data=mocked_etc_default_grub_content),
        ) as mocked_open_file:
            agw_network_configurator.configure_network_interfaces()
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

    def test_given_agw_installer_network_configurator_when_network_interfaces_names_need_to_be_changed_then_new_grub_config_is_created(  # noqa: E501
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
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._update_interfaces_names_in_cloud_init",  # noqa: E501
            Mock(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._configure_grub",  # noqa: E501
            Mock(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.check_call",
            Mock(),
        ) as mock_check_call:
            agw_network_configurator.configure_network_interfaces()
        mock_check_call.assert_called_once_with(
            ["grub-mkconfig", "-o", agw_network_configurator.BOOT_GRUB_GRUB_CFG_PATH]
        )

    def test_given_agw_installer_network_configurator_when_dns_config_needs_to_be_changed_then_correct_dns_ips_are_added_to_dns_config(  # noqa: E501
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
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.os", Mock()
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.check_call", Mock()
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.open",
            new=mock_open(read_data=mocked_etc_systemd_resolved_conf_content),
        ) as mocked_open_file:
            agw_network_configurator.configure_network_interfaces()
        mocked_open_file_calls = mocked_open_file.mock_calls
        self.assertTrue(
            call(agw_network_configurator.ETC_SYSTEMD_RESOLVED_CONF_PATH, "r")
            in mocked_open_file_calls
        )
        self.assertTrue(
            call(agw_network_configurator.ETC_SYSTEMD_RESOLVED_CONF_PATH, "w")
            in mocked_open_file_calls
        )
        mocked_open_file().writelines.assert_called_once_with(
            [line + "\n" for line in expected_etc_systemd_resolved_conf_content.splitlines()]
        )

    def test_given_agw_installer_network_configurator_when_network_interfaces_config_files_need_to_be_created_then_interfaces_configuration_dir_is_created(  # noqa: E501
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
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._prepare_eth0_configuration",  # noqa: E501
            Mock(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._prepare_eth1_configuration",  # noqa: E501
            Mock(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.open", mock_open()
        ), patch(
            "os.makedirs", Mock()
        ) as mock_makedirs:
            agw_network_configurator.configure_network_interfaces()
        mock_makedirs.assert_called_once_with(agw_network_configurator.INTERFACES_DIR)

    def test_given_agw_installer_network_configurator_when_network_interfaces_config_files_need_to_be_created_then_interfaces_configuration_dir_is_sourced_in_etc_network_interfaces(  # noqa: E501
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
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._prepare_eth0_configuration",  # noqa: E501
            Mock(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._prepare_eth1_configuration",  # noqa: E501
            Mock(),
        ), patch(
            "os.makedirs", Mock()
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.open", mock_open()
        ) as mock_open_file:
            agw_network_configurator.configure_network_interfaces()
        mock_open_file.assert_called_with("/etc/network/interfaces", "w")
        mock_open_file().write.assert_called_once_with(
            f"source-directory {agw_network_configurator.INTERFACES_DIR}"
        )

    def test_given_agw_installer_network_configurator_when_network_interfaces_config_files_need_to_be_created_and_dhcp_is_used_then_correct_eth0_configuration_is_created(  # noqa: E501
        self,
    ):
        expected_config = [
            "auto eth0\n",
            "iface eth0 inet dhcp\n",
        ]
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
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._prepare_interfaces_configuration_dir_if_doesnt_exist",  # noqa: E501
            Mock(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._prepare_eth1_configuration",  # noqa: E501
            Mock(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.open", mock_open()
        ) as mock_open_file:
            agw_network_configurator.configure_network_interfaces()
        mock_open_file.assert_called_with(f"{agw_network_configurator.INTERFACES_DIR}/eth0", "w")
        mock_open_file().writelines.assert_called_once_with(expected_config)

    def test_given_agw_installer_network_configurator_when_network_interfaces_config_files_need_to_be_created_and_static_addressing_is_used_then_correct_eth0_configuration_is_created(  # noqa: E501
        self,
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
            self.TEST_NETWORK_INTERFACES,
            test_static_ip_address,
            test_static_gw_ip_address,
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
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._prepare_interfaces_configuration_dir_if_doesnt_exist",  # noqa: E501
            Mock(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._prepare_eth1_configuration",  # noqa: E501
            Mock(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.open", mock_open()
        ) as mock_open_file:
            agw_network_configurator.configure_network_interfaces()
        mock_open_file.assert_called_with(f"{agw_network_configurator.INTERFACES_DIR}/eth0", "w")
        mock_open_file().writelines.assert_called_once_with(expected_config)

    def test_given_agw_installer_network_configurator_when_network_interfaces_config_files_need_to_be_created_then_correct_eth1_configuration_is_created(  # noqa: E501
        self,
    ):
        expected_config = [
            "auto eth1\n",
            "iface eth1 inet static\n",
            "address 10.0.2.1\n",
            "netmask 255.255.255.0\n",
        ]
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
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._netplan_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._prepare_interfaces_configuration_dir_if_doesnt_exist",  # noqa: E501
            Mock(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._prepare_eth0_configuration",  # noqa: E501
            Mock(),
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.open", mock_open()
        ) as mock_open_file:
            agw_network_configurator.configure_network_interfaces()
        mock_open_file.assert_called_with(f"{agw_network_configurator.INTERFACES_DIR}/eth1", "w")
        mock_open_file().writelines.assert_called_once_with(expected_config)

    def test_given_agw_installer_network_configurator_when_netplan_needs_to_be_removed_then_correct_command_is_executed(  # noqa: E501
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
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.AGWInstallerNetworkConfigurator._networking_service_enabled",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.check_call", Mock()
        ) as mock_check_call:
            agw_network_configurator.configure_network_interfaces()
        mock_check_call.assert_called_once_with(["apt", "remove", "-y", "--purge", "netplan.io"])

    def test_given_agw_installer_network_configurator_when_networking_service_needs_to_be_enabled_then_correct_commands_is_executed(  # noqa: E501
        self,
    ):
        expected_commands_to_be_called = [
            call(["systemctl", "unmask", "networking"]),
            call(["systemctl", "enable", "networking"]),
        ]
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
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_network_configurator.check_call", Mock()
        ) as mock_check_call:
            agw_network_configurator.configure_network_interfaces()
        mock_check_call.assert_has_calls(expected_commands_to_be_called)
