# AGENT_LOG

Decision and outcome log for FoodFlow, maintained by the orchestrator. Read before producing any artifact (core-principles §4).

---

## 2026-09-04 — Frontend language switch (session)

### Decisions

- **D-1 — New feature: frontend language switch.** Human request (verbatim): "Quiero agregar la funcionalidad de poder cambiar el idioma del frontend a español". Discovery interpretation confirmed by the human: **(a) a language selector English ↔ Spanish**. The choice persists **per device** (browser/device). **Default language: English**. Artifact: `docs/discovery-language-switch.md`.
- **D-2 — Session language policy.** All files generated in this session within the repo will be written in **English**, even though the conversation with the human is in Spanish. Human decision; overrides core-principles §11 for this session.
- **D-3 — AGENT_LOG.md created.** Human requested this file to record decisions taken. It was previously absent from the repository (noted in `docs/delivery-checklist.md:79`).

### Outcomes

- `docs/discovery-language-switch.md` updated: translated to English (per D-2), open questions resolved per D-1 (option (a), per-device persistence, English default). New assumption recorded: per-device persistence means local browser storage, not cross-device sync.
- `docs/discovery-language-switch.md` — ✅ approved by human (2026-09-04).
- `docs/requirements-language-switch.md` — created by scopper (English, 🟡 pending approval). 5 FR, 3 NFR, 6 AC, 8 edge cases, no open questions. Scoping choice flagged: selector placed in the app header (`frontend/src/App.tsx:19-32`).
- `docs/requirements-language-switch.md` — ✅ approved by human (2026-09-04).
- `docs/implementation-plan-language-switch.md` — created by planner (English, 🟡 pending approval). 6 tasks: T-1 i18n infrastructure [requires architecture], T-2 translation dictionaries, T-3 language selector, T-4/T-5/T-6 view strings. All P0, Area Frontend, Status Backlog.
- `docs/implementation-plan-language-switch.md` — ✅ approved by human (2026-09-08).
- `docs/adr/2026-09-08_frontend-i18n-mechanism.md` (ADR-6) — created by architect (English, 🟡 pending approval). Decision: hand-rolled React Context + `localStorage`; no new dependency; consistent with ADR-2 guard rails. `docs/architecture.md` updated with ADR-6 in both ADR tables (🔄 proposed).
- `docs/adr/2026-09-08_frontend-i18n-mechanism.md` (ADR-6) — ✅ approved by human (2026-09-08).
- Implementation (T-1..T-6) — developer completed on branch `feat/language-switch` (7 commits), PR #3 open against `main`. Build passes; backend tests 32 passed. Notes: `docs/notes/2026-09-08_language-switch-implementation.md` (no ADR deviations).
- Test report — `docs/tests/2026-09-08_language-switch.md`: AC-1..AC-6 ✅ Pass (code inspection + build), 0 defects, gaps: no frontend test framework, no headless browser, DOM observation not done.
- Review report — `docs/reviews/2026-09-08_language-switch_review.md`: verdict 🔄 Changes requested. Findings: B-1 (blocking — `TranslationKey` type in `translations.ts` instead of `types.ts`, dead code, ADR-6 file-structure deviation), NB-1 (untranslated `aria-label` in selector), NB-2 (ADR-6 status stale in `docs/architecture.md` — fixed by orchestrator), NB-3 (`t()` interpolation `$`-pattern edge case), P-1 (robust localStorage try/catch).
- Re-review — human decided to fix only B-1 (move type to `types.ts`); developer commit `c09140b`. NB-1 and NB-3 left open by human decision. Re-review verdict: ✅ Approved (`docs/reviews/2026-09-08_language-switch_review.md`).
- `AGENT_LOG.md` created at repo root (D-3).

### Pipeline state (updated 2026-09-11)

- PR #3 (`feat/language-switch`) — **merged** to `main` (2026-09-09).
- Both deliveries **accepted by human** (2026-09-11):
  - Delivery 1 (core T-1..T-10): `docs/delivery-checklist.md` ✅ accepted.
  - Delivery 2 (language-switch T-1..T-6): `docs/delivery-checklist.md` ✅ accepted.
- Board items #5–#20 (all 16 tasks): Status `Ready` → **human must move to `Done`** (per `github-projects-policy.md`).
- **Pipeline complete.** No pending stages remain.

