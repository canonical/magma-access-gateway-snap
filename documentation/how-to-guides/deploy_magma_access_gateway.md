# How-to: Deploy Magma Access Gateway using snap

The goal of this document is to guide the operator through the process of deploying 
Magma Access Gateway using [snap](https://snapcraft.io/magma-access-gateway).

> **WARNING:** **magma-access-gateway** snap will affect your computer's networking configuration.
> Make sure it is installed on designated hardware (personal computers are strongly discouraged).

### System requirements

**Hardware (baremetal strongly recommended)**

- Processor: x86-64 dual-core processor (around 2GHz clock speed or faster)
- Memory: 4GB RAM
- Storage: 32GB or greater SSD

**Networking**

- At least two ethernet interfaces (SGi and S1)
- Internet connectivity from SGi interface

**Operating System**

- Ubuntu 20.04 LTS
  ([Ubuntu installation guide](https://help.ubuntu.com/lts/installation-guide/amd64/index.html))

## 1. Install

> **NOTES:**<br>
> 1. To see the list of currently supported configuration options, execute:
> ```bash
> magma-access-gateway.install --help
> ```
> 2. Unless specified otherwise, all actions in this guide are executed using `root` account.<br>
> 3. Installation progress can be monitored at all times using `journalctl`.

Connect to the machine where you want to install Magma Access Gateway and execute the following command:

```bash
snap install magma-access-gateway --classic
magma-access-gateway.install
```

> **NOTE**: To see the list of currently supported configuration options, execute:
> ```bash
> magma-access-gateway.install --help
> ```

## 2. Configure

Fetch `rootCA.pem` certificate from Orchestrator, upload it to AGW host and execute:

```bash
magma-access-gateway.configure --domain <Orc8r domain> --root-ca-pem-path <path to Root CA PEM>
```

## 3. Verify the deployment

Run the following command:

```bash
magma-access-gateway.post-install
```
