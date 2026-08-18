# Escalation

Feature: public-mirror-gh-pages
Raised at: 2026-08-18T11:47:58Z
Updated at: 2026-08-18T11:50:00Z

## Question

Two Wix-org blockers prevent the intended public mirror + GH Pages auto-publish on `wix/universal-scheduling-protocol`. Which ops path should we take?

### Blocker 1: GitHub Actions disabled by organization

API `PUT .../actions/permissions` returns 409: "GitHub Actions is disabled on this repository by the organization". Public `pages.yml` cannot run until an org admin enables Actions for this repo (or exempts it).

### Blocker 2: Org branch rulesets on `master`

Org rulesets `PR Flow (Admins)` and `PR Flow (All)` apply to `master` and require:

- required linear history (private history has merge commits; rejected commit example `824bd49`)
- non-fast-forward protection (blocks `--force` mirror)
- pull_request required before landing on `master`

Direct `git push` of private history to `master` was rejected (GH013). Push to non-`master` branch `mirror-seed` succeeded.

### Also needed: PAT secret

`mirror-to-public.yml` needs private repo secret `PUBLIC_MIRROR_TOKEN` (PAT with Contents: Write on `wix/universal-scheduling-protocol`). User can create the token; secret set on private repo appears possible with current maintain access.

Also: repo reports `permissions.admin=true` but changing `default_branch` via API failed with "You don't have permission to change the default branch" (org policy). Default remains `mirror-seed` until an org admin switches it to `synced`.

Pages site shell is already created: `build_type=workflow`, URL `https://wix.github.io/universal-scheduling-protocol/` (custom domain can be attached later by sibling). Content not published yet.

## Options

A) Org admin: (1) enable Actions on `wix/universal-scheduling-protocol`, (2) exempt the repo from linear-history / PR-required / non-FF rules on the mirror target branch (or allow merge commits + force sync to `master`). User creates PAT and sets `PUBLIC_MIRROR_TOKEN`. Keep `pages.yml` + mirror to `master`. Closest to "public repo looks like a normal master mirror".

B) No org rule/Actions changes: mirror private `master` to public branch `synced` (non-protected); private self-hosted job builds MkDocs and force-pushes `site/` to public `gh-pages`; Pages source = `gh-pages` branch. Still need `PUBLIC_MIRROR_TOKEN`. Public `master` stays empty or PR-only.

C) Hybrid: org enables Actions only; mirror targets `synced` (avoid master rules); `pages.yml` runs on `synced` pushes. Still need PAT. Public default branch may be set to `synced`.

## Recommendation

A if an org admin can exempt this public docs/mirror repo quickly (cleanest consumer UX). Otherwise B so Pages auto-publishes without waiting on org Actions + ruleset exceptions.

## Status

PENDING
