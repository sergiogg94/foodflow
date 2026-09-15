# Implementation notes: AI ingredient suggestions — GOOGLE_API_KEY deployment setup (T-6)

**Date:** 2026-09-15  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** T-6  
**Branch:** `feat/ai-suggestions-devops`  
**ADR(s):** N/A  
**Status:** 🟡 pending review

---

## Summary

Wired and documented the server-side Google AI Studio API key for deployment (T-6). `docker-compose.yml` passes `GOOGLE_API_KEY` from the host `.env` into the container environment via `environment: GOOGLE_API_KEY=${GOOGLE_API_KEY:-}`; a committed `.env.example` documents the variable name with no value; `README.md` documents the setup and the HTTP 503 behavior when the key is absent. Satisfies NFR-1 (key never in the frontend build, served to the browser, or committed) and AC-3 (deployment context). No ADR governs this change; ADR-7 covers the backend HTTP client, not deployment env wiring.

---

## Implementation per task

### T-6 — Document `GOOGLE_API_KEY` setup for deployment

- `docker-compose.yml` — added an `environment` entry to the `foodflow` service: `GOOGLE_API_KEY=${GOOGLE_API_KEY:-}`. Docker Compose reads the host `.env` file automatically, so the key flows host `.env` → container environment → backend endpoint (`backend/app/routes/recipes.py:67` reads `os.environ.get("GOOGLE_API_KEY", "").strip()`). No value is hardcoded; the `:-` default yields an empty string when the variable is unset, which the endpoint maps to HTTP 503 (FR-2).
- `.env.example` (new, committed) — contains only the variable name with no value (`GOOGLE_API_KEY=`), plus a comment pointing at `.gitignore:15` and NFR-1. Documents the required variable without exposing any secret.
- `README.md` — new "AI ingredient suggestions (optional)" section under "Run it": create a local `.env` with `GOOGLE_API_KEY=<your-key>`, never commit it (NFR-1), `docker compose up -d --build` picks it up automatically, and the endpoint returns HTTP 503 with detail `"AI suggestions are not configured"` when the key is absent (AC-3).

Satisfies NFR-1 (key flows exclusively environment → backend endpoint → Google API) and AC-3 (deployment context: missing key yields the configured 503 error path, rest of the app unaffected).

---

## Deviations from the ADR

None — no ADR governs this change (ADR-7 covers the backend HTTP client, not deployment env wiring).

Task-brief note (not an ADR deviation): the brief said "`env` section", but `env` is not a valid Compose service attribute — `docker compose config` (v2.40.3) rejects it with `services.foodflow additional properties 'env' not allowed`. The standard `environment` attribute is used instead; it matches the brief's own example syntax (`GOOGLE_API_KEY: ${GOOGLE_API_KEY:-}`) and the required flow (host `.env` → container environment → backend endpoint) is intact.

---

## Validation performed

- `docker compose config` → parses successfully; renders `GOOGLE_API_KEY: ""` when unset (the `${GOOGLE_API_KEY:-}` default).
- `GOOGLE_API_KEY=test-key docker compose config` → renders `GOOGLE_API_KEY: test-key` (value flows through the interpolation).
- Not validated: live container run with a real key (no `GOOGLE_API_KEY` in this environment). The backend endpoint behavior with/without the key is covered by the T-2 test report (`docs/tests/2026-09-14_ai-suggestions-backend.md`).

---

## Follow-up issues discovered

- None.

---

## Board updates

```text
Move #26 ([AI suggestions] T-6) Ready -> In Progress — evidence: branch feat/ai-suggestions-devops, comment https://github.com/sergiogg94/foodflow/issues/26#issuecomment-5685667429
Move #26 ([AI suggestions] T-6) In Progress -> Review — evidence: PR https://github.com/sergiogg94/foodflow/pull/28, docker compose config validated
Set Linked PR on #26 — evidence: PR https://github.com/sergiogg94/foodflow/pull/28 (auto-populated via "Closes #26" in the PR body)
```

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** tester (+ reviewer after)