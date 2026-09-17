# Code review: AI ingredient suggestions — full feature (T-1..T-6)

**Date:** 2026-09-17  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** T-1, T-2, T-3, T-4, T-5, T-6  
**Requirements:** `docs/requirements-ai-suggestions.md`  
**Implementation notes:** `docs/notes/2026-09-14_ai-suggestions-backend.md`, `docs/notes/2026-09-14_ai-suggestions-frontend.md`, `docs/notes/2026-09-15_ai-suggestions-devops.md`  
**Test report:** `docs/tests/2026-09-17_ai-suggestions-full.md`  
**Branch:** `main` (PRs #27, #28, #29 merged)  
**Status:** 🟡 pending human decision

---

## Review summary

Reviewed the merged AI ingredient suggestions feature (backend T-1/T-2, frontend T-3/T-4/T-5, devops T-6) on `main` against ADR-7, ADR-6, requirements FR-1..FR-9, NFR-1..NFR-4, AC-1..AC-6, and the requirements edge cases. The backend matches ADR-7 field-by-field (pinned `httpx==0.28.1`, per-request sync client, timeout 30.0, exact error contract, D-9 pantry-staples exclusion, D-10 model `gemini-3.1-flash-lite`, all guard rails respected). The frontend matches ADR-6 and NFR-2 (8 en/es i18n keys, no new npm dependencies, button + proposal UI in both create and edit modes, append-only-selected, 503/502 error mapping). The devops wiring satisfies NFR-1 (key never in frontend or committed; `.env` gitignored; compose config verified locally — key resolves, length 53, value not printed). The tester's claims cross-check against the code: 41 backend tests (9 new), frontend build, live Gemini results, and the NB-1 defect are all corroborated. Two non-blocking findings are carried or added: NB-1 (array of non-strings → HTTP 500, re-verified) and NB-2 (empty `candidates` array → uncaught `IndexError` → HTTP 500, same class as NB-1); plus one documentation inaccuracy NB-3 (README references a non-existent `env` section). Zero blocking findings. Verdict: ✅ Approved — the human decides on the follow-up findings.

---

## Scope reviewed

Reviewed completely (not just diffs):

- **Backend** — `backend/app/routes/recipes.py` (162 lines): `POST /recipes/suggest-ingredients` at lines 56-107; existing CRUD endpoints unchanged. `backend/app/schemas.py` (94 lines): `SuggestIngredientsRequest` (lines 50-60) and `SuggestIngredientsResponse` (lines 63-64). `backend/requirements.txt` (4 lines): `httpx==0.28.1` as the sole change. `backend/tests/test_foodflow.py` (591 lines): 9 new tests at lines 447-591; 32 pre-existing tests unchanged (41 total, verified by count).
- **Frontend** — `frontend/src/api/recipes.ts` (33 lines): `suggestIngredients` at lines 28-33. `frontend/src/api/types.ts` (31 lines): `SuggestIngredientsResponse` at lines 29-31. `frontend/src/i18n/translations.ts` (164 lines): 8 new en keys at lines 34-41 and 8 es keys at lines 114-121. `frontend/src/views/RecipesView.tsx` (354 lines): `handleSuggest` at lines 124-152, `addProposalIngredients` at lines 172-185, button + proposal UI at lines 229-279. `frontend/src/styles/global.css` (323 lines): `.suggest-*` styles at lines 236-270. `frontend/package.json`: unchanged (react/react-dom only, NFR-2).
- **Devops** — `docker-compose.yml` (16 lines): `environment: GOOGLE_API_KEY=${GOOGLE_API_KEY:-}` at lines 15-16. `.env.example` (3 lines): variable name only, no value. `README.md` (51 lines): "AI ingredient suggestions (optional)" section at lines 32-44.
- **Merged diffs** — PR #27 (`b6cffee`): 5 files, +365/-5. PR #28 (`41b3e1c`): 4 files, +87/-1. PR #29 (`d125581`): 6 files, +280/-1. All files are within the approved task scope.
- **Docs** — `docs/requirements-ai-suggestions.md`, `docs/adr/2026-09-14_backend-http-client-for-gemini.md` (ADR-7), `docs/adr/2026-09-08_frontend-i18n-mechanism.md` (ADR-6), the three implementation notes, `docs/tests/2026-09-17_ai-suggestions-full.md`, `docs/reviews/2026-09-14_ai-suggestions-backend_review.md`, `AGENT_LOG.md` (D-6..D-10).

Verified independently (not just trusted): NFR-1 repo scan (no `GOOGLE_API_KEY` / `generativelanguage` / `x-goog-api-key` / `AIza` in `frontend/`; key name only in `backend/app/routes/recipes.py` and `backend/tests/test_foodflow.py`; `.env` confirmed gitignored via `git check-ignore`); `docker compose config` parses and `GOOGLE_API_KEY` resolves non-empty (length 53, value not printed); exception-hierarchy check confirming `IndexError` is not caught by the except tuple at `recipes.py:106`.

Could not be reviewed from code alone: live browser interaction (button click, loading indicator, toggling, editing, appending, dismissing) — the repo has no headless browser or frontend test framework; the tester's report marks this as a manual check, and this review agrees. The live Gemini calls were performed by the tester with the real key and are accepted as evidence.

---

## Acceptance criteria cross-check

| AC | Tester status | Reviewer verification |
|---|---|---|
| AC-1 | ✅ Pass | ✅ Agrees. Button with `disabled={suggesting}` and loading text at `RecipesView.tsx:229-237`; editable proposal list at `:251-279`; `handleSuggest` (`:124-152`) sets `suggesting` for the request duration. The form is shared between create and edit modes (`:192-300`). Live browser interaction remains a manual check (no headless browser in the repo). |
| AC-2 | ✅ Pass | ✅ Agrees. `addProposalIngredients` (`RecipesView.tsx:172-185`) filters `item.selected` (`:174-177`), trims and drops blanks (`:176-177`), appends only the selected suggestions to `form.ingredients` (`:179-182`), then dismisses the proposal (`:184`). |
| AC-3 | ✅ Pass | ✅ Agrees. Backend 503 at `recipes.py:67-71` precedes any httpx usage (no Gemini call); tests `test_suggest_ingredients_503_when_key_missing` (`test_foodflow.py:447-454`) and `_503_when_key_whitespace_only` (`:457-464`). Frontend maps 503 → `recipes.error_suggest_not_configured` (`RecipesView.tsx:137-138`). The AC wording "no API call is made from the frontend that would result in a 503" is read as "no Gemini call is made" — the frontend cannot know the server-side key state (NFR-1), and the 503 is raised before httpx. |
| AC-4 | ✅ Pass | ✅ Agrees. `recipes.py:106-107` catches `(httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError)` → 502 with detail `"Failed to get AI suggestions"`. Tests cover HTTP error (`:504-513`), network error (`:516-525`), malformed body (`:528-543`), unexpected shape (`:546-561`). Frontend maps 502 → `recipes.error_suggest_failed` (`RecipesView.tsx:139-140`). Tester's live evidence (invalid key → 502; Gemini intermittent 503 → 502 twice) corroborates. |
| AC-5 | ✅ Pass | ✅ Agrees. `suggesting` set true at `RecipesView.tsx:131`, cleared in `finally` at `:150`; button `disabled={suggesting}` at `:233` — no duplicate request while in flight. |
| AC-6 | ✅ Pass | ✅ Agrees. `language_name = "Spanish"` at `recipes.py:73`; prompt at `:74-82`; test `test_suggest_ingredients_prompt_and_request` (`:564-591`) asserts `"Spanish"` in the prompt. Tester's live end-to-end call with `language: "es"` returned genuinely Spanish suggestions. |

---

## Findings

### 🔴 Blocking

None.

### 🟡 Non-blocking

**NB-1** — `backend/app/routes/recipes.py:105`  
When Gemini returns a valid JSON array whose elements are not strings (e.g. `[1, 2, 3]`), `SuggestIngredientsResponse(suggestions=suggestions)` raises an uncaught `pydantic.ValidationError`, resulting in HTTP 500. The requirements edge case (`docs/requirements-ai-suggestions.md:126`) expects HTTP 502 for a malformed response. The implementation matches the ADR-7 exception tuple exactly (`docs/adr/2026-09-14_backend-http-client-for-gemini.md:94`), so this is a gap between the requirements edge case and the ADR contract, not an ADR deviation. Carried from the previous backend review (`docs/reviews/2026-09-14_ai-suggestions-backend_review.md:54-56`); the tester re-verified it empirically on `main` (`docs/tests/2026-09-17_ai-suggestions-full.md:85`). Low likelihood in practice (`responseSchema` constrains Gemini to strings), but factual.  
**Fix:** Add `pydantic.ValidationError` to the except clause at `recipes.py:106`: `except (httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError, ValidationError)`.

**NB-2** — `backend/app/routes/recipes.py:101`  
When Gemini returns an empty `candidates` array (a documented response shape when a prompt is blocked by safety filters) or an empty `parts` array, `data["candidates"][0]["content"]["parts"][0]["text"]` raises an uncaught `IndexError`, resulting in HTTP 500 instead of the required 502. `IndexError` is a sibling of `KeyError` under `LookupError`, not a subclass, so the except tuple at `recipes.py:106` does not catch it (verified against the exception hierarchy). Same class as NB-1: the implementation matches the ADR-7 contract exactly, but the requirements edge case (`docs/requirements-ai-suggestions.md:126`) expects 502 for a malformed response. Not covered by the tester's suite — `test_suggest_ingredients_502_on_unexpected_shape` (`test_foodflow.py:546-561`) covers a non-array JSON object (TypeError) and the tester verified a missing `candidates` key (KeyError), but not an empty `candidates` array.  
**Fix:** Add `IndexError` to the except clause at `recipes.py:106`, or validate the response shape before indexing (e.g. check `data.get("candidates")` is a non-empty list).

**NB-3** — `README.md:42`  
The README states "docker-compose passes it to the container via the `env` section in `docker-compose.yml`", but the compose file uses the `environment` attribute (`docker-compose.yml:15-16`). `env` is not a valid Compose service attribute — the devops notes document this deviation (`docs/notes/2026-09-15_ai-suggestions-devops.md:35`), but the README was not updated to match. The instructions still work, but the reference is factually wrong and would confuse a reader looking for an `env` section.  
**Fix:** Change `README.md:42` to reference "the `environment` section in `docker-compose.yml`".

### 🟢 Positive

**P-1** — `backend/app/routes/recipes.py:84-90`  
The `responseSchema` configuration (`"type": "ARRAY", "items": {"type": "STRING"}`) goes beyond the minimum required by the ADR and actively reduces parse errors by instructing Gemini to return only JSON arrays of strings. Carried from the previous review; still valid on `main`.

**P-2** — `backend/app/routes/recipes.py:101`  
The `KeyError` catch on the nested data access correctly handles missing or malformed Gemini response shapes, including the empirical edge case of a missing `candidates` key that the tester verified returns 502. Carried from the previous review; still valid on `main`.

**P-3** — `frontend/src/views/RecipesView.tsx:136-143` + `frontend/src/i18n/translations.ts:40-41,120-121`  
The frontend error mapping satisfies FR-8 precisely: the English translations (`"AI suggestions are not configured"`, `"Failed to get AI suggestions"`) match the backend detail strings character-for-character (`recipes.py:70,107`), and the Spanish translations are faithful equivalents. The `ApiError` class (`client.ts:8-16`) carries the backend `detail` as the message, so the fallback branch (`RecipesView.tsx:142`) also surfaces the backend detail for unexpected statuses.

**P-4** — `frontend/src/views/RecipesView.tsx:67,81,96,292`  
The proposal and suggest-error state are cleared on every form reset path — save success (`:67-68`), edit load (`:81-82`), delete of the edited recipe (`:96-97`), and cancel (`:292-293`) — so a stale proposal never leaks across recipes. This matches the implementation note's claim and prevents a subtle state bug.

---

## Final recommendation

✅ **Approved** — Zero blocking findings. The merged implementation matches ADR-7 and ADR-6 field-by-field, all in-scope acceptance criteria (AC-1..AC-6) pass, all ADR-7 guard rails are respected, D-9 and D-10 are correctly implemented, NFR-1/NFR-2/NFR-3/NFR-4 are satisfied, the tester's claims cross-check against the code, and the merged diffs contain exactly the approved tasks with no scope creep. Three non-blocking findings remain: NB-1 (carried, re-verified) and NB-2 (new, same class) are requirements-vs-ADR gaps on malformed Gemini responses returning HTTP 500 instead of 502; NB-3 is a README documentation inaccuracy. The human decides whether to file a follow-up for NB-1/NB-2 or accept as-is.

---

## Board updates

```text
No transitions needed — #21, #22, #23, #24, #25, #26 are already in Done on Project 2 (verified 2026-09-17; all closed with state_reason "completed").
Attach this review report (docs/reviews/2026-09-17_ai-suggestions-full_review.md) and the test report (docs/tests/2026-09-17_ai-suggestions-full.md) as evidence for the completed items.
Optional follow-up (human decision): file a new issue for NB-1 + NB-2 (malformed Gemini response → HTTP 500 instead of 502 at backend/app/routes/recipes.py:101,105) and NB-3 (README.md:42 references the non-existent "env" section).
```

---

**Decision by:** human  
**Date:** 2026-09-17  
**Next step:** ✅ → documenter + merge · 🔄 → developer re-work · ⛔ → architect/human decision
