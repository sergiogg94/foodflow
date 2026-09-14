# Implementation notes: AI ingredient suggestions — backend (T-1, T-2)

**Date:** 2026-09-14  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** T-1, T-2  
**Branch:** `feat/ai-ingredient-suggestions`  
**ADR(s):** `docs/adr/2026-09-14_backend-http-client-for-gemini.md`  
**Status:** 🟡 pending review

---

## Summary

Implemented the backend track of the AI ingredient suggestions feature per ADR-7: added the pinned `httpx==0.28.1` dependency to `backend/requirements.txt` (T-1) and added the `POST /recipes/suggest-ingredients` endpoint (T-2) that reads `GOOGLE_API_KEY` from the environment, calls the Gemini API (`gemini-3.1-flash-lite`, per D-10) synchronously with a per-request `httpx.Client(timeout=30.0)`, and returns `{"suggestions": [...]}`. The endpoint returns HTTP 503 with detail `"AI suggestions are not configured"` when the key is missing or empty (FR-2) and HTTP 502 with detail `"Failed to get AI suggestions"` on any Gemini failure (FR-4). The prompt includes the recipe name, the requested output language, a JSON-array-only instruction, and the D-9 instruction to exclude pantry staples and return only main ingredients for a weekly shopping list.

---

## Implementation per task

### T-1 — Add HTTP client dependency to backend requirements

Added `httpx==0.28.1` to `backend/requirements.txt` (the only change to that file, per ADR-7). The five transitive dependencies (`httpcore`, `h11`, `certifi`, `idna`, `sniffio`) install automatically. Satisfies FR-3 (HTTP client for the Gemini call), NFR-4 (sync client aligns with the existing sync route pattern), AC-4 (typed httpx exceptions map to the 502 contract).

### T-2 — Implement `POST /recipes/suggest-ingredients` endpoint with Gemini integration

- `backend/app/schemas.py` — added `SuggestIngredientsRequest` (`name`: required, non-blank via `field_validator`; `language`: required, `Literal["en", "es"]`) and `SuggestIngredientsResponse` (`suggestions: list[str]`), following the existing `*Request`/`*Read` naming pattern (FR-1).
- `backend/app/routes/recipes.py` — added the `POST /recipes/suggest-ingredients` endpoint on the existing recipe router:
  - Reads `GOOGLE_API_KEY` via `os.environ.get("GOOGLE_API_KEY", "").strip()`; missing or empty → HTTP 503 `"AI suggestions are not configured"` (FR-2, AC-3). The check happens before any httpx client is created (ADR-7).
  - Builds the prompt with the recipe name, the requested output language ("English"/"Spanish"), an instruction to return only a JSON array of ingredient name strings, and the D-9 instruction (exclude pantry staples such as salt, oil, spices; only main ingredients that would commonly go on a weekly shopping list) (FR-3, D-9).
  - Calls Gemini via `httpx.Client(timeout=30.0)` in sync mode at `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent` (D-10), with `x-goog-api-key` header, `responseMimeType: application/json`, and `responseSchema` array-of-strings (ADR-7 usage pattern).
  - Parses `candidates[0].content.parts[0].text` as JSON into the `suggestions` list and returns `SuggestIngredientsResponse` (FR-3). A parsed body that is not a JSON array raises `TypeError`, mapping "unexpected shape" to 502 per the ADR-7 error handling contract.
  - Catches `(httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError)` in a single block → HTTP 502 `"Failed to get AI suggestions"` (FR-4, AC-4). No raw Gemini error details are exposed (ADR-7 guard rail).
  - Sync function pattern (NFR-4); no async, no retry, no Google SDK, no streaming, no module-level client (ADR-7 guard rails).
- `backend/tests/test_foodflow.py` — added a new section with 9 tests for the endpoint using the existing TestClient + `client` fixture pattern, with a fake `httpx.Client`/`httpx.Response` injected via `monkeypatch`: 503 when the key is missing, 503 when the key is whitespace-only, 422 validation (blank name, whitespace name, invalid language, missing field), 200 success, 502 on Gemini HTTP error, 502 on network error, 502 on malformed body, 502 on unexpected shape, and a prompt/request-shape assertion (recipe name, Spanish output, pantry-staples rule, `responseMimeType`, `responseSchema`, `x-goog-api-key` header, model URL).

Satisfies FR-1, FR-2, FR-3, FR-4, NFR-1 (key stays server-side), NFR-4, AC-3, AC-4, AC-6 (language passed to the prompt).

---

## Deviations from the ADR

None.

---

## Validation performed

- `python -m compileall backend/app backend/tests` → OK, no syntax errors.
- `python -m pytest backend/tests -q` (fresh venv, `backend/dev-requirements.txt`) → **41 passed, 0 failed, 0 skipped** (32 pre-existing + 9 new). Warnings are pre-existing fastapi/starlette deprecation warnings on Python 3.14, not from changed code.
- App import + OpenAPI check: `POST /recipes/suggest-ingredients` registered; `SuggestIngredientsRequest` (name required minLength 1, language enum `["en", "es"]`) and `SuggestIngredientsResponse` (suggestions array of strings) present in the schema.
- Not validated: a real call to the Gemini API (no `GOOGLE_API_KEY` in this environment; the endpoint is exercised through mocked httpx). The tester should verify a live call with a real key.

---

## Follow-up issues discovered

- None.

---

## Board updates

```text
Move #21 ([AI suggestions] T-1) Ready -> In Progress — evidence: branch feat/ai-ingredient-suggestions, ADR-7 approved
Move #22 ([AI suggestions] T-2) Ready -> In Progress — evidence: branch feat/ai-ingredient-suggestions, ADR-7 approved
Move #21 ([AI suggestions] T-1) In Progress -> Review — evidence: PR <url> (branch feat/ai-ingredient-suggestions), tests run (41 passed)
Move #22 ([AI suggestions] T-2) In Progress -> Review — evidence: PR <url> (branch feat/ai-ingredient-suggestions), tests run (41 passed)
Set Linked PR on #21 and #22 — evidence: PR <url>
```

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** tester (+ reviewer after)