#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import os
import pathlib
from subprocess import check_call

from jinja2 import Environment, FileSystemLoader, Template

logger = logging.getLogger("magma_access_gateway_installer")


class AGWInstallerNetworkConfigurator:

    MAGMA_NETPLAN_CONFIG_FILE = "/etc/netplan/99-magma-config.yaml"
    MAGMA_NETPLAN_CONFIG_TEMPLATE = "netplan_config.yaml.j2"
    ETC_SYSTEMD_RESOLVED_CONF_PATH = "/etc/systemd/resolved.conf"
    CLOUDINIT_CONFIG_DIR = "/etc/cloud/cloud.cfg.d"

    def __init__(
        self,
        network_config: dict,
    ):
        self.network_config = network_config

    def configure_dns(self):
        """Configures specified DNS servers if needed."""
        if not self._dns_configured:
            self._configure_dns()

    def configure_network_interfaces(self):
        """Creates and applies network configuration required by Magma AGW."""
        self._create_netplan_config()

    def disable_cloudinit_network_management(self):
        """Disable network management by cloudinit."""
        cloudinit_dir = pathlib.Path(self.CLOUDINIT_CONFIG_DIR)
        cloudinit_dir.mkdir(parents=True, exist_ok=True)
        disable_network_conf = cloudinit_dir / "99-disable-network-config.cfg"
        disable_network_conf.write_text("network: {config: disabled}")

    @staticmethod
    def apply_netplan_configuration():
        """Applies newly created netplan configuration."""
        logger.info("Applying new netplan configuration...")
        check_call(["netplan", "apply"])

    def _create_netplan_config(self):
        """Creates netplan configuration file reflecting required network configuration."""
        netplan_config_template = self._load_netplan_config_template()
        with open(self.MAGMA_NETPLAN_CONFIG_FILE, "w") as magma_netplan_config:
            magma_netplan_config.write(
                netplan_config_template.render(
                    sgi_ipv4_address_cidr=self.network_config["sgi_ipv4_address_cidr"],
                    sgi_ipv4_gateway=self.network_config["sgi_ipv4_gateway"],
                    sgi_ipv6_address_cidr=self.network_config["sgi_ipv6_address_cidr"],
                    sgi_ipv6_gateway=self.network_config["sgi_ipv6_gateway"],
                    s1_ipv4_address_cidr=self.network_config["s1_ipv4_address_cidr"],
                    s1_ipv4_address=self.network_config["s1_ipv4_address"],
                    s1_ipv4_gateway=self.network_config["s1_ipv4_gateway"],
                    s1_ipv6_address_cidr=self.network_config["s1_ipv6_address_cidr"],
                    s1_ipv6_address=self.network_config["s1_ipv6_address"],
                    s1_ipv6_gateway=self.network_config["s1_ipv6_gateway"],
                    sgi_mac_address=self.network_config["sgi_mac_address"],
                    s1_mac_address=self.network_config["s1_mac_address"],
                ),
            )

    def _load_netplan_config_template(self) -> Template:
        file_loader = FileSystemLoader(
            os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
        )
        env = Environment(loader=file_loader)
        return env.get_template(self.MAGMA_NETPLAN_CONFIG_TEMPLATE)

    @property
    def _dns_configured(self) -> bool:
        """Checks whether DNS has already been configured."""
        with open(self.ETC_SYSTEMD_RESOLVED_CONF_PATH, "r") as dns_config_file:
            dns_config = dns_config_file.readlines()
        return all(
            [
                any(
                    dns_ip in line
                    for line in dns_config
                    if line.startswith("DNS=") or line.startswith("FallbackDNS=")
                )
                for dns_ip in self.network_config["dns_address"]
            ]
        )

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
            line.replace(line, f"DNS={self.network_config['dns_address']}\n")
            if line.startswith("#DNS=") or line.startswith("DNS=")
            else line
            for line in original_resolved_conf_file_content
        ]

        with open(self.ETC_SYSTEMD_RESOLVED_CONF_PATH, "w") as updated_resolved_conf_file:
            updated_resolved_conf_file.writelines(updated_resolved_conf_file_content)

        logger.info("Restarting systemd-resolved service...")
        check_call(["service", "systemd-resolved", "restart"])
