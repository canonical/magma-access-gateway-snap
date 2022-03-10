#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import os

logger = logging.getLogger("magma_access_gateway_installer")


class AGWInstallerInstallationServiceCreator:

    AGW_INSTALLATION_SERVICE_FILE_PATH = "/lib/systemd/system/agw_installation.service"
    AGW_INSTALLATION_SERVICE_LINK_PATH = (
        "/etc/systemd/system/multi-user.target.wants/agw_installation.service"
    )

    def create_magma_agw_installation_service(self):
        """Creates Magma AGW installation service which will be used to resume AGW installation
        process after system reboot which is triggered by the pre-installation part.
        """
        logger.info("Creating Magma AGW installation service...")
        magma_installation_service_configuration = """[Unit]
Description=AGW Installation
After=network-online.target
Wants=network-online.target
[Service]
Environment=MAGMA_VERSION=1.6.0
Type=oneshot
ExecStart=/snap/magma-access-gateway/current/bin/python3 -c "from magma_access_gateway_installer.agw_installer import AGWInstaller; AGWInstaller().install()"
SyslogIdentifier=magma_access_gateway_installer
TimeoutStartSec=3800
TimeoutSec=3600
User=root
Group=root
[Install]
WantedBy=multi-user.target
"""  # noqa: E501
        with open(self.AGW_INSTALLATION_SERVICE_FILE_PATH, "w") as installation_service:
            installation_service.write(magma_installation_service_configuration)
        os.chmod(self.AGW_INSTALLATION_SERVICE_FILE_PATH, 0o644)

    def create_magma_agw_installation_service_link(self):
        logger.info("Creating Magma AGW installation service link...")
        try:
            os.symlink(
                self.AGW_INSTALLATION_SERVICE_FILE_PATH, self.AGW_INSTALLATION_SERVICE_LINK_PATH
            )
        except FileExistsError:
            os.remove(self.AGW_INSTALLATION_SERVICE_LINK_PATH)
            os.symlink(
                self.AGW_INSTALLATION_SERVICE_FILE_PATH, self.AGW_INSTALLATION_SERVICE_LINK_PATH
            )
