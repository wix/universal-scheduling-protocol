# Feature: pin-actions-sha

## Goal

Pin every GitHub Actions `uses:` to a full-length 40-character commit SHA (org policy: "Require actions to be pinned to a full-length commit SHA") and update Pages deploy docs and script comments so they describe auto-publish via `.github/workflows/pages.yml` (GitHub Actions source), not org-disabled Actions or manual `gh-pages` as the only path.

## Non-goals

- Do not change GitHub UI (user must switch Pages Source to GitHub Actions themselves).
- Do not bump to action major v5/v7 unless already in use; keep current majors.
- Do not add peaceiris/actions-gh-pages.
- Do not push to remote.
- Do not commit secrets.
- Do not merge to integration (master runs mt-land.sh).
- Do not rewrite historical CHANGE_LOG entries that mention Actions being disabled.

## Must-preserve constraints

- Keep existing `with:` / `id:` / permissions / triggers / `if:` / `runs-on` / concurrency on all workflows.
- Do not switch CI or mirror jobs off self-hosted runners.
- Manual `scripts/publish-pages.sh` / `npm run publish:pages` remains as fallback only.
- Site-docs is not a counterpart of `docs/website-deployment.md` (deployment ops, not specification). Do not invent a site-docs page unless one already exists.

## File actions

| Path | Action | Reason |
|------|--------|--------|
| PLAN.md | modify | Plan-first artifact with Goal, Non-goals, File actions, Work units |
| .github/workflows/pages.yml | modify | Pin checkout, setup-python, upload-pages-artifact, deploy-pages to SHAs; comments for Pages source and SHA policy |
| .github/workflows/ci.yml | modify | Pin checkout@v4 and setup-python@v5 to the same SHAs as pages.yml |
| .github/workflows/mirror-to-public.yml | modify | Pin checkout@v4 to the same SHA |
| docs/website-deployment.md | modify | Stop saying Actions is org-disabled; document auto-publish, SHA pinning, Pages Source, fallback |
| scripts/publish-pages.sh | modify | Comments currently claim Actions is disabled |
| CHANGE_LOG.md | modify | AGENTS.md newest-first entry with motivation |

## Work units

| ID | Description | Files | Verification | Status |
|----|-------------|-------|--------------|--------|
| U1 | Plan and commit this PLAN.md | PLAN.md | test -f PLAN.md | done |
| U2 | SHA-pin pages.yml and workflow comments | .github/workflows/pages.yml | grep -E 'uses:.*@v[0-9]' .github/workflows/pages.yml must be empty; each SHA is 40 hex | done |
| U3 | SHA-pin ci.yml and mirror-to-public.yml | .github/workflows/ci.yml, .github/workflows/mirror-to-public.yml | grep -E 'uses:.*@v[0-9]' .github/workflows/ must be empty (or comments only) | done |
| U4 | Update deploy docs and publish-pages.sh comments | docs/website-deployment.md, scripts/publish-pages.sh | grep must not claim Actions is org-disabled in those files | pending |
| U5 | Append CHANGE_LOG.md and verify pinning | CHANGE_LOG.md | newest CHANGE_LOG heading; grep workflows for tag-style uses | pending |

## Revisions

(none yet)
