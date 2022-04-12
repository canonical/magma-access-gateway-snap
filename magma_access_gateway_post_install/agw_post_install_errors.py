#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import sys

logger = logging.getLogger("magma_access_gateway_post_install")
sys.tracebacklimit = 0


class PostInstallError(Exception):
    def __init__(self, message):
        self._message = f"ERROR: {message}"
        logger.error(self._message)

    @property
    def message(self):
        return self._message


class AGWConfigurationError(PostInstallError):
    def __init__(self, message):
        super().__init__(message)


class AGWServicesNotRunningError(PostInstallError):
    def __init__(self, not_running_services: list):
        super().__init__(
            f'Following services are not running: {" ".join(not_running_services)}\n'
            "Please check Magma FAQ at https://docs.magmacore.org/docs/next/faq/faq_magma."
        )


class AGWPackagesMissingError(PostInstallError):
    def __init__(self, missing_packages: list):
        super().__init__(
            f'Following Magma AGW packages are not installed: {" ".join(missing_packages)}\n'
            "Please try running Magma AGW installation again."
        )


class AGWRootCertificateMissingError(PostInstallError):
    def __init__(self):
        super().__init__(
            "Root Certificate not found under /var/opt/magma/tmp/certs/.\n"
            "Please follow Access Gateway Configuration section of Magma AGW documentation "
            "(https://docs.magmacore.org/docs/next/lte/deploy_config_agw) and retry."
        )


class AGWControlProxyConfigFileMissingError(PostInstallError):
    def __init__(self):
        super().__init__(
            "Control Proxy configuration file missing!\n"
            "Please follow Access Gateway Configuration section of Magma AGW documentation "
            "(https://docs.magmacore.org/docs/next/lte/deploy_config_agw) and retry."
        )


class AGWControlProxyConfigurationError(PostInstallError):
    def __init__(self, missing_keys: list):
        super().__init__(
            f'Following Control Proxy parameters are not configured: {" ".join(missing_keys)}\n'
            "Please follow Access Gateway Configuration section of Magma AGW documentation "
            "(https://docs.magmacore.org/docs/next/lte/deploy_config_agw) and retry."
        )


class AGWCloudCheckinError(PostInstallError):
    def __init__(self):
        super().__init__(
            "Cloud checkin failed!"
            "Please follow Access Gateway Configuration section of Magma AGW documentation "
            "(https://docs.magmacore.org/docs/next/lte/deploy_config_agw) and retry."
        )
