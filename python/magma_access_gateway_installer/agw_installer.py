#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import os
import time
from subprocess import check_call, check_output

import ruamel.yaml

logger = logging.getLogger("magma_access_gateway_installer")


class AGWInstaller:
    MAGMA_VERSION = "focal-1.8.0"
    MAGMA_ARTIFACTORY = "linuxfoundation.jfrog.io/artifactory"
    MAGMA_AGW_RUNTIME_DEPENDENCIES = [
        "graphviz",
        "python-all",
        "module-assistant",
        "openssl",
        "dkms",
        "uuid-runtime",
        "ca-certificates",
    ]
    MAGMA_INTERFACES = ["gtp_br0", "mtr0", "uplink_br0", "ipfix0", "dhcp0"]
    PIPELINED_CONFIG_FILE = "/etc/magma/pipelined.yml"

    def install(self, unblock_local_ips: bool = False, no_reboot: bool = False):
        if self._magma_agw_installed:
            logger.info("Magma Access Gateway already installed. Exiting...")
            return
        else:
            logger.info("Starting Magma AGW deployment...")
            self.update_apt_cache()
            self.update_ca_certificates_package()
            self.forbid_usage_of_expired_dst_root_ca_x3_certificate()
            self.configure_apt_for_magma_agw_deb_package_installation()
            self.install_runtime_dependencies()
            self.preconfigure_wireshark_suid_property()
            self.install_magma_agw()
            self.start_open_vswitch()
            self.start_magma()
            if unblock_local_ips:
                self.unblock_local_ips()
            if no_reboot:
                logger.info(
                    "Magma AGW deployment completed successfully!\n"
                    "\t\t--no-reboot specified. To complete the installation process,\n"
                    "\t\tplease reboot manually.\n"
                    "\t\tOnce the system is online again, run magma-access-gateway.configure to "
                    "integrate Access Gateway with the Orchestrator."
                )
                return
            else:
                logger.info(
                    "Magma AGW deployment completed successfully!\n"
                    "\t\tSystem will now go down for the reboot to apply all changes.\n"
                    "\t\tOnce the system is online again, run magma-access-gateway.configure to "
                    "integrate Access Gateway with the Orchestrator."
                )
                time.sleep(5)
                os.system("reboot")

    @property
    def _magma_agw_installed(self) -> bool:
        """Checks whether Magma Access Gateway is already installed or not."""
        return "magma" in check_output(["apt", "-qq", "list", "--installed"]).decode()

    @staticmethod
    def update_apt_cache():
        """Updates apt cache."""
        logger.info("Updating apt cache...")
        check_call(["apt", "-qq", "update"])

    @staticmethod
    def update_ca_certificates_package():
        """Updates ca-certificates package"""
        logger.info("Updating ca-certificates package...")
        check_call(["apt", "-qq", "install", "ca-certificates"])

    def forbid_usage_of_expired_dst_root_ca_x3_certificate(self):
        """Forbids usage of mozilla/DST_Root_CA_X3.crt certificate."""
        if not self._expired_dst_root_ca_x3_certificate_forbidden:
            logger.info("Forbidding usage of expired mozilla/DST_Root_CA_X3.crt certificate...")
            self._forbid_usage_of_expired_dst_root_ca_x3_certificate()
            self._update_ca_certificates()

    @property
    def _expired_dst_root_ca_x3_certificate_forbidden(self) -> bool:
        """Checks whether mozilla/DST_Root_CA_X3.crt is forbidden or not."""
        with open("/etc/ca-certificates.conf", "r") as ca_certificates_file:
            ca_certificates_file_content = ca_certificates_file.readlines()
        for line in ca_certificates_file_content:
            if line.startswith("!mozilla/DST_Root_CA_X3.crt"):
                return True
        return False

    @staticmethod
    def _forbid_usage_of_expired_dst_root_ca_x3_certificate():
        """Comments out mozilla/DST_Root_CA_X3.crt certificate in /etc/ca-certificates.conf."""
        with open("/etc/ca-certificates.conf", "r") as ca_certificates_file:
            original_ca_certificates_file_content = ca_certificates_file.readlines()
        updated_ca_certificates_file_content = [
            line.replace(line, "!mozilla/DST_Root_CA_X3.crt\n")
            if line.startswith("mozilla/DST_Root_CA_X3.crt")
            else line
            for line in original_ca_certificates_file_content
        ]

        with open("/etc/ca-certificates.conf", "w") as updated_ca_certificates_file:
            updated_ca_certificates_file.writelines(updated_ca_certificates_file_content)

    @staticmethod
    def _update_ca_certificates():
        """Updates ca-certificates."""
        logger.info("Updating ca-certificates...")
        check_call(["update-ca-certificates"])

    def configure_apt_for_magma_agw_deb_package_installation(self):
        """Prepares apt repository for Magma AGW installation."""
        if not self._magma_apt_repository_configured:
            self._configure_apt_for_magma_agw_deb_package_installation()
            self.update_apt_cache()

    @property
    def _magma_apt_repository_configured(self) -> bool:
        """Checks whether Magma custom apt repository has already been configured."""
        return os.path.exists("/etc/apt/sources.list.d/magma.list")

    def _configure_apt_for_magma_agw_deb_package_installation(self):
        """Configures apt (repository and keys) to allow Magma AGW deb package installation."""
        self._configure_private_apt_repository_to_install_magma_agw_from()
        self._add_unvalidated_apt_signing_key()

    def _configure_private_apt_repository_to_install_magma_agw_from(self):
        """Creates an apt repository configuration to allow Magma AGW deb package installation."""
        logger.info("Configuring private apt repository for install Magma AGW from...")
        with open("/etc/apt/sources.list.d/magma.list", "w") as magma_private_apt_repo:
            magma_private_apt_repo.write(
                f"deb https://{self.MAGMA_ARTIFACTORY}/magma-packages {self.MAGMA_VERSION} main"
            )

    def _add_unvalidated_apt_signing_key(self):
        """Adds unvalidated apt signing key."""
        logger.info("Adding unvalidated apt signing key...")
        check_call(
            [
                "apt-key",
                "adv",
                "--fetch-keys",
                f"https://{self.MAGMA_ARTIFACTORY}/api/security/keypair/magmaci/public",
            ]
        )
        self._ignore_magma_apt_repository_ssl_cert()

    def _ignore_magma_apt_repository_ssl_cert(self):
        """Ignores Magma apt repository's SSL certificate."""
        logger.info("Ignoring Magma apt repository's SSL certificate...")
        ignore_cert = f"""Acquire::https::{self.MAGMA_ARTIFACTORY}/magma-packages {{
Verify-Peer "false";
Verify-Host "false";
}};
"""
        with open("/etc/apt/apt.conf.d/99insecurehttpsrepo", "w") as insecured_repo_host:
            insecured_repo_host.write(ignore_cert)

    def install_runtime_dependencies(self):
        """Installs Magma AGW's runtime dependencies using apt."""
        logger.info("Installing Magma AGW's runtime dependencies...")
        for required_package in self.MAGMA_AGW_RUNTIME_DEPENDENCIES:
            self._install_apt_package(required_package)

    @staticmethod
    def preconfigure_wireshark_suid_property():
        """Prevents Wireshark popup while installing Magma AGW."""
        configure_debconf_entry_command = 'echo "wireshark-common wireshark-common/install-setuid boolean true" | debconf-set-selections'  # noqa: E501
        check_call(configure_debconf_entry_command, shell=True)

    def install_magma_agw(self):
        """Installs Magma AGW's deb packages from the private apt repository."""
        logger.info("Installing Magma Access Gateway...")
        dpkg_options = ["force-overwrite", "force-confold", "force-confdef"]
        self._install_apt_package("magma", dpkg_options)

    def start_open_vswitch(self):
        """Start openvswitch-switch service."""
        self._start_service("openvswitch-switch")

    def start_magma(self):
        """Starts Magma AGW."""
        self._stop_service("magma@*")
        self._bring_up_magma_interfaces()
        self._start_service("magma@magma")

    def unblock_local_ips(self):
        """Unblocks access to AGW local IPs from UEs."""
        yaml = ruamel.yaml.YAML()
        logger.info("Unblocking AGW local IPs usage...")
        with open(self.PIPELINED_CONFIG_FILE, "r") as pipelined_config_orig:
            pipelined_config = yaml.load(pipelined_config_orig)
        pipelined_config["access_control"]["block_agw_local_ips"] = False
        with open(self.PIPELINED_CONFIG_FILE, "w") as pipelined_config_updated:
            yaml.dump(pipelined_config, pipelined_config_updated)

    def _bring_up_magma_interfaces(self):
        """Brings up interfaces created by Magma AGW."""
        for interface in self.MAGMA_INTERFACES:
            logger.info(f"Bringing up {interface} interface...")
            self._bring_up_interface(interface)

    @staticmethod
    def _install_apt_package(package_name, dpkg_options: list = None):  # type: ignore[assignment]
        """Installs package using apt."""
        logger.info(f"Installing {package_name} package...")
        apt_install_command = [
            "apt",
            "-qq",
            "install",
            "-y",
            "--no-install-recommends",
            package_name,
        ]
        if dpkg_options:
            for option in dpkg_options:
                apt_install_command.insert(1, f'-o "Dpkg::Options::=--{option}"')
        try:
            check_call(" ".join(apt_install_command), shell=True)
        except Exception as any_exception:
            logging.error(any_exception)
            raise any_exception

    @staticmethod
    def _bring_up_interface(interface_name):
        """Brings up interface using ifup command."""
        logger.info(f"Bringing up {interface_name}...")
        check_call(["ifup", interface_name])

    @staticmethod
    def _stop_service(service_name):
        """Stops system service."""
        logger.info(f"Stopping {service_name} service...")
        check_call(["service", service_name, "stop"])

    @staticmethod
    def _start_service(service_name):
        """Starts system service."""
        logger.info(f"Starting {service_name} service...")
        check_call(["service", service_name, "start"])
