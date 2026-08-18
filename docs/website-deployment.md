# Website deployment

The protocol website is hosted on GitHub Pages for
[`wix/universal-scheduling-protocol`](https://github.com/wix/universal-scheduling-protocol)
and served at <https://wix.github.io/universal-scheduling-protocol/>.

## Current setup

| Setting | Value |
|---------|-------|
| Pages source | Deploy from a branch: `gh-pages`, folder `/ (root)` |
| Branch contents | Pre-built MkDocs output plus `.nojekyll` |
| Site source | `site-docs/` and `mkdocs.yml` on `master` |

GitHub Actions is disabled for this repository by the organisation, so the site
cannot be built by a workflow. The `.nojekyll` marker tells Pages to serve the
branch as-is instead of running a Jekyll build, which is what allows the site to
publish while Actions is unavailable.

## Publishing an update

After site content is merged to `master`:

```bash
npm run publish:pages     # or: ./scripts/publish-pages.sh
```

This runs `mkdocs gh-deploy`, which builds `site/` and force-pushes it to
`gh-pages` together with `.nojekyll`. Pages picks the change up within a few
minutes.

Publishing is a separate step from merging because no workflow can run here. Do
not edit `gh-pages` by hand: every publish overwrites it.

## Switching to fully automatic publishing

[`.github/workflows/pages.yml`](../.github/workflows/pages.yml) already builds
and deploys the site on every push to `master`. Once an organisation admin
enables Actions for this repository:

1. Set Pages **Source** to **GitHub Actions** in
   [Settings → Pages](https://github.com/wix/universal-scheduling-protocol/settings/pages).
2. Push to `master` and confirm the `pages` workflow deploys.
3. Stop using `npm run publish:pages`; the `gh-pages` branch can then be deleted.

## Custom domain

When a custom domain is attached in Pages settings, GitHub writes a `CNAME`
file to the serving branch. Because `mkdocs gh-deploy` replaces the whole
branch on each publish, add the same `CNAME` file to `site-docs/` as well so
every build carries it into `site/`. Otherwise the next publish drops the
domain binding.
