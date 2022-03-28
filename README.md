# magma-access-gateway-snap

## Description

The Access Gateway (AGW) provides network services and policy enforcement. In an LTE network,
the AGW implements an evolved packet core (EPC), and a combination of an AAA and a PGW. It works
with existing, unmodified commercial radio hardware.<br>
For detailed description visit
[Magma Architecture Overview](https://docs.magmacore.org/docs/next/lte/architecture_overview).

With this [Snap](https://snapcraft.io/) user can easily [deploy](#Usage) Magma Access Gateway to a
[compliant](#System requirements) piece of hardware.<br>
This [Snap](https://snapcraft.io/) is part the
[Charmed Magma](https://github.com/canonical/charmed-magma) initiative.

## System requirements

- 64bit-X86 machine
- Baremetal strongly recommended
- Two ethernet interfaces (SGi and S1)
- Ubuntu 20.04 LTS installed
  ([Ubuntu installation guide](https://help.ubuntu.com/lts/installation-guide/amd64/index.html))

## Usage

This Snap is available in the official [Snap store](https://snapcraft.io/store), as 
[magma-access-gateway](https://snapcraft.io/magma-access-gateway). <br>
This Snap is currently delivered as a [classic](https://snapcraft.io/docs/snap-confinement) Snap.

**Installing Magma AGW snap:**

To install [magma-access-gateway](https://snapcraft.io/magma-access-gateway) execute:<br>
`snap install magma-access-gateway --classic`<br>
Once Snap is installed (it will be indicated by the `magma-access-gateway 1.6.0 installed`
message printed to the console), start AGW deployment by executing:<br>
`magma-access-gateway.install`<br>
[magma-access-gateway](https://snapcraft.io/magma-access-gateway) installer exposes various
deployment configuration parameters. To see the list of currently supported parameters along with
their descriptions, execute:<br>
`magma-access-gateway.install --help`

**Configuring Magma Access Gateway:**

Magma Access Gateway can be configured by executing:<br>
`magma-access-gateway.configure --domain <your domain> --root-ca-pem-path <path to Root CA PEM>`
<br>
For more details about Magma Access Gateway configuration, visit 
[Magma documentation](https://docs.magmacore.org/docs/next/lte/deploy_config_agw).

**Magma Access Gateway post-installation checks**

Once Magma Access Gateway is installed and configured, post-installation checks can be run to 
make sure everything has been configured correctly.<br>
Post-installation checks can be executed by issuing:<br>
`magma-access-gateway.post-install`

## Contributing

Please see `CONTRIBUTING.md` for developer guidance.
