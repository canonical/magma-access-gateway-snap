#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import platform

from systemd.journal import JournalHandler  # type: ignore[import]

from .agw_installation_errors import InvalidNumberOfInterfacesError, UnsupportedOSError

logger = logging.getLogger(__name__)
logger.addHandler(JournalHandler())
logger.setLevel(logging.INFO)


class AGWInstallerPreinstallChecks:

    REQUIRED_NUMBER_OF_NICS = 2

    def __init__(self, network_interfaces):
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

    @property
    def _ubuntu_is_installed(self) -> bool:
        """Checks whether installed OS is Ubuntu."""
        return "Ubuntu" in platform.version()

    @property
    def _required_amount_of_network_interfaces_is_available(self) -> bool:
        """Checks whether required amount of network interfaces has been attached."""
        return len(self.network_interfaces) == self.REQUIRED_NUMBER_OF_NICS
