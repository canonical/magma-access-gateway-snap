#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import os
import sys
from argparse import ArgumentParser

import validators  # type: ignore[import]
from systemd.journal import JournalHandler  # type: ignore[import]

from .agw_configurator import AGWConfigurator

logger = logging.getLogger(__name__)
handler = JournalHandler()
handler.setFormatter(logging.Formatter("Magma AGW Configurator: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def main():
    args = cli_arguments_parser(sys.argv[1:])
    validate_args(args)

    aws_configurator = AGWConfigurator(args.domain, args.root_ca_path)

    logger.info("Starting Magma AGW configuration...")
    aws_configurator.copy_root_ca_pem()
    aws_configurator.configure_control_proxy()
    aws_configurator.restart_magma_services()
    logger.info(
        "Magma AGW configuration done! "
        "To add your Access Gateway to the network, please refer "
        "https://docs.magmacore.org/docs/next/lte/deploy_config_agw#registering-and-configuring-your-access-gateway"  # noqa: E501, W505
    )


def cli_arguments_parser(cli_arguments):
    cli_options = ArgumentParser()
    cli_options.add_argument(
        "--domain",
        dest="domain",
        required=True,
        help="Domain name used during Orc8r deployment. Example: example.com",
    )
    cli_options.add_argument(
        "--root-ca-pem-path",
        dest="root_ca_path",
        required=True,
        help="Path to Root CA PEM used during Orc8r deployment. Example: /home/magma/rootCA.pem",
    )
    return cli_options.parse_args(cli_arguments)


def validate_args(args):
    if "ValidationFailure" in str(validators.domain(args.domain)):
        raise AGWConfigurationError("Invalid domain!")

    if not os.path.exists(args.root_ca_path):
        raise FileNotFoundError(f"Given Root CA PEM path {args.root_ca_path} doesn't exist!")


class AGWConfigurationError(Exception):
    def __init__(self, message):
        logger.error(message)
        super().__init__(message)
