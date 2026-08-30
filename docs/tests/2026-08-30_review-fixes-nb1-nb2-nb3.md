# Test report: Review fixes NB-1, NB-2, NB-3

**Date:** 2026-08-30  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** Review fixes NB-1, NB-2, NB-3 (re-work of T-1..T-10)  
**Requirements:** `docs/requirements.md`  
**Implementation notes:** `docs/notes/2026-08-30_review-fixes-nb1-nb2-nb3.md`  
**Branch:** feat/meal-planner-core  
**Status:** 🟡 pending review

---

## Validation summary

Re-validated the review-fix commit `715aa5a` on `feat/meal-planner-core`. The committed 32-test suite in `backend/tests/` passes in full (32 passed, 0 failed, 0 skipped). NB-1 (whitespace-only recipe name → 422) and NB-2 (recipe uniqueness per plan per ADR-5) behave correctly in the code and are covered by committed tests; both were independently re-confirmed via a standalone TestClient script (17/17 checks passed). One test-suite soundness defect found: `test_four_table_schema` and `test_wal_and_busy_timeout_pragmas` use the collection-time engine bound to the default `data/foodflow.db` instead of the per-test isolated DB, so `test_four_table_schema` fails on a fresh checkout without that gitignored file.

---

## Scope tested

**Tested:** The committed pytest suite (`backend/tests/test_foodflow.py`, 32 tests) — AC-1..AC-6, all nine requirements edge cases, the ADR 404/422 error cases, the ADR-1 four-table schema, the ADR-4 pragmas, `remove_meal_ids` semantics, shopping list alphabetical sort, name-substring filter, plan delete, and the two new behaviors (whitespace-name rejection NB-1, duplicate-add dedupe NB-2). Independent TestClient verification of NB-1 (6 checks) and NB-2 (11 checks) against an isolated temp DB.  
**Not tested:** Browser-based UI interaction of the three views (Recipes, Plans, Shopping list) — no headless browser available; unchanged from the original validation. Frontend build and docker-compose deployment were not re-run in this pass — the fix commit `715aa5a` touches no frontend, docker, or CI files (verified via `git diff 95d9a89 715aa5a --stat`), so those layers are unchanged from the original validation. No linter is configured in the repository, so none was run.

---

## Acceptance criteria coverage

| AC | Status | Evidence |
|---|---|---|
| AC-1 | ✅ Pass | `test_ac1_create_list_read`, `test_ac1_update`, `test_ac1_delete` — create "Pasta Carbonara" with 4 ingredients, list shows name + count 4, read by id returns same name and list; partial update and delete verified. UI interaction not browser-tested (see Test gaps). |
| AC-2 | ✅ Pass | `test_ac2_shopping_list_dedup` — plan with "Pasta Carbonara" + "Caesar Salad" yields the 6 required ingredients with "cheese" once. |
| AC-3 | ✅ Pass | `test_ac3_multiple_plans_history` — "This week" and "Next week" coexist; "This week" retains its original meal. |
| AC-4 | ✅ Pass | `test_ac4_no_ingredients_tag` — "Plain Rice" has `ingredient_count == 0` in the plan and contributes nothing to the shopping list. Tag rendering not browser-tested (see Test gaps). |
| AC-5 | ✅ Pass | `test_ac5_concurrent_last_change_wins` — two writes to the same recipe; last write wins, no corruption. Two-browser scenario not browser-tested (see Test gaps). |
| AC-6 | ✅ Pass | `test_ac6_plan_edit_cascades` — removing "Caesar Salad" drops "lettuce"/"croutons" from the shopping list; the recipe still exists. |

---

## Edge case coverage

| Edge case / error case | Test | Result |
|---|---|---|
| Empty recipe base | `test_edge_empty_recipe_base` | PASS |
| Recipe with no ingredients | `test_edge_recipe_no_ingredients` | PASS |
| Duplicate ingredient names within a recipe | `test_edge_duplicate_ingredient_names` | PASS |
| Plan with no meals | `test_edge_plan_with_no_meals` | PASS |
| Shopping list from multiple plans | `test_edge_shopping_list_multiple_plans` | PASS |
| Editing a recipe that is in a plan | `test_edge_edit_recipe_in_plan` | PASS |
| Deleting a recipe that is in a plan | `test_edge_delete_recipe_in_plan` | PASS |
| Concurrent recipe edits | `test_edge_concurrent_recipe_edits` | PASS |
| Concurrent plan edits | `test_edge_concurrent_plan_edits` | PASS |
| ADR: 404 recipe not found (GET/PATCH/DELETE) | `test_404_recipe_not_found` | PASS |
| ADR: 404 plan not found (GET/PATCH/DELETE) | `test_404_plan_not_found` | PASS |
| ADR: 404 plan in shopping list | `test_404_plan_in_shopping_list` | PASS |
| ADR: 404 add-meal recipe not found | `test_404_add_meal_recipe_not_found` | PASS |
| ADR: 422 empty recipe name | `test_validation_empty_recipe_name` | PASS |
| ADR: 422 empty plan name | `test_validation_empty_plan_name` | PASS |
| ADR-1: four-table schema | `test_four_table_schema` | PASS (see Defects observed — isolation defect) |
| ADR-4: WAL / busy_timeout / foreign_keys pragmas | `test_wal_and_busy_timeout_pragmas` | PASS (see Defects observed — isolation defect) |
| Developer-flagged: `remove_meal_ids` uses recipe ids | `test_remove_meal_ids_uses_recipe_ids` | PASS |
| Developer-flagged: `remove_meal_ids` removes all occurrences | `test_remove_meal_ids_removes_all_occurrences` | PASS (name stale under ADR-5, see Test gaps) |
| Developer-flagged: shopping list alphabetical sort | `test_shopping_list_sorted_alphabetically` | PASS |
| Report scope: name-substring filter | `test_recipe_name_substring_filter` | PASS |
| Report scope: plan delete | `test_plan_delete` | PASS |
| **NB-1:** whitespace-only recipe name → 422 (create and update, stored name preserved) | `test_validation_whitespace_recipe_name` | PASS |
| **NB-2 / ADR-5:** duplicate recipe add silently deduped (200, appears once; dedupe within one `add_meals` list) | `test_add_meal_deduplicates_existing_recipe` | PASS |
| ADR-5: 404 plan not found on PATCH | `test_404_plan_not_found` | PASS |
| ADR-5: 404 `add_meals` id references nonexistent recipe | `test_404_add_meal_recipe_not_found` | PASS |
| ADR-5: 422 malformed request body | `test_validation_empty_plan_name` | PARTIAL — 422 exercised via empty plan name; no test for malformed `add_meals`/`remove_meal_ids` types (e.g., string instead of `list[int]`) |

