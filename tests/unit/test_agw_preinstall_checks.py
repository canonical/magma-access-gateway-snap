#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from unittest.mock import PropertyMock, call, patch

from magma_access_gateway_installer.agw_installation_errors import (
    InvalidNumberOfInterfacesError,
    InvalidUserError,
    UnsupportedOSError,
)
from magma_access_gateway_installer.agw_preinstall_checks import (
    AGWInstallerPreinstallChecks,
)


class TestAGWInstallerPreinstallChecks(unittest.TestCase):

    TEST_NETWORK_INTERFACES = ["eth0", "eth1"]

    def setUp(self) -> None:
        self.agw_preinstall_checks = AGWInstallerPreinstallChecks(self.TEST_NETWORK_INTERFACES)

    @patch(
        "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._user_is_root",  # noqa: E501
        new_callable=PropertyMock,
    )
    def test_given_installation_user_is_not_root_when_preinstall_checks_then_invalid_user_error_is_raised(  # noqa: E501
        self, mock_user_is_root
    ):
        mock_user_is_root.return_value = False

        with self.assertRaises(InvalidUserError):
            self.agw_preinstall_checks.preinstall_checks()

    @patch(
        "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._ubuntu_is_installed",  # noqa: E501
        new_callable=PropertyMock,
    )
    @patch(
        "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._user_is_root",  # noqa: E501
        new_callable=PropertyMock,
    )
    def test_given_os_is_not_ubuntu_when_preinstall_checks_then_unsupported_os_error_is_raised(
        self, _, mock_ubuntu_is_installed
    ):
        mock_ubuntu_is_installed.return_value = False

        with self.assertRaises(UnsupportedOSError):
            self.agw_preinstall_checks.preinstall_checks()

    @patch(
        "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._required_amount_of_network_interfaces_is_available",  # noqa: E501
        new_callable=PropertyMock,
    )
    @patch(
        "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._user_is_root",  # noqa: E501
        new_callable=PropertyMock,
    )
    @patch(
        "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._ubuntu_is_installed",  # noqa: E501
        new_callable=PropertyMock,
    )
    def test_given_insufficient_number_of_network_interfaces_when_preinstall_checks_then_invalid_number_of_interfaces_error_is_raised(  # noqa: E501
        self, _, __, mock_required_amount_of_network_interfaces_is_available
    ):
        mock_required_amount_of_network_interfaces_is_available.return_value = False

        with self.assertRaises(InvalidNumberOfInterfacesError):
            self.agw_preinstall_checks.preinstall_checks()

    @patch("magma_access_gateway_installer.agw_preinstall_checks.check_call")
    def test_given_system_meeting_installation_requirements_when_install_required_system_packages_then_apt_installs_required_packages(  # noqa: E501
        self, mock_check_call
    ):
        expected_apt_calls = [call(["apt", "update"])]
        for required_package in self.agw_preinstall_checks.REQUIRED_SYSTEM_PACKAGES:
            expected_apt_calls.append(call(["apt", "install", "-y", required_package]))

        self.agw_preinstall_checks.install_required_system_packages()

        mock_check_call.assert_has_calls(expected_apt_calls)
