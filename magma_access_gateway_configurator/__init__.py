#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import base64
import logging
import os
import sys
from argparse import ArgumentParser
from typing import Union

import snowflake  # type: ignore[import]
import validators  # type: ignore[import]
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
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
        "Magma AGW configuration done!\n"
        "\t\tTo add Access Gateway to the network, please use hardware secrets printed below:\n"
        "\t\tHardware ID:\n"
        f"\t\t{snowflake.snowflake()}\n"
        "\t\tChallenge Key:\n"
        f'\t\t{load_public_key_to_base64der(PUBLIC_KEY_FILE).decode("utf-8")}\n'
        "\t\tOnce Access Gateway is integrated with the Orchestrator, run "
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


def load_public_key_to_base64der(key_file: str) -> bytes:
    """Load the public key of a private key and convert to base64 encoded DER
    The return value can be used directly for device registration.

    Args:
        key_file: path to the private key file, pem encoded

    Returns:
        base64 encoded public key in DER format

    Raises:
        IOError: If file cannot be opened
        ValueError: If the file content cannot be decoded successfully
        TypeError: If the key_file is encrypted
    """

    key = load_key(key_file)
    pub_key = key.public_key()
    pub_bytes = pub_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    encoded = base64.b64encode(pub_bytes)
    return encoded


def load_key(key_file: str) -> Union[RSAPrivateKey, EllipticCurvePrivateKey]:
    """Load a private key encoded in PEM format

    Args:
        key_file: path to the key file

    Returns:
        RSAPrivateKey or EllipticCurvePrivateKey depending on the contents of key_file

    Raises:
        IOError: If file cannot be opened
        ValueError: If the file content cannot be decoded successfully
        TypeError: If the key_file is encrypted
    """
    with open(key_file, "rb") as f:
        key_bytes = f.read()
    return serialization.load_pem_private_key(key_bytes, None, default_backend())  # type: ignore[return-value]  # noqa: E501


class AGWConfigurationError(Exception):
    def __init__(self, message: str):
        logger.error(message)
        super().__init__(message)
