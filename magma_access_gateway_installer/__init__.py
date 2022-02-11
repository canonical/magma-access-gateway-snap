#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

from .agw_installer_ubuntu import AGWInstallerUbuntu


def main():
    agw_installer = AGWInstallerUbuntu()
    agw_installer.preinstall_checks()
    agw_installer.magma_service_user_creation()
