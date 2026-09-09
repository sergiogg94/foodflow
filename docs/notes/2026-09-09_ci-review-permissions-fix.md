# Implementation notes: Remove opencode-review workflow (CI permission hang unresolved)

**Date:** 2026-09-09  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** INFRA-3  
**Branch:** `fix/ci-review-permissions`  
**ADR(s):** N/A  
**Status:** 🟡 pending review

---

## Summary

Removed the `opencode-review` GitHub Actions workflow and its `ci-review` agent config. The workflow hung indefinitely in non-interactive CI because opencode's `github run` command prompts for tool permissions that no human can answer. An explicit per-tool permission fix (commit `8fc6ea8`) did not resolve the hang — the PR #4 run also stuck on `bash`. By human decision, the workflow is deleted because the automated PR review adds no value beyond what opencode local sessions already provide. The root cause is an upstream issue in `anomalyco/opencode`.

---

## Implementation per task

### INFRA-3 — Remove opencode-review workflow and ci-review agent

Three changes:

1. **Deleted `.github/workflows/opencode-review.yml`** — the workflow that triggered on `pull_request` events and ran `anomalyco/opencode/github@latest` with agent `ci-review`. This is the file that hung.

2. **Deleted `.opencode/agent/ci-review.md`** — the agent config only used by the removed workflow. Left as dead config otherwise.

3. **Updated `docs/notes/2026-09-09_ci-review-permissions-fix.md`** — rewritten to document the final outcome: the explicit-permissions fix did not resolve the hang, the workflow was removed by human decision, and the upstream issue remains open.

The prior commit `8fc6ea8` (explicit per-tool permissions) is preserved in git history for reference.

---

## Deviations from the ADR

None.

---

## Validation performed

- `git rm` confirmed both files deleted and staged.
- Grep for `opencode-review` and `ci-review` across all `.md`, `.yml`, `.yaml` files: references found only in historical notes (`docs/notes/2026-08-29_*`, `docs/notes/2026-08-30_*`), the review doc (`docs/reviews/2026-08-30_*`), and `docs/delivery-checklist.md`. Historical notes and review doc are left untouched (they document what happened). Delivery checklist updated to note the removal.
- Not validated: the workflow will no longer run (it is deleted); no CI validation needed.

---

## Follow-up issues discovered

- **Upstream issue in `anomalyco/opencode`** (to be filed): `github.handler.ts` creates sessions with hardcoded `[{permission: "question", action: "deny", pattern: "*"}]` and does not merge config permissions (including `OPENCODE_PERMISSION`) into the session. Neither the agent frontmatter permissions nor the env var reliably override per-tool evaluation. A proper fix requires modifying the `github run` command to merge `cfg.permission` into `session.permission` at creation time. This blocks any non-interactive use of the `anomalyco/opencode/github` action.

---

## Board updates

```text
No board transitions suggested: this is an infrastructure removal with no corresponding board item in the current MVP mode.
```

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** tester (+ reviewer after)
