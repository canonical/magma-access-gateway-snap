#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import argparse
import logging
import sys
from ipaddress import ip_address, ip_network

import netifaces  # type: ignore[import]

try:
    from systemd.journal import JournalHandler  # type: ignore[import]
except ModuleNotFoundError:
    sys.tracebacklimit = None  # type: ignore[assignment]
    raise Exception("systemd module not found! Make sure you're using Ubuntu 20.04!")

from .agw_installation_errors import AGWInstallationError, ArgumentError
from .agw_installer import AGWInstaller
from .agw_network_configurator import AGWInstallerNetworkConfigurator
from .agw_preinstall import AGWInstallerPreinstall
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
    try:
        preinstall = AGWInstallerPreinstall(network_interfaces)
        preinstall.preinstall_checks()
        args = cli_arguments_parser(sys.argv[1:])
        validate_args(args)
    except AGWInstallationError:
        return

    preinstall.install_required_system_packages()

    service_user_creator = AGWInstallerServiceUserCreator()
    service_user_creator.create_magma_user()
    service_user_creator.add_magma_user_to_sudo_group()
    service_user_creator.add_magma_user_to_sudoers_file()

    if not args.skip_networking:
        configure_network(args)

    AGWInstaller().install(args.no_reboot)


def cli_arguments_parser(cli_arguments: list) -> argparse.Namespace:
    cli_options = argparse.ArgumentParser()
    cli_options.add_argument(
        "--sgi-ipv4-address",
        dest="sgi_ipv4_address",
        required=False,
        help="Statically allocated IPv4 address for SGi interface. Example: 1.1.1.1/24.",
    )
    cli_options.add_argument(
        "--sgi-ipv4-gateway",
        dest="sgi_ipv4_gateway",
        required=False,
        help="IPv4 address of an upstream router for SGi interface. Example: 1.1.1.200.",
    )
    cli_options.add_argument(
        "--sgi-ipv6-address",
        dest="sgi_ipv6_address",
        required=False,
        help="Statically allocated IPv6 address for SGi interface. "
        "Example: fd9c:0175:3d65:cfbd:1:1:1:1/64.",
    )
    cli_options.add_argument(
        "--sgi-ipv6-gateway",
        dest="sgi_ipv6_gateway",
        required=False,
        help="IPv6 address of an upstream router for SGi interface. "
        "Example: fd9c:0175:3d65:cfbd:1:1:1:200.",
    )
    cli_options.add_argument(
        "--s1-ipv4-address",
        dest="s1_ipv4_address",
        required=False,
        help="Statically allocated IPv4 address fot S1 interface. Example: 1.1.1.1/24.",
    )
    cli_options.add_argument(
        "--s1-ipv4-gateway",
        dest="s1_ipv4_gateway",
        required=False,
        help="IPv4 address of an upstream router for S1 interface. Example: 1.1.1.200.",
    )
    cli_options.add_argument(
        "--s1-ipv6-address",
        dest="s1_ipv6_address",
        required=False,
        help="Statically allocated IPv6 address for S1 interface. "
        "Example: fd9c:0175:3d65:cfbd:1:1:1:1/64.",
    )
    cli_options.add_argument(
        "--s1-ipv6-gateway",
        dest="s1_ipv6_gateway",
        required=False,
        help="IPv6 address of an upstream router for S1 interface. "
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
        default=set_default_sgi_interface(),
        help="Defines which interface should be used as SGi interface.",
    )
    cli_options.add_argument(
        "--s1",
        dest="s1",
        required=False,
        default=set_default_s1_interface(),
        help="Defines which interface should be used as S1 interface.",
    )
    cli_options.add_argument(
        "--no-reboot",
        dest="no_reboot",
        action="store_true",
        required=False,
        help="If used, the installer will not automatically reboot "
        "and will invite the user to reboot manually.",
    )
    return cli_options.parse_args(cli_arguments)


def validate_args(args: argparse.Namespace):
    """Validates operator provided arguments and raises when invalid."""
    validate_static_ip_allocation(
        args.sgi_ipv4_address,
        args.sgi_ipv4_gateway,
        args.sgi_ipv6_address,
        args.sgi_ipv6_gateway,
        args.s1_ipv4_address,
        args.s1_ipv4_gateway,
        args.s1_ipv6_address,
        args.s1_ipv6_gateway,
    )
    validate_arbitrary_dns(args)
    validate_custom_sgi_and_s1_interfaces(args)


def validate_custom_sgi_and_s1_interfaces(args: argparse.Namespace):
    if args.sgi not in network_interfaces:
        raise ArgumentError("Invalid --sgi argument. It must match an interface name.")
    if args.s1 not in network_interfaces:
        raise ArgumentError("Invalid --s1 argument. It must match an interface name.")


