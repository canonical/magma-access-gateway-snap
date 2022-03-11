#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import os
from copy import deepcopy
from subprocess import check_call, check_output
from typing import Optional

import ipcalc  # type: ignore[import]
import yaml

logger = logging.getLogger("magma_access_gateway_installer")


class AGWInstallerNetworkConfigurator:

    DNS_ADDRESSES = "8.8.8.8 208.67.222.222"
    BOOT_GRUB_GRUB_CFG_PATH = "/boot/grub/grub.cfg"
    CLOUD_INIT_YAML_PATH = "/etc/netplan/50-cloud-init.yaml"
    ETC_DEFAULT_GRUB_PATH = "/etc/default/grub"
    ETC_SYSTEMD_RESOLVED_CONF_PATH = "/etc/systemd/resolved.conf"
    INTERFACES_DIR = "/etc/network/interfaces.d"

    def __init__(
        self,
        network_interfaces: list,
        eth0_address: Optional[str],
        eth0_gw_ip_address: Optional[str],
    ):
        self.eth0_address = eth0_address
        self.eth0_gw_ip_address = eth0_gw_ip_address
        self.network_interfaces = network_interfaces
        self.reboot_needed = False

    def update_interfaces_names(self):
        if not self._network_interfaces_are_named_eth0_and_eth1:
            self._update_interfaces_names_in_cloud_init()
            self._configure_grub()
            self._update_grub_cfg()

    def configure_dns(self):
        if not self._dns_configured:
            self._configure_dns()

    def create_interfaces_config_files(self):
        if not self._network_interfaces_config_files_exist:
            self._create_interfaces_config_files()

    def remove_netplan(self):
        if self._netplan_installed:
            self._remove_netplan()

    def enable_networking_service(self):
        if not self._networking_service_enabled:
            self._enable_networking_service()

    @property
    def _network_interfaces_are_named_eth0_and_eth1(self) -> bool:
        """Checks whether available network interfaces are named correctly."""
        return all(interface in self.network_interfaces for interface in ["eth0", "eth1"])

    def _update_interfaces_names_in_cloud_init(self):
        """Changes names of network interfaces in /etc/netplan/50-cloud-init.yaml to ethX."""
        with open(self.CLOUD_INIT_YAML_PATH, "r") as cloud_init_file:
            initial_cloud_init_content = yaml.safe_load(cloud_init_file)

        cloud_init_interfaces = list(initial_cloud_init_content["network"]["ethernets"].keys())
        modified_cloud_init_content = deepcopy(initial_cloud_init_content)
        for network_interface in cloud_init_interfaces:
            network_interface_index = cloud_init_interfaces.index(network_interface)
            logger.info(
                f"Changing interface name in {self.CLOUD_INIT_YAML_PATH}. "
                f"Old interface name: {network_interface} "
                f"New interface name: eth{network_interface_index}."
            )
            modified_cloud_init_content["network"]["ethernets"][
                f"eth{network_interface_index}"
            ] = modified_cloud_init_content["network"]["ethernets"][network_interface]
            del modified_cloud_init_content["network"]["ethernets"][network_interface]
            modified_cloud_init_content["network"]["ethernets"][f"eth{network_interface_index}"][
                "set-name"
            ] = f"eth{network_interface_index}"

        with open(self.CLOUD_INIT_YAML_PATH, "w") as cloud_init_file:
            yaml.dump(modified_cloud_init_content, cloud_init_file)

    def _configure_grub(self):
        """Adds required configuration to /etc/default/grub"""
        logger.info(f"Configuring {self.ETC_DEFAULT_GRUB_PATH}...")
        with open(self.ETC_DEFAULT_GRUB_PATH, "r") as original_grub_file:
            original_grub_file_content = original_grub_file.readlines()
        updated_grub_file_content = [
            line.replace(line, 'GRUB_CMDLINE_LINUX="net.ifnames=0 biosdevname=0"\n')
            if line.startswith("GRUB_CMDLINE_LINUX=")
            else line
            for line in original_grub_file_content
        ]

        with open(self.ETC_DEFAULT_GRUB_PATH, "w") as updated_grub_file:
            updated_grub_file.writelines(updated_grub_file_content)

    def _update_grub_cfg(self):
        """Updates /boot/grub/grub.cfg."""
        logger.info(f"Updating {self.BOOT_GRUB_GRUB_CFG_PATH}...")
        check_call(["grub-mkconfig", "-o", self.BOOT_GRUB_GRUB_CFG_PATH])
        self.reboot_needed = True

    @property
    def _dns_configured(self) -> bool:
        """Checks whether DNS has already been configured."""
        with open(self.ETC_SYSTEMD_RESOLVED_CONF_PATH, "r") as dns_config:
            for line in dns_config.readlines():
                if f"DNS={self.DNS_ADDRESSES}" in line:
                    return True
        return False

    def _configure_dns(self):
        """Configures Ubuntu's DNS."""
        logger.info("Configuring DNS...")
        try:
            os.symlink("/var/run/systemd/resolve/resolv.conf", "/etc/resolv.conf")
        except FileExistsError:
            os.remove("/etc/resolv.conf")
            os.symlink("/var/run/systemd/resolve/resolv.conf", "/etc/resolv.conf")
        with open(self.ETC_SYSTEMD_RESOLVED_CONF_PATH, "r") as original_resolved_conf_file:
            original_resolved_conf_file_content = original_resolved_conf_file.readlines()
        updated_resolved_conf_file_content = [
            line.replace(line, f"DNS={self.DNS_ADDRESSES}\n")
            if line.startswith("#DNS=") or line.startswith("DNS=")
            else line
            for line in original_resolved_conf_file_content
        ]

        with open(self.ETC_SYSTEMD_RESOLVED_CONF_PATH, "w") as updated_resolved_conf_file:
            updated_resolved_conf_file.writelines(updated_resolved_conf_file_content)

        logger.info("Restarting systemd-resolved service...")
        check_call(["service", "systemd-resolved", "restart"])

    @property
    def _network_interfaces_config_files_exist(self) -> bool:
        """Checks whether configuration files for eth0 and eth1 exist in {self.INTERFACES_DIR}."""
        return bool(
            os.path.exists(f"{self.INTERFACES_DIR}/eth0")
            and os.path.exists(f"{self.INTERFACES_DIR}/eth1")  # noqa W503
        )

    def _create_interfaces_config_files(self):
        """Configures SGi and S1 AGW interfaces."""
        logger.info("Configuring SGi and S1 interfaces...")
        self._prepare_interfaces_configuration_dir_if_doesnt_exist()
        self._prepare_eth0_configuration()
        self._prepare_eth1_configuration()
        self.reboot_needed = True

    def _prepare_interfaces_configuration_dir_if_doesnt_exist(self):
        """Creates a directory to store network interfaces configuration files."""
        if not os.path.exists(self.INTERFACES_DIR):
            logger.info(f"Preparing interfaces configuration directory: {self.INTERFACES_DIR}...")
            os.makedirs(self.INTERFACES_DIR)
        with open("/etc/network/interfaces", "w") as interfaces_file:
            interfaces_file.write(f"source-directory {self.INTERFACES_DIR}")

    def _prepare_eth0_configuration(self):
        """Creates eth0 configuration file under {self.INTERFACES_DIR}/eth0."""
        logger.info("Preparing configuration for SGi interface (eth0)...")
        if self.eth0_address:
            logger.info(
                f"Using statically configured IP {self.eth0_address} "
                f"and Gateway {self.eth0_gw_ip_address}..."
            )
        else:
            logger.info("Using DHCP allocated addresses...")
        eth0_configuration = [line + "\n" for line in self._eth0_config]
        with open(f"{self.INTERFACES_DIR}/eth0", "w") as eth0_config_file:
            eth0_config_file.writelines(eth0_configuration)

    def _prepare_eth1_configuration(self):
        """Creates eth1 configuration file under {self.INTERFACES_DIR}/eth1."""
        logger.info("Preparing configuration for S1 interface (eth1)...")
        eth1_configuration = [line + "\n" for line in self._eth1_config]
        with open(f"{self.INTERFACES_DIR}/eth1", "w") as eth1_config_file:
            eth1_config_file.writelines(eth1_configuration)

    @property
    def _networking_service_enabled(self) -> bool:
        return any(
            all(status in service for status in ["networking.service", "enabled"])
            for service in check_output(["systemctl", "list-unit-files"]).decode().splitlines()
        )

    @staticmethod
    def _enable_networking_service():
        """Enables networking service which replaces netplan."""
        logger.info("Enabling networking service...")
        check_call(["systemctl", "unmask", "networking"])
        check_call(["systemctl", "enable", "networking"])

    @property
    def _netplan_installed(self) -> bool:
        """Checks whether netplan is installed."""
        return "netplan.io" in str(check_output(["apt", "list", "--installed"]))

    @staticmethod
    def _remove_netplan():
        """Removes netplan."""
        logger.info("Removing netplan...")
        check_call(["apt", "remove", "-y", "--purge", "netplan.io"])

    @property
    def _eth0_config(self) -> list:
        """Returns eth0 interface configuration depending on ip address allocation
        type (static or DHCP)."""
        if self.eth0_address:
            eth0_ip_address = self.eth0_address.split("/")[0]
            eth0_subnet = str(ipcalc.Network(self.eth0_address).netmask())
            return [
                "auto eth0",
                "iface eth0 inet static",
                f"address {eth0_ip_address}",
                f"netmask {eth0_subnet}",
                f"gateway {self.eth0_gw_ip_address}",
            ]
        else:
            return [
                "auto eth0",
                "iface eth0 inet dhcp",
            ]

    @property
    def _eth1_config(self) -> list:
        """Returns eth1 interface configuration."""
        return [
            "auto eth1",
            "iface eth1 inet static",
            "address 10.0.2.1",
            "netmask 255.255.255.0",
        ]
