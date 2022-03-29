#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging

logger = logging.getLogger("magma_access_gateway_installer")


class AGWInstallationError(Exception):
    """Base class for Magma AGW installation exceptions."""

    pass


class InvalidUserError(AGWInstallationError):
    """Exception raised when installation has been started by user different than root."""

    ERROR_MESSAGE = (
        "Invalid user used! \n"
        "Magma AGW installation should be performed by the root user! Exiting..."
    )

    def __init__(self):
        logger.error(self.ERROR_MESSAGE)
        super().__init__(self.ERROR_MESSAGE)


class UnsupportedOSError(AGWInstallationError):
    """Exception raised when installation has been started on an OS other than Ubuntu."""

    ERROR_MESSAGE = "Invalid OS! \n Magma AGW can only be installed on Ubuntu! Exiting..."

    def __init__(self):
        logger.error(self.ERROR_MESSAGE)
        super().__init__(self.ERROR_MESSAGE)


class InvalidNumberOfInterfacesError(AGWInstallationError):
    """Exception raised if number of available network interfaces is different from expected."""

    ERROR_MESSAGE = (
        "Invalid number of network interfaces! \n"
        "Magma AGW needs at least two network interfaces available - SGi and S1! Exiting..."
    )

    def __init__(self):
        logger.error(self.ERROR_MESSAGE)
        super().__init__(self.ERROR_MESSAGE)
