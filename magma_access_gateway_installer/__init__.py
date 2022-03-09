#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import os
import sys
import time
from argparse import ArgumentParser
from ipaddress import ip_address, ip_network

import netifaces  # type: ignore[import]
from systemd.journal import JournalHandler  # type: ignore[import]

from .agw_installation_service_creator import AGWInstallerInstallationServiceCreator
from .agw_network_configurator import AGWInstallerNetworkConfigurator
from .agw_preinstall_checks import AGWInstallerPreinstallChecks
from .agw_service_user_creator import AGWInstallerServiceUserCreator

logger = logging.getLogger(__name__)
handler = JournalHandler()
handler.setFormatter(logging.Formatter("Magma AGW Installer: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def main():
    args = cli_arguments_parser(sys.argv[1:])
    validate_args(args)

    network_interfaces = netifaces.interfaces()
    network_interfaces.remove("lo")

    preinstall_checks = AGWInstallerPreinstallChecks(network_interfaces)
    network_configurator = AGWInstallerNetworkConfigurator(
        network_interfaces, args.ip_address, args.gw_ip_address
    )
    service_user_creator = AGWInstallerServiceUserCreator()
    installation_service_creator = AGWInstallerInstallationServiceCreator()

    preinstall_checks.preinstall_checks()
    preinstall_checks.install_required_system_packages()

    network_configurator.update_interfaces_names()
    network_configurator.configure_dns()
    network_configurator.create_interfaces_config_files()
    network_configurator.remove_netplan()
    network_configurator.enable_networking_service()

    service_user_creator.create_magma_user()
    service_user_creator.add_magma_user_to_sudo_group()
    service_user_creator.add_magma_user_to_sudoers_file()

    installation_service_creator.create_magma_agw_installation_service()
    installation_service_creator.create_magma_agw_installation_service_link()

    if network_configurator.reboot_needed:
        logger.info(
            "Rebooting system to apply pre-installation changes...\n"
            "Magma AGW installation process will be resumed automatically once machine is back up."
        )
        time.sleep(5)
        os.system("reboot")


def cli_arguments_parser(cli_arguments):
    cli_options = ArgumentParser()
    cli_options.add_argument(
        "--ip-address",
        dest="ip_address",
        required=False,
        help="Statically allocated SGi interface IP address. Example: 1.1.1.1/24",
    )
    cli_options.add_argument(
        "--gw-ip-address",
        dest="gw_ip_address",
        required=False,
        help="Upstream router IP for SGi interface. Example: 1.1.1.200",
    )
    return cli_options.parse_args(cli_arguments)


def validate_args(args):
    if args.ip_address and not args.gw_ip_address:
        raise ValueError("Upstream router IP for SGi interface is missing! Exiting...")
    elif not args.ip_address and args.gw_ip_address:
        raise ValueError("SGi interface IP address is missing! Exiting...")
    elif args.ip_address and args.gw_ip_address:
        try:
            ip_network(args.ip_address, False)
            ip_address(args.gw_ip_address)
        except Exception as e:
            raise e
