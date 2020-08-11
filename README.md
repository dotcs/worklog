# Worklog - Simple CLI util to track work hours

Worklog is a simple and straight-forward tool to track working times via CLI.
It uses a plain text file as it's storage backend which makes it easy to
process the logged information with other tools.

## Getting started

You need to have Python >= 3.6 installed.

```bash
pip install dcs-worklog
```

### Command Line Interface (CLI)

The tool registers itself as a CLI tool with the name `wl` (short for
`worklog`).

It provides the basic commands to start and stop tracking work times.

```bash
wl commit start    # starts a new work session
wl commit stop     # stops a running session
```

It's also possible to give a time offset to the current time:

```bash
wl commit start --offset-minutes 5
wl commit stop --offset-minutes -5
```

Learn about all options by using the `--help` flag for any command:

```bash
wl commit --help   # show more options
```

To see how the current status of the worklog use the `status` command:

```
$ wl status

Status         : Tracking on
Total time     : 07:49:40 ( 98%)
Remaining time : 00:10:20 (  2%)
Overtime       : 00:00:00 (  0%)
End of work    : 17:18:27
```

To see historical entries use the `log` command:

```bash
wl log             # shows the last 10 records (latest first)
wl log --all       # shows all records  (latest first)
```

### Configuration

By default the log file is written to `~/.worklog`.
The format is CSV with pipe symbols (`|`) as delimiters.

A working day is configured to have 8 hours.
2 hours are set as a (soft) limit for overtime.

This configuration can be changed by creating a config file in
`~/.config/worklog/config`.
Partial changes are allowed and are merged with the [default
configuration](./worklog/config.cfg).

An example customized configuration could be the following file:
```ini
[workday]
hours_target = 8.5
hours_max = 12
```

### Integration in task bars

tbd

```bash
wl status --fmt '{status} | {remaining_time} (percentage}%'
```

### Sanity check

The current log file can be sanity-checked with the `doctor` command.
In case entries are missing the doctor command will tell so:

```
$ wl doctor
ERROR:worklog:Date 2020-04-08 has no stop entry.
```

## Development

Clone this repository and install the development version:

```bash
pip install -e ".[testing]"
```

Run tests via

```bash
pytest worklog/
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

## Troubleshooting

If you are behind a proxy the installation might not work.
In this case try to setup the proxy via the `--proxy` flag:

```bash
pip install --proxy=http://localhost:3128 dcs-worklog
```
