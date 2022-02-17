#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import pwd
import unittest
from unittest.mock import Mock, PropertyMock, call, mock_open, patch

from magma_access_gateway_installer.agw_service_user_creator import (
    AGWInstallerServiceUserCreator,
)


class TestAGWInstallerServiceUserCreator(unittest.TestCase):

    MAGMA_USER_DETAILS = ("magma", "x", 1001, 1001, ",,,", "/home/magma", "/bin/bash")

    def setUp(self) -> None:
        self.agw_service_user_creator = AGWInstallerServiceUserCreator()

    @patch("pwd.getpwnam", Mock(auto_spec=True))
    def test_given_agw_installer_service_user_creator_when_magma_user_doesnt_exist_then_magma_user_exists_property_is_false(  # noqa: E501
        self,
    ):
        pwd.getpwnam.side_effect = KeyError  # type: ignore[attr-defined]
        self.assertFalse(self.agw_service_user_creator._magma_user_exists)

    @patch("pwd.getpwnam", Mock(return_value=MAGMA_USER_DETAILS))
    def test_given_agw_installer_service_user_creator_when_magma_user_exists_then_magma_user_exists_property_is_true(  # noqa: E501
        self,
    ):
        self.assertTrue(self.agw_service_user_creator._magma_user_exists)

    def test_given_agw_installer_service_user_creator_when_magma_user_doesnt_exist_then_installer_creates_and_configures_magma_user(  # noqa: E501
        self,
    ):
        with patch(
            "magma_access_gateway_installer.agw_service_user_creator.AGWInstallerServiceUserCreator._magma_user_exists",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch.object(
            self.agw_service_user_creator, "_create_magma_user"
        ) as create_magma_user_mock, patch.object(
            self.agw_service_user_creator, "_add_magma_user_to_sudoers"
        ) as configure_magma_user_mock:
            self.agw_service_user_creator.create_magma_service_user()
        create_magma_user_mock.assert_called_once()
        configure_magma_user_mock.assert_called_once()

    def test_given_agw_installer_service_user_creator_when_magma_user_exists_then_user_creation_is_skipped(  # noqa: E501
        self,
    ):
        with patch(
            "magma_access_gateway_installer.agw_service_user_creator.AGWInstallerServiceUserCreator._magma_user_exists",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch.object(
            self.agw_service_user_creator, "_create_magma_user"
        ) as create_magma_user_mock, patch.object(
            self.agw_service_user_creator, "_add_magma_user_to_sudoers"
        ) as configure_magma_user_mock:
            self.agw_service_user_creator.create_magma_service_user()
        create_magma_user_mock.assert_not_called()
        configure_magma_user_mock.assert_not_called()

    @patch(
        "magma_access_gateway_installer.agw_service_user_creator.AGWInstallerServiceUserCreator.MAGMA_USER"  # noqa: E501, W505
    )
    @patch("magma_access_gateway_installer.agw_service_user_creator.check_call")
    def test_given_agw_installer_service_user_creator_when__create_magma_user_is_called_then_correct_message_is_logged(  # noqa: E501
        self, mock_check_call, mock_magma_user
    ):
        mock_magma_user.return_value = "test"
        with self.assertLogs() as logs, patch("builtins.open", mock_open()):
            self.agw_service_user_creator._create_magma_user()
        self.assertEqual(
            logs.records[0].getMessage(),
            f"Adding Magma user: {mock_magma_user}...",
        )

    @patch(
        "magma_access_gateway_installer.agw_service_user_creator.AGWInstallerServiceUserCreator.MAGMA_USER"  # noqa: E501, W505
    )
    @patch("magma_access_gateway_installer.agw_service_user_creator.check_call")
    def test_given_agw_installer_service_user_creator_when_create_magma_user_is_called_then_correct_adduser_command_is_executed(  # noqa: E501
        self, mock_check_call, mock_magma_user
    ):
        mock_magma_user.return_value = "test"
        with patch("builtins.open", mock_open()):
            self.agw_service_user_creator._create_magma_user()
        mock_check_call.assert_called_once_with(
            ["adduser", "--disabled-password", "--gecos", '""', f"{mock_magma_user}"]
        )

    @patch(
        "magma_access_gateway_installer.agw_service_user_creator.AGWInstallerServiceUserCreator.MAGMA_USER"  # noqa: E501, W505
    )
    @patch("magma_access_gateway_installer.agw_service_user_creator.check_call")
    def test_given_agw_installer_service_user_creator_when_add_magma_user_to_sudoers_is_called_then_correct_adduser_command_is_executed(  # noqa: E501
        self, mock_check_call, mock_magma_user
    ):
        mock_magma_user.return_value = "test"
        with patch("builtins.open", mock_open()):
            self.agw_service_user_creator._add_magma_user_to_sudoers()
        mock_check_call.assert_called_once_with(["adduser", f"{mock_magma_user}", "sudo"])

    @patch(
        "magma_access_gateway_installer.agw_service_user_creator.AGWInstallerServiceUserCreator.MAGMA_USER"  # noqa: E501, W505
    )
    @patch("magma_access_gateway_installer.agw_service_user_creator.check_call")
    def test_given_agw_installer_service_user_creator_when_add_magma_user_to_sudoers_is_called_then_correct_message_is_logged(  # noqa: E501
        self, mock_check_call, mock_magma_user
    ):
        mock_magma_user.return_value = "test"
        with self.assertLogs() as logs, patch("builtins.open", mock_open()):
            self.agw_service_user_creator._add_magma_user_to_sudoers()
        self.assertEqual(
            logs.records[0].getMessage(),
            f'Adding Magma user "{mock_magma_user}" to sudoers...',
        )

    @patch(
        "magma_access_gateway_installer.agw_service_user_creator.AGWInstallerServiceUserCreator.MAGMA_USER"  # noqa: E501, W505
    )
    @patch("magma_access_gateway_installer.agw_service_user_creator.check_call")
    def test_given_agw_installer_service_user_creator_when_add_magma_user_to_sudoers_is_called_then_correct_entry_is_added_to_etc_sudoers(  # noqa: E501
        self, mock_check_call, mock_magma_user
    ):
        mock_magma_user.return_value = "test"
        with patch("builtins.open", mock_open()) as mocked_open_file:
            self.agw_service_user_creator._add_magma_user_to_sudoers()
        mocked_open_file.assert_called_with("/etc/sudoers", "a")
        etc_sudoers_write_calls = [
            call("\n"),
            call(f"{mock_magma_user} ALL=(ALL) NOPASSWD:ALL"),
            call("\n"),
        ]
        mocked_open_file().write.assert_has_calls(etc_sudoers_write_calls)
