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

This Snap is not yet available in the official [Snap store](https://snapcraft.io/store), which
means it needs to be built locally on user's hardware.<br>
This Snap is currently delivered as a [classic](https://snapcraft.io/docs/snap-confinement) Snap.

**Required software:**

- [Snapcraft](https://snapcraft.io/docs/snapcraft-overview)
- [Multipass](https://multipass.run/)
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

**Building and installing Magma AGW snap:**

1. Install required software listed above
2. Checkout [magma-access-gateway-snap](https://github.com/canonical/magma-access-gateway-snap)
3. Inside checked out repository's main directory execute:<br>
   `snapcraft`<br>
   To see what's happening during Snap's building process, `-d` can be used along with above command.
4. Once `magma-access-gateway_1.6.0_amd64.snap` file is built, move it to AGW host machine.
5. On AGW host machine, as `root` execute<br>
   `snap install ${PATH_TO_THE_SNAP_FILE} --dangerous --classic`<br>
   Since Snap has been built locally, `--dangerous` flag is required to deploy it.
6. Once Snap is installed (it will be indicated by the `magma-access-gateway 1.6.0 installed`
   message printed to the console), start AGW deployment by executing:<br>
   - `magma-access-gateway` - to deploy Magma AGW using DHCP configured SGi interface
   - `magma-access-gateway --ip-address 1.1.1.1/24 --gw-ip-address 1.1.1.1` - to deploy Magma AGW
     using statically configured SGi interface

**Configuring Magma Access Gateway:**

Magma Access Gateway can be configured by executing:<br>
`magma-access-gateway.configure --domain <your domain> --root-ca-pem-path <path to Root CA PEM>`
<br>
For more details about Magma Access Gateway configuration, visit 
[Magma documentation](https://docs.magmacore.org/docs/next/lte/deploy_config_agw).

## Contributing

Please see `CONTRIBUTING.md` for developer guidance.
