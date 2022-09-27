#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

import unittest
from unittest.mock import MagicMock, Mock, PropertyMock, call, mock_open, patch

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
    @patch("magma_access_gateway_installer.agw_installer.open")
    @patch("magma_access_gateway_installer.agw_installer.os.path.exists", return_value=True)
    def test_given_magma_apt_repo_configured_when_configure_apt_for_magma_agw_deb_package_installation_then_new_apt_repo_is_not_created(  # noqa: E501
        self, _, mock_open_file, mock_check_call
    ):
        self.agw_installer.configure_apt_for_magma_agw_deb_package_installation()

        mock_open_file.assert_not_called()
        mock_check_call.assert_not_called()

    @patch("magma_access_gateway_installer.agw_installer.open", new_callable=mock_open)
    @patch(
        "magma_access_gateway_installer.agw_installer.AGWInstaller.MAGMA_VERSION",
        new_callable=PropertyMock,
    )
    @patch("magma_access_gateway_installer.agw_installer.check_call", Mock())
    @patch("magma_access_gateway_installer.agw_installer.os.path.exists", return_value=False)
    def test_given_magma_apt_repo_not_configured_when_configure_apt_for_magma_agw_deb_package_installation_then_new_apt_repo_config_file_is_created(  # noqa: E501
        self, _, mock_magma_version, mock_open_file
    ):
        mock_magma_version.return_value = self.TEST_MAGMA_VERSION
        expected_apt_repo_config_file_content = (
            "deb https://artifactory.magmacore.org/artifactory/debian "
            f"{self.TEST_MAGMA_VERSION} main"
        )

        self.agw_installer.configure_apt_for_magma_agw_deb_package_installation()

        self.assertTrue(
            call("/etc/apt/sources.list.d/magma.list", "w") in mock_open_file.mock_calls
        )
        self.assertTrue(
            call(expected_apt_repo_config_file_content) in mock_open_file().write.mock_calls
        )

    @patch("magma_access_gateway_installer.agw_installer.open", new_callable=mock_open)
    @patch("magma_access_gateway_installer.agw_installer.check_call")
    @patch("magma_access_gateway_installer.agw_installer.os.path.exists", return_value=False)
    def test_given_magma_apt_repo_not_configured_when_configure_apt_for_magma_agw_deb_package_installation_then_unvalidated_apt_signing_key_is_added(  # noqa: E501
        self, _, mock_check_call, mock_open_file
    ):
        expected_99insecurehttpsrepo_content = """Acquire::https::artifactory.magmacore.org/artifactory/debian {
Verify-Peer "false";
Verify-Host "false";
};
"""  # noqa: E501

        self.agw_installer.configure_apt_for_magma_agw_deb_package_installation()

        self.assertTrue(
            call(
                [
                    "apt-key",
                    "adv",
                    "--fetch-keys",
                    "https://artifactory.magmacore.org/artifactory/api/gpg/key/public",
                ]
            )
            in mock_check_call.mock_calls
        )
        self.assertTrue(
            call("/etc/apt/apt.conf.d/99insecurehttpsrepo", "w") in mock_open_file.mock_calls
        )
        self.assertTrue(
            call(expected_99insecurehttpsrepo_content) in mock_open_file().write.mock_calls
        )

    @patch("magma_access_gateway_installer.agw_installer.check_call")
    @patch("magma_access_gateway_installer.agw_installer.open", new_callable=mock_open)
    @patch("magma_access_gateway_installer.agw_installer.os.path.exists", return_value=False)
    def test_given_magma_apt_repo_not_configured_when_configure_apt_for_magma_agw_deb_package_installation_then_apt_cache_is_updated(  # noqa: E501
        self, _, __, mock_check_call
    ):
        self.agw_installer.configure_apt_for_magma_agw_deb_package_installation()

        self.assertTrue(call(["apt", "-qq", "update"]) in mock_check_call.mock_calls)

    @patch("magma_access_gateway_installer.agw_installer.check_call")
    def test_given_magma_agw_not_installed_when_install_runtime_dependencies_then_apt_installs_required_packages(  # noqa: E501
        self, mock_check_call
    ):
        expected_apt_calls = [
            call(f"apt -qq install -y --no-install-recommends {package_name}", shell=True)
            for package_name in self.agw_installer.MAGMA_AGW_RUNTIME_DEPENDENCIES
        ]

        self.agw_installer.install_runtime_dependencies()

        mock_check_call.assert_has_calls(expected_apt_calls)

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

        mock_check_call.assert_called_once_with(
            'apt -o "Dpkg::Options::=--force-confdef" -o "Dpkg::Options::=--force-confold" '
            '-o "Dpkg::Options::=--force-overwrite" -qq install -y --no-install-recommends magma',
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
