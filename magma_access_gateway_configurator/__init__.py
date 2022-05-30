#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import os
import sys
from argparse import ArgumentParser
from subprocess import check_output

import validators  # type: ignore[import]
from systemd.journal import JournalHandler  # type: ignore[import]

from .agw_configurator import AGWConfigurator

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
journal_handler = JournalHandler()
journal_handler.setFormatter(logging.Formatter("Magma AGW Configurator: %(message)s"))
logger.addHandler(journal_handler)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter("Magma AGW Configurator: %(message)s"))
logger.addHandler(stdout_handler)


PUBLIC_KEY_FILE = "/var/opt/magma/certs/gw_challenge.key"


def main():
    args = cli_arguments_parser(sys.argv[1:])
    validate_args(args)

    aws_configurator = AGWConfigurator(args.domain, args.root_ca_path)

    logger.info("Starting Magma AGW configuration...")
    if aws_configurator.control_proxy_configured:
        logger.info("Control Proxy configuration file already exists!")
        logger.info(
            "This may indicate that this instance of Magma AGW is already integrated to an "
            "Orchestrator instance."
        )
        logger.info("If you continue, all existing configurations will be erased!")
        if input("Do you want to proceed with the configuration process [Y/N]?") == "Y":
            aws_configurator.cleanup_old_configs()
        else:
            exit(0)
    aws_configurator.copy_root_ca_pem()
    aws_configurator.configure_control_proxy()
    aws_configurator.restart_magma_services()
    logger.info(
        "Magma AGW configuration done!"
    )
    logger.info("To add Access Gateway to the network, please use hardware secrets printed below:")
    for line in check_output(["show_gateway_info.py"]).decode().split("\n"):
        logger.info(f"{line}")
    logger.info(
        "Once Access Gateway is integrated with the Orchestrator, run "
        "magma-access-gateway.post-install to verify the installation."
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
    def __init__(self, message: str):
        logger.error(message)
        super().__init__(message)
