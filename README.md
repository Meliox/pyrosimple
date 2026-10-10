# pyrosimple

[![GitHub Workflow Status](http://img.shields.io/github/actions/workflow/status/kannibalox/pyrosimple/pylint.yml?branch=main)](https://github.com/kannibalox/pyrosimple/actions/workflows/pylint.yml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyrosimple)](https://pypi.org/project/pyrosimple/)
[![PyPI](https://img.shields.io/pypi/v/pyrosimple)](https://pypi.org/project/pyrosimple/)
[![Docker Image Version (tag latest semver)](https://img.shields.io/docker/v/kannibalox/pyrosimple/2?label=docker&link=https%3A%2F%2Fhub.docker.com%2Fr%2Fkannibalox%2Fpyrosimple%2Ftags)](https://hub.docker.com/r/kannibalox/pyrosimple/tags)


A overhauled Python 3 fork of the [pyrocore
tools](https://github.com/pyroscope/pyrocore), for working with the
[rTorrent client](https://github.com/rakshasa/rtorrent).

> **Note:** This repository is a fork of
> [kannibalox/pyrosimple](https://github.com/kannibalox/pyrosimple).
> It is not published to PyPI, so `pip install pyrosimple` installs
> the original project, not this fork. Likewise, the Docker image
> `kannibalox/pyrosimple` on Docker Hub is built from the original project,
> not this fork; to use Docker with this fork, build the image yourself
> from the included `Dockerfile` (`docker build -t pyrosimple .`).
>
> Supported rTorrent version: 0.16.25. The original project does not
> support the updated rTorrent versions, which is the main reason for this
> fork.

## Installation

This fork must be installed manually from source:

```bash
git clone https://github.com/Meliox/pyrosimple.git
cd pyrosimple
poetry install
# poetry install --extras torque # Optional dependencies for using pyrotorque
```

Alternatively, install into the current environment with
`pip install .` from the cloned directory.

See the [documentation for usage](https://kannibalox.github.io/pyrosimple/).
If you've used rtcontrol/rtxmlrpc before, you should feel right at home.

## What's the point of this?

The pyrocore tools are great, but being stuck on python 2, along with
the complicated install procedure made integrating both the tools and
the code into other processes very painful.

## Differences from pyrocore

The following lists are not exhaustive, and don't cover many of the
internal improvements and refactoring.

- Only supports python 3 and rTorrent 0.16.25
  - pypy is supported, but not as well tested
- Simpler poetry-based build system, with a single package to install
- Performance improvements (faster templating and only fetching
  required fields)
- Replaced Tempita with [Jinja2](https://jinja.palletsprojects.com/en/3.0.x/)

### New features

- Multi-instance support for rtcontrol/rtxmlrpc
- Support for JSON-RPC (currently only implemented by
  [jesec/rtorrent](https://github.com/jesec/rtorrent))
- Actions to move torrents between paths, or torrents between hosts

See https://kannibalox.github.io/pyrosimple/migrate/ for how to
migrate scripts to the new features.

## Legacy branch

If you just want to use the pyrocore tools on python 3 without all the
new features, you can use the `release-1.X` branch (1.3 is the latest
release at time of writing).  These releases will only receive bug
fixes or changes to maintain compatibility with the original pyrocore
tools.
