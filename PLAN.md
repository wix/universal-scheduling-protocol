# Feature: public-mirror-gh-pages

## Goal

Retarget the private-to-public USP mirror from `yahalomran/universal-scheduling-protocol` to `wix/universal-scheduling-protocol`, host the MkDocs site on GitHub Pages from that public repo (auto-publish on master, parity with prior Vercel-on-merge), remove obsolete Vercel artifacts, require agents to keep `site-docs/` in sync with spec changes via AGENTS.md/CLAUDE.md, and close private issue #205.

## Non-goals

- Transferring the private repo or migrating issues/PRs to the public Wix repo
- Changing custom domain / DNS / CNAME for `usp-protocol.dev` (sibling `usp-domain-acs-156` / issue 156)
- Changing canonical `usp.live` site URL strings in site-docs (domain work is sibling-owned)
- Deleting or replacing Render (`render.yaml`) hosting config beyond updating the `/github` redirect target
- Changing private CI validation behavior in `.github/workflows/ci.yml` beyond coexistence with new workflows
- Editing sibling worktree `usp-domain-acs-156`

## Must-preserve constraints

- Private source of truth remains `wix-private/universal-scheduling-protocol-spec`
- Private CI stays on `self-hosted` runners (org policy)
- Spec schemas stay canonical under `schemas/`; site-docs stay derived content under `site-docs/`
- Public Pages deploy must use GitHub Actions build type so sibling can attach a custom domain later
- Do not break unrelated private CI jobs
- CLAUDE.md is a symlink to AGENTS.md; keep that relationship (one edit covers both)

## Discovery summary (U1)

| Item | Finding |
|------|---------|
| Current mirror | Local git `origin` dual `pushurl`: private + `yahalomran/universal-scheduling-protocol`. Not a GitHub Action. No repo secrets listed. |
| Public old | `yahalomran/universal-scheduling-protocol` homepage `https://universal-scheduling-protocol.vercel.app` |
| Public new | `wix/universal-scheduling-protocol` empty; viewer ADMIN; Actions currently **disabled**; Pages not configured |
| Private perms | Maintain + push, **not** admin (cannot manage Actions org policy / likely cannot create secrets) |
| Site build | MkDocs Material; `package.json` / CI run `mkdocs build` → `site/`; `vercel.json` sets `outputDirectory: site` |
| Hosting files | `vercel.json` (live path), `render.yaml` (older Render blueprint) |

## File actions

| Path | Action | Reason |
|------|--------|--------|
| PLAN.md | modify | Plan-first Multitask contract |
| .github/workflows/mirror-to-public.yml | create | On private `master` push, mirror to `wix/universal-scheduling-protocol` (self-hosted) |
| .github/workflows/ci.yml | modify | Gate check job to private repo so mirrored public does not request missing self-hosted runners |
| .github/workflows/pages.yml | create | Build MkDocs and deploy GitHub Pages on public `master` (Actions source; custom-domain ready) |
| vercel.json | delete | Vercel hosting replaced by GH Pages |
| mkdocs.yml | modify | Point `repo_url` / social GitHub link at public Wix repo |
| render.yaml | modify | Point `/github` redirect at public Wix repo for consistency |
| AGENTS.md | modify | Require agents updating spec files to also update corresponding `site-docs/` (CLAUDE.md via symlink) |
| CHANGE_LOG.md | modify | Repo policy after file changes |

## Work units

| ID | Description | Files | Verification | Status |
|----|-------------|-------|--------------|--------|
| U1 | Complete and commit PLAN.md with discovery | PLAN.md | `test -f PLAN.md` && grep -q mirror-to-public PLAN.md | done |
| U2 | Add private→public mirror workflow; gate private CI to private repo | .github/workflows/mirror-to-public.yml, .github/workflows/ci.yml | `test -f .github/workflows/mirror-to-public.yml` && grep -q "wix-private/universal-scheduling-protocol-spec" .github/workflows/ci.yml | done |
| U3 | Add GH Pages deploy workflow (gated to public repo, Actions Pages) | .github/workflows/pages.yml | `test -f .github/workflows/pages.yml` | done |
| U4 | Remove Vercel config; retarget public GitHub links in mkdocs/render | vercel.json, mkdocs.yml, render.yaml | `test ! -f vercel.json` && grep -q 'wix/universal-scheduling-protocol' mkdocs.yml | done |
| U5 | Add site-docs sync rule to AGENTS.md (covers CLAUDE.md symlink) | AGENTS.md | grep -q 'site-docs/' AGENTS.md | pending |
| U6 | Enable public Actions/Pages; escalate PAT secret if needed; verify mirror/Pages as far as perms allow; close #205 with summary comment | (ops + issue) | `gh issue view 205 --repo wix-private/universal-scheduling-protocol-spec --json state -q .state` == CLOSED | pending |

## Manual / secret steps (user or escalate)

1. Create a fine-grained or classic PAT with write access to `wix/universal-scheduling-protocol` (contents: write).
2. Add private repo secret `PUBLIC_MIRROR_TOKEN` (or agreed name) on `wix-private/universal-scheduling-protocol-spec` (requires repo admin; escalate if maintain-only blocks this).
3. Optionally update local `origin` pushurl from yahalomran to wix public (machine-local; not required if Actions mirror is primary).
4. Sibling feature attaches custom domain after Pages is live.

## Revisions

### 2026-08-18T11:42:00Z - initial full plan after discovery
- Replaced seed PLAN with Goal, Non-goals, Must-preserve, File actions, Work units U1-U6
- Documented dual-pushurl discovery and empty public Wix repo / Actions-disabled state
