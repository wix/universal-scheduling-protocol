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
| Site source | `site-docs/` and `mkdocs.yml` on `master` |
| Fallback branch | Pre-built MkDocs output plus `.nojekyll` on `gh-pages` if Source is still Deploy from a branch |

GitHub Actions is enabled for this repository. The `pages` workflow builds MkDocs
to `site/`, packs that directory as a tar, uploads the tar with
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

This runs `mkdocs gh-deploy`, which force-pushes pre-built HTML to `gh-pages`
together with `.nojekyll`. Once Pages Source is GitHub Actions, that branch is
not what Pages serves. Running the script then fights the Actions deploy: the
next successful `pages` workflow overwrites the live site, and a branch push
does not update what Actions-sourced Pages shows. Do not use the script as the
day-to-day publish path after Actions is live. Do not edit `gh-pages` by hand.

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
