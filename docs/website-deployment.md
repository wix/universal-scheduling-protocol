# Website deployment

The protocol website is hosted on GitHub Pages for
[`wix/universal-scheduling-protocol`](https://github.com/wix/universal-scheduling-protocol)
and served at <https://wix.github.io/universal-scheduling-protocol/>.

## Current setup

| Setting | Value |
|---------|-------|
| Pages source | GitHub Actions (required). Do not use Deploy from branch `gh-pages`. |
| Auto-publish | [`.github/workflows/pages.yml`](../.github/workflows/pages.yml) on push to `master` when the repository is `wix/universal-scheduling-protocol` |
| Action pins | Every `uses:` in workflows is a full-length commit SHA (org policy) |
| Site source | `site-docs/` and `mkdocs.yml` on `master` |

GitHub Actions is enabled for this repository. The `pages` workflow builds MkDocs
and deploys with `actions/upload-pages-artifact` and `actions/deploy-pages`.
That only publishes if Pages **Source** in
[Settings → Pages](https://github.com/wix/universal-scheduling-protocol/settings/pages)
is set to **GitHub Actions**. Switching that setting is a GitHub UI step; it is
not done in this repository.

If Source is still **Deploy from a branch** (`gh-pages`), the workflow will
build but Pages will keep serving the old branch until Source is changed.

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

This runs `mkdocs gh-deploy`, which force-pushes pre-built HTML to `gh-pages`.
Once Pages Source is GitHub Actions, that branch is not what Pages serves.
Running the script then fights the Actions deploy: the next successful
`pages` workflow overwrites the live site, and a branch push does not update
what Actions-sourced Pages shows. Do not use the script as the day-to-day
publish path after Actions is live. Do not edit `gh-pages` by hand.

## Custom domain

When a custom domain is attached in Pages settings, GitHub writes a `CNAME`
file into the published site. Keep a matching `CNAME` under `site-docs/` so
every MkDocs build includes it. Otherwise a later deploy can drop the domain
binding.