---

## 2026-09-11 — Delivery acceptance

### Decisions

- **D-4 — Delivery 1 accepted.** Human approved `docs/delivery-checklist.md` for core implementation (T-1..T-10). All 6 ACs pass (AC-1/AC-4/AC-5 UI portions accepted as ⚠️ manual checks). Zero blocking findings.
- **D-5 — Delivery 2 accepted.** Human approved `docs/delivery-checklist.md` for frontend language switch (T-1..T-6). All 6 ACs pass (AC-1/AC-2 accepted as ⚠️ manual checks). NB-1 and NB-3 left open by human decision. PR #3 merged.

### Outcomes

- `docs/delivery-checklist.md` updated: both deliveries marked ✅ accepted, signed by human (2026-09-11).
- Board sync completed: 16 issues (#5–#20) created in Project 2 with correct Priority, Effort, Issue Type, Area fields; Status set to `Ready`.
- **Board updates pending:** human must move all 16 items from `Ready` → `Done` on Project 2.

---

## 2026-09-14 — AI ingredient suggestions (session)

### Decisions

- **D-6 — Permanent English policy.** All files and issues created from now on must be written in **English**, even though the conversation with the human is in Spanish. Overrides core-principles §11 for all future sessions. Human decision (2026-09-14).
- **D-7 — New feature: AI ingredient suggestions.** Human request (verbatim): "Quiero agregar una nueva feature. A momento de crear una nueva receta quiero agregar un botón para que se sugieran ingredientes de la receta mediante una inteligencia artificial. Quiero usar una api key de google AI studio para ello". Artifact: `docs/discovery-ai-suggestions.md`.
- **D-8 — Discovery open questions resolved.** Human answers (2026-09-14): (1) the suggestion button appears in **both create and edit modes**; (2) suggestions are **added as a proposal for the user to confirm** before incorporating; (3) suggestions are generated in the **current interface language** (en/es).

### Outcomes

- `docs/discovery-ai-suggestions.md` — translated to English (per D-6), open questions resolved per D-8, ✅ approved by human (2026-09-14).
- `docs/requirements-ai-suggestions.md` — created by scopper (English), ✅ approved by human (2026-09-14). 9 FR, 4 NFR, 6 AC, 7 edge cases, no open questions.
- `docs/implementation-plan-ai-suggestions.md` — created by planner (English), ✅ approved by human (2026-09-14). 6 tasks (T-1..T-6), issues #21–#26 created in Project 2 (Status Backlog).
- `docs/adr/2026-09-14_backend-http-client-for-gemini.md` (ADR-7) — created by architect (English), ✅ approved by human (2026-09-14). Decision: httpx (sync, `httpx==0.28.1`) as backend HTTP client for Gemini. `docs/architecture.md` updated with ADR-7 in both ADR tables (🔄 proposed).
- **D-9 — Prompt refinement (T-2).** Human instruction (2026-09-14): the Gemini prompt must exclude pantry staples (salt, oil, spices, etc.) and return only main ingredients that would commonly go on a weekly shopping list. Recorded in AGENT_LOG and passed to the developer; no requirements change (fits within FR-3's prompt instruction).
- **D-10 — Model choice (T-2).** Human instruction (2026-09-14): use model `gemini-3.1-flash-lite` (GA, May 2026; the `-preview` variant was shut down 2026-05-25). ADR-7 implementation guidance example URL updated from `gemini-2.0-flash` to `gemini-3.1-flash-lite` by the orchestrator (factual correction reflecting the human's decision).
- Implementation (T-1, T-2) — developer completed on branch `feat/ai-ingredient-suggestions` (3 commits: `6b35a43`, `1a31e12`, `ffb91df`), PR #27 open against `main`. Tests: 41 passed (32 pre-existing + 9 new). Notes: `docs/notes/2026-09-14_ai-suggestions-backend.md` (no ADR deviations). Board: #21, #22 moved Ready → In Progress → Review, Linked PR #27 set.
- Test report — `docs/tests/2026-09-14_ai-suggestions-backend.md`: AC-3 ✅, AC-4 ✅, AC-6 ✅ (backend contract), 41 passed, 0 failed. 1 defect: array of non-strings → HTTP 500 instead of 502 (`recipes.py:105`, gap between requirements edge case and ADR-7 contract). Gaps: no live Gemini call (no `GOOGLE_API_KEY` in env — manual check required), timeout not dedicated-tested, frontend out of scope.
- Review report — `docs/reviews/2026-09-14_ai-suggestions-backend_review.md`: verdict ✅ Approved. 1 non-blocking finding (NB-1: array of non-strings → 500; fix: add `ValidationError` to except clause). Zero blocking findings. Scope discipline: exactly 5 files, no scope creep.
- **Human gate:** merge decision on PR #27 (reviewer recommends holding #21/#22 in Review pending human decision; after merge, move Review → Done).
- Next agent: **documenter** (delivery checklist) after T-3..T-6 complete; or developer for T-3..T-6 after PR #27 merge.

---

## 2026-09-17 — AI ingredient suggestions (merge, test, review, delivery)

### Decisions

- **D-11 — Human accepts NB-1 and NB-2 as-is.** The human decided not to fix the malformed-Gemini-response error handling (array of non-strings → HTTP 500 at `recipes.py:105`; empty `candidates` array → `IndexError` → HTTP 500 at `recipes.py:101`). Both are low-likelihood gaps between the requirements edge cases and the ADR-7 contract; the implementation matches ADR-7 exactly. No follow-up issue filed for NB-1/NB-2.
- **D-12 — NB-3 tracked as follow-up issue.** The human requested a follow-up issue for NB-3 (README.md:42 references non-existent `env` section; should be `environment`). Issue #30 created on GitHub. The fix is included in the doc-alignment commit; the human closes the issue when satisfied.

### Outcomes

- **PRs merged to `main`:** PR #27 (`b6cffee`, T-1/T-2 backend), PR #28 (`41b3e1c`, T-6 devops), PR #29 (`d125581`, T-3/T-4/T-5 frontend). All three confirmed merged via `pull_request_read`.
- **Full test report** — `docs/tests/2026-09-17_ai-suggestions-full.md`: 41 backend tests passed, 0 failed; frontend build passed (tsc + vite); live Gemini verified (13 attempts, 11× 200, 2× 502); `docker compose config` parses; NFR-1 scan clean. All 6 ACs verified. 1 defect (NB-1, accepted as-is by human).
- **Full review report** — `docs/reviews/2026-09-17_ai-suggestions-full_review.md`: verdict ✅ Approved. Zero blocking findings. NB-1 (carried, re-verified) and NB-2 (new, same class) accepted as-is by human. NB-3 (README `env`→`environment`) resolved via doc-alignment commit and tracked as issue #30.
- **Doc alignment:** README.md NB-3 fixed (`env`→`environment`). Status headers aligned: `docs/requirements-ai-suggestions.md`, `docs/implementation-plan-ai-suggestions.md`, `docs/adr/2026-09-14_backend-http-client-for-gemini.md` (ADR-7) all updated from "🟡 pending approval" to "✅ approved (2026-09-14)". ADR-7 status updated to "✅ approved" in both ADR tables in `docs/architecture.md`.
- **Delivery checklist** — `docs/delivery-checklist.md` updated with Delivery 3 (AI ingredient suggestions, T-1..T-6): scope delivered, AC statuses, implementation references, review/test status, open risks, final checklist. Status: ✅ pending human acceptance.
- **Follow-up issue** — GitHub issue #30 created: `[AI suggestions] NB-3: README references non-existent "env" section in docker-compose`. Labeled `bug`. Fix included in doc-alignment commit.

### Pipeline state (updated 2026-09-17)

- PR #27 (`feat/ai-ingredient-suggestions`) — **merged** to `main` as `b6cffee` (2026-09-15).
- PR #28 (`feat/ai-suggestions-devops`) — **merged** to `main` as `41b3e1c` (2026-09-17).
- PR #29 (`feat/ai-suggestions-frontend`) — **merged** to `main` as `d125581` (2026-09-17).
- Delivery 3 checklist: **✅ pending human acceptance** (`docs/delivery-checklist.md`).
- Board items #21–#26 (T-1..T-6): currently in Review on Project 2 → **human must move to `Done`** upon acceptance.
- **Next step:** human reviews the delivery checklist, exercises the suggest button in a browser, and accepts or rejects the delivery.
