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
    DNS_LIST_WITH_VALID_ADDRESS = ["1.2.3.4", "5.6.7.8"]
    DNS_LIST_WITH_INVALID_ADDRESS = ["1.2.3.4", "321.3.4.5", "5.6.7.8"]
    TEST_INTERFACES_LIST = ["bear", "rabbit", "eagle", "moose"]
    VALID_TEST_SGi_INTERFACE_NAME = "rabbit"
    INVALID_TEST_SGi_INTERFACE_NAME = "wolf"
    VALID_TEST_S1_INTERFACE_NAME = "moose"
    INVALID_TEST_S1_INTERFACE_NAME = "snake"

    def test_given_only_ip_address_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(ip_address=self.VALID_TEST_IP_ADDRESS, gw_ip_address=None)

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args, self.TEST_INTERFACES_LIST)

    def test_given_only_gw_ip_address_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(ip_address=None, gw_ip_address=self.VALID_TEST_GW_IP_ADDRESS)

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args, self.TEST_INTERFACES_LIST)

    def test_given_invalid_gw_ip_address_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(
            ip_address=self.VALID_TEST_IP_ADDRESS, gw_ip_address=self.INVALID_TEST_GW_IP_ADDRESS
        )

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args, self.TEST_INTERFACES_LIST)

    def test_given_invalid_ip_address_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(
            ip_address=self.INVALID_TEST_IP_ADDRESS, gw_ip_address=self.VALID_TEST_GW_IP_ADDRESS
        )

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args, self.TEST_INTERFACES_LIST)

    def test_given_invalid_dns_ip_address_passed_when_validate_args_then_value_error_is_raised(
        self,
    ):
        test_args = Namespace(
            ip_address=None, gw_ip_address=None, dns=self.DNS_LIST_WITH_INVALID_ADDRESS
        )

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args, self.TEST_INTERFACES_LIST)

    def test_given_dns_flag_used_without_any_dns_ips_when_validate_args_then_value_error_is_raised(
        self,
    ):
        test_args = Namespace(ip_address=None, gw_ip_address=None, dns=None)

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args, self.TEST_INTERFACES_LIST)

    def test_given_only_sgi_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(
        self,
    ):
        test_args = Namespace(
            ip_address=None,
            gw_ip_address=None,
            dns=self.DNS_LIST_WITH_VALID_ADDRESS,
            sgi=self.VALID_TEST_SGi_INTERFACE_NAME,
            s1=None,
        )

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args, self.TEST_INTERFACES_LIST)

    def test_given_only_s1_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(
        self,
    ):
        test_args = Namespace(
            ip_address=None,
            gw_ip_address=None,
            dns=self.DNS_LIST_WITH_VALID_ADDRESS,
            sgi=None,
            s1=self.VALID_TEST_S1_INTERFACE_NAME,
        )

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args, self.TEST_INTERFACES_LIST)

    def test_given_invalid_sgi_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(
            ip_address=None,
            gw_ip_address=None,
            dns=self.DNS_LIST_WITH_VALID_ADDRESS,
            sgi=self.INVALID_TEST_SGi_INTERFACE_NAME,
            s1=self.VALID_TEST_S1_INTERFACE_NAME,
        )

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args, self.TEST_INTERFACES_LIST)

    def test_given_invalid_s1_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(
        self,
    ):
        test_args = Namespace(
            ip_address=None,
            gw_ip_address=None,
            dns=self.DNS_LIST_WITH_VALID_ADDRESS,
            sgi=self.VALID_TEST_SGi_INTERFACE_NAME,
            s1=self.INVALID_TEST_S1_INTERFACE_NAME,
        )

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args, self.TEST_INTERFACES_LIST)

    def test_given_invalid_sgi_and_s1_cli_argument_is_passed_when_validate_args_then_value_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(
            ip_address=None,
            gw_ip_address=None,
            dns=self.DNS_LIST_WITH_VALID_ADDRESS,
            sgi=self.INVALID_TEST_SGi_INTERFACE_NAME,
            s1=self.INVALID_TEST_S1_INTERFACE_NAME,
        )

        with self.assertRaises(magma_access_gateway_installer.ArgumentError):
            magma_access_gateway_installer.validate_args(test_args, self.TEST_INTERFACES_LIST)
