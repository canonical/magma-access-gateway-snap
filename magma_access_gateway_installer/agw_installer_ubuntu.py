#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

""" The Access Gateway (AGW) provides network services and policy enforcement. In an LTE network,
  the AGW implements an evolved packet core (EPC), and a combination of an AAA and a PGW. It works
  with existing, unmodified commercial radio hardware.
  For detailed description visit https://docs.magmacore.org/docs/next/lte/architecture_overview.
"""

import logging
import os
import platform
import pwd

import netifaces  # type: ignore[import]
from systemd.journal import JournalHandler  # type: ignore[import]

from .agw_installation_errors import InvalidNumberOfInterfacesError, UnsupportedOSError

logger = logging.getLogger(__name__)
logger.addHandler(JournalHandler())
logger.setLevel(logging.INFO)


class AGWInstallerUbuntu:
    """Main class of Magma Access Gateway installer for Ubuntu."""

    MAGMA_USER = "magma"
    REQUIRED_NUMBER_OF_NICS = 2

    def __init__(self):
        self.network_interfaces = netifaces.interfaces()
        self.network_interfaces.remove("lo")

    def preinstall_checks(self):
        """Checks whether installation preconditions are met. If not, relevant errors are being
        logged and installation is cancelled.

        :raises:
            UnsupportedOSException: if OS is not Ubuntu
            InvalidNumberOfInterfaces: if number of available network interfaces is different from
                expected
        """
        if not self._ubuntu_is_installed:
            logger.error("Invalid OS! \n Magma AGW can only be installed on Ubuntu! Exiting...")
            raise UnsupportedOSError()
        elif not self._required_amount_of_network_interfaces_is_available:
            logger.error(
                "Invalid number of network interfaces!"
                "Magma AGW needs two network interfaces - SGi and S1! Exiting..."
            )
            raise InvalidNumberOfInterfacesError()
        else:
            logger.info("Magma AGW pre-install checks completed. Starting installation...")

    def magma_service_user_creation(self):
        """Creates and configures Magma service user if necessary."""
        if not self._magma_user_exists:
            self._create_magma_user()
            self._add_magma_user_to_sudoers()

    @property
    def _ubuntu_is_installed(self) -> bool:
        """Checks whether installed OS is Ubuntu."""
        return "Ubuntu" in platform.version()

    @property
    def _required_amount_of_network_interfaces_is_available(self) -> bool:
        """Checks whether required amount of network interfaces has been attached."""
        return len(self.network_interfaces) == self.REQUIRED_NUMBER_OF_NICS

    @property
    def _magma_user_exists(self) -> bool:
        """Checks whether Magma user exists."""
        try:
            pwd.getpwnam(self.MAGMA_USER)
            return True
        except KeyError:
            logger.warning("Magma user not found!")
            return False

    def _create_magma_user(self):
        """Adds Magma user."""
        logger.info(f"Adding Magma user: {self.MAGMA_USER}...")
        os.system(f'adduser --disabled-password --gecos "" {self.MAGMA_USER}')

    def _add_magma_user_to_sudoers(self):
        """Adds Magma user to sudoers."""
        logger.info(f'Adding Magma user "{self.MAGMA_USER}" to sudoers...')
        os.system(f"adduser ${self.MAGMA_USER} sudo")
        with open("/etc/sudoers", "w") as sudoers:
            sudoers.write(f"{self.MAGMA_USER} ALL=(ALL) NOPASSWD:ALL")
