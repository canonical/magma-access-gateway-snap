#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from unittest.mock import Mock, PropertyMock, call, mock_open, patch

from magma_access_gateway_installer.agw_service_user_creator import (
    AGWInstallerServiceUserCreator,
)


class TestAGWInstallerServiceUserCreator(unittest.TestCase):
    def setUp(self) -> None:
        self.agw_service_user_creator = AGWInstallerServiceUserCreator()

    @patch(
        "magma_access_gateway_installer.agw_service_user_creator.AGWInstallerServiceUserCreator._add_magma_user_to_sudoers",  # noqa: E501
        Mock(),
    )
    @patch(
        "magma_access_gateway_installer.agw_service_user_creator.AGWInstallerServiceUserCreator._magma_user_exists",  # noqa: E501
        new_callable=PropertyMock,
    )
    @patch("magma_access_gateway_installer.agw_service_user_creator.check_call")
    def test_given_magma_user_doesnt_exist_when_create_magma_service_user_is_called_then_magma_user_is_created(  # noqa: E501
        self, mock_check_call, mocked_magma_user_exists
    ):
        mocked_magma_user_exists.return_value = False
        self.agw_service_user_creator.create_magma_service_user()
        mock_check_call.assert_called_once_with(
            [
                "adduser",
                "--disabled-password",
                "--gecos",
                '""',
                f"{self.agw_service_user_creator.MAGMA_USER}",
            ]
        )

    @patch(
        "magma_access_gateway_installer.agw_service_user_creator.AGWInstallerServiceUserCreator._create_magma_user"  # noqa: E501, W505
    )
    @patch(
        "magma_access_gateway_installer.agw_service_user_creator.AGWInstallerServiceUserCreator._add_magma_user_to_sudoers"  # noqa: E501, W505
    )
    @patch(
        "magma_access_gateway_installer.agw_service_user_creator.AGWInstallerServiceUserCreator._magma_user_exists",  # noqa: E501
        new_callable=PropertyMock,
    )
    def test_given_magma_user_exists_when_create_magma_service_user_is_called_then_user_creation_is_skipped(  # noqa: E501
        self, mocked_magma_user_exists, mocked_add_magma_user_to_sudoers, mocked_create_magma_user
    ):
        mocked_magma_user_exists.return_value = True
        self.agw_service_user_creator.create_magma_service_user()
        mocked_create_magma_user.assert_not_called()
        mocked_add_magma_user_to_sudoers.assert_not_called()

    @patch(
        "magma_access_gateway_installer.agw_service_user_creator.AGWInstallerServiceUserCreator._create_magma_user",  # noqa: E501
        Mock(),
    )
    @patch("builtins.open", new_callable=mock_open())
    @patch(
        "magma_access_gateway_installer.agw_service_user_creator.AGWInstallerServiceUserCreator._magma_user_exists",  # noqa: E501
        new_callable=PropertyMock,
    )
    @patch("magma_access_gateway_installer.agw_service_user_creator.check_call")
    def test_given_magma_user_doesnt_exist_when_create_magma_service_user_is_called_then_magma_user_is_added_to_sudoers(  # noqa: E501
        self, mock_check_call, mocked_magma_user_exists, mocked_open_file
    ):
        mocked_magma_user_exists.return_value = False
        self.agw_service_user_creator.create_magma_service_user()
        mock_check_call.assert_called_once_with(
            ["adduser", f"{self.agw_service_user_creator.MAGMA_USER}", "sudo"]
        )
        mocked_open_file.assert_called_with("/etc/sudoers", "a")
        etc_sudoers_write_calls = [
            call("\n"),
            call(f"{self.agw_service_user_creator.MAGMA_USER} ALL=(ALL) NOPASSWD:ALL"),
            call("\n"),
        ]
        mocked_open_file().__enter__().write.assert_has_calls(etc_sudoers_write_calls)
