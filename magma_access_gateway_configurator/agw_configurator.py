#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import os
import shutil
from subprocess import check_call

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger("magma_access_gateway_configurator")


class AGWConfigurator:

    ROOT_CA_PEM_DESTINATION_DIR = "/var/opt/magma/tmp/certs"
    ROOT_CA_PEM_FILE_NAME = "rootCA.pem"
    MAGMA_CONTROL_PROXY_CONFIG_DIR = "/var/opt/magma/configs"
    MAGMA_CONTROL_PROXY_CONFIG_FILE_NAME = "control_proxy.yml"

    def __init__(self, domain: str, root_ca_pem_path: str):
        self.domain = domain
        self.root_ca_pem_path = root_ca_pem_path

    def copy_root_ca_pem(self):
        """Copies Root CA PEM from specified location to /var/opt/magma/tmp/certs/."""
        logger.info(
            f"Copying Root CA PEM from {self.root_ca_pem_path} "
            f"to {self.ROOT_CA_PEM_DESTINATION_DIR}..."
        )
        if not os.path.exists(self.ROOT_CA_PEM_DESTINATION_DIR):
            os.makedirs(self.ROOT_CA_PEM_DESTINATION_DIR)
        shutil.copy(
            self.root_ca_pem_path,
            os.path.join(self.ROOT_CA_PEM_DESTINATION_DIR, self.ROOT_CA_PEM_FILE_NAME),
        )

    def configure_control_proxy(self):
        """Creates Control Proxy's configuration file."""
        logger.info("Configuring Control Proxy...")
        if not os.path.exists(self.MAGMA_CONTROL_PROXY_CONFIG_DIR):
            os.makedirs(self.MAGMA_CONTROL_PROXY_CONFIG_DIR)
        if not os.path.exists(
            os.path.join(
                self.MAGMA_CONTROL_PROXY_CONFIG_DIR,
                self.MAGMA_CONTROL_PROXY_CONFIG_FILE_NAME,
            )
        ):
            file_loader = FileSystemLoader(
                os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
            )
            env = Environment(loader=file_loader)
            template = env.get_template("control_proxy.yml.j2")

            with open(
                os.path.join(
                    self.MAGMA_CONTROL_PROXY_CONFIG_DIR,
                    self.MAGMA_CONTROL_PROXY_CONFIG_FILE_NAME,
                ),
                "w",
            ) as control_proxy_file:
                control_proxy_file.write(
                    template.render(
                        domain=self.domain,
                        root_ca_pem_path=self.ROOT_CA_PEM_DESTINATION_DIR,
                        root_ca_pem_file_name=self.ROOT_CA_PEM_FILE_NAME,
                    ),
                )

    def restart_magma_services(self):
        """Restart Magma AGW services."""
        logger.info("Restarting Magma AGW services...")
        self._stop_service("magma@*")
        self._restart_service("magma@magmad")

    @property
    def _control_proxy_config_dir_exists(self):
        """Checks whether directory in which Proxy Config stores its configuration exists."""
        return os.path.exists(self.MAGMA_CONTROL_PROXY_CONFIG_DIR)

    @staticmethod
    def _stop_service(service_name):
        """Stops system service."""
        logger.info(f"Stopping {service_name} service...")
        check_call(["service", service_name, "stop"])

    @staticmethod
    def _restart_service(service_name):
        """Restarts system service."""
        logger.info(f"Restarting {service_name} service...")
        check_call(["service", service_name, "restart"])
