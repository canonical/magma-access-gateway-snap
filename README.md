# magma-access-gateway-snap

## Description

Magma is an open-source software platform that gives network operators a mobile core network
solution. Magma has three major components:

1. **Access Gateway**
2. Orchestrator
3. Federation Gateway

The Access Gateway (AGW) provides network services and policy enforcement. In an LTE network,
the AGW implements an evolved packet core (EPC), and a combination of an AAA and a PGW. It works
with existing, unmodified commercial radio hardware.<br>
For more information on Magma please visit the [official website](https://magmacore.org/)

With this [Snap](https://snapcraft.io/) user can easily [deploy](#Usage) Magma Access Gateway.

## System requirements

**Hardware (baremetal strongly recommended)**

- Processor: x86-64 dual-core processor (around 2GHz clock speed or faster)
- Memory: 4GB RAM
- Storage: 32GB or greater SSD

**Networking**

- At least two ethernet interfaces (SGi and S1)
- Internet connectivity from SGi interface

> **WARNING:** **magma-access-gateway** snap will affect your computer's networking configuration.
> Make sure it is installed on designated hardware (personal computers are strongly discouraged).

**Operating System**

- Ubuntu 20.04 LTS
  ([Ubuntu installation guide](https://help.ubuntu.com/lts/installation-guide/amd64/index.html))

## Usage

This Snap is available in the official [Snap store](https://snapcraft.io/store), as 
[magma-access-gateway](https://snapcraft.io/magma-access-gateway). <br>
This Snap is currently delivered as a [classic](https://snapcraft.io/docs/snap-confinement) Snap.

**Installing Magma AGW snap:**

> **NOTE:** Installation progress can be monitored at all times using `journalctl`.

To install [magma-access-gateway](https://snapcraft.io/magma-access-gateway) execute:

```bash
snap install magma-access-gateway --classic
```

Once Snap is installed (it will be indicated by the `magma-access-gateway 1.6.0 installed`
message printed to the console), start AGW deployment by executing:

```bash
magma-access-gateway.install
```

[magma-access-gateway](https://snapcraft.io/magma-access-gateway) installer exposes various
deployment configuration parameters. To see the list of currently supported parameters along with
their descriptions, execute:

```bash
magma-access-gateway.install --help
```

**Configuring Magma Access Gateway:**

Magma Access Gateway can be configured by executing:

```bash
magma-access-gateway.configure --domain <your domain> --root-ca-pem-path <path to Root CA PEM>
```

For more details about Magma Access Gateway configuration, visit 
[Magma documentation](https://docs.magmacore.org/docs/next/lte/deploy_config_agw).

**Magma Access Gateway post-installation checks**

Once Magma Access Gateway is installed and configured, post-installation checks can be run to 
make sure everything has been configured correctly.<br>
Post-installation checks can be executed by issuing:

```bash
magma-access-gateway.post-install
```

## Contributing

Please see `CONTRIBUTING.md` for developer guidance.
