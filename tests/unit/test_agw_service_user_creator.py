#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import pwd
import unittest
from unittest.mock import Mock, mock_open, patch

from magma_access_gateway_installer.agw_service_user_creator import (
    AGWInstallerServiceUserCreator,
)


class TestAGWInstallerServiceUserCreator(unittest.TestCase):

    MAGMA_USER_DETAILS = pwd.struct_passwd(
        ("magma", "x", 1001, 1001, ",,,", "/home/magma", "/bin/bash")
    )
    MAGMA_USER_NOT_IN_SUDO_GROUP = b"magma : magma\n"
    MAGMA_USER_IN_SUDO_GROUP = b"magma : magma sudo\n"
    ETC_SUDOERS_WITH_MAGMA_USER = """Defaults	env_reset
Defaults	mail_badpass
Defaults	secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin"

# User privilege specification
root	ALL=(ALL:ALL) ALL

# Members of the admin group may gain root privileges
%admin ALL=(ALL) ALL

# Allow members of group sudo to execute any command
%sudo	ALL=(ALL:ALL) ALL

magma ALL=(ALL) NOPASSWD:ALL
"""
    ETC_SUDOERS_WITHOUT_MAGMA_USER = """Defaults	env_reset
Defaults	mail_badpass
Defaults	secure_path="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin"

# User privilege specification
root	ALL=(ALL:ALL) ALL

# Members of the admin group may gain root privileges
%admin ALL=(ALL) ALL

# Allow members of group sudo to execute any command
%sudo	ALL=(ALL:ALL) ALL
"""

    def setUp(self) -> None:
        self.agw_service_user_creator = AGWInstallerServiceUserCreator()

    @patch("magma_access_gateway_installer.agw_service_user_creator.check_call")
    def test_given_magma_user_doesnt_exist_when_create_magma_service_user_then_magma_user_is_created(  # noqa: E501
        self, mock_check_call
    ):
        self.agw_service_user_creator.create_magma_user()

        mock_check_call.assert_called_once_with(
            [
                "adduser",
                "--disabled-password",
                "--gecos",
                '""',
                f"{self.agw_service_user_creator.MAGMA_USER}",
            ]
        )

    @patch("pwd.getpwnam", Mock(return_value=MAGMA_USER_DETAILS))
    @patch("magma_access_gateway_installer.agw_service_user_creator.check_call")
    def test_given_magma_user_exists_when_create_magma_service_user_then_adduser_is_not_called(
        self, mock_check_call
    ):
        self.agw_service_user_creator.create_magma_user()

        mock_check_call.assert_not_called()

    @patch(
        "magma_access_gateway_installer.agw_service_user_creator.check_output",
        Mock(return_value=MAGMA_USER_NOT_IN_SUDO_GROUP),
    )
    @patch("magma_access_gateway_installer.agw_service_user_creator.check_call")
    def test_given_magma_user_not_in_sudo_group_when_add_magma_user_to_sudo_group_then_user_is_added_to_sudo_group(  # noqa: E501
        self, mock_check_call
    ):
        self.agw_service_user_creator.add_magma_user_to_sudo_group()

        mock_check_call.assert_called_once_with(
            ["adduser", self.agw_service_user_creator.MAGMA_USER, "sudo"]
        )

    @patch(
        "magma_access_gateway_installer.agw_service_user_creator.check_output",
        Mock(return_value=MAGMA_USER_IN_SUDO_GROUP),
    )
    @patch("magma_access_gateway_installer.agw_service_user_creator.check_call")
    def test_given_magma_user_in_sudo_group_when_add_magma_user_to_sudo_group_then_adduser_is_not_called(  # noqa: E501
        self, mock_check_call
    ):
        self.agw_service_user_creator.add_magma_user_to_sudo_group()

        mock_check_call.assert_not_called()

    @patch(
        "magma_access_gateway_installer.agw_service_user_creator.open",
        new_callable=mock_open,
        read_data=ETC_SUDOERS_WITHOUT_MAGMA_USER,
    )
    def test_given_magma_user_not_in_etc_sudoers_when_add_magma_user_to_sudoers_file_then_user_is_added_to_etc_sudoers(  # noqa: E501
        self, mock_open_file
    ):
        self.agw_service_user_creator.add_magma_user_to_sudoers_file()

        mock_open_file.assert_called_with("/etc/sudoers", "a")
        mock_open_file().write.called_once_with(
            f"\n{self.agw_service_user_creator.MAGMA_USER} ALL=(ALL) NOPASSWD:ALL\n"
        )

    @patch(
        "magma_access_gateway_installer.agw_service_user_creator.open",
        new_callable=mock_open,
        read_data=ETC_SUDOERS_WITH_MAGMA_USER,
    )
    def test_given_magma_user_in_etc_sudoers_when_add_magma_user_to_sudoers_file_then_nothing_is_written_to_etc_sudoers(  # noqa: E501
        self, mock_check_call
    ):
        self.agw_service_user_creator.add_magma_user_to_sudoers_file()

        mock_check_call.assert_called_once_with("/etc/sudoers", "r")
