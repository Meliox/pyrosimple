# pyrosimple
An overhauled Python 3 fork of [pyrocore](https://github.com/pyroscope/pyrocore), for working with the
[rTorrent client](https://github.com/rakshasa/rtorrent).

> **Note:** This repository is a fork of
> [kannibalox/pyrosimple](https://github.com/kannibalox/pyrosimple).
> It is not published to PyPI, so `pip install pyrosimple` installs
> the original project, not this fork. Likewise, the Docker image
> `kannibalox/pyrosimple` on Docker Hub is built from the original project;
> to use Docker with this fork, build the image yourself from the included
> `Dockerfile` (`docker build -t pyrosimple .`).
>
> Supported rTorrent version: 0.16.27. The original project does not
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

## Differences from pyrocore

The following lists are not exhaustive, and don't cover many of the
internal improvements and refactoring.

- Requires Python 3.12 or newer and supports rTorrent 0.16.27
- Simpler poetry-based build system, with a single package to install
- Performance improvements (faster templating and only fetching
  required fields)
- Replaced Tempita with [Jinja2](https://jinja.palletsprojects.com/)

### New features

- Multi-instance support for rtcontrol/rtxmlrpc
- Support for JSON-RPC (see the
  [experimental features](https://kannibalox.github.io/pyrosimple/experimental/))
- Actions to move torrents between paths, or torrents between hosts

See https://kannibalox.github.io/pyrosimple/migrate/ for how to
migrate scripts to the new features.

## Releases

Releases are published on the
[GitHub releases page](https://github.com/Meliox/pyrosimple/releases),
with notes taken from the [changelog](CHANGELOG.md).

To prepare a release, run the **Release** workflow on `main` with a version
number or `major`, `minor`, or `patch`. It opens a version-bump pull request;
after the pull request is merged into `main`, the workflow builds the merged
commit and publishes its packages and release notes on GitHub.

The workflow requires a repository secret named `RELEASE_PR_TOKEN` containing
a personal access token with repository contents and pull requests write
access. This token allows the release pull request to trigger the normal
checks. If a release tag already exists, resolve
it manually before retrying; the failed first release run left an orphaned
`v3.0.0` tag that must be removed before releasing that version.
