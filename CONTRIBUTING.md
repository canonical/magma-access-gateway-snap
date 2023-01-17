# Contributing / Hacking

## Required software:

- [Snapcraft](https://snapcraft.io/docs/snapcraft-overview)
- [Multipass](https://multipass.run/)
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

## Building the snap with snapcraft

1. Install required software listed above
2. Clone the repository
3. From the repository's root directory execute:

   ```bash
   export SNAPCRAFT_BUILD_ENVIRONMENT_MEMORY=8G
   export SNAPCRAFT_BUILD_ENVIRONMENT_CPU=4
   snapcraft
   ```

   To see what's happening during the snap building process, `-d` can be used along with above
   command.

## Installing the locally built snap

1. Copy the snap to a host
2. Connect to the host and execute:

   ```bash
   sudo snap install <PATH_TO_THE_SNAP_FILE> --dangerous --classic
   ```

## Testing

Testing the python component of the snap is done using `tox`. To run tests, navigate to the
`python` directory and execute one of the following commands:

```shell
cd python
tox -e lint      # code style
tox -e static    # static analysis
tox -e unit      # unit tests
```

To run all test envs at once, just run:

```bash
tox
```

tox creates virtual environment for every tox environment defined in
[tox.ini](tox.ini). Create and activate a virtualenv with the development requirements, i.e.:

```bash
source .tox/unit/bin/activate
```
