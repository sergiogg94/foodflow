# Test report: AI ingredient suggestions — full feature (T-1..T-6)

**Date:** 2026-09-17  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** T-1, T-2, T-3, T-4, T-5, T-6  
**Requirements:** `docs/requirements-ai-suggestions.md`  
**Implementation notes:** `docs/notes/2026-09-14_ai-suggestions-backend.md`, `docs/notes/2026-09-14_ai-suggestions-frontend.md`, `docs/notes/2026-09-15_ai-suggestions-devops.md`  
**Branch:** `main` (PRs #27, #28, #29 merged)  
**Status:** 🟡 pending review

---

## Validation summary

Validated the full AI ingredient suggestions feature (backend T-1/T-2, frontend T-3/T-4/T-5, devops T-6) against FR-1..FR-9, NFR-1..NFR-4, AC-1..AC-6, the ADR-7 error handling contract, the ADR-6 i18n contract, and the requirements edge cases. Ran the full backend suite in a fresh venv from `backend/dev-requirements.txt`: 41 passed, 0 failed, 0 skipped (32 pre-existing + 9 new). Frontend `npm run build` (tsc + vite) passed. Live Gemini calls with the real `GOOGLE_API_KEY` verified: a real request returns 200 with a `suggestions` array of strings; `language: "es"` returns genuinely Spanish suggestions (AC-6 end-to-end); an invalid key returns 502 with `"Failed to get AI suggestions"`; and the raw response shape matches `candidates[0].content.parts[0].text` as a JSON array. Gemini's intermittent 503 "high demand" was observed twice across 13 live attempts and correctly mapped to 502. The devops key flow was verified end-to-end (host `.env` → compose config → container environment). One defect remains from the previous report: NB-1 — a Gemini response that is a valid JSON array of non-strings returns HTTP 500 instead of the required 502 (`backend/app/routes/recipes.py:105`). Live browser interaction (clicking the button, toggling suggestions, appending) could not be exercised — this repo has no headless browser or frontend test framework — and remains a manual check.

---

## Scope tested

**Tested:** `POST /recipes/suggest-ingredients` endpoint (`backend/app/routes/recipes.py:56-107`); `SuggestIngredientsRequest` / `SuggestIngredientsResponse` schemas (`backend/app/schemas.py:50-64`); `httpx==0.28.1` dependency (`backend/requirements.txt:4`); the 9 new tests in `backend/tests/test_foodflow.py:403-591`; OpenAPI registration; NFR-1 repo scan (no key in frontend source, frontend build, or committed files); NFR-4 sync pattern by code inspection. **Live Gemini calls with the real key** (against the container rebuilt from `main`): success → 200, Spanish output → 200 (AC-6 end-to-end), invalid key → 502, raw response shape verified, intermittent 503 → 502 observed. **Frontend:** `npm run build` (tsc + vite) passed; `suggestIngredients(name, language)` (`frontend/src/api/recipes.ts:28-33`); 8 en/es i18n keys (`frontend/src/i18n/translations.ts:34-41`, `:114-121`); suggest button + proposal UI in the shared form (`frontend/src/views/RecipesView.tsx:229-279`); 503/502 error mapping (`RecipesView.tsx:136-143`); no new npm dependencies (NFR-2, `frontend/package.json` unchanged since core). **Devops:** `docker compose config` parses; `GOOGLE_API_KEY` resolves non-empty (length 53) into the `foodflow` service; container has the key set (length 53). Error paths exercised: missing key → 503, whitespace-only key → 503, validation → 422, success → 200, Gemini HTTP error → 502, network error → 502, malformed body → 502, unexpected shape → 502, array of non-strings → 500 (NB-1, see Defects).  
**Not tested:** Live browser interaction — no headless browser or frontend test framework in this repo; the button/proposal flow (clicking, loading indicator, toggling, editing, appending, dismissing) is verified by code inspection + build only and requires a manual browser check. The `httpx.TimeoutException` path has no dedicated test (covered by the except clause, `TimeoutException ⊂ HTTPError`).

---

## Acceptance criteria coverage

| AC | Status | Evidence |
|---|---|---|
| AC-1 | ✅ Pass | Button + loading + proposal list in the shared form (`frontend/src/views/RecipesView.tsx:229-237` button with `disabled={suggesting}` and loading text; `:251-279` editable proposal list). `handleSuggest` (`:124-152`) sets `suggesting` true for the request duration. `npm run build` passed. Live browser interaction remains a manual check — see Test gaps. |
| AC-2 | ✅ Pass | `addProposalIngredients` (`RecipesView.tsx:172-185`): filters `item.selected`, trims, drops blanks, appends only the selected suggestions to `form.ingredients` (`:179-182`), then dismisses the proposal (`:184`). |
| AC-3 | ✅ Pass | Backend 503 verified live: local uvicorn without `GOOGLE_API_KEY` → 503 `{"detail":"AI suggestions are not configured"}`; tests `test_suggest_ingredients_503_when_key_missing` (`backend/tests/test_foodflow.py:447-454`) and `_503_when_key_whitespace_only` (`:457-464`). Frontend maps 503 → `recipes.error_suggest_not_configured` (`RecipesView.tsx:137-138`). No Gemini call: the 503 raise at `recipes.py:68-71` precedes any httpx usage. |
| AC-4 | ✅ Pass | Live: invalid key → 502 `{"detail":"Failed to get AI suggestions"}`; Gemini intermittent 503 "high demand" observed twice across 13 live attempts, both mapped to 502 with the same detail. Tests: `test_suggest_ingredients_502_on_gemini_http_error` (`:504-513`), `_502_on_network_error` (`:516-525`), `_502_on_malformed_body` (`:528-543`), `_502_on_unexpected_shape` (`:546-561`). Frontend maps 502 → `recipes.error_suggest_failed` (`RecipesView.tsx:139-140`). |
| AC-5 | ✅ Pass | `handleSuggest` sets `suggesting` true at `RecipesView.tsx:131` and clears it in `finally` at `:150`; the button is `disabled={suggesting}` at `:233`, so no duplicate request can be sent while in flight. |
| AC-6 | ✅ Pass | Live end-to-end: `POST /recipes/suggest-ingredients` with `{"name":"Paella Valenciana","language":"es"}` → 200 `{"suggestions":["arroz bomba","pollo","conejo","judía verde plana","garrofón","tomate","azafrán"]}` — genuinely Spanish output. Backend prompt contract: `language_name = "Spanish"` at `recipes.py:73`, prompt at `:74-82`; test `test_suggest_ingredients_prompt_and_request` (`:564-591`) asserts `"Spanish"` in the prompt. |

---

## Edge case coverage

| Edge case / error case | Test | Result |
|---|---|---|
| Empty recipe name → 422 | `test_suggest_ingredients_validation` (`test_foodflow.py:467-481`) | ✅ Pass |
| Whitespace-only recipe name → 422 | `test_suggest_ingredients_validation` (`:467-481`) | ✅ Pass |
| Invalid language (`fr`) → 422 | `test_suggest_ingredients_validation` (`:467-481`) | ✅ Pass |
| Missing `name` field → 422 | `test_suggest_ingredients_validation` (`:467-481`) | ✅ Pass |
| API key with extra whitespace → 503 | `test_suggest_ingredients_503_when_key_whitespace_only` (`:457-464`) | ✅ Pass |
| Empty recipe name in the form (no request sent) | Code inspection `RecipesView.tsx:127-130` — `form.name.trim() === ""` sets `recipes.suggest_name_required` and returns before calling the API | ✅ Pass |
| Gemini returns empty list → 200 `{"suggestions": []}` | Verified empirically (probe) + code inspection `recipes.py:102-105`; frontend shows `recipes.suggest_empty` with dismiss button (`RecipesView.tsx:239-250`) | ✅ Pass |
| Gemini returns non-JSON text → 502 | `test_suggest_ingredients_502_on_malformed_body` (`:528-543`) | ✅ Pass |
| Gemini returns non-array JSON (object) → 502 | `test_suggest_ingredients_502_on_unexpected_shape` (`:546-561`) | ✅ Pass |
| Gemini returns array of non-strings → 502 | Empirical probe (mocked httpx, `raise_server_exceptions=False`): `[1, 2, 3]` → HTTP 500 (uncaught `pydantic.ValidationError` at `recipes.py:105`); control `["pasta","eggs"]` → 200 | ❌ Fail — see Defects |
| ADR-7: network error (`httpx.ConnectError`) → 502 | `test_suggest_ingredients_502_on_network_error` (`:516-525`) | ✅ Pass |
| ADR-7: timeout (`httpx.TimeoutException`) → 502 | No dedicated test; covered by except clause `recipes.py:106` (`TimeoutException ⊂ HTTPError`, verified) | ✅ Pass |
| ADR-7: non-200 (`httpx.HTTPStatusError`) → 502 | `test_suggest_ingredients_502_on_gemini_http_error` (`:504-513`); live Gemini 503 "high demand" → 502 observed twice | ✅ Pass |
| ADR-7: malformed body (`json.JSONDecodeError`) → 502 | `test_suggest_ingredients_502_on_malformed_body` (`:528-543`) | ✅ Pass |
| ADR-7: unexpected shape (`KeyError`, `TypeError`) → 502 | `test_suggest_ingredients_502_on_unexpected_shape` (`:546-561`, TypeError); KeyError verified empirically (missing `candidates` → 502) | ✅ Pass |
| Existing ingredients in edit mode (append, not replace) | Code inspection `RecipesView.tsx:172-185` — `addProposalIngredients` appends to the existing `form.ingredients`; the form is shared between create and edit modes (`:192-300`) | ✅ Pass |
| Rapid repeated clicks (no duplicate request) | Code inspection `RecipesView.tsx:131,150,233` — `disabled={suggesting}` during the request | ✅ Pass |

---

## Result summary

- `python -m pytest backend/tests -q` (fresh venv, `backend/dev-requirements.txt`) → 41 passed, 0 failed, 0 skipped (2241 warnings — pre-existing fastapi/starlette deprecation warnings on Python 3.14, not from changed code)
- `python -m pytest backend/tests -q -k suggest_ingredients` → 9 passed, 32 deselected
- `npm run build` in `frontend/` (tsc + vite) → passed, 41 modules transformed, built in 523ms
- `docker compose config` → parses; `GOOGLE_API_KEY` resolves non-empty (length 53) into the `foodflow` service environment
- `docker compose exec -T foodflow sh -c 'test -n "$GOOGLE_API_KEY" && echo SET || echo EMPTY'` → SET (length 53)
- Live Gemini (real key, container rebuilt from `main`): `{"name":"Pasta Carbonara","language":"en"}` → 200 `{"suggestions":["spaghetti","guanciale","pecorino romano","eggs"]}`; `{"name":"Paella Valenciana","language":"es"}` → 200 with Spanish suggestions; 13 attempts total → 11× 200, 2× 502 (both `{"detail":"Failed to get AI suggestions"}` — Gemini intermittent 503 mapped to 502)
- Live invalid key (local uvicorn, port 8001) → 502 `{"detail":"Failed to get AI suggestions"}`
- Live missing key (local uvicorn, port 8002) → 503 `{"detail":"AI suggestions are not configured"}`
- Raw Gemini response shape (direct API call) → top-level keys `['candidates','usageMetadata','modelVersion','responseId']`; `candidates[0].content.parts[0].text` is a JSON array of strings
- Empirical probe (mocked httpx): array of numbers `[1,2,3]` → 500 ❌ (see Defects); control array of strings → 200
- OpenAPI check → `POST /recipes/suggest-ingredients` registered; `SuggestIngredientsRequest` (name required, minLength 1; language enum `["en", "es"]`); `SuggestIngredientsResponse` (suggestions: array of strings, required) — matches FR-1
- NFR-1 scan → no `GOOGLE_API_KEY` / `generativelanguage` / `x-goog-api-key` in `frontend/src/` or `frontend/dist/`; key name only in `backend/app/routes/recipes.py` and `backend/tests/test_foodflow.py`; no `AIza` prefix anywhere in the repo

**Totals:** 41 backend tests passed · 0 failed · 0 skipped · frontend build passed · live Gemini verified

---

## Defects observed

- `backend/app/routes/recipes.py:105` — when Gemini returns a valid JSON array whose elements are not strings (e.g. `[1, 2, 3]`), `SuggestIngredientsResponse(suggestions=suggestions)` raises an uncaught `pydantic.ValidationError` and the endpoint returns HTTP 500. The requirements edge case "Gemini returns non-JSON or malformed response: the backend returns HTTP 502" (`docs/requirements-ai-suggestions.md:126`) expects 502. The ADR-7 contract (`docs/adr/2026-09-14_backend-http-client-for-gemini.md:94`) lists only `(httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError)`, which the implementation matches exactly — so this is a gap between the requirements edge case and the ADR contract, not an ADR deviation. Re-verified on `main` with a mocked probe (`raise_server_exceptions=False`): `[1, 2, 3]` → HTTP 500; control `["pasta","eggs"]` → 200. Low likelihood in practice (`responseSchema` instructs Gemini to return strings), but factual. Not fixed by the tester — the developer decides after review. Suggested fix (for the developer): validate element types or extend the except clause with `pydantic.ValidationError`.

---

## Test gaps

- **Live browser interaction NOT tested** — this repo has no headless browser or frontend test framework. Manual check required: click the "Suggest ingredients" button in create and edit modes, observe the loading indicator and disabled button, toggle/edit suggestions in the proposal list, append only selected suggestions, dismiss the proposal, and observe the 503/502 error messages against a running backend.
- **Timeout path not exercised by a dedicated test** — `httpx.TimeoutException` is covered by the except clause (`recipes.py:106`, subclass of `httpx.HTTPError`, verified), but no test raises it explicitly.
- **Array-of-non-strings response → 500** — see Defects; no test covers it and the current behavior violates the requirements' malformed-response edge case.
- **Documentation status headers stale** — `docs/requirements-ai-suggestions.md:7` and `docs/adr/2026-09-14_backend-http-client-for-gemini.md:8` still read "🟡 pending approval" although the human approved both on 2026-09-14 (AGENT_LOG.md:68,70). Not a code issue; the orchestrator may want to update the headers.

---

## Board updates

Tester has no board permissions (`can_update_projects: false`); the following are suggestions for the human:

- Attach this test report (`docs/tests/2026-09-17_ai-suggestions-full.md`) as evidence when deciding the review outcomes for #21–#26.
- #21 (T-1) and #22 (T-2) — PR #27 merged to `main`; currently in `Review` → move to `Done`.
- #23 (T-3), #24 (T-4), #25 (T-5) — PR #29 merged to `main`; currently in `Review` → move to `Done`.
- #26 (T-6) — PR #28 merged to `main`; currently in `Review` → move to `Done`.
- NB-1 (array of non-strings → 500) remains open from the backend review (`docs/reviews/2026-09-14_ai-suggestions-backend_review.md`); the human may decide whether to file a follow-up issue or accept as-is.

---

**Approved by:** human  
**Approval date:** 2026-09-17  
**Next agent:** reviewer
