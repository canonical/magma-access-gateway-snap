#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import argparse
import logging
import os
import sys
import time
from ipaddress import ip_address, ip_network
from typing import List

import netifaces  # type: ignore[import]
from systemd.journal import JournalHandler  # type: ignore[import]

from .agw_installation_errors import AGWInstallationError, ArgumentError
from .agw_installation_service_creator import AGWInstallerInstallationServiceCreator
from .agw_installer import AGWInstaller
from .agw_network_configurator import AGWInstallerNetworkConfigurator
from .agw_preinstall_checks import AGWInstallerPreinstallChecks
from .agw_service_user_creator import AGWInstallerServiceUserCreator

logger = logging.getLogger(__name__)
handler = JournalHandler()
handler.setFormatter(logging.Formatter("Magma AGW Installer: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def main():
    network_interfaces = netifaces.interfaces()
    network_interfaces.remove("lo")

    args = cli_arguments_parser(sys.argv[1:])
    try:
        validate_args(args, network_interfaces)
    except ArgumentError as e:
        print(e.message)
        return

    try:
        preinstall_checks = AGWInstallerPreinstallChecks(network_interfaces)
        network_configurator = AGWInstallerNetworkConfigurator(
            network_interfaces, args.dns, args.ip_address, args.gw_ip_address, args.sgi, args.s1
        )
        service_user_creator = AGWInstallerServiceUserCreator()
        installation_service_creator = AGWInstallerInstallationServiceCreator()

        preinstall_checks.preinstall_checks()
        preinstall_checks.install_required_system_packages()

        if not args.skip_networking:
            network_configurator.update_interfaces_names()
            network_configurator.configure_dns()
            network_configurator.create_interfaces_config_files()
        network_configurator.remove_netplan()
        network_configurator.enable_networking_service()

        service_user_creator.create_magma_user()
        service_user_creator.add_magma_user_to_sudo_group()
        service_user_creator.add_magma_user_to_sudoers_file()

        if network_configurator.reboot_needed:
            installation_service_creator.create_magma_agw_installation_service()
            installation_service_creator.create_magma_agw_installation_service_link()
            logger.info(
                "Rebooting system to apply pre-installation changes...\n"
                "Magma AGW installation process will be resumed automatically once machine is "
                "back up."
            )
            time.sleep(5)
            os.system("reboot")
        else:
            AGWInstaller().install()
    except AGWInstallationError as e:
        print(e.message)
        return


def cli_arguments_parser(cli_arguments: list) -> argparse.Namespace:
    cli_options = argparse.ArgumentParser()
    cli_options.add_argument(
        "--ip-address",
        dest="ip_address",
        required=False,
        help="Statically allocated SGi interface IP address. Example: 1.1.1.1/24.",
    )
    cli_options.add_argument(
        "--gw-ip-address",
        dest="gw_ip_address",
        required=False,
        help="Upstream router IP for SGi interface. Example: 1.1.1.200.",
    )
    cli_options.add_argument(
        "--skip-networking",
        dest="skip_networking",
        action="store_true",
        required=False,
        help="If used, network configuration part of the installation process will be skipped. "
        "In this case operator is responsible for providing expected network configuration.",
    )
    cli_options.add_argument(
        "--dns",
        dest="dns",
        nargs="+",
        required=False,
        default=["8.8.8.8", "208.67.222.222"],
        help="Space separated list of DNS IP addresses. Example: --dns 1.2.3.4 5.6.7.8.",
    )
    cli_options.add_argument(
        "--sgi",
        dest="sgi",
        required=False,
        help="Defines which interface should be used as SGi interface.",
    )
    cli_options.add_argument(
        "--s1",
        dest="s1",
        required=False,
        help="Defines which interface should be used as S1 interface.",
    )
    return cli_options.parse_args(cli_arguments)


def validate_args(args: argparse.Namespace, network_interfaces: List[str]):
    """Validates operator provided arguments and raises when invalid."""
    validate_static_ip_allocation(args)
    validate_arbitrary_dns(args)
    validate_custom_sgi_and_s1_interfaces(args, network_interfaces)


def validate_custom_sgi_and_s1_interfaces(args: argparse.Namespace, network_interfaces: List[str]):
    if args.sgi or args.s1:
        if not args.sgi or args.sgi not in network_interfaces:
            raise ArgumentError("Invalid or empty --sgi argument. It must match an interface name.")
        if not args.s1 or args.s1 not in network_interfaces:
            raise ArgumentError("Invalid or empty --s1 argument. It must match an interface name.")


def validate_arbitrary_dns(args: argparse.Namespace):
    if not args.dns:
        raise ArgumentError("--dns flag specified, but no addresses given.")
    for dns_ip in args.dns:
        try:
            ip_address(dns_ip)
        except ValueError:
            raise ArgumentError(f"Invalid IP address provided for --dns ({dns_ip}).")


def validate_static_ip_allocation(args: argparse.Namespace):
    if args.ip_address and not args.gw_ip_address:
        raise ArgumentError("--gw-ip-address is missing.")
    elif not args.ip_address and args.gw_ip_address:
        raise ArgumentError("--ip-address is missing.")
    elif args.ip_address and args.gw_ip_address:
        try:
            ip_network(args.ip_address, False)
        except ValueError:
            raise ArgumentError(f"Invalid IP address provided for --ip-address ({args.ip_address}).")
        try:
            ip_address(args.gw_ip_address)
        except ValueError:
            raise ArgumentError(
                f"Invalid IP address provided for --gw-ip-address ({args.gw_ip_address})."
            )
