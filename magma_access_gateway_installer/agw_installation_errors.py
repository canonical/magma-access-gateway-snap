#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.


class AGWInstallationError(Exception):
    """Base class for Magma AGW installation exceptions."""

    pass


class UnsupportedOSError(AGWInstallationError):
    """Exception raised when installation has been started on an OS other than Ubuntu."""

    def __init__(self):
        super().__init__("Invalid OS! \n Magma AGW can only be installed on Ubuntu! Exiting...")


class InvalidNumberOfInterfacesError(AGWInstallationError):
    """Exception raised if number of available network interfaces is different from expected."""

    def __init__(self):
        super().__init__(
            "Invalid number of network interfaces!"
            "Magma AGW needs two network interfaces - SGi and S1! Exiting..."
        )
