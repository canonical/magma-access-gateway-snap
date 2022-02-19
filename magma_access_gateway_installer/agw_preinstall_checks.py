#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import platform
from subprocess import check_call

from systemd.journal import JournalHandler  # type: ignore[import]

from .agw_installation_errors import InvalidNumberOfInterfacesError, UnsupportedOSError

logger = logging.getLogger(__name__)
logger.addHandler(JournalHandler())
logger.setLevel(logging.INFO)


class AGWInstallerPreinstallChecks:

    REQUIRED_NUMBER_OF_NICS = 2
    REQUIRED_SYSTEM_PACKAGES = ["ifupdown", "net-tools", "sudo"]

    def __init__(self, network_interfaces: list):
        self.network_interfaces = network_interfaces

    def preinstall_checks(self):
        """Checks whether installation preconditions are met. If not, relevant errors are being
        logged and installation is cancelled.

        :raises:
            UnsupportedOSException: if OS is not Ubuntu
            InvalidNumberOfInterfaces: if number of available network interfaces is different from
                expected
        """
        if not self._ubuntu_is_installed:
            raise UnsupportedOSError()
        elif not self._required_amount_of_network_interfaces_is_available:
            raise InvalidNumberOfInterfacesError()
        else:
            logger.info("Magma AGW pre-install checks completed.")

    def install_required_system_packages(self):
        """Installs required system packages using apt."""
        logger.info("Updating apt cache...")
        check_call(["apt", "update"])
        logger.info("Installing required system packages...")
        for required_package in self.REQUIRED_SYSTEM_PACKAGES:
            logger.info(f"Installing {required_package}")
            check_call(["apt", "install", "-y", required_package])

    @property
    def _ubuntu_is_installed(self) -> bool:
        """Checks whether installed OS is Ubuntu."""
        return "Ubuntu" in platform.version()

    @property
    def _required_amount_of_network_interfaces_is_available(self) -> bool:
        """Checks whether required amount of network interfaces has been attached."""
        return len(self.network_interfaces) == self.REQUIRED_NUMBER_OF_NICS
