# Contributing — Sehaty

## Change flow (every change)
1. **Open an issue** describing the change. Assign it to `mks-zakaria`.
2. **Branch** off `main`: `feat/<slug>`, `fix/<slug>`, `chore/<slug>` (never commit to `main`).
3. **Commit** with [Conventional Commits](https://www.conventionalcommits.org)
   (`feat:`, `fix:`, `perf:` bump the version; `chore/ci/docs/refactor/test/style` don't).
   The **only** author on any commit is `mks-zakaria` (plus the release bot for
   auto-release commits). No other bot/tool attribution.
4. **Push** the branch and open a **PR** whose body says `Closes #<issue>`.
5. CI (`primary`) must be green. **Merge** (squash) → the `release` workflow runs
   semantic-release, bumps the version, updates `CHANGELOG.md`, tags `vX.Y.Z`.

## Local gates (pre-commit — runs on every commit)
- `ruff` (lint + format)
- Conventional-commit message check
- `pytest` (the test suite)

Install once: `uvx pre-commit install --install-hooks && uvx pre-commit install --hook-type commit-msg`.

## Testing rules
- **Every added functionality ships with its own unit test** (isolated).
- **A global behaviour (end-to-end) test** is extended to cover the new
  functionality and re-run so the whole flow is re-tested together. In `sehaty-db`
  the behaviour guardrail is `tests/test_metadata.py` (every table registers);
  service/API behaviour tests live in `sehaty-core` / `sehaty-api`.
- CI runs the full suite on every PR and push to `main`.

## CI secrets
- `SEHATY_CI_PAT` — a fine-grained PAT (Contents: read+write on the sehaty repos).
  Used for (a) cross-repo checkout of `sehaty-db` in `sehaty-core`/`sehaty-api`
  CI, and (b) letting the `release` workflow push the version commit to protected
  `main`. Add with `gh secret set SEHATY_CI_PAT`.
