# Contributing / Hacking

## Intended use case

The Snap in this repository is specifically developed for the
[Magma](https://www.magmacore.org/) use case.

## Developing and testing

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

## Integration tests

TBD