def validate_arbitrary_dns(args: argparse.Namespace):
    for dns_ip in args.dns:
        try:
            ip_address(dns_ip)
        except ValueError:
            raise ArgumentError(f"Invalid IP address provided for --dns ({dns_ip}).")


def validate_static_ip_allocation(
    sgi_ipv4_address: str,
    sgi_ipv4_gateway: str,
    sgi_ipv6_address: str,
    sgi_ipv6_gateway: str,
    s1_ipv4_address: str,
    s1_ipv4_gateway: str,
    s1_ipv6_address: str,
    s1_ipv6_gateway: str,
):
    if (sgi_ipv6_address or sgi_ipv6_gateway) and not (sgi_ipv4_address or sgi_ipv4_gateway):
        raise ArgumentError(
            "Pure IPv6 configuration not supported. "
            "Static IPv6 configuration can only be specified along with IPv4."
        )
    validate_sgi_addressing(sgi_ipv4_address, sgi_ipv4_gateway)
    validate_sgi_addressing(sgi_ipv6_address, sgi_ipv6_gateway)
    validate_s1_addressing(s1_ipv4_address, s1_ipv4_gateway)
    validate_s1_addressing(s1_ipv6_address, s1_ipv6_gateway)


def validate_sgi_addressing(sgi_ip_address: str, sgi_gw_ip_address: str):
    if sgi_ip_address and not sgi_gw_ip_address:
        raise ArgumentError(
            f"Gateway address is missing for given SGi address ({sgi_ip_address}). "
            "Specify gateway address using --gw-ipv4-address or --gw-ipv6-address."
        )
    elif not sgi_ip_address and sgi_gw_ip_address:
        raise ArgumentError(
            f"SGi address is missing for given gateway address ({sgi_gw_ip_address}). "
            "Specify SGi address using --sgi-ipv4-address or --sgi-ipv6-address."
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


def validate_s1_addressing(s1_ip_address: str, s1_gw_ip_address: str):
    if s1_gw_ip_address and not s1_ip_address:
        raise ArgumentError(
            f"S1 address is missing for given gateway address ({s1_gw_ip_address}). "
            "Specify S1 address using --s1-ipv4-address or --s1-ipv6-address."
        )
    if s1_ip_address:
        try:
            ip_network(s1_ip_address, False)
        except ValueError:
            raise ArgumentError(f"Invalid SGi IP address provided ({s1_ip_address}).")
    if s1_gw_ip_address:
        try:
            ip_address(s1_gw_ip_address)
        except ValueError:
            raise ArgumentError(f"Invalid S1 gateway IP address provided ({s1_gw_ip_address}).")


def configure_network(args: argparse.Namespace):
    network_config = generate_network_config(args)
    network_configurator = AGWInstallerNetworkConfigurator(network_config)
    network_configurator.disable_cloudinit_network_management()
    network_configurator.configure_dns()
    network_configurator.configure_network_interfaces()
    network_configurator.apply_netplan_configuration()


def generate_network_config(args: argparse.Namespace) -> dict:
    return {
        "sgi_ipv4_address_cidr": args.sgi_ipv4_address,
        "sgi_ipv4_gateway": args.sgi_ipv4_gateway,
        "sgi_ipv6_address_cidr": args.sgi_ipv6_address,
        "sgi_ipv6_gateway": args.sgi_ipv6_gateway,
        "s1_ipv4_address_cidr": args.s1_ipv4_address,
        "s1_ipv4_address": args.s1_ipv4_address.split("/")[0] if args.s1_ipv4_address else None,
        "s1_ipv4_gateway": args.s1_ipv4_gateway,
        "s1_ipv6_address_cidr": args.s1_ipv6_address,
        "s1_ipv6_address": args.s1_ipv6_address.split("/")[0] if args.s1_ipv6_address else None,
        "s1_ipv6_gateway": args.s1_ipv6_gateway,
        "sgi_mac_address": get_mac_address(args.sgi),
        "s1_mac_address": get_mac_address(args.s1),
        "dns_address": " ".join(args.dns),
    }


def get_mac_address(interface_name: str) -> str:
    return netifaces.ifaddresses(interface_name)[netifaces.AF_LINK][0]["addr"]


def set_default_sgi_interface() -> str:
    return "eth0" if "eth0" in network_interfaces else network_interfaces[0]


def set_default_s1_interface() -> str:
    return "eth1" if "eth1" in network_interfaces else network_interfaces[1]
