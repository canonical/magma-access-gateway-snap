# How-to: Deploy Magma Access Gateway using snap

The goal of this document is to guide the Operator through the process of deploying 
Magma Access Gateway to a [compliant](#System requirements) piece of hardware using 
[magma-access-gateway](https://snapcraft.io/magma-access-gateway) snap.<br>
Unless specified otherwise, all actions in this guide are executed using `root` account.<br>
Installation progress can be monitored at all times using `journalctl`.

### System requirements

- 64bit-X86 machine
- Baremetal strongly recommended
  - AMD64 dual-core processor around 2GHz clock speed or faster
  - 4GB RAM
  - 32GB or greater SSD storage
- At least two ethernet interfaces (SGi and S1)
- Internet connectivity from SGi interface
- Ubuntu 20.04 LTS installed
  ([Ubuntu installation guide](https://help.ubuntu.com/lts/installation-guide/amd64/index.html))

## 1. Install magma-access-gateway snap

From your Magma AGW host machine execute:

```bash
snap install magma-access-gateway --classic
```

## 2. Install magma-access-gateway

From your Magma AGW host machine execute:

```bash
magma-access-gateway.install
```

[magma-access-gateway](https://snapcraft.io/magma-access-gateway) installer supports various 
configuration options which can be used in the form of flags added to the main installation 
command. To see the list of currently supported configuration options, execute:

```bash
magma-access-gateway.install --help
```

## 3. Configure magma-access-gateway

- Get `rootCA.pem` certificate used during the Orc8r deployment.
- Upload `rootCA.pem` to AGW host
- From AGW host execute:

```bash
magma-access-gateway.configure --domain <Orc8r domain> --root-ca-pem-path <path to Root CA PEM>
```

## 4. Verify magma-access-gateway deployment

Once Access Gateway has been successfully attached to the network, deployment can be verified 
by running below command from the AGW host:

```bash
magma-access-gateway.post-install
```

