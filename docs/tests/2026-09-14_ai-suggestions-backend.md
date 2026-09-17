# Test report: AI ingredient suggestions — backend (T-1, T-2)

**Date:** 2026-09-14  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** T-1, T-2  
**Requirements:** `docs/requirements-ai-suggestions.md`  
**Implementation notes:** `docs/notes/2026-09-14_ai-suggestions-backend.md`  
**Branch:** `feat/ai-ingredient-suggestions`  
**Status:** 🟡 pending review

---

## Validation summary

Validated the backend track of the AI ingredient suggestions feature (T-1, T-2) against FR-1..FR-4, NFR-1, NFR-4, AC-3, AC-4, AC-6, the ADR-7 error handling contract, and the requirements edge cases. Ran the full backend suite in a fresh venv from `backend/dev-requirements.txt`: 41 passed, 0 failed, 0 skipped (32 pre-existing + 9 new). All in-scope acceptance criteria pass. One minor defect observed: a Gemini response that is a valid JSON array of non-strings returns HTTP 500 instead of the required 502. A live Gemini call was NOT tested — no `GOOGLE_API_KEY` in this environment; the endpoint was exercised only through mocked httpx. That remains a manual check with a real key.

---

## Scope tested

**Tested:** `POST /recipes/suggest-ingredients` endpoint (`backend/app/routes/recipes.py:56-107`); `SuggestIngredientsRequest` / `SuggestIngredientsResponse` schemas (`backend/app/schemas.py:50-64`); `httpx==0.28.1` dependency (`backend/requirements.txt:4`); the 9 new tests in `backend/tests/test_foodflow.py:403-591`; OpenAPI registration; NFR-1 repo scan (no key in frontend or committed files); NFR-4 sync pattern by code inspection. Error paths exercised: missing key → 503, whitespace-only key → 503, validation → 422, success → 200, Gemini HTTP error → 502, network error → 502, malformed body → 502, unexpected shape → 502, missing `candidates` key → 502 (empirical probe), empty list → 200 (empirical probe).  
**Not tested:** A live call to the Gemini API — no `GOOGLE_API_KEY` in the environment; all Gemini interaction is mocked. Actual Spanish-language output from Gemini (the end-to-end half of AC-6) is therefore unverified. Frontend behaviors (AC-1, AC-2, AC-5, FR-5..FR-9) are out of scope — T-3..T-6 are not implemented.

---

## Acceptance criteria coverage

| AC | Status | Evidence |
|---|---|---|
| AC-3 | ✅ Pass | `test_suggest_ingredients_503_when_key_missing` (`backend/tests/test_foodflow.py:447-454`) and `test_suggest_ingredients_503_when_key_whitespace_only` (`:457-464`): 503 + detail `"AI suggestions are not configured"`. No Gemini call: the 503 raise at `recipes.py:68-71` precedes any httpx usage, and the 503 tests do not patch httpx — a call attempt would fail the assertion. |
| AC-4 | ✅ Pass | `test_suggest_ingredients_502_on_gemini_http_error` (`:504-513`), `_502_on_network_error` (`:516-525`), `_502_on_malformed_body` (`:528-543`), `_502_on_unexpected_shape` (`:546-561`): all return 502 + detail `"Failed to get AI suggestions"`. Timeout is covered by the except clause — `httpx.TimeoutException` is a subclass of `httpx.HTTPError` (verified). |
| AC-6 | ✅ Pass | `test_suggest_ingredients_prompt_and_request` (`:564-591`): with `language: "es"`, the prompt sent to Gemini contains `"Spanish"` (`recipes.py:73`). The backend contract (language passed to the prompt) is proven; actual Spanish output from Gemini requires a live call — see Test gaps. |

---

## Edge case coverage

