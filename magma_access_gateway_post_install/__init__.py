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
from argparse import ArgumentParser

from systemd.journal import JournalHandler  # type: ignore[import]

from .agw_post_install import AGWPostInstallChecks

logger = logging.getLogger(__name__)
handler = JournalHandler()
handler.setFormatter(logging.Formatter("Magma AGW Post-Install: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def main():
    args = cli_arguments_parser(sys.argv[1:])

    agw_post_install_checks = AGWPostInstallChecks(args.root_ca_path)

    logger.info("Starting Magma AGW post-installation checks...")
    agw_post_install_checks.check_whether_required_interfaces_are_configured()
    agw_post_install_checks.check_eth0_internet_connectivity()
    agw_post_install_checks.check_whether_required_services_are_running()
    agw_post_install_checks.check_whether_required_packages_are_installed()
    agw_post_install_checks.check_whether_root_certificate_exists()
    agw_post_install_checks.check_control_proxy()
    agw_post_install_checks.check_cloud_check_in()
    logger.info("Magma AGW post-installation checks finished successfully.")


def cli_arguments_parser(cli_arguments):
    cli_options = ArgumentParser()
    cli_options.add_argument(
        "--root-ca-pem-path",
        dest="root_ca_path",
        required=True,
        help="Path to Root CA PEM used during Orc8r deployment. Example: /home/magma/rootCA.pem",
    )
    return cli_options.parse_args(cli_arguments)
