#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from argparse import Namespace

import magma_access_gateway_installer


class TestAGWInstallerInit(unittest.TestCase):

    VALID_TEST_IP_ADDRESS = "1.2.3.4/24"
    INVALID_TEST_IP_ADDRESS = "321.0.1.5/24"
    VALID_TEST_GW_IP_ADDRESS = "2.3.4.5"
    INVALID_TEST_GW_IP_ADDRESS = "321.3.4.5"

    def test_given_only_ip_address_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(ip_address=self.VALID_TEST_IP_ADDRESS, gw_ip_address=None)

        with self.assertRaises(ValueError):
            magma_access_gateway_installer.validate_args(test_args)

    def test_given_only_gw_ip_address_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(ip_address=None, gw_ip_address=self.VALID_TEST_GW_IP_ADDRESS)

        with self.assertRaises(ValueError):
            magma_access_gateway_installer.validate_args(test_args)

    def test_given_invalid_gw_ip_address_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(
            ip_address=self.VALID_TEST_IP_ADDRESS, gw_ip_address=self.INVALID_TEST_GW_IP_ADDRESS
        )

        with self.assertRaises(ValueError):
            magma_access_gateway_installer.validate_args(test_args)

    def test_given_invalid_ip_address_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(
            ip_address=self.INVALID_TEST_IP_ADDRESS, gw_ip_address=self.VALID_TEST_GW_IP_ADDRESS
        )

        with self.assertRaises(ValueError):
            magma_access_gateway_installer.validate_args(test_args)
