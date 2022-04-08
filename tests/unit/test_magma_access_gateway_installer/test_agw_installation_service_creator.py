#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from unittest.mock import mock_open, patch

from magma_access_gateway_installer.agw_installation_service_creator import (
    AGWInstallerInstallationServiceCreator,
)


class TestAGWInstallerInstallationServiceCreator(unittest.TestCase):
    def setUp(self) -> None:
        self.agw_installation_service_creator = AGWInstallerInstallationServiceCreator()

    @patch(
        "magma_access_gateway_installer.agw_installation_service_creator.open",
        new_callable=mock_open,
    )
    @patch("magma_access_gateway_installer.agw_installation_service_creator.os")
    def test_given_agw_installation_process_when_create_magma_agw_installation_service_then_proper_installation_config_is_written(  # noqa: E501
        self, _, mock_open_file
    ):
        expected_magma_installation_service_configuration = """[Unit]
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
        self.agw_installation_service_creator.create_magma_agw_installation_service()

        mock_open_file.assert_called_once_with(
            self.agw_installation_service_creator.AGW_INSTALLATION_SERVICE_FILE_PATH, "w"
        )
        mock_open_file().write.assert_called_once_with(
            expected_magma_installation_service_configuration
        )

    @patch("magma_access_gateway_installer.agw_installation_service_creator.os.chmod")
    @patch(
        "magma_access_gateway_installer.agw_installation_service_creator.open",
        new_callable=mock_open,
    )
    def test_given_created_installation_service_descriptor_when_create_magma_agw_installation_service_then_installation_service_descriptor_gets_644_permissions(  # noqa: E501
        self, _, mock_os_chmod
    ):
        self.agw_installation_service_creator.create_magma_agw_installation_service()

        mock_os_chmod.assert_called_with(
            self.agw_installation_service_creator.AGW_INSTALLATION_SERVICE_FILE_PATH, 0o644
        )

    @patch("magma_access_gateway_installer.agw_installation_service_creator.os.symlink")
    def test_given_agw_installation_process_descriptor_created_when_create_magma_agw_installation_service_link_then_symlink_to_installation_service_descriptor_is_created(  # noqa: E501
        self, mock_os_symlink
    ):
        self.agw_installation_service_creator.create_magma_agw_installation_service_link()

        mock_os_symlink.assert_called_once_with(
            self.agw_installation_service_creator.AGW_INSTALLATION_SERVICE_FILE_PATH,
            self.agw_installation_service_creator.AGW_INSTALLATION_SERVICE_LINK_PATH,
        )

    @patch("magma_access_gateway_installer.agw_installation_service_creator.os.symlink")
    @patch("magma_access_gateway_installer.agw_installation_service_creator.os.remove")
    def test_given_agw_installation_process_descriptor_link_exists_when_create_magma_agw_installation_service_link_then_symlink_to_installation_service_descriptor_is_recreated(  # noqa: E501
        self, mock_os_remove, mock_os_symlink
    ):
        mock_os_symlink.side_effect = [FileExistsError, None]
        self.agw_installation_service_creator.create_magma_agw_installation_service_link()

        mock_os_remove.assert_called_once_with(
            self.agw_installation_service_creator.AGW_INSTALLATION_SERVICE_LINK_PATH
        )
        mock_os_symlink.assert_called_with(
            self.agw_installation_service_creator.AGW_INSTALLATION_SERVICE_FILE_PATH,
            self.agw_installation_service_creator.AGW_INSTALLATION_SERVICE_LINK_PATH,
        )
