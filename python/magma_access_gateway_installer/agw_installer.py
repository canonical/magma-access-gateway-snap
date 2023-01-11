#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import os
import time
from subprocess import check_call, check_output

logger = logging.getLogger("magma_access_gateway_installer")


class AGWInstaller:

    MAGMA_VERSION = "focal-1.6.1"
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
    MAGMA_PACKAGES = [
        "/snap/magma-access-gateway/current/libopenvswitch_2.15.4-10-magma_amd64.deb",
        "/snap/magma-access-gateway/current/openvswitch-common_2.15.4-10-magma_amd64.deb",
        "/snap/magma-access-gateway/current/openvswitch-datapath-dkms_2.15.4-10-magma_all.deb",
        "/snap/magma-access-gateway/current/openvswitch-switch_2.15.4-10-magma_amd64.deb",
    ]
    MAGMA_INTERFACES = ["gtp_br0", "mtr0", "uplink_br0", "ipfix0", "dhcp0"]

    def install(self, no_reboot: bool = False):
        if self._magma_agw_installed:
            logger.info("Magma Access Gateway already installed. Exiting...")
            return
        else:
            logger.info("Starting Magma AGW deployment...")
            self.update_apt_cache()
            self.update_ca_certificates_package()
            self.forbid_usage_of_expired_dst_root_ca_x3_certificate()
            self.install_runtime_dependencies()
            self.preconfigure_wireshark_suid_property()
            self.install_magma_agw()
            self.start_open_vswitch()
            self.start_magma()
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
        for magma_package in self.MAGMA_PACKAGES:
            self._install_apt_package(magma_package, dpkg_options)

    def start_open_vswitch(self):
        """Start openvswitch-switch service."""
        self._start_service("openvswitch-switch")

    def start_magma(self):
        """Starts Magma AGW."""
        self._stop_service("magma@*")
        self._bring_up_magma_interfaces()
        self._start_service("magma@magma")

    def _bring_up_magma_interfaces(self):
        """Brings up interfaces created by Magma AGW."""
        for interface in self.MAGMA_INTERFACES:
            logger.info(f"Bringing up {interface} interface...")
            self._bring_up_interface(interface)

    @staticmethod
    def _install_apt_package(package_name: str, dpkg_options: list = None):
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
    def _bring_up_interface(interface_name: str):
        """Brings up interface using ifup command."""
        logger.info(f"Bringing up {interface_name}...")
        check_call(["ifup", interface_name])

    @staticmethod
    def _stop_service(service_name: str):
        """Stops system service."""
        logger.info(f"Stopping {service_name} service...")
        check_call(["service", service_name, "stop"])

    @staticmethod
    def _start_service(service_name: str):
        """Starts system service."""
        logger.info(f"Starting {service_name} service...")
        check_call(["service", service_name, "start"])
