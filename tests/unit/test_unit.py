#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import pwd
import unittest
from unittest.mock import MagicMock, Mock, PropertyMock, patch

from magma_access_gateway_installer.agw_installation_errors import (
    InvalidNumberOfInterfacesError,
    UnsupportedOSError,
)
from magma_access_gateway_installer.agw_installer_ubuntu import AGWInstallerUbuntu


class TestSnap(unittest.TestCase):

    MAGMA_USER_DETAILS = ("magma", "x", 1001, 1001, ",,,", "/home/magma", "/bin/bash")

    def setUp(self) -> None:
        self.agw_ubuntu_installer = AGWInstallerUbuntu()

    def test_given_agw_installer_when_installation_attempted_on_redhat_then_ubuntu_is_installed_property_is_false(  # noqa: E501
        self,
    ):
        with patch(
            "platform.version", MagicMock(return_value="#1 SMP Thu Apr 29 08:54:30 EDT 2021")
        ):
            self.assertFalse(self.agw_ubuntu_installer._ubuntu_is_installed)

    def test_given_agw_installer_when_installation_attempted_on_ubuntu_then_ubuntu_is_installed_property_is_true(  # noqa: E501
        self,
    ):
        with patch(
            "platform.version",
            MagicMock(return_value="#23~20.04.1-Ubuntu SMP Mon Nov 15 14:03:19 UTC 2021"),
        ):
            self.assertTrue(self.agw_ubuntu_installer._ubuntu_is_installed)

    def test_given_agw_installer_when_given_insufficient_number_of_network_interfaces_then_required_amount_of_network_interfaces_is_available_property_is_false(  # noqa: E501
        self,
    ):
        with patch.object(self.agw_ubuntu_installer, "network_interfaces", ["eth0"]):
            self.assertFalse(
                self.agw_ubuntu_installer._required_amount_of_network_interfaces_is_available  # noqa: E501
            )

    def test_given_agw_installer_when_os_is_not_ubuntu_then_installer_throws_unsupported_os_error(  # noqa: E501
        self,
    ):
        with patch(
            "magma_access_gateway_installer.agw_installer_ubuntu.AGWInstallerUbuntu._ubuntu_is_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ):
            self.assertRaises(UnsupportedOSError)

    def test_given_agw_installer_when_os_is_not_ubuntu_then_unsupported_os_error_is_logged(  # noqa: E501
        self,
    ):
        with patch(
            "magma_access_gateway_installer.agw_installer_ubuntu.AGWInstallerUbuntu._ubuntu_is_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_installer_ubuntu.AGWInstallerUbuntu._required_amount_of_network_interfaces_is_available",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), self.assertLogs() as logs:
            try:
                self.agw_ubuntu_installer.preinstall_checks()
            except UnsupportedOSError:
                pass
        self.assertEqual(
            logs.records[0].getMessage(),
            "Invalid OS! \n Magma AGW can only be installed on Ubuntu! Exiting...",
        )

    def test_given_agw_installer_when_given_insufficient_number_of_network_interfaces_then_installer_throws_invalid_number_of_interfaces_error(  # noqa: E501
        self,
    ):
        with patch(
            "magma_access_gateway_installer.agw_installer_ubuntu.AGWInstallerUbuntu._required_amount_of_network_interfaces_is_available",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ):
            self.assertRaises(InvalidNumberOfInterfacesError)

    def test_given_agw_installer_when_given_insufficient_number_of_network_interfaces_then_invalid_number_of_interfaces_error_is_logged(  # noqa: E501
        self,
    ):
        with patch(
            "magma_access_gateway_installer.agw_installer_ubuntu.AGWInstallerUbuntu._ubuntu_is_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_installer_ubuntu.AGWInstallerUbuntu._required_amount_of_network_interfaces_is_available",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), self.assertLogs() as logs:
            try:
                self.agw_ubuntu_installer.preinstall_checks()
            except InvalidNumberOfInterfacesError:
                pass
        self.assertEqual(
            logs.records[0].getMessage(),
            "Invalid number of network interfaces!Magma AGW needs two network interfaces - SGi and S1! Exiting...",  # noqa: E501
        )

    @patch("pwd.getpwnam", Mock(auto_spec=True))
    def test_given_agw_installer_when_magma_user_doesnt_exist_then_magma_user_exists_property_is_false(  # noqa: E501
        self,
    ):
        pwd.getpwnam.side_effect = KeyError  # type: ignore[attr-defined]
        self.assertFalse(self.agw_ubuntu_installer._magma_user_exists)

    @patch("pwd.getpwnam", Mock(return_value=MAGMA_USER_DETAILS))
    def test_given_agw_installer_when_magma_user_exists_then_magma_user_exists_property_is_true(
        self,
    ):
        self.assertTrue(self.agw_ubuntu_installer._magma_user_exists)

    @patch("pwd.getpwnam", Mock(auto_spec=True))
    def test_given_agw_installer_when_magma_user_doesnt_exist_then_installer_creates_and_configures_magma_user(  # noqa: E501
        self,
    ):
        pwd.getpwnam.side_effect = KeyError  # type: ignore[attr-defined]
        with patch.object(
            self.agw_ubuntu_installer, "_create_magma_user"
        ) as create_magma_user_mock, patch.object(
            self.agw_ubuntu_installer, "_add_magma_user_to_sudoers"
        ) as configure_magma_user_mock:
            self.agw_ubuntu_installer.create_magma_service_user()
        create_magma_user_mock.assert_called_once()
        configure_magma_user_mock.assert_called_once()