| Edge case / error case | Test | Result |
|---|---|---|
| Empty recipe name → 422 | `test_suggest_ingredients_validation` (`test_foodflow.py:467-481`) | ✅ Pass |
| Whitespace-only recipe name → 422 | `test_suggest_ingredients_validation` (`:467-481`) | ✅ Pass |
| Invalid language (`fr`) → 422 | `test_suggest_ingredients_validation` (`:467-481`) | ✅ Pass |
| Missing `name` field → 422 | `test_suggest_ingredients_validation` (`:467-481`) | ✅ Pass |
| API key with extra whitespace → 503 | `test_suggest_ingredients_503_when_key_whitespace_only` (`:457-464`) | ✅ Pass |
| Gemini returns empty list → 200 `{"suggestions": []}` | No dedicated test; verified empirically (probe) + code inspection `recipes.py:102-105` | ✅ Pass |
| Gemini returns non-JSON text → 502 | `test_suggest_ingredients_502_on_malformed_body` (`:528-543`) | ✅ Pass |
| Gemini returns non-array JSON (object) → 502 | `test_suggest_ingredients_502_on_unexpected_shape` (`:546-561`) | ✅ Pass |
| Gemini returns array of non-strings → 502 | No test; empirical probe shows HTTP 500 (uncaught `pydantic.ValidationError` at `recipes.py:105`) | ❌ Fail — see Defects |
| ADR-7: network error (`httpx.ConnectError`) → 502 | `test_suggest_ingredients_502_on_network_error` (`:516-525`) | ✅ Pass |
| ADR-7: timeout (`httpx.TimeoutException`) → 502 | No dedicated test; covered by except clause `recipes.py:106` (`TimeoutException ⊂ HTTPError`, verified) | ✅ Pass |
| ADR-7: non-200 (`httpx.HTTPStatusError`) → 502 | `test_suggest_ingredients_502_on_gemini_http_error` (`:504-513`) | ✅ Pass |
| ADR-7: malformed body (`json.JSONDecodeError`) → 502 | `test_suggest_ingredients_502_on_malformed_body` (`:528-543`) | ✅ Pass |
| ADR-7: unexpected shape (`KeyError`, `TypeError`) → 502 | `test_suggest_ingredients_502_on_unexpected_shape` (`:546-561`, TypeError); KeyError verified empirically (missing `candidates` → 502) | ✅ Pass |
| Existing ingredients in edit mode (append, not replace) | Frontend behavior — out of scope (T-3..T-6) | not covered |
| Rapid repeated clicks (no duplicate request) | Frontend behavior — out of scope (T-3..T-6) | not covered |

---

## Result summary

- `python -m pytest backend/tests -q` (fresh venv, `backend/dev-requirements.txt`) → 41 passed, 0 failed, 0 skipped (2241 warnings — pre-existing fastapi/starlette deprecation warnings on Python 3.14, not from changed code)
- `python -m pytest backend/tests -q -k suggest_ingredients` → 9 passed, 32 deselected
- `python -m compileall backend/app backend/tests` → OK
- OpenAPI check → `POST /recipes/suggest-ingredients` registered; `SuggestIngredientsRequest` (name required, minLength 1; language enum `["en", "es"]`); `SuggestIngredientsResponse` (suggestions: array of strings, required)
- Empirical probes (mocked httpx): missing `candidates` key → 502 ✅; empty list → 200 `{"suggestions": []}` ✅; array of numbers → 500 ❌ (see Defects)

**Totals:** 41 passed · 0 failed · 0 skipped

---

## Defects observed

- `backend/app/routes/recipes.py:105` — when Gemini returns a valid JSON array whose elements are not strings (e.g. `[1, 2, 3]`), `SuggestIngredientsResponse(suggestions=suggestions)` raises an uncaught `pydantic.ValidationError` and the endpoint returns HTTP 500. The requirements edge case "Gemini returns non-JSON or malformed response: the backend returns HTTP 502" (`docs/requirements-ai-suggestions.md:126`) expects 502. The ADR-7 contract (`docs/adr/2026-09-14_backend-http-client-for-gemini.md:94`) lists only `(httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError)`, which the implementation matches exactly — so this is a gap between the requirements edge case and the ADR contract, not an ADR deviation. Low likelihood in practice (`responseSchema` instructs Gemini to return strings), but factual. Suggested fix (for the developer, not applied by the tester): validate element types or extend the except clause with `pydantic.ValidationError`.

---

## Test gaps

- **Live Gemini call NOT tested** — no `GOOGLE_API_KEY` in this environment; the endpoint was exercised only through mocked httpx. Manual check required with a real key: (1) a real request returns 200 with a `suggestions` array; (2) with `language: "es"` the suggestions are actually in Spanish (AC-6 end-to-end); (3) an invalid key returns 502 with `"Failed to get AI suggestions"`; (4) the real Gemini response shape matches `candidates[0].content.parts[0].text` as a JSON array.
- **Timeout path not exercised by a dedicated test** — `httpx.TimeoutException` is covered by the except clause (`recipes.py:106`, subclass of `httpx.HTTPError`, verified), but no test raises it explicitly.
- **Array-of-non-strings response → 500** — see Defects; no test covers it and the current behavior violates the requirements' malformed-response edge case.
- **Frontend behaviors out of scope** — AC-1, AC-2, AC-5, FR-5..FR-9 belong to T-3..T-6 (not implemented); this report covers the backend track only.
- **Documentation status headers stale** — `docs/requirements-ai-suggestions.md:7` and `docs/adr/2026-09-14_backend-http-client-for-gemini.md:8` still read "🟡 pending approval" although the human approved both on 2026-09-14 (AGENT_LOG.md:68,70). Not a code issue; the orchestrator may want to update the headers.

---

## Board updates

Tester has no board permissions (`can_update_projects: false`); the following are suggestions for the human:

- None required now — #21 (T-1) and #22 (T-2) are already in `Review` (moved by the developer with PR #27 linked). The human may attach this test report (`docs/tests/2026-09-14_ai-suggestions-backend.md`) as evidence when deciding the review outcome.

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** reviewer