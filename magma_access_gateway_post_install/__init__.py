#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

""" The Access Gateway (AGW) provides network services and policy enforcement. In an LTE network,
  the AGW implements an evolved packet core (EPC), and a combination of an AAA and a PGW. It works
  with existing, unmodified commercial radio hardware.
  For detailed description visit https://docs.magmacore.org/docs/next/lte/architecture_overview.
"""

import logging
import sys

from systemd.journal import JournalHandler  # type: ignore[import]

from .agw_post_install import AGWPostInstallChecks
from .agw_post_install_errors import PostInstallError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
journal_handler = JournalHandler()
journal_handler.setFormatter(logging.Formatter("Magma AGW Post-Install: %(message)s"))
logger.addHandler(journal_handler)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter("Magma AGW Post-Install: %(message)s"))
logger.addHandler(stdout_handler)


def main():
    try:
        logger.info("Starting Magma AGW post-installation checks...")
        agw_post_install_checks = AGWPostInstallChecks()
        agw_post_install_checks.check_whether_required_interfaces_are_configured()
        agw_post_install_checks.check_eth0_internet_connectivity()
        agw_post_install_checks.check_whether_required_services_are_running()
        agw_post_install_checks.check_whether_required_packages_are_installed()
        agw_post_install_checks.check_whether_root_certificate_exists()
        agw_post_install_checks.check_control_proxy()
        agw_post_install_checks.check_connectivity_with_orc8r()
        logger.info("Magma AGW post-installation checks finished successfully.")
    except PostInstallError:
        return
