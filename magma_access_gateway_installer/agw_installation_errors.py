#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging

logger = logging.getLogger("magma_access_gateway_installer")


class AGWInstallationError(Exception):
    """Base class for Magma AGW installation exceptions."""

    def __init__(self, message):
        self._message = f"ERROR: {message} Exiting installation!"
        logger.error(self._message)


class InvalidUserError(AGWInstallationError):
    """Exception raised when installation has been started by user different from root."""

    def __init__(self):
        super().__init__("Invalid user. Installation should be performed by the root user.")


class UnsupportedOSError(AGWInstallationError):
    """Exception raised when installation has been started on an OS other than Ubuntu."""

    def __init__(self):
        super().__init__("Invalid OS. Only Ubuntu 20.04 is supported.")


class InvalidNumberOfInterfacesError(AGWInstallationError):
    """Exception raised if number of available network interfaces is different from expected."""

    def __init__(self):
        super().__init__(
            "Invalid number of network interfaces. "
            "Installation requires at least two network interfaces available."
        )


class ArgumentError(AGWInstallationError):
    """Exception raised if argument provided by operator is invalid."""

    def __init__(self, message):
        super().__init__(f"Invalid argument. {message}")