---

## Result summary

- `python3 -m venv /tmp/opencode/tester-venv` → created (Python 3.14.4)
- `pip install -r backend/dev-requirements.txt` → installed (pytest 9.1.1, httpx 0.28.1, fastapi 0.115.6, SQLAlchemy 2.0.36, pydantic 2.13.5)
- `python -m pytest backend/tests -q` → 32 passed, 0 failed, 0 skipped (1616 deprecation warnings from fastapi/starlette internals on Python 3.14, not from the changed code)
- `FOODFLOW_DB_PATH=/tmp/opencode/collect-time.db python -m pytest backend/tests -q` (isolation probe) → 1 failed (`test_four_table_schema`), 31 passed — proves the two engine-based tests use the collection-time DB, not the per-test isolated DB
- Independent TestClient verification script (`/tmp/opencode/verify_nb1_nb2.py`, isolated temp DB) → 17/17 checks passed (NB-1: 6, NB-2: 11)

**Totals:** 32 passed · 0 failed · 0 skipped

---

## Defects observed

- `backend/tests/test_foodflow.py:14` (with `backend/tests/test_foodflow.py:275-292`) — **test-suite defect, not app code.** `test_four_table_schema` and `test_wal_and_busy_timeout_pragmas` use the module-level `engine` imported at collection time, which is bound to the default `data/foodflow.db` (gitignored, untracked), not to the per-test isolated DB the `client` fixture creates. The suite passes in this repo only because `data/foodflow.db` exists from a prior run. Proven: with `FOODFLOW_DB_PATH` set to an empty path at collection time, `test_four_table_schema` fails (1 failed, 31 passed). On a fresh checkout without the `data/` directory, the committed suite fails. This contradicts the isolation claim in `backend/tests/conftest.py:4-6` and the developer's note (`docs/notes/2026-08-30_review-fixes-nb1-nb2-nb3.md:31`). Expected: both tests should use the fixture's isolated DB (e.g., obtain the engine from the re-imported `app.db` inside the test, or drop the module-level import). `test_wal_and_busy_timeout_pragmas` passes even on a fresh file because the pragmas are applied per-connection by the connect listener, but it still opens the default DB as a side effect.

---

## Test gaps

- `test_four_table_schema` / `test_wal_and_busy_timeout_pragmas` are not isolated — they depend on the untracked `data/foodflow.db` existing at collection time (see Defects observed). The other 30 tests are isolated per the `client` fixture.
- ADR-5's "422 malformed request body" is only exercised via an empty plan name; a malformed `add_meals`/`remove_meal_ids` payload (wrong type) is not explicitly tested. Low risk — Pydantic rejects it the same way, but the specific contract case is untested.
- `test_remove_meal_ids_removes_all_occurrences` (`backend/tests/test_foodflow.py:308`) has a stale name: under ADR-5 a recipe appears at most once per plan, so "removes all occurrences" is no longer the semantics. The test itself is correct (it verifies dedupe of duplicate adds and single-meal removal); only the name is misleading.
- The original report's 29th test is not identifiable from `docs/tests/implementation-t1-t10.md` (only 28 tests are named there). The committed suite's 32 = 28 named + 2 scope tests (name-substring filter, plan delete) + 2 new behavior tests. The coverage of the unnamed 29th test cannot be confirmed as preserved.
- Browser-based UI interaction of the three views remains unvalidated — no headless browser available. The human should exercise in a real browser (mobile viewport): AC-1 create → list → read flow, AC-4 "no ingredients" tag rendering, AC-5 two-browser concurrent view, and plan edits updating the shopping list in the UI.
- Frontend build and docker-compose deployment were not re-run in this pass; the fix commit touches no frontend/docker/CI files, so those layers are unchanged from the original validation.
- `AGENT_LOG.md` does not exist in the repository (core-principles step 4 lists it as required reading); noted for the human, not blocking.

---

## Board updates

None — the reviewer consumes this report.

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** reviewer