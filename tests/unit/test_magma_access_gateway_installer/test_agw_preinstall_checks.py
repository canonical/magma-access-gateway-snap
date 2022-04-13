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
    VALID_TEST_USER = b"root"
    INVALID_TEST_USER = b"test_user"
    INVALID_SYSTEM = "#1 SMP Thu Apr 29 08:54:30 EDT 2021"
    INVALID_UBUNTU_VERSION = "#23~21.10.1-Ubuntu SMP Mon Nov 15 14:03:19 UTC 2021"
    VALID_UBUNTU_VERSION = "#23~20.04.1-Ubuntu SMP Mon Nov 15 14:03:19 UTC 2021"
    INVALID_TEST_NETWORK_INTERFACES = ["test1"]

    def setUp(self) -> None:
        self.agw_preinstall_checks = AGWInstallerPreinstallChecks(self.TEST_NETWORK_INTERFACES)

    @patch(
        "magma_access_gateway_installer.agw_preinstall_checks.check_output",
        return_value=INVALID_TEST_USER,
    )
    def test_given_installation_user_is_not_root_when_preinstall_checks_then_invalid_user_error_is_raised(  # noqa: E501
        self, _
    ):
        with self.assertRaises(InvalidUserError):
            self.agw_preinstall_checks.preinstall_checks()

    @patch(
        "magma_access_gateway_installer.agw_preinstall_checks.platform.version",
        return_value=INVALID_SYSTEM,
    )
    @patch(
        "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._user_is_root",  # noqa: E501
        new_callable=PropertyMock,
    )
    def test_given_os_is_not_ubuntu_when_preinstall_checks_then_unsupported_os_error_is_raised(
        self, _, __
    ):
        with self.assertRaises(UnsupportedOSError):
            self.agw_preinstall_checks.preinstall_checks()

    @patch(
        "magma_access_gateway_installer.agw_preinstall_checks.platform.version",
        return_value=INVALID_UBUNTU_VERSION,
    )
    @patch(
        "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._user_is_root",  # noqa: E501
        new_callable=PropertyMock,
    )
    def test_given_os_is_ubuntu_in_unsupported_version_when_preinstall_checks_then_unsupported_os_error_is_raised(  # noqa: E501
        self, _, __
    ):
        with self.assertRaises(UnsupportedOSError):
            self.agw_preinstall_checks.preinstall_checks()

    @patch(
        "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._user_is_root",  # noqa: E501
        new_callable=PropertyMock,
    )
    @patch(
        "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._ubuntu_is_installed",  # noqa: E501
        new_callable=PropertyMock,
    )
    def test_given_insufficient_number_of_network_interfaces_when_preinstall_checks_then_invalid_number_of_interfaces_error_is_raised(  # noqa: E501
        self, _, __
    ):
        agw_preinstall_checks = AGWInstallerPreinstallChecks(self.INVALID_TEST_NETWORK_INTERFACES)
        with self.assertRaises(InvalidNumberOfInterfacesError):
            agw_preinstall_checks.preinstall_checks()

    @patch("magma_access_gateway_installer.agw_preinstall_checks.check_call")
    def test_given_system_meeting_installation_requirements_when_install_required_system_packages_then_apt_installs_required_packages(  # noqa: E501
        self, mock_check_call
    ):
        expected_apt_calls = [call(["apt", "-qq", "update"])]
        for required_package in self.agw_preinstall_checks.REQUIRED_SYSTEM_PACKAGES:
            expected_apt_calls.append(call(["apt", "-qq", "install", "-y", required_package]))

        self.agw_preinstall_checks.install_required_system_packages()

        mock_check_call.assert_has_calls(expected_apt_calls)

    @patch(
        "magma_access_gateway_installer.agw_preinstall_checks.platform.version",
        return_value=VALID_UBUNTU_VERSION,
    )
    @patch(
        "magma_access_gateway_installer.agw_preinstall_checks.check_output",
        return_value=VALID_TEST_USER,
    )
    def test_given_system_meets_installation_requirements_when_preinstall_checks_then_no_errors_are_raised(  # noqa: E501
        self, _, __
    ):
        self.assertEqual(self.agw_preinstall_checks.preinstall_checks(), None)
