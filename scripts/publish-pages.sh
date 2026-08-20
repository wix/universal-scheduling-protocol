#!/usr/bin/env bash
# Build the MkDocs site and force-push it to the gh-pages branch.
#
# Fallback only. The normal path is .github/workflows/pages.yml on push to
# master (repo wix/universal-scheduling-protocol) with Pages Source set to
# GitHub Actions. Do not run this after that path is live: it fights the
# Actions deploy (gh-pages is not what Actions-sourced Pages serves).
# mkdocs gh-deploy writes .nojekyll so a branch-sourced Pages setup can still
# serve the tree without a Jekyll build. --dirty preserves the authority
# artifacts copied into site/ by build-site.sh.
set -euo pipefail

cd "$(dirname "$0")/.."

./scripts/build-site.sh
python3 -m mkdocs gh-deploy --dirty --remote-branch gh-pages --force

echo "Published. Site: https://usp-protocol.dev (fallback: https://wix.github.io/universal-scheduling-protocol/)"
