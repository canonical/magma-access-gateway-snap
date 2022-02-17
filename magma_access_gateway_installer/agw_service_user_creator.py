#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import pwd
from subprocess import check_call

from systemd.journal import JournalHandler  # type: ignore[import]

logger = logging.getLogger(__name__)
logger.addHandler(JournalHandler())
logger.setLevel(logging.INFO)


class AGWInstallerServiceUserCreator:

    MAGMA_USER = "magma"

    def __init__(self):
        pass

    def create_magma_service_user(self):
        """Creates and configures Magma service user if necessary."""
        if not self._magma_user_exists:
            self._create_magma_user()
            self._add_magma_user_to_sudoers()

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
        check_call(["adduser", "--disabled-password", "--gecos", '""', f"{self.MAGMA_USER}"])

    def _add_magma_user_to_sudoers(self):
        """Adds Magma user to sudoers."""
        logger.info(f'Adding Magma user "{self.MAGMA_USER}" to sudoers...')
        check_call(["adduser", f"{self.MAGMA_USER}", "sudo"])
        with open("/etc/sudoers", "a") as sudoers:
            sudoers.write("\n")
            sudoers.write(f"{self.MAGMA_USER} ALL=(ALL) NOPASSWD:ALL")
            sudoers.write("\n")
