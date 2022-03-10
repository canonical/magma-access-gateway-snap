#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import pwd
from subprocess import check_call, check_output

logger = logging.getLogger("magma_access_gateway_installer")


class AGWInstallerServiceUserCreator:

    MAGMA_USER = "magma"

    def create_magma_user(self):
        """Creates Magma user."""
        if not self._magma_user_exists:
            logger.info(f"Adding Magma user: {self.MAGMA_USER}...")
            check_call(["adduser", "--disabled-password", "--gecos", '""', self.MAGMA_USER])

    def add_magma_user_to_sudo_group(self):
        """Adds Magma user to sudo group."""
        if not self._magma_user_in_sudo_group:
            logger.info(f'Adding Magma user "{self.MAGMA_USER}" to the sudo group...')
            check_call(["adduser", self.MAGMA_USER, "sudo"])

    def add_magma_user_to_sudoers_file(self):
        """Adds Magma user to /etc/sudoers."""
        if not self._magma_user_in_sudoers:
            logger.info(f'Adding Magma user "{self.MAGMA_USER}" to /etc/sudoers...')
            with open("/etc/sudoers", "a") as sudoers:
                sudoers.write(f"\n{self.MAGMA_USER} ALL=(ALL) NOPASSWD:ALL\n")

    @property
    def _magma_user_exists(self) -> bool:
        """Checks whether Magma user exists."""
        try:
            pwd.getpwnam(self.MAGMA_USER)
            return True
        except KeyError:
            return False

    @property
    def _magma_user_in_sudo_group(self) -> bool:
        """Checks whether Magma user belongs to sudo group."""
        return "sudo" in check_output(["groups", self.MAGMA_USER]).decode()

    @property
    def _magma_user_in_sudoers(self) -> bool:
        """Checks whether Magma user belongs to sudoers."""
        with open("/etc/sudoers", "r") as sudoers:
            sudoers_content = sudoers.readlines()
        return any(
            line for line in sudoers_content if f"{self.MAGMA_USER} ALL=(ALL) NOPASSWD:ALL" in line
        )
