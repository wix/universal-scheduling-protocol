# Website deployment

The protocol website is hosted on GitHub Pages for
[`wix/universal-scheduling-protocol`](https://github.com/wix/universal-scheduling-protocol)
and served at <https://usp-protocol.dev>. The project URL
<https://wix.github.io/universal-scheduling-protocol/> still works as a
fallback. `www.usp-protocol.dev` 301s to the apex.

## Current setup

| Setting | Value |
|---------|-------|
| Pages source | GitHub Actions (required). Do not use Deploy from branch `gh-pages`. |
| Auto-publish | [`.github/workflows/pages.yml`](../.github/workflows/pages.yml) on push to `master` when the repository is `wix/universal-scheduling-protocol` |
| Action pins | Every `uses:` in the workflow file is a full-length commit SHA of a GitHub-owned action (org policy). Composite parents are not enough: nested `uses:` are checked too. |
| Site source | `site-docs/`, canonical artifacts under `schemas/`, `openapi/`, and `openrpc/`, and `mkdocs.yml` on `master` |
| Fallback branch | Pre-built MkDocs output plus `.nojekyll` on `gh-pages` if Source is still Deploy from a branch |

GitHub Actions is enabled for this repository. The `pages` workflow runs
`npm run build`, which builds MkDocs and copies every authority artifact to its
canonical public path. It then packs `site/` as a tar and uploads the tar with
`actions/upload-artifact` (artifact name `github-pages`), and deploys with
`actions/deploy-pages`.

Do not use `actions/upload-pages-artifact`. That action is a composite whose
`action.yml` still contains `uses: actions/upload-artifact@v4` (a moving tag).
Wix org policy requires every action, including nested composite steps, to be
GitHub-created and pinned to a full-length commit SHA. The nested `@v4` ref
fails at **Set up job**, even when the parent composite is SHA-pinned in
`pages.yml`. Calling `actions/upload-artifact` from the workflow file with a
40-character SHA (v4.6.2) keeps the pin in our YAML. `actions/deploy-pages`
v4.0.5 is a Node action (`dist/index.js`), not a composite, so it has no nested
`uses:` to pin.

That only publishes if Pages **Source** in
[Settings → Pages](https://github.com/wix/universal-scheduling-protocol/settings/pages)
is set to **GitHub Actions**. Switching that setting is a GitHub UI step; it is
not done in this repository.

If Source is still **Deploy from a branch** (`gh-pages`), the workflow will
build but Pages will keep serving the old branch until Source is changed. The
`.nojekyll` marker tells Pages to serve that branch as-is instead of running a
Jekyll build.

## Publishing an update

After site content is merged to `master` on `wix/universal-scheduling-protocol`,
the `pages` workflow deploys automatically. Confirm the run under Actions, then
check the live site.

### Manual fallback

Use this only if the workflow cannot run (for example a failed Actions deploy
you cannot wait on):

```bash
npm run publish:pages     # or: ./scripts/publish-pages.sh
```

This runs the artifact-aware site build and then `mkdocs gh-deploy --dirty`,
which preserves the copied JSON while force-pushing the output to `gh-pages`
together with `.nojekyll`. Once Pages Source is GitHub Actions, that branch is
not what Pages serves. Running the script then fights the Actions deploy: the
next successful `pages` workflow overwrites the live site, and a branch push
does not update what Actions-sourced Pages shows. Do not use the script as the
day-to-day publish path after Actions is live. Do not edit `gh-pages` by hand.

## Canonical published layout

| Resource | Public path |
|---|---|
| Specification | `/specification` |
| Domain schemas | Each schema's exact `$id` path under `/schemas/` |
| REST binding | `/schemas/openapi/usp-rest.json` |
| MCP binding | `/schemas/openrpc/usp-mcp.json` |
| Problem documentation | `/errors/{kebab-case-slug}` |
| Namespace registry | `/namespace/` |

`scripts/build-site.sh` derives every schema destination from its `$id`, so a
schema cannot silently publish at a path different from its canonical
identifier. The existing conformance checker validates source identifiers,
published paths, binding references, problem pages, playground mirrors, and
stale-name absence after every CI and Pages build.

GitHub Pages serves `.json` files as `application/json`, which satisfies the
binding and JSON Schema publication requirement. It cannot configure arbitrary
HTTP 301 responses. The former binding paths under `/services/` are therefore
direct static JSON copies, while `/spec`, `/problems/*`, underscore problem
slugs, and `/errors/validation` are static HTML compatibility pages that point
directly to their canonical targets. Normative examples never advertise those
aliases.

## Custom domain

Canonical host is `usp-protocol.dev` (AC-S3e option B: this origin is the full
MkDocs site plus published artifacts). `usp.live` should later redirect here.

When a custom domain is attached in Pages settings, GitHub writes a `CNAME`
file into the published site. Keep a matching [`site-docs/CNAME`](../site-docs/CNAME)
so every MkDocs build (Actions or `gh-deploy`) includes it. Otherwise a later
deploy can drop the domain binding.

Apex DNS uses GitHub Pages A records (`185.199.108.153` through
`185.199.111.153`). `www` CNAMEs to `wix.github.io`. DNS check succeeded and
**Enforce HTTPS** is on. GitHub's Pages banner may still show `http://` even
when HTTPS is enforced; use curl against `https://usp-protocol.dev` as the
source of truth.

## Cutover verification

Before announcing the hard cutover, build locally and verify all repository
invariants:

```bash
python3 tools/usp_check.py schemas
python3 tools/usp_check.py refs
python3 tools/usp_check.py vectors
npm run build
python3 tools/usp_check.py authority
```

After the branch is merged and Pages deploys, perform safe GET requests for
`/specification`, every schema `$id`, both canonical bindings, and every
canonical problem type collected by the authority check. They must return 200
over HTTPS. Only then coordinate the same-release downstream rename with the
CLI, business adapter, discovery registry, and checkout owners.

Two operations remain external to this repository:

1. The owner of `usp.live` must configure an HTTP 301 redirect directly to
   `https://usp-protocol.dev` without an intermediate host.
2. Downstream owners must land and deploy their `dev.usp-protocol.*` hard
   cutovers, then confirm live profiles no longer advertise the retired names.
