#!/bin/bash
set -eu
poetry check
prev_version="$(poetry version -s --no-ansi)"
poetry version "$1"
new_version="$(poetry version -s --no-ansi)"

repo_url="https://github.com/Meliox/pyrosimple"
# Releases from before this fork was tagged only exist upstream
if git rev-parse -q --verify "refs/tags/v${prev_version}" > /dev/null; then
    version_link="${repo_url}/compare/v${prev_version}...v${new_version}"
else
    version_link="${repo_url}/releases/tag/v${new_version}"
fi

sed -i -e "/## \[Unreleased\]/a \\\n## [${new_version}] - $(date +%Y-%m-%d)" \
    -e "s|\[Unreleased\]: .*|[Unreleased]: ${repo_url}/compare/v${new_version}...HEAD|" \
    -e "/^\[Unreleased\]/a [${new_version}]: ${version_link}" \
    CHANGELOG.md
awk "/## \\[${new_version}\\]/,/## \\[${prev_version}\\]/" CHANGELOG.md | sed -e 1,2d | head -n -2 > RELEASE_NOTE.md
poetry build
