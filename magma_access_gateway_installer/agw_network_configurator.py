#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import os
from subprocess import check_call

import ipcalc  # type: ignore[import]
import yaml
from systemd.journal import JournalHandler  # type: ignore[import]

logger = logging.getLogger(__name__)
logger.addHandler(JournalHandler())
logger.setLevel(logging.INFO)


class AGWInstallerNetworkConfigurator:

    INTERFACES_DIR = "/etc/network/interfaces.d"
    REBOOT_NEEDED = False

    def __init__(self, network_interfaces, eth0_address, eth0_gw_ip_address):
        self.eth0_address = eth0_address
        self.eth0_gw_ip_address = eth0_gw_ip_address
        self.network_interfaces = network_interfaces

    def configure_network_interfaces(self):
        """Configures network interfaces if necessary."""
        if not self._network_interfaces_are_named_eth0_and_eth1:
            self._update_interfaces_names_in_cloud_init()
            self._configure_grub()
            self._update_grub_cfg()
        self._configure_dns()
        self._configure_interfaces()

    @property
    def _network_interfaces_are_named_eth0_and_eth1(self) -> bool:
        """Checks whether available network interfaces are named correctly."""
        return all(interface in self.network_interfaces for interface in ["eth0", "eth1"])

    @staticmethod
    def _configure_grub():
        """Adds required configuration to /etc/default/grub"""
        logger.info("Configuring /etc/default/grub...")
        original_grub_file = open("/etc/default/grub", "r")
        original_grub_file_content = original_grub_file.readlines()
        updated_grub_file_content = [
            line.replace(line, 'GRUB_CMDLINE_LINUX="net.ifnames=0 biosdevname=0"\n')
            if line.startswith("GRUB_CMDLINE_LINUX=")
            else line
            for line in original_grub_file_content
        ]
        original_grub_file.close()

        updated_grub_file = open("/etc/default/grub", "w")
        updated_grub_file.writelines(updated_grub_file_content)
        updated_grub_file.close()

    @staticmethod
    def _update_interfaces_names_in_cloud_init():
        """Changes names of network interfaces in /etc/netplan/50-cloud-init.yaml to ethX."""
        cloud_init_config_file = "/etc/netplan/50-cloud-init.yaml"
        with open(cloud_init_config_file, "r") as cloud_init_file:
            cloud_init_content = yaml.safe_load(cloud_init_file)

        cloud_init_interfaces = list(cloud_init_content["network"]["ethernets"].keys())
        for network_interface in cloud_init_interfaces:
            network_interface_index = cloud_init_interfaces.index(network_interface)
            logger.info(
                f"Changing interface name in {cloud_init_config_file}. "
                f"Old interface name: {network_interface} "
                f"New interface name: eth{network_interface_index}."
            )
            cloud_init_content["network"]["ethernets"][
                f"eth{network_interface_index}"
            ] = cloud_init_content["network"]["ethernets"][network_interface]
            del cloud_init_content["network"]["ethernets"][network_interface]
            cloud_init_content["network"]["ethernets"][f"eth{network_interface_index}"][
                "set-name"
            ] = f"eth{network_interface_index}"

        with open(cloud_init_config_file, "w") as cloud_init_file:
            yaml.dump(cloud_init_content, cloud_init_file)

    @staticmethod
    def _update_grub_cfg():
        """Updates /boot/grub/grub.cfg."""
        logger.info("Updating /boot/grub/grub.cfg...")
        check_call(["grub-mkconfig", "-o", "/boot/grub/grub.cfg"])

    @staticmethod
    def _configure_dns():
        """Configures Ubuntu's DNS."""
        logger.info("Configuring DNS...")
        try:
            os.symlink("/var/run/systemd/resolve/resolv.conf", "/etc/resolv.conf")
        except FileExistsError:
            os.remove("/etc/resolv.conf")
            os.symlink("/var/run/systemd/resolve/resolv.conf", "/etc/resolv.conf")
        original_resolved_conf_file = open("/etc/systemd/resolved.conf", "r")
        original_resolved_conf_file_content = original_resolved_conf_file.readlines()
        updated_resolved_conf_file_content = [
            line.replace(line, "DNS=8.8.8.8 208.67.222.222\n")
            if line.startswith("#DNS=")
            else line
            for line in original_resolved_conf_file_content
        ]
        original_resolved_conf_file.close()

        updated_resolved_conf_file = open("/etc/systemd/resolved.conf", "w")
        updated_resolved_conf_file.writelines(updated_resolved_conf_file_content)
        updated_resolved_conf_file.close()
        logger.info("Restarting systemd-resolved service...")
        check_call(["service", "systemd-resolved", "restart"])

    def _configure_interfaces(self):
        """Configures SGi and S1 AGW interfaces."""
        logger.info("Configuring SGi and S1 interfaces...")
        self._prepare_interfaces_configuration_dir_if_doesnt_exist()
        self._prepare_eth0_configuration()
        self._prepare_eth1_configuration()
        self._remove_netplan()
        self.REBOOT_NEEDED = True

    def _prepare_interfaces_configuration_dir_if_doesnt_exist(self):
        if not os.path.exists(self.INTERFACES_DIR):
            logger.info(f"Preparing interfaces configuration directory: {self.INTERFACES_DIR}...")
            os.makedirs(self.INTERFACES_DIR)
        with open("/etc/network/interfaces", "w") as interfaces_file:
            interfaces_file.write(f"source-directory {self.INTERFACES_DIR}")

    def _prepare_eth0_configuration(self):
        logger.info("Preparing configuration for SGi interface (eth0)...")
        if self.eth0_address:
            logger.info(
                f"Using statically configured IP {self.eth0_address} "
                f"and Gateway {self.eth0_gw_ip_address}..."
            )
        else:
            logger.info("Using DHCP allocated addresses...")
        with open(f"{self.INTERFACES_DIR}/eth0", "w") as eth0_config_file:
            eth0_config_file.writelines(line + "\n" for line in self._eth0_config)

    def _prepare_eth1_configuration(self):
        logger.info("Preparing configuration for S1 interface (eth1)...")
        with open(f"{self.INTERFACES_DIR}/eth1", "w") as eth1_config_file:
            eth1_config_file.writelines(line + "\n" for line in self._eth1_config)

    @staticmethod
    def _remove_netplan():
        logger.info("Removing netplan...")
        check_call(["systemctl", "unmask", "networking"])
        check_call(["systemctl", "enable", "networking"])
        check_call(["apt", "remove", "-y", "--purge", "netplan.io"])

    @property
    def _eth0_config(self) -> list:
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
        return [
            "auto eth1",
            "iface eth1 inet static",
            "address 10.0.2.1",
            "netmask 255.255.255.0",
        ]
