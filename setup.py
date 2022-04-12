#!/snap/magma-access-gateway/current/bin/python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.

from distutils.core import setup

LONG_DESCRIPTION = """ The Access Gateway (AGW) provides network services and policy enforcement.
                       In an LTE network, the AGW implements an evolved packet core (EPC),
                       and a combination of an AAA and a PGW. It works with existing, unmodified
                       commercial radio hardware.
                       For detailed description visit
                       https://docs.magmacore.org/docs/next/lte/architecture_overview."""

with open("requirements.txt") as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name="magma-access-gateway-installer",
    version="1.7.0",
    description="Snap installing Magma Access Gateway component.",
    long_description=LONG_DESCRIPTION,
    author="Canonical Ltd.",
    author_email="bartlomiej.gmerek@canonical.com",
    install_requires=REQUIREMENTS,
    include_package_data=True,
    package_data={
        "magma_access_gateway_configurator": [
            "resources/control_proxy.yml.j2",
            "resources/control_proxy.yml.j2",
        ],
        "magma_access_gateway_installer": [
            "resources/netplan_config.yaml.j2",
        ],
    },
    packages=[
        "magma_access_gateway_installer",
        "magma_access_gateway_configurator",
        "magma_access_gateway_post_install",
    ],
    entry_points={
        "console_scripts": [
            "install-agw=magma_access_gateway_installer:main",
            "configure-agw=magma_access_gateway_configurator:main",
            "agw-postinstall=magma_access_gateway_post_install:main",
        ],
    },
)
