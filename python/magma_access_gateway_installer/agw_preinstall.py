#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
from subprocess import check_call, check_output

from .agw_installation_errors import (
    InvalidNumberOfInterfacesError,
    InvalidUserError,
    UnsupportedKernelVersionError,
    UnsupportedOSError,
)

logger = logging.getLogger("magma_access_gateway_installer")


class AGWInstallerPreinstall:
    REQUIRED_NUMBER_OF_NICS = 2
    REQUIRED_SYSTEM_PACKAGES = ["ifupdown", "net-tools", "sudo"]
    SUPPORTED_KERNEL_VERSION = "5.4.0"

    def __init__(self, network_interfaces: list):
        self.network_interfaces = network_interfaces

    def preinstall_checks(self):
        """Checks whether installation preconditions are met. If not, relevant errors are being
        logged and installation is cancelled.

        :raises:
            InvalidUserError: if installation wasn't started using root user
            UnsupportedOSException: if OS is not Ubuntu
            InvalidNumberOfInterfaces: if number of available network interfaces is different from
                expected
        """
        logger.info("Starting pre-install checks...")
        if not self._user_is_root:
            raise InvalidUserError()
        elif not self._ubuntu_is_installed:
            raise UnsupportedOSError()
        elif not self._kernel_version_is_supported:
            raise UnsupportedKernelVersionError()
        elif not self._required_amount_of_network_interfaces_is_available:
            raise InvalidNumberOfInterfacesError()
        else:
            logger.info("Magma AGW pre-install checks completed.")

    def install_required_system_packages(self):
        """Installs required system packages using apt."""
        logger.info("Updating apt cache...")
        check_call(["apt", "-qq", "update"])
        logger.info("Installing required system packages...")
        for required_package in self.REQUIRED_SYSTEM_PACKAGES:
            logger.info(f"Installing {required_package}")
            check_call(["apt", "-qq", "install", "-y", required_package])

    @property
    def _user_is_root(self) -> bool:
        """Check whether root user is used."""
        return check_output(["whoami"]).decode("utf-8").rstrip() == "root"

    @property
    def _ubuntu_is_installed(self) -> bool:
        """Checks whether installed OS is Ubuntu 20.04."""
        system_info = {}
        with open("/etc/os-release", "r") as etc_os_release:
            for line in etc_os_release:
                key, value = line.partition("=")[::2]
                system_info[key.strip()] = str(value.strip().replace('"', ""))
        return system_info["ID"].lower() == "ubuntu" and system_info["VERSION_ID"] == "20.04"

    @property
    def _required_amount_of_network_interfaces_is_available(self) -> bool:
        """Checks whether required amount of network interfaces has been attached."""
        return len(self.network_interfaces) >= self.REQUIRED_NUMBER_OF_NICS

    @property
    def _kernel_version_is_supported(self) -> bool:
        """Checks whether kernel version is supported."""
        kernel_version = check_output(["uname", "-r"]).decode("utf-8").rstrip()
        return self.SUPPORTED_KERNEL_VERSION in kernel_version
