#!/snap/magma-access-gateway/current/bin/python3
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
    network_interfaces = netifaces.interfaces()
    network_interfaces.remove("lo")

    args = cli_arguments_parser(sys.argv[1:])
    validate_args(args, network_interfaces)

    preinstall_checks = AGWInstallerPreinstallChecks(network_interfaces)
    network_configurator = AGWInstallerNetworkConfigurator(
        network_interfaces, args.dns, args.ip_address, args.gw_ip_address, args.sgi, args.s1
    )
    service_user_creator = AGWInstallerServiceUserCreator()
    installation_service_creator = AGWInstallerInstallationServiceCreator()

    preinstall_checks.preinstall_checks()
    preinstall_checks.install_required_system_packages()

    if not args.maas_networking:
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
        help="Statically allocated SGi interface IP address. Example: 1.1.1.1/24.",
    )
    cli_options.add_argument(
        "--gw-ip-address",
        dest="gw_ip_address",
        required=False,
        help="Upstream router IP for SGi interface. Example: 1.1.1.200.",
    )
    cli_options.add_argument(
        "--maas-networking",
        dest="maas_networking",
        action="store_true",
        required=False,
        help="Use network configuration provided by MAAS. If used, network configuration part of "
        "the installation process will be skipped.",
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


def validate_args(args, network_interfaces):
    validate_static_ip_allocation(args)
    validate_arbitrary_dns(args)
    validate_custom_sgi_and_s1_interfaces(args, network_interfaces)


def validate_custom_sgi_and_s1_interfaces(args, network_interfaces):
    if args.sgi and not args.s1:
        raise ValueError("S1 interface not specified! Exiting...")
    elif not args.sgi and args.s1:
        raise ValueError("SGi interface not specified! Exiting...")
    elif args.sgi and args.s1:
        if not all([interface in network_interfaces for interface in [args.sgi, args.s1]]):
            raise ValueError("One or both specified SGi/S1 interfaces do not exist! Exiting...")


def validate_arbitrary_dns(args):
    if not args.dns:
        raise ValueError("--dns flag specified, but no addresses given! Exiting...")
    else:
        for dns_ip in args.dns:
            try:
                ip_address(dns_ip)
            except Exception as e:
                raise e


def validate_static_ip_allocation(args):
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
