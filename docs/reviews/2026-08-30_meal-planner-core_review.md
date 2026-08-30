# Code review: Meal Planner Core (T-1..T-10)

**Date:** 2026-08-30  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** T-1..T-10  
**Requirements:** `docs/requirements.md`  
**Implementation notes:** `docs/notes/2026-08-30_review-fixes-nb1-nb2-nb3.md`  
**Test report:** `docs/tests/2026-08-30_review-fixes-nb1-nb2-nb3.md`  
**Branch:** feat/meal-planner-core  
**Status:** 🟡 pending human decision

---

## Review summary

This is the re-review of the FoodFlow core implementation (T-1..T-10) after the developer addressed the four findings of the initial review (`docs/reviews/2026-08-30_meal-planner-core_review.md`). All four findings are resolved: B-1 (the CI/infrastructure commits are no longer on `feat/meal-planner-core`), NB-1 (whitespace-only recipe names are rejected with 422), NB-2 (duplicate recipe adds are silently deduped per ADR-5), and NB-3 (the 32-test pytest suite is committed in `backend/tests/`). The committed suite passes in full (32 passed) in the normal run, with the collection-time isolation probe, and with the gitignored `data/` directory removed (fresh-checkout scenario). Two new non-blocking findings are recorded below (NB-4, NB-5). The browser-based UI behavior of AC-1, AC-4, and AC-5 still requires manual human confirmation.

---

## Scope reviewed

Reviewed completely (not just diffs):

- **Re-work commits** — `715aa5a` (NB-1, NB-2, NB-3), `074df28` (test isolation fix), `73950c1` (test report), and the full diff `95d9a89..73950c1`.
- **Backend** — `backend/app/schemas.py`, `routes/plans.py`, `routes/recipes.py`, `routes/shopping_list.py`, `db.py`, `models.py`, `main.py`, `dev-requirements.txt`.
- **Tests** — `backend/tests/conftest.py`, `backend/tests/test_foodflow.py` (32 tests).
- **Docs** — `docs/adr/2026-08-30_recipe-uniqueness-per-plan.md` (ADR-5), `docs/notes/2026-08-30_review-fixes-nb1-nb2-nb3.md`, `docs/tests/2026-08-30_review-fixes-nb1-nb2-nb3.md`, the ADR-2 supersession note, and the `docs/architecture.md` ADR-5 rows.
- **Branch history** — `git log --oneline main..feat/meal-planner-core`, `git diff main feat/meal-planner-core` (full branch diff), `git ls-tree` comparisons against `ci/opencode-review-workflow`, and ancestor checks for the six original CI commit hashes.

The committed test suite was re-run independently in a fresh venv (`pip install -r backend/dev-requirements.txt`, then `python -m pytest backend/tests -q`): 32 passed in the normal run, 32 passed with `FOODFLOW_DB_PATH` pointed at an empty path (isolation probe), and 32 passed with the `data/` directory removed (fresh-checkout scenario). An independent TestClient probe of NB-1, NB-2, and the ADR-5 malformed-body 422 cases passed 10/10.

Could not be reviewed from code alone: real browser-based UI interaction of the three views (Recipes, Plans, Shopping list) — unchanged from the initial review; no headless browser is available. The visual rendering of the "no ingredients" tag, the empty states, and the two-browser concurrent scenario require manual human confirmation. `AGENT_LOG.md` does not exist in the repository (also noted by the tester); this is a framework-level observation, not a defect of this re-work.

---

## Acceptance criteria cross-check

| AC | Tester status | Reviewer verification |
|---|---|---|
| AC-1 | ✅ Pass | ✅ Agrees at the API and build level. `test_ac1_create_list_read`, `test_ac1_update`, `test_ac1_delete` cover create → list → read → update → delete. The end-to-end browser interaction was not browser-tested; the UI portion needs manual confirmation. |
| AC-2 | ✅ Pass | ✅ Agrees. `test_ac2_shopping_list_dedup` verifies the 6 required ingredients with "cheese" appearing once. |
| AC-3 | ✅ Pass | ✅ Agrees. `test_ac3_multiple_plans_history` verifies "This week" and "Next week" coexist and retain their own meal lists. |
| AC-4 | ✅ Pass | ✅ Agrees at the data level. `test_ac4_no_ingredients_tag` verifies `ingredient_count == 0` and an empty shopping-list contribution. The visual rendering of the tag was not browser-tested; needs manual confirmation. |
| AC-5 | ✅ Pass | ✅ Agrees at the data layer. `test_ac5_concurrent_last_change_wins` verifies last-write-wins with no corruption. The actual two-browser scenario was not browser-tested; needs manual confirmation. |
| AC-6 | ✅ Pass | ✅ Agrees. `test_ac6_plan_edit_cascades` verifies removing a meal drops its ingredients from the shopping list while the recipe remains in the base. |

---

## Findings

### Re-review outcome of the original findings

