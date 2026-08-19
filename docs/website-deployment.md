# Website deployment

The protocol website is hosted on GitHub Pages for
[`wix/universal-scheduling-protocol`](https://github.com/wix/universal-scheduling-protocol)
and served at <https://usp-protocol.dev>. The project URL
<https://wix.github.io/universal-scheduling-protocol/> still works as a
fallback. `www.usp-protocol.dev` 301s to the apex.

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

Canonical host is `usp-protocol.dev` (AC-S3e option B: this origin is the full
MkDocs site plus published artifacts). `usp.live` should later redirect here.

[`site-docs/CNAME`](../site-docs/CNAME) is required because `mkdocs gh-deploy`
replaces the whole `gh-pages` branch on each publish. GitHub also writes a
`CNAME` when you save the custom domain in
[Settings → Pages](https://github.com/wix/universal-scheduling-protocol/settings/pages).
Without the file in `site-docs/`, the next publish would drop the binding.

Apex DNS uses GitHub Pages A records (`185.199.108.153` through
`185.199.111.153`). `www` CNAMEs to `wix.github.io`. DNS check succeeded and
**Enforce HTTPS** is on. GitHub's Pages banner may still show `http://` even
when HTTPS is enforced; use curl against `https://usp-protocol.dev` as the
source of truth.
