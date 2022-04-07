#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging

logger = logging.getLogger("magma_access_gateway_installer")


class AGWInstallationError(Exception):
    """Base class for Magma AGW installation exceptions."""

    def __init__(self, message):
        self._message = f"ERROR: {message} Exiting installation!"
        logger.info(self._message)

    @property
    def message(self):
        return self._message


class InvalidUserError(AGWInstallationError):
    """Exception raised when installation has been started by user different from root."""

    ERROR_MESSAGE = "Invalid user. Installation should be performed by the root user."

    def __init__(self):
        super().__init__(self.ERROR_MESSAGE)


class UnsupportedOSError(AGWInstallationError):
    """Exception raised when installation has been started on an OS other than Ubuntu."""

    ERROR_MESSAGE = "Invalid OS. Only Ubuntu 20.04 is supported."

    def __init__(self):
        super().__init__(self.ERROR_MESSAGE)


class InvalidNumberOfInterfacesError(AGWInstallationError):
    """Exception raised if number of available network interfaces is different from expected."""

    ERROR_MESSAGE = (
        "Invalid number of network interfaces. "
        "Installation requires at least two network interfaces available."
    )

    def __init__(self):
        super().__init__(self.ERROR_MESSAGE)
