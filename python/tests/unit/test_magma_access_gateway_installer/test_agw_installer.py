#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from unittest.mock import MagicMock, Mock, call, mock_open, patch

from magma_access_gateway_installer.agw_installer import AGWInstaller


class TestAGWInstaller(unittest.TestCase):

    TEST_MAGMA_VERSION = "bla-bla-123"
    APT_LIST_WITH_MAGMA = b"""lua-cjson/focal,now 2.1.0+dfsg-2.1 amd64 [installed,automatic]\n
lvm2/focal,now 2.03.07-1ubuntu1 amd64 [installed,automatic]\n
lxd-agent-loader/focal,now 0.4 all [installed,automatic]\n
lz4/focal-updates,focal-security,now 1.9.2-2ubuntu0.20.04.1 amd64 [installed,automatic]\n
magma-cpp-redis/focal-1.6.1,now 4.3.1.1-2 amd64 [installed,automatic]\n
magma-libfluid/focal-1.6.1,now 0.1.0.6-1 amd64 [installed,automatic]\n
magma-libtacopie/focal-1.6.1,now 3.2.0.1-1 amd64 [installed,automatic]\n
magma-sctpd/focal-1.6.1,now 1.6.1-1636529012-5d886707 amd64 [installed,automatic]\n
magma/focal-1.6.1,now 1.6.1-1636529012-5d886707 amd64 [installed]\n
make/focal,now 4.2.1-1.2 amd64 [installed,automatic]\n
man-db/focal,now 2.9.1-1 amd64 [installed,automatic]\n
"""
    ETC_CA_CERTIFICATES_CONF_WITH_DST_ROOT_CA_X3_FORBIDDEN = """mozilla/Cybertrust_Global_Root.crt
mozilla/D-TRUST_Root_Class_3_CA_2_2009.crt
mozilla/D-TRUST_Root_Class_3_CA_2_EV_2009.crt
!mozilla/DST_Root_CA_X3.crt
!mozilla/Deutsche_Telekom_Root_CA_2.crt
mozilla/DigiCert_Assured_ID_Root_CA.crt
mozilla/DigiCert_Assured_ID_Root_G2.crt
"""
    ETC_CA_CERTIFICATES_CONF_WITH_DST_ROOT_CA_X3_ALLOWED = """mozilla/Cybertrust_Global_Root.crt
mozilla/D-TRUST_Root_Class_3_CA_2_2009.crt
mozilla/D-TRUST_Root_Class_3_CA_2_EV_2009.crt
mozilla/DST_Root_CA_X3.crt
!mozilla/Deutsche_Telekom_Root_CA_2.crt
mozilla/DigiCert_Assured_ID_Root_CA.crt
mozilla/DigiCert_Assured_ID_Root_G2.crt
"""

    def setUp(self) -> None:
        self.agw_installer = AGWInstaller()

    @patch(
        "magma_access_gateway_installer.agw_installer.check_output",
        return_value=APT_LIST_WITH_MAGMA,
    )
    def test_given_magma_agw_installed_when_agw_installer_then_installer_exits_without_executing_any_commands(  # noqa: E501
        self, _
    ):
        self.assertEqual(self.agw_installer.install(), None)

    @patch("magma_access_gateway_installer.agw_installer.check_call")
    def test_given_magma_agw_not_installed_when_update_apt_cache_then_apt_update_is_called(
        self, mock_check_call
    ):
        self.agw_installer.update_apt_cache()

        mock_check_call.assert_called_once_with(["apt", "-qq", "update"])

    @patch("magma_access_gateway_installer.agw_installer.check_call")
    def test_given_magma_agw_not_installed_when_update_ca_certificates_package_then_relevant_apt_command_is_called(  # noqa: E501
        self, mock_check_call
    ):
        self.agw_installer.update_ca_certificates_package()

        mock_check_call.assert_called_once_with(["apt", "-qq", "install", "ca-certificates"])

    @patch(
        "magma_access_gateway_installer.agw_installer.open",
        new_callable=mock_open,
        read_data=ETC_CA_CERTIFICATES_CONF_WITH_DST_ROOT_CA_X3_FORBIDDEN,
    )
    @patch("magma_access_gateway_installer.agw_installer.check_call")
    def test_given_dst_root_ca_x3_certificate_forbidden_when_forbid_usage_of_expired_dst_root_ca_x3_certificate_then_no_changes_are_done_to_etc_ca_certificates_conf(  # noqa: E501
        self, mock_check_call, mock_open_file
    ):
        self.agw_installer.forbid_usage_of_expired_dst_root_ca_x3_certificate()

        mock_open_file.assert_called_once_with("/etc/ca-certificates.conf", "r")
        mock_check_call.assert_not_called()

    @patch(
        "magma_access_gateway_installer.agw_installer.open",
        new_callable=mock_open,
        read_data=ETC_CA_CERTIFICATES_CONF_WITH_DST_ROOT_CA_X3_ALLOWED,
    )
    @patch("magma_access_gateway_installer.agw_installer.check_call", Mock())
    def test_given_dst_root_ca_x3_certificate_allowed_when_forbid_usage_of_expired_dst_root_ca_x3_certificate_then_certificate_is_marked_as_forbidden_in_etc_ca_certificates_conf(  # noqa: E501
        self, mock_open_file
    ):
        expected_etc_ca_certificates_conf = [
            "mozilla/Cybertrust_Global_Root.crt\n",
            "mozilla/D-TRUST_Root_Class_3_CA_2_2009.crt\n",
            "mozilla/D-TRUST_Root_Class_3_CA_2_EV_2009.crt\n",
            "!mozilla/DST_Root_CA_X3.crt\n",
            "!mozilla/Deutsche_Telekom_Root_CA_2.crt\n",
            "mozilla/DigiCert_Assured_ID_Root_CA.crt\n",
            "mozilla/DigiCert_Assured_ID_Root_G2.crt\n",
        ]

        self.agw_installer.forbid_usage_of_expired_dst_root_ca_x3_certificate()

        mock_open_file().writelines.assert_called_once_with(expected_etc_ca_certificates_conf)

    @patch("magma_access_gateway_installer.agw_installer.check_call")
    @patch(
        "magma_access_gateway_installer.agw_installer.open",
        new_callable=mock_open,
        read_data=ETC_CA_CERTIFICATES_CONF_WITH_DST_ROOT_CA_X3_ALLOWED,
    )
    def test_given_dst_root_ca_x3_certificate_allowed_when_forbid_usage_of_expired_dst_root_ca_x3_certificate_then_ca_certificates_are_updated(  # noqa: E501
        self, _, mock_check_call
    ):
        self.agw_installer.forbid_usage_of_expired_dst_root_ca_x3_certificate()

        mock_check_call.assert_called_once_with(["update-ca-certificates"])

    @patch("magma_access_gateway_installer.agw_installer.check_call")
    def test_given_magma_agw_not_installed_when_install_runtime_dependencies_then_apt_installs_required_packages(  # noqa: E501
        self, mock_check_call
    ):

        self.agw_installer.install_runtime_dependencies()

        mock_check_call.assert_called_with(
            "apt -qq install -y --no-install-recommends graphviz python-all module-assistant openssl dkms uuid-runtime ca-certificates",  # noqa: E501
            shell=True,
        )

    @patch("magma_access_gateway_installer.agw_installer.check_call")
    def test_given_magma_agw_not_installed_when_preconfigure_wireshark_suid_property_then_correct_configuration_is_sent_to_debconf_database(  # noqa: E501
        self, mock_check_call
    ):
        self.agw_installer.preconfigure_wireshark_suid_property()

        mock_check_call.assert_called_once_with(
            'echo "wireshark-common wireshark-common/install-setuid boolean true" | debconf-set-selections',  # noqa: E501
            shell=True,
        )

    @patch("magma_access_gateway_installer.agw_installer.check_call")
    def test_given_magma_agw_not_installed_when_install_magma_agw_then_correct_apt_command_is_called(  # noqa: E501
        self, mock_check_call
    ):
        self.agw_installer.install_magma_agw()

        mock_check_call.assert_called_with(
            "apt -qq install -y --no-install-recommends /snap/magma-access-gateway/current/libopenvswitch_2.15.4-10-magma_amd64.deb /snap/magma-access-gateway/current/openvswitch-common_2.15.4-10-magma_amd64.deb /snap/magma-access-gateway/current/openvswitch-datapath-dkms_2.15.4-10-magma_all.deb /snap/magma-access-gateway/current/openvswitch-switch_2.15.4-10-magma_amd64.deb /snap/magma-access-gateway/current/magma-libtacopie_3.2.0.1-1_amd64.deb /snap/magma-access-gateway/current/magma-cpp-redis_4.3.1.2-2_amd64.deb /snap/magma-access-gateway/current/prometheus-cpp-dev_1.0.2-1_amd64.deb /snap/magma-access-gateway/current/bcc-tools_0.23-1_amd64.deb /snap/magma-access-gateway/current/oai-nettle_2.5-1_amd64.deb /snap/magma-access-gateway/current/oai-gnutls_3.1.23-1_amd64.deb /snap/magma-access-gateway/current/oai-freediameter_0.0.2-1_amd64.deb /snap/magma-access-gateway/current/liblfds710_7.1.0-1_amd64.deb /snap/magma-access-gateway/current/oai-asn1c_0~20190423+c0~rf12568d6-0_amd64.deb /snap/magma-access-gateway/current/magma-dhcp-cli_1.9.0-VERSION-SUFFIX_amd64.deb /snap/magma-access-gateway/current/sentry-native_0.4.12-1_amd64.deb /snap/magma-access-gateway/current/grpc-dev_-3_amd64.deb /snap/magma-access-gateway/current/magma-libfluid_0.1.0.7-7_amd64.deb /snap/magma-access-gateway/current/libfolly-dev_-7_amd64.deb /snap/magma-access-gateway/current/td-agent-bit_1.7.8_amd64.deb /snap/magma-access-gateway/current/getenvoy-envoy_1.16.2.p0.ge98e41a-1p71.gbe6132a_amd64.deb /snap/magma-access-gateway/current/sctpd_deb_pkg.deb /snap/magma-access-gateway/current/magma_deb_pkg.deb",  # noqa: E501
            shell=True,
        )

    @patch("magma_access_gateway_installer.agw_installer.check_call")
    def test_given_magma_installation_process_when_start_open_vswitch_then_correct_service_is_started(  # noqa: E501
        self, mock_check_call
    ):
        self.agw_installer.start_open_vswitch()

        mock_check_call.assert_called_once_with(["service", "openvswitch-switch", "start"])

    @patch("magma_access_gateway_installer.agw_installer.check_call")
    def test_given_magma_installation_process_when_start_magma_then_magma_services_are_stopped_interfaces_are_brought_up_and_magma_services_are_started(  # noqa: E501
        self, mock_check_call
    ):
        expected_calls = [call(["service", "magma@*", "stop"])]
        expected_calls.extend(
            [
                call(["ifup", magma_interface])
                for magma_interface in self.agw_installer.MAGMA_INTERFACES
            ]
        )
        expected_calls.append(call(["service", "magma@magma", "start"]))

        self.agw_installer.start_magma()

        mock_check_call.assert_has_calls(expected_calls)

    @patch("magma_access_gateway_installer.agw_installer.os.system")
    @patch("magma_access_gateway_installer.agw_installer.check_call", Mock())
    @patch("magma_access_gateway_installer.agw_installer.check_output", MagicMock())
    @patch("magma_access_gateway_installer.agw_installer.open", mock_open())
    @patch("magma_access_gateway_installer.agw_installer.time.sleep", Mock())
    def test_given_magma_not_installed_when_install_then_system_goes_for_reboot_once_installation_is_done(  # noqa: E501
        self, mock_os_system
    ):
        self.agw_installer.install()

        mock_os_system.assert_called_once_with("reboot")

    @patch("magma_access_gateway_installer.agw_installer.os.system")
    @patch("magma_access_gateway_installer.agw_installer.check_call", Mock())
    @patch("magma_access_gateway_installer.agw_installer.check_output", MagicMock())
    @patch("magma_access_gateway_installer.agw_installer.open", mock_open())
    @patch("magma_access_gateway_installer.agw_installer.time.sleep", Mock())
    def test_given_magma_not_installed_and_no_reboot_specified_when_install_then_system_does_not_reboot_once_installation_is_done(  # noqa: E501
        self, mock_os_system
    ):
        self.agw_installer.install(no_reboot=True)

        mock_os_system.assert_not_called()
