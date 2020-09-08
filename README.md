# Worklog - Simple CLI util to track work hours

[![Documentation Status](https://readthedocs.org/projects/dcs-worklog/badge/?version=latest)](https://dcs-worklog.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/dotcs/worklog/branch/develop/graph/badge.svg)](https://codecov.io/gh/dotcs/worklog)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


Worklog is a simple and straight-forward tool to track working times via CLI.
It uses a plain text file as its storage backend which makes it easy to
process the logged information with other tools.

## Getting started

You need to have Python >= 3.6 installed.

```bash
pip install dcs-worklog
```

Please follow the [documentation on
readthedocs](https://dcs-worklog.readthedocs.io) to learn how to use the CLI
tool.

## Development

Clone this repository and install the development version:

```bash
pip install -e ".[develop]"
```

Run tests via

```bash
pytest --cov worklog
```

### Create a release

**Attention**: This should not be needed. Releases are auto-generated from the
*GitHub CI. See the [configuration file](./.github/workflows/package.yaml).

To create a release use [git flow](), update the version number in setup.py first.
Then execute the following commands:

```bash
python setup.py sdist bdist_wheel
twine upload --skip-existing -r pypi dist/*
```
