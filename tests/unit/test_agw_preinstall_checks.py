#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from unittest.mock import MagicMock, PropertyMock, patch

from magma_access_gateway_installer.agw_installation_errors import (
    InvalidNumberOfInterfacesError,
    UnsupportedOSError,
)
from magma_access_gateway_installer.agw_preinstall_checks import (
    AGWInstallerPreinstallChecks,
)


class TestAGWInstallerPreinstallChecks(unittest.TestCase):

    MAGMA_USER_DETAILS = ("magma", "x", 1001, 1001, ",,,", "/home/magma", "/bin/bash")
    TEST_NETWORK_INTERFACES = ["eth0", "eth1"]

    def setUp(self) -> None:
        self.agw_preinstall_checks = AGWInstallerPreinstallChecks(self.TEST_NETWORK_INTERFACES)

    def test_given_agw_installer_preinstall_checks_when_installation_attempted_on_redhat_then_ubuntu_is_installed_property_is_false(  # noqa: E501
        self,
    ):
        with patch(
            "platform.version", MagicMock(return_value="#1 SMP Thu Apr 29 08:54:30 EDT 2021")
        ):
            self.assertFalse(self.agw_preinstall_checks._ubuntu_is_installed)

    def test_given_agw_installer_preinstall_checks_when_installation_attempted_on_ubuntu_then_ubuntu_is_installed_property_is_true(  # noqa: E501
        self,
    ):
        with patch(
            "platform.version",
            MagicMock(return_value="#23~20.04.1-Ubuntu SMP Mon Nov 15 14:03:19 UTC 2021"),
        ):
            self.assertTrue(self.agw_preinstall_checks._ubuntu_is_installed)

    def test_given_agw_installer_preinstall_checks_when_given_insufficient_number_of_network_interfaces_then_required_amount_of_network_interfaces_is_available_property_is_false(  # noqa: E501
        self,
    ):
        with patch.object(self.agw_preinstall_checks, "network_interfaces", ["eth0"]):
            self.assertFalse(
                self.agw_preinstall_checks._required_amount_of_network_interfaces_is_available  # noqa: E501
            )

    def test_given_agw_installer_preinstall_checks_when_os_is_not_ubuntu_then_installer_throws_unsupported_os_error(  # noqa: E501
        self,
    ):
        with patch(
            "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._ubuntu_is_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ):
            self.assertRaises(UnsupportedOSError)

    def test_given_agw_installer_preinstall_checks_when_os_is_not_ubuntu_then_unsupported_os_error_is_logged(  # noqa: E501
        self,
    ):
        with patch(
            "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._ubuntu_is_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), patch(
            "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._required_amount_of_network_interfaces_is_available",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), self.assertLogs() as logs:
            try:
                self.agw_preinstall_checks.preinstall_checks()
            except UnsupportedOSError:
                pass
        self.assertEqual(
            logs.records[0].getMessage(),
            "Invalid OS! \n Magma AGW can only be installed on Ubuntu! Exiting...",
        )

    def test_given_agw_installer_preinstall_checks_when_given_insufficient_number_of_network_interfaces_then_installer_throws_invalid_number_of_interfaces_error(  # noqa: E501
        self,
    ):
        with patch(
            "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._required_amount_of_network_interfaces_is_available",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ):
            self.assertRaises(InvalidNumberOfInterfacesError)

    def test_given_agw_installer_preinstall_checks_when_given_insufficient_number_of_network_interfaces_then_invalid_number_of_interfaces_error_is_logged(  # noqa: E501
        self,
    ):
        with patch(
            "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._ubuntu_is_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._required_amount_of_network_interfaces_is_available",  # noqa: E501
            new_callable=PropertyMock,
            return_value=False,
        ), self.assertLogs() as logs:
            try:
                self.agw_preinstall_checks.preinstall_checks()
            except InvalidNumberOfInterfacesError:
                pass
        self.assertEqual(
            logs.records[0].getMessage(),
            "Invalid number of network interfaces!Magma AGW needs two network interfaces - SGi and S1! Exiting...",  # noqa: E501
        )

    def test_given_agw_installer_preinstall_checks_when_all_checks_pass_then_appropriate_message_is_logged(  # noqa: E501
        self,
    ):
        with patch(
            "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._ubuntu_is_installed",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), patch(
            "magma_access_gateway_installer.agw_preinstall_checks.AGWInstallerPreinstallChecks._required_amount_of_network_interfaces_is_available",  # noqa: E501
            new_callable=PropertyMock,
            return_value=True,
        ), self.assertLogs() as logs:
            self.agw_preinstall_checks.preinstall_checks()
        self.assertEqual(
            logs.records[0].getMessage(),
            "Magma AGW pre-install checks completed. Starting installation...",
        )
