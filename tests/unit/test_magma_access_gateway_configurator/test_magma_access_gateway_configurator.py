#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from argparse import Namespace
from unittest.mock import Mock, patch

import magma_access_gateway_configurator


class TestAGWConfiguratorInit(unittest.TestCase):

    VALID_TEST_DOMAIN = "agw-test.com"
    INVALID_TEST_DOMAIN = "agw-test"

    @patch(
        "magma_access_gateway_configurator.os.path.exists",
        Mock(return_value=True),
    )
    def test_given_invalid_domain_cli_argument_is_passed_when_validate_args_then_validationfailure_error_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(domain=self.INVALID_TEST_DOMAIN, root_ca_path="whatever")

        with self.assertRaises(magma_access_gateway_configurator.AGWConfigurationError):
            magma_access_gateway_configurator.validate_args(test_args)

    @patch(
        "magma_access_gateway_configurator.os.path.exists",
        Mock(return_value=False),
    )
    def test_given_non_existent_root_ca_path_cli_argument_is_passed_when_validate_args_then_filenotfounderror_is_raised(  # noqa: E501
        self,
    ):
        test_args = Namespace(domain=self.VALID_TEST_DOMAIN, root_ca_path="whatever")

        with self.assertRaises(FileNotFoundError):
            magma_access_gateway_configurator.validate_args(test_args)