| Finding | Status | Verification |
|---|---|---|
| B-1 — CI/infrastructure commits on the PR branch | ✅ Resolved | `git log --oneline main..feat/meal-planner-core` shows only `95d9a89` (implementation), `715aa5a` (review fixes), `074df28` (isolation fix), `73950c1` (test report). The CI commits now live on `ci/opencode-review-workflow` (`df866e2`, `6085323`, `50f48f1`, `3fdac42`, `8e80fec`, `3ff2de0`, `240a2cb`). The CI files still present on the feature branch (`.github/workflows/opencode-review.yml`, `.opencode/agent/*`) are byte-identical to main's versions (`git diff main feat/meal-planner-core -- <ci files>` is empty); the INFRA-1 additions (`.opencode/agent/ci-review.md`, `docs/notes/2026-08-29_opencode-review-google-ai-studio.md`) are absent from the feature branch. All six original CI commit hashes (`e2948c5`, `11ee89c`, `31a5b44`, `c741dc5`, `7e0c40e`, `8573b99`) are confirmed not ancestors of the feature branch. The full branch diff `main..feat` contains only FoodFlow implementation, docs, and tests. |
| NB-1 — whitespace-only recipe names accepted | ✅ Resolved | `backend/app/schemas.py:10-20` (`RecipeCreate`) and `:27-33` (`RecipeUpdate`) reject names where `name.strip() == ""` with 422. Verified by `test_validation_whitespace_recipe_name` and an independent probe (create 422, update 422, stored name preserved, non-blank names with surrounding spaces still accepted). |
| NB-2 — recipe uniqueness per plan | ✅ Resolved | `backend/app/routes/plans.py:63-78` silently skips `add_meals` ids already present in the plan, dedupes within a single list, and preserves the 404 for nonexistent recipes. Matches ADR-5 exactly; all guard rails respected (no `meal_id` field, no `UNIQUE` constraint, no 409, `PlanMeal` shape unchanged). Verified by `test_add_meal_deduplicates_existing_recipe` and an independent probe. |
| NB-3 — no committed test suite | ✅ Resolved | `backend/tests/conftest.py` (per-test isolated DB fixture) and `backend/tests/test_foodflow.py` (32 tests) are committed; `backend/dev-requirements.txt` added. Suite passes: 32 passed in the normal run, with the collection-time isolation probe, and with the gitignored `data/` directory removed (fresh-checkout scenario). |

### 🔴 Blocking

None.

### 🟡 Non-blocking

**NB-4** — `docs/adr/2026-08-30_recipe-uniqueness-per-plan.md:8` (also `docs/architecture.md:100,112`)  
ADR-5 is recorded as "🔄 proposed" in the ADR file and in both `docs/architecture.md` ADR tables, but the human has approved it (per the re-work direction). The implementation matches ADR-5's content exactly, so this is a record-keeping staleness, not an implementation deviation.  
**Fix:** Update the ADR-5 status field to "✅ approved" with the approval date, and update the two `docs/architecture.md` ADR tables to match.

**NB-5** — `backend/tests/test_foodflow.py`  
ADR-5's "422 — malformed request body" error case is only exercised via an empty plan name (`test_validation_empty_plan_name`); a wrong-typed `add_meals`/`remove_meal_ids` payload (e.g., a string instead of `list[int]`) is not covered by a committed test. The behavior is correct — an independent probe confirmed Pydantic rejects both with 422 — so this is a coverage gap, not a code defect.  
**Fix:** Add a test asserting 422 for a malformed `add_meals`/`remove_meal_ids` payload (e.g., `{"add_meals": "not-a-list"}` and `{"remove_meal_ids": ["a"]}`).

### 🟢 Positive

**P-1** — `backend/tests/test_foodflow.py:273-298`  
The developer fixed the tester's isolation defect in a follow-up commit (`074df28`) before the re-review: `test_four_table_schema` and `test_wal_and_busy_timeout_pragmas` now import `app.db` inside the test instead of using the collection-time module-level engine. The fix is correct — the suite passes with the `data/` directory removed and with `FOODFLOW_DB_PATH` pointed at an empty path — and the stale test name `test_remove_meal_ids_removes_all_occurrences` was renamed to `test_remove_meal_ids_removes_single_meal` with an added cross-plan assertion, matching ADR-5 semantics.

---

## Final recommendation

✅ **Approved** — All four original findings (B-1, NB-1, NB-2, NB-3) are resolved, the committed 32-test suite passes in the normal, isolation-probe, and fresh-checkout runs, and the re-work introduces no blocking issues. The two new non-blocking findings (NB-4, NB-5) do not prevent merge; the human decides.

---

## Board updates

```text
Move T-1..T-10 Review -> Done after the human merges PR #1 (branch feat/meal-planner-core) — evidence: all four review findings resolved, backend/tests/ suite 32 passed in normal + fresh-checkout runs (human applies the transition).
The INFRA-1 CI workflow work remains tracked separately on ci/opencode-review-workflow and is not part of PR #1.
```

---

**Decision by:** ________________ *(human)*  
**Date:** ________________  
**Next step:** ✅ → documenter + merge · 🔄 → developer re-work · ⛔ → architect/human decision