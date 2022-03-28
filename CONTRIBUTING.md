# Contributing / Hacking

## Intended use case

The Snap in this repository is specifically developed for the
[Magma](https://www.magmacore.org/) use case.

## Developing and testing

**Required software:**

- [Snapcraft](https://snapcraft.io/docs/snapcraft-overview)
- [Multipass](https://multipass.run/)
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

**Building Magma AGW snap:**

1. Install required software listed above
2. From the repository's main directory execute:

   ```bash
   snapcraft
   ```
   
   To see what's happening during Snap's building process, `-d` can be used along with above
   command.

**Installing locally built Magma AGW snap:**

1. Copy snap to AGW host machine.
2. On AGW host machine, as `root` execute:

   ```bash
   snap install <PATH_TO_THE_SNAP_FILE> --dangerous --classic
   ```
   Since Snap has been built locally, `--dangerous` flag is required to deploy it. <br>

To learn more about [magma-access-gateway](https://snapcraft.io/magma-access-gateway) deployment, 
please see `README.md`.

**Unit tests and static code analysis**

Testing of the Snap is done using `tox`. To run tests, from this repository's main directory
execute one of the following commands:

```shell
tox -e lint      # code style
tox -e static    # static analysis
tox -e unit      # unit tests
```

To run all test envs at once, just run:<br>

```bash
tox
```

tox creates virtual environment for every tox environment defined in
[tox.ini](tox.ini). Create and activate a virtualenv with the development requirements, i.e.:

```bash
source .tox/unit/bin/activate
```

**Integration tests**

TBD
