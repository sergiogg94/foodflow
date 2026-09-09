# Implementation notes: Fix ci-review agent permissions for non-interactive CI

**Date:** 2026-09-09  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** INFRA-3  
**Branch:** `fix/ci-review-permissions`  
**ADR(s):** N/A  
**Status:** 🟡 pending review

---

## Summary

Fixed the `opencode-review` GitHub Actions workflow hanging on permission prompts in non-interactive CI. The root cause is that opencode's `github run` command creates sessions with hardcoded permissions (`question: deny` only), and the `OPENCODE_PERMISSION` env var with `{"*": "allow"}` does not reliably override per-tool evaluation. The fix replaces the catch-all format with explicit per-tool permission entries in both the agent markdown config and the `OPENCODE_PERMISSION` env var, ensuring every tool resolves to `allow` (or `deny` for restricted tools) without relying on wildcard matching across code paths.

---

## Implementation per task

### INFRA-3 — Fix ci-review agent permissions to prevent CI hangs

Two files modified, no other changes.

1. **`.opencode/agent/ci-review.md`** (lines 4-18) — replaced the single `"*": allow` catch-all in the frontmatter `permission` block with explicit entries for every opencode permission key: `bash: allow`, `edit: allow`, `read: allow`, `glob: allow`, `grep: allow`, `webfetch: allow`, `websearch: allow`, `task: allow`, `skill: allow`, `lsp: allow`, `question: allow`, `external_directory: deny`, `doom_loop: deny`. The `"*": allow` catch-all is retained as a fallback.

2. **`.github/workflows/opencode-review.yml`** (lines 36-40) — replaced the `OPENCODE_PERMISSION` value `'{"*": "allow"}'` with an explicit per-tool JSON object: `'{"*": "allow", "bash": "allow", "edit": "allow", "read": "allow", "glob": "allow", "grep": "allow", "question": "allow", "external_directory": "deny", "doom_loop": "deny"}'`. Updated the comment to explain the rationale. `external_directory` and `doom_loop` are denied because the agent only reads files and returns text.

---

## Deviations from the ADR

None.

---

## Validation performed

- `node -e "JSON.parse(...)"` on the `OPENCODE_PERMISSION` value → valid JSON, all expected keys present.
- `python3 yaml.safe_load()` on the workflow file → valid YAML, `OPENCODE_PERMISSION` string parses to the expected JSON object.
- Agent markdown frontmatter indentation and YAML structure verified by visual inspection and `python3 yaml.safe_load()`.
- Source code of `anomalyco/opencode` read and traced: `packages/opencode/src/permission/index.ts` (`evaluate()`, `fromConfig()`, `merge()`), `packages/opencode/src/cli/cmd/github.handler.ts` (`Session.create()` hardcoded permissions), `packages/opencode/src/session/prompt.ts` (permission evaluation ruleset), `packages/opencode/src/agent/agent.ts` (agent config loading). Confirmed that `"*": allow` should match all tools via `Wildcard.match()`, but the session creation hardcodes only `question: deny`.
- Not validated: workflow execution in GitHub Actions (requires PR event + API key secret; cannot be run locally).

---

## Follow-up issues discovered

- **Upstream issue in `anomalyco/opencode`**: `github.handler.ts` creates sessions with hardcoded `[{permission: "question", action: "deny", pattern: "*"}]` and does not merge config permissions (including `OPENCODE_PERMISSION`) into the session. This means the env var relies on agent-level permission merging, which may not apply consistently across all evaluation code paths. A proper fix would modify the `github run` command to merge `cfg.permission` into `session.permission` at creation time. This should be filed as an upstream issue or PR if the explicit per-tool fix does not resolve the hang.

---

## Board updates

```text
No board transitions suggested: this is an infrastructure fix with no corresponding board item in the current MVP mode.
```

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** tester (+ reviewer after)
