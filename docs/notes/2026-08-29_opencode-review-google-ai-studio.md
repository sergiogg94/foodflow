# Implementation notes: OpenCode review workflow — Google AI Studio

**Date:** 2026-08-29  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** INFRA-1  
**Branch:** feat/meal-planner-core  
**ADR(s):** N/A  
**Status:** 🟡 pending review

---

## Summary

Switched the `opencode-review` GitHub Actions workflow (`.github/workflows/opencode-review.yml`) from the Anthropic provider to Google AI Studio: the `env` block now passes `GOOGLE_API_KEY` (the secret the human added to the repo), the model is now `google/gemini-2.5-pro`, and the setup comment references the `GOOGLE_API_KEY` repo secret. No ADR governs this change; it is a provider swap in an existing CI workflow.

---

## Implementation per task

### INFRA-1 — Switch opencode-review workflow to Google AI Studio

Three edits in `.github/workflows/opencode-review.yml`, nothing else:

1. Setup comment (line 10): replaced the two-line `ANTHROPIC_API_KEY` setup note with `# 1. Store your Google AI Studio API key as the GOOGLE_API_KEY repo secret.`
2. `env` block (line 36): `ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}` → `GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}`. Only `GOOGLE_API_KEY` is referenced; `GEMINI_API_KEY` is not used because the human did not add that secret.
3. `model` input (line 39): `anthropic/claude-sonnet-4-20250514` → `google/gemini-2.5-pro`.

The prompt, permissions, triggers, and all other steps are unchanged.

---

## Deviations from the ADR

None.

---

## Validation performed

- Read-back of `.github/workflows/opencode-review.yml` → all three edits present (lines 10, 36, 39); no other content changed.
- `git diff` → exactly 3 insertions / 4 deletions, all within the intended lines.
- `git commit` → `e2948c5` "Use Google AI Studio for opencode review workflow" on `feat/meal-planner-core`.
- Not validated: workflow execution in GitHub Actions (requires the `GOOGLE_API_KEY` secret and a `pull_request` event; cannot be run locally). Push to `origin` NOT performed — `gh` is not authenticated (no cached token in the environment); blocker escalated to the human.

---

## Follow-up issues discovered

None.

---

## Board updates

```text
No transition suggested yet: the push to origin is blocked (gh not authenticated), so PR #1 does not yet contain commit e2948c5.
Once the push succeeds, if a CI/automation board item tracks this workflow, move it In Progress -> Review — evidence: PR #1 (https://github.com/sergiogg94/foodflow/pull/1)
```

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** tester (+ reviewer after)