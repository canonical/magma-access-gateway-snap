#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import os
import time
from subprocess import DEVNULL, call, check_output

import yaml
from ping3 import ping  # type: ignore[import]
from systemd import journal  # type: ignore[import]

from .agw_post_install_errors import (
    AGWConfigurationError,
    AGWControlProxyConfigFileMissingError,
    AGWControlProxyConfigurationError,
    AGWPackagesMissingError,
    AGWRootCertificateMissingError,
    AGWServicesNotRunningError,
    Orc8rConnectivityError,
)

logger = logging.getLogger("magma_access_gateway_post_install")


class AGWPostInstallChecks:

    MAGMA_AGW_INTERFACES = ["eth0", "eth1", "gtp_br0", "uplink_br0"]
    MAGMA_AGW_SERVICES = [
        "magma@control_proxy",
        "magma@directoryd",
        "magma@dnsd",
        "magma@enodebd",
        "magma@magmad",
        "magma@mme",
        "magma@mobilityd",
        "magma@pipelined",
        "magma@policydb",
        "magma@redis",
        "magma@sessiond",
        "magma@state",
        "magma@subscriberdb",
    ]
    NON_MAGMA_SERVICES = ["sctpd"]
    REQUIRED_PACKAGES = [
        "magma",
        "magma-cpp-redis",
        "magma-libfluid",
        "libopenvswitch",
        "openvswitch-datapath-dkms",
        "openvswitch-common",
        "openvswitch-switch",
    ]
    REQUIRED_CONTROL_PROXY_KEYS = [
        "cloud_address",
        "cloud_port",
        "bootstrap_address",
        "bootstrap_port",
        "rootca_cert",
        "fluentd_address",
        "fluentd_port",
    ]
    GOT_HEARTBEAT_MSG = "[SyncRPC] Got heartBeat from cloud"
    ORC8R_CHECKIN_SUCCESSFUL_MSG = "Checkin Successful! Successfully sent states to the cloud!"
    TIMEOUT_WAITING_FOR_SERVICE = 60
    WAIT_FOR_SERVICE_INTERVAL = 10

    def check_whether_required_interfaces_are_configured(self):
        """Checks whether Magma AGW interfaces are configured or not.

        :raises:
            AGWConfigurationError: if any of specified interfaces hasn't been configured
        """
        logger.info("Checking network interfaces configuration...")
        if faulty_interfaces := [
            interface
            for interface in self.MAGMA_AGW_INTERFACES
            if not os.path.exists(os.path.join("/sys/class/net", interface, "operstate"))
            or "down" in self._get_interface_state(interface)  # noqa: W503
        ]:
            raise AGWConfigurationError(
                f'Following interfaces are not configured: {" ".join(faulty_interfaces)}\n'
                "Most common reasons for this error include:\n"
                "  - Invalid configuration in /etc/netplan/99-magma-config.yaml.\n"
                "  - Interface not being connected to the network.\n"
                "  - Problem with Open vSwitch installation."
            )

    @staticmethod
    def check_ovs_has_not_unsupported_gpt_error():
        """Checks whether ovs has unsupported gtp error.

        :raises:
            AGWConfigurationError: if OVS has any gtp error
        """
        logger.info("Checking whether OVS has unsupported gtp error")
        error = b'error: "could not add network device'

        if (ovs_show_result := check_output(["sudo", "ovs-vsctl", "show"])).decode(
            "utf-8"
        ).rstrip() and error in ovs_show_result:  # noqa: E501  # noqa: W503
            raise AGWConfigurationError(
                "OVS does not support gtp. Make sure your kernel is 5.4. For downgrading your kernel, please refer to:"  # noqa E501, W505
                "https://discourse.ubuntu.com/t/how-to-downgrade-the-kernel-on-ubuntu-20-04-to-the-5-4-lts-version/26459"  # noqa E501, W505
            )

    @staticmethod
    def check_eth0_internet_connectivity():
        """Checks eth0's network connectivity by pinging DNS.

        :raises:
            AGWConfigurationError: if eth0 fails to connect to the internet
        """
        logger.info("Checking eth0's internet connectivity...")
        if not bool(ping(dest_addr="artifactory.magmacore.org", interface="eth0")):
            raise AGWConfigurationError(
                "eth0 is not connected to the internet!\n"
                "Make sure the hardware has been properly plugged in (eth0 to internet)."
            )

    def check_whether_required_services_are_running(self):
        """Checks whether all services required by Magma AGW are running.

        :raises:
            AGWServiceNotRunningError: if any of required services is not running
        """
        logger.info("Checking whether required services are running...")
        if services_down := [
            service
            for service in self.MAGMA_AGW_SERVICES + self.NON_MAGMA_SERVICES
            if self._wait_for_service(service)
        ]:
            raise AGWServicesNotRunningError(services_down)

    def check_whether_required_packages_are_installed(self):
        """Checks whether all packages required by Magma AGW are installed.

        :raises:
            AGWPackageMissingError: if any Magma AGW packages are missing
        """
        logger.info("Checking whether required packages are installed...")
        if missing_packages := [
            package
            for package in self.REQUIRED_PACKAGES
            if not self._package_is_installed(package)
        ]:
            raise AGWPackagesMissingError(missing_packages)

    @staticmethod
    def check_whether_root_certificate_exists():
        """Checks whether rootCA.pem certificate exists under /var/opt/magma/tmp/certs/.

        :raises:
            AGWRootCertificateMissingError: if the certificate is missing
        """
        logger.info("Checking whether Root Certificate exists...")
        if not os.path.exists("/var/opt/magma/tmp/certs/rootCA.pem"):
            raise AGWRootCertificateMissingError()

    def check_control_proxy(self):
        """Checks whether Control Proxy is configured."""
        logger.info("Checking Control Proxy configuration...")
        if not self._control_proxy_config_exists:
            raise AGWControlProxyConfigFileMissingError()
        self._check_control_proxy_configuration()

    def check_connectivity_with_orc8r(self):
        """Checks whether Access Gateway successfully connected to the Orchestrator."""
        logger.info("Checking AGW connectivity with Orchestrator...")
        journal_reader = journal.Reader()
        journal_reader.log_level(journal.LOG_INFO)
        journal_reader.this_boot()
        journal_reader.add_match(SYSLOG_IDENTIFIER="magmad")
        if not (
            any(
                entry["MESSAGE"]
                for entry in journal_reader
                if self.GOT_HEARTBEAT_MSG in entry["MESSAGE"]
            )
            or any(  # noqa: W503
                entry["MESSAGE"]
                for entry in journal_reader
                if self.ORC8R_CHECKIN_SUCCESSFUL_MSG in entry["MESSAGE"]
            )
        ):
            raise Orc8rConnectivityError()

    @staticmethod
    def _get_interface_state(interface_name):
        """Gets interface state from operstate file."""
        with open(os.path.join("/sys/class/net", interface_name, "operstate"), "r") as if_conf:
            return if_conf.read().strip()

    @property
    def _control_proxy_config_exists(self) -> bool:
        """Checks whether Control Proxy config file exists."""
        return os.path.exists("/var/opt/magma/configs/control_proxy.yml")

    def _check_control_proxy_configuration(self):
        """Checks whether Control Proxy config file contains all required keys.

        :raises:
            AGWControlProxyConfigurationError: if any of the required configuration parameters
            is missing
        """
        with open("/var/opt/magma/configs/control_proxy.yml", "r") as control_proxy_file:
            control_proxy_file_content = yaml.safe_load(control_proxy_file)
        if missing_config_keys := list(
            set(self.REQUIRED_CONTROL_PROXY_KEYS) - set(control_proxy_file_content.keys())
        ):
            raise AGWControlProxyConfigurationError(missing_config_keys)

    def _wait_for_service(self, service_name):
        """Waits for specified service to become active. If it doesn't happen within 60 seconds,
        service name is returned.
        """
        now = time.time()
        while time.time() < now + self.TIMEOUT_WAITING_FOR_SERVICE:
            if self._service_is_running(service_name):
                return
            time.sleep(self.WAIT_FOR_SERVICE_INTERVAL)
        return service_name

    @staticmethod
    def _service_is_running(service_name) -> bool:
        """Checks whether specified systemd service is running."""
        return call(["systemctl", "is-active", "--quiet", service_name]) == 0

    @staticmethod
    def _package_is_installed(package_name) -> bool:
        """Checks whether specified system package is installed."""
        return call(["dpkg-query", "-W", "-f='${Status}'", package_name], stdout=DEVNULL) == 0
