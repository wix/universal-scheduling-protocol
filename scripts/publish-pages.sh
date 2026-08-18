#!/usr/bin/env bash
# Build the MkDocs site and publish it to the gh-pages branch.
#
# GitHub Actions is disabled for this repository by the organisation, so the
# site cannot be built by a workflow. Pages therefore serves pre-built HTML
# from gh-pages (mkdocs gh-deploy writes .nojekyll so no Jekyll build runs).
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m mkdocs gh-deploy --remote-branch gh-pages --force

echo "Published. Site: https://wix.github.io/universal-scheduling-protocol/"
