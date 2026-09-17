# Code review: AI ingredient suggestions — backend (T-1, T-2)

**Date:** 2026-09-14  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** T-1, T-2  
**Requirements:** `docs/requirements-ai-suggestions.md`  
**Implementation notes:** `docs/notes/2026-09-14_ai-suggestions-backend.md`  
**Test report:** `docs/tests/2026-09-14_ai-suggestions-backend.md`  
**Branch:** `feat/ai-ingredient-suggestions`  
**Status:** 🟡 pending human decision

---

## Review summary

Reviewed the backend implementation of the AI ingredient suggestions feature (T-1, T-2) against ADR-7, requirements FR-1..FR-4, NFR-1, NFR-4, and in-scope acceptance criteria AC-3, AC-4, AC-6. The implementation matches the ADR specification field-by-field: httpx dependency pinned correctly, per-request synchronous client, error handling contract implemented exactly, prompt construction follows the ADR pattern, model is `gemini-3.1-flash-lite` (D-10), pantry staples exclusion present (D-9). All ADR-7 guard rails respected. One non-blocking finding: a Gemini response containing an array of non-strings (e.g. `[1, 2, 3]`) would raise an uncaught `pydantic.ValidationError` resulting in HTTP 500 instead of the expected 502. The tester classified this as low likelihood due to the `responseSchema` constraint; this review agrees and classifies it as non-blocking. Zero blocking findings. Verdict: ✅ Approved — the merge decision belongs to the human.

---

## Scope reviewed

Reviewed completely (not just diffs):

- **Dependency** — `backend/requirements.txt` (4 lines total): `httpx==0.28.1` added as the sole change.
- **Endpoint** — `backend/app/routes/recipes.py` (162 lines total): `POST /recipes/suggest-ingredients` added at lines 56-107; existing CRUD endpoints unchanged.
- **Schemas** — `backend/app/schemas.py` (94 lines total): `SuggestIngredientsRequest` (lines 50-60) and `SuggestIngredientsResponse` (lines 63-64) added; existing schemas unchanged.
- **Tests** — `backend/tests/test_foodflow.py` (591 lines total): 9 new tests in lines 403-591; 32 pre-existing tests unchanged.
- **Branch diff** — `git diff main...feat/ai-ingredient-suggestions`: 5 files, +365/-5 lines. Three commits (`6b35a43`, `1a31e12`, `ffb91df`).
- **Docs** — `docs/requirements-ai-suggestions.md`, `docs/adr/2026-09-14_backend-http-client-for-gemini.md` (ADR-7), `docs/notes/2026-09-14_ai-suggestions-backend.md`, `docs/tests/2026-09-14_ai-suggestions-backend.md`, `AGENT_LOG.md` (D-9, D-10).

Could not be reviewed from code alone: a live call to the Gemini API with a real `GOOGLE_API_KEY`. All Gemini interaction is mocked. The human should verify end-to-end with a real key before final acceptance.

---

## Acceptance criteria cross-check

| AC | Tester status | Reviewer verification |
|---|---|---|
| AC-3 | ✅ Pass | ✅ Agrees. `recipes.py:67-71` reads `GOOGLE_API_KEY` via `os.environ.get().strip()`; missing or empty raises `HTTPException(503)`. `test_suggest_ingredients_503_when_key_missing` (`:447-454`) and `test_suggest_ingredients_503_when_key_whitespace_only` (`:457-464`) both assert 503 + correct detail. No httpx client is created before the key check — the 503 tests do not patch httpx, and a call attempt would fail the assertion. |
| AC-4 | ✅ Pass | ✅ Agrees. `recipes.py:92-107` catches `(httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError)` and raises `HTTPException(502)`. Four tests cover the ADR-7 error cases: `_502_on_gemini_http_error` (`:504-513`), `_502_on_network_error` (`:516-525`), `_502_on_malformed_body` (`:528-543`), `_502_on_unexpected_shape` (`:546-561`). Timeout is covered by the except clause (`httpx.TimeoutException` is a subclass of `httpx.HTTPError`, verified). |
| AC-6 | ✅ Pass | ✅ Agrees. `recipes.py:73` maps `"es"` to `"Spanish"`; `test_suggest_ingredients_prompt_and_request` (`:564-591`) asserts `"Spanish"` appears in the prompt text. The backend contract (language correctly passed to the prompt) is proven; actual Spanish output from Gemini requires a live call — see Scope reviewed. |

---

## Findings

### 🔴 Blocking

None.

### 🟡 Non-blocking

**NB-1** — `backend/app/routes/recipes.py:105`  
When Gemini returns a valid JSON array whose elements are not strings (e.g. `[1, 2, 3]`), `SuggestIngredientsResponse(suggestions=suggestions)` raises an uncaught `pydantic.ValidationError`, resulting in HTTP 500. The requirements edge case (`docs/requirements-ai-suggestions.md:126`) expects HTTP 502 for a malformed response. The `responseSchema` (`{"type": "ARRAY", "items": {"type": "STRING"}}`) instructs Gemini to return strings, making this edge case practically impossible. The tester classified this as low likelihood and not an ADR-7 deviation — this review agrees.  
**Fix (recommended):** Add `pydantic.ValidationError` to the except clause at `recipes.py:106`: `except (httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError, ValidationError)`.

### 🟢 Positive

**P-1** — `backend/app/routes/recipes.py:84-90`  
The `responseSchema` configuration (`"type": "ARRAY", "items": {"type": "STRING"}`) goes beyond the minimum required by the ADR and actively reduces parse errors by instructing Gemini to return only JSON arrays of strings. This is a well-chosen defense that aligns with both the ADR prompt construction guidance and D-10's model choice.

**P-2** — `backend/app/routes/recipes.py:101`  
The `KeyError` catch on the nested data access (`data["candidates"][0]["content"]["parts"][0]["text"]`) correctly handles missing or malformed Gemini response shapes, including the empirical edge case of a missing `candidates` key that the tester verified returns 502.

---

## Final recommendation

✅ **Approved** — Zero blocking findings. The implementation matches ADR-7 field-by-field, all in-scope acceptance criteria pass, all ADR-7 guard rails are respected, D-9 (pantry staples exclusion) and D-10 (`gemini-3.1-flash-lite`) are correctly implemented, and the branch diff contains exactly the files specified by the ADR with no scope creep. One non-blocking finding (NB-1) is noted for a future follow-up. The merge decision belongs to the human.

---

## Board updates

```text
Hold #21 ([AI suggestions] T-1) and #22 ([AI suggestions] T-2) in Review pending human merge decision of PR #27 (branch feat/ai-ingredient-suggestions) — evidence: zero blocking findings, 41 tests passed, docs/reviews/2026-09-14_ai-suggestions-backend_review.md (human applies the transition).
After merge: move #21 and #22 Review -> Done.
```

---

**Decision by:** ________________ *(human)*  
**Date:** ________________  
**Next step:** ✅ → documenter + merge · 🔄 → developer re-work · ⛔ → architect/human decision
