#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

""" The Access Gateway (AGW) provides network services and policy enforcement. In an LTE network,
  the AGW implements an evolved packet core (EPC), and a combination of an AAA and a PGW. It works
  with existing, unmodified commercial radio hardware.
  For detailed description visit https://docs.magmacore.org/docs/next/lte/architecture_overview.
"""
import sys
from argparse import ArgumentParser

import netifaces  # type: ignore[import]

from .agw_network_configurator import AGWInstallerNetworkConfigurator
from .agw_preinstall_checks import AGWInstallerPreinstallChecks
from .agw_service_user_creator import AGWInstallerServiceUserCreator


def _cli_arguments_parser(args):
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
    return cli_options.parse_args(args)


def main():
    args = _cli_arguments_parser(sys.argv[1:])
    if args.ip_address and not args.gw_ip_address:
        raise ValueError("Upstream router IP for SGi interface is missing! Exiting...")
    elif not args.ip_address and args.gw_ip_address:
        raise ValueError("SGi interface IP address is missing! Exiting...")

    network_interfaces = netifaces.interfaces()
    network_interfaces.remove("lo")

    AGWInstallerPreinstallChecks(network_interfaces).preinstall_checks()
    AGWInstallerNetworkConfigurator(
        network_interfaces, args.ip_address, args.gw_ip_address
    ).configure_network_interfaces()
    AGWInstallerServiceUserCreator().create_magma_service_user()
