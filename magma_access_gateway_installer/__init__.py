#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import argparse
import logging
import os
import sys
import time
from ipaddress import ip_address, ip_network

import netifaces  # type: ignore[import]
from systemd.journal import JournalHandler  # type: ignore[import]

from .agw_installation_errors import AGWInstallationError, ArgumentError
from .agw_installer import AGWInstaller
from .agw_network_configurator import AGWInstallerNetworkConfigurator
from .agw_preinstall_checks import AGWInstallerPreinstallChecks
from .agw_service_user_creator import AGWInstallerServiceUserCreator

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
journal_handler = JournalHandler()
journal_handler.setFormatter(logging.Formatter("Magma AGW Installer: %(message)s"))
logger.addHandler(journal_handler)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter("Magma AGW Installer: %(message)s"))
logger.addHandler(stdout_handler)

network_interfaces = netifaces.interfaces()
network_interfaces.remove("lo")


def main():
    preinstall_checks = AGWInstallerPreinstallChecks(network_interfaces)
    try:
        preinstall_checks.preinstall_checks()
    except AGWInstallationError:
        return

    args = cli_arguments_parser(sys.argv[1:])
    try:
        validate_args(args)
    except ArgumentError:
        return

    preinstall_checks.install_required_system_packages()

    network_config = generate_network_config(args)
    network_configurator = AGWInstallerNetworkConfigurator(network_config)
    if not args.skip_networking:
        network_configurator.configure_network_interfaces()
        network_configurator.configure_dns()

    service_user_creator = AGWInstallerServiceUserCreator()
    service_user_creator.create_magma_user()
    service_user_creator.add_magma_user_to_sudo_group()
    service_user_creator.add_magma_user_to_sudoers_file()

    installer = AGWInstaller()
    if installer.magma_agw_installed:
        logger.info("Magma Access Gateway already installed. Exiting...")
        return
    else:
        logger.info("Starting Magma AGW deployment...")
        installer.update_apt_cache()
        installer.update_ca_certificates_package()
        installer.forbid_usage_of_expired_dst_root_ca_x3_certificate()
        installer.configure_apt_for_magma_agw_deb_package_installation()
        installer.install_runtime_dependencies()
        installer.preconfigure_wireshark_suid_property()
        installer.install_magma_agw()
        installer.start_open_vswitch()
        installer.start_magma()
        logger.info(
            "Magma AGW deployment completed successfully!\n"
            "System will now go down for the reboot to apply all changes.\n"
            "After configuring Magma AGW run magma-access-gateway.post-install to verify "
            "configuration."
        )
        time.sleep(5)
        os.system("reboot")


def cli_arguments_parser(cli_arguments: list) -> argparse.Namespace:
    cli_options = argparse.ArgumentParser()
    cli_options.add_argument(
        "--ipv4-address",
        dest="ipv4_address",
        required=False,
        help="Statically allocated IPv4 SGi interface IP address. Example: 1.1.1.1/24.",
    )
    cli_options.add_argument(
        "--gw-ipv4-address",
        dest="gw_ipv4_address",
        required=False,
        help="IPv4 address of an upstream router for SGi interface. Example: 1.1.1.200.",
    )
    cli_options.add_argument(
        "--ipv6-address",
        dest="ipv6_address",
        required=False,
        help="Statically allocated IPv6 SGi interface IP address. "
        "Example: fd9c:0175:3d65:cfbd:1:1:1:1/64.",
    )
    cli_options.add_argument(
        "--gw-ipv6-address",
        dest="gw_ipv6_address",
        required=False,
        help="IPv6 address of an upstream router for SGi interface. "
        "Example: fd9c:0175:3d65:cfbd:1:1:1:200.",
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
        default=network_interfaces[0],
        help="Defines which interface should be used as SGi interface.",
    )
    cli_options.add_argument(
        "--s1",
        dest="s1",
        required=False,
        default=network_interfaces[1],
        help="Defines which interface should be used as S1 interface.",
    )
    return cli_options.parse_args(cli_arguments)


def validate_args(args: argparse.Namespace):
    """Validates operator provided arguments and raises when invalid."""
    validate_static_ip_allocation(args)
    validate_arbitrary_dns(args)
    validate_custom_sgi_and_s1_interfaces(args)


def validate_custom_sgi_and_s1_interfaces(args: argparse.Namespace):
    if args.sgi or args.s1:
        if not args.sgi or args.sgi not in network_interfaces:
            raise ArgumentError(
                "Invalid or empty --sgi argument. It must match an interface name."
            )
        if not args.s1 or args.s1 not in network_interfaces:
            raise ArgumentError("Invalid or empty --s1 argument. It must match an interface name.")


def validate_arbitrary_dns(args: argparse.Namespace):
    for dns_ip in args.dns:
        try:
            ip_address(dns_ip)
        except ValueError:
            raise ArgumentError(f"Invalid IP address provided for --dns ({dns_ip}).")


def validate_static_ip_allocation(args: argparse.Namespace):
    if (args.ipv6_address or args.gw_ipv6_address) and not (
        args.ipv4_address or args.gw_ipv4_address
    ):
        raise ArgumentError(
            "Pure IPv6 configuration not supported. "
            "Static IPv6 configuration can only be specified along with IPv4."
        )
    validate_addressing(args.ipv4_address, args.gw_ipv4_address)
    validate_addressing(args.ipv6_address, args.gw_ipv6_address)


def validate_addressing(sgi_ip_address: str, sgi_gw_ip_address: str):
    if sgi_ip_address and not sgi_gw_ip_address:
        raise ArgumentError(
            f"Gateway address is missing for given SGi address ({sgi_ip_address}). "
            "Specify gateway address using --gw-ipv4-address or --gw-ipv6-address."
        )
    elif not sgi_ip_address and sgi_gw_ip_address:
        raise ArgumentError(
            f"SGi address is missing for given gateway address ({sgi_gw_ip_address}). "
            "Specify SGi address using --ipv4-address or --ipv6-address."
        )
    elif sgi_ip_address and sgi_gw_ip_address:
        try:
            ip_network(sgi_ip_address, False)
        except ValueError:
            raise ArgumentError(f"Invalid SGi IP address provided ({sgi_ip_address}).")
        try:
            ip_address(sgi_gw_ip_address)
        except ValueError:
            raise ArgumentError(f"Invalid SGi gateway IP address provided ({sgi_gw_ip_address}).")


def generate_network_config(args: argparse.Namespace):
    return {
        "sgi_ipv4_address": args.ipv4_address,
        "sgi_ipv4_gateway": args.gw_ipv4_address,
        "sgi_ipv6_address": args.ipv6_address,
        "sgi_ipv6_gateway": args.gw_ipv6_address,
        "sgi_mac_address": get_mac_address(args.sgi),
        "s1_mac_address": get_mac_address(args.s1),
        "dns_address": " ".join(args.dns),
    }


def get_mac_address(interface_name: str):
    return netifaces.ifaddresses(interface_name)[netifaces.AF_LINK][0]["addr"]
