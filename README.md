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
For more information on Magma please visit the [official website](https://magmacore.org/).

> **WARNING:** Installing this snap will affect your computer's networking configuration.
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


## Usage

All actions in this guide are executed using `root` account.

### 1. Install

Connect to the machine where you want to install Magma Access Gateway and execute the following 
commands:

```bash
snap install magma-access-gateway --classic
magma-access-gateway.install
```

> **NOTE:** To see the list of currently supported installation options, execute:
> ```bash
> magma-access-gateway.install --help
> ```

> **NOTE:** By default, the installation assumes DHCP for IP allocation. If statically allocated IPs have been explicitly specified in the configuration options, the system will  
> restart to apply new network configuration. Once the server is restarted, reconnect to the system 
> and use `journalctl` to continue monitoring the installation process.

Successful installation will be indicated by the `Magma AGW deployment
completed successfully!` message.

After successful Access Gateway installation, installer will perform automatic system restart. Once 
the server is restarted, reconnect to the system to perform AGW configuration.

### 2. Configure

Fetch `rootCA.pem` certificate from Orchestrator, upload it to the Access Gateway host and execute:

```bash
magma-access-gateway.configure --domain <Orc8r domain> --root-ca-pem-path <path to Root CA PEM>
```

Successful Magma AGW configuration will be indicated by the `Magma AGW configuration done!` 
message.

### 3. Verify the deployment

Run the following command:

```bash
magma-access-gateway.post-install
```

Successful Magma AGW deployment check will be indicated by the `Magma AGW post-installation checks 
finished successfully.` message.

## Contributing

Please see [CONTRIBUTING.md](/CONTRIBUTING.md) for developer guidance.
