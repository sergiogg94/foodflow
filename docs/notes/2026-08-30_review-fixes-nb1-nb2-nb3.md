# Implementation notes: Review fixes NB-1, NB-2, NB-3

**Date:** 2026-08-30  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** Review fixes NB-1, NB-2, NB-3 (re-work of T-1..T-10)  
**Branch:** feat/meal-planner-core  
**ADR(s):** `docs/adr/2026-08-30_recipe-uniqueness-per-plan.md` (ADR-5)  
**Status:** 🟡 pending review

---

## Summary

Addressed the three non-blocking findings of `docs/reviews/2026-08-30_meal-planner-core_review.md` on the FoodFlow core implementation: whitespace-only recipe names are now rejected with 422 (NB-1), `update_plan` silently deduplicates `add_meals` so each recipe appears at most once per plan per ADR-5 (NB-2), and the previously `/tmp`-only pytest suite is committed to `backend/tests/` with 32 tests covering AC-1..AC-6, the requirements edge cases, the ADR-1/ADR-4 error cases, and the two new behaviors (NB-3). No schema change, no `PlanMeal` shape change, and no frontend or CI changes were made.

---

## Implementation per task

### NB-1 — Reject whitespace-only recipe names

`backend/app/schemas.py` — added a Pydantic v2 `field_validator` (`name_not_blank`) on `RecipeCreate.name` and `RecipeUpdate.name` that raises `ValueError` when `name.strip() == ""`, producing HTTP 422. `min_length=1` still rejects truly empty strings. The stored value is preserved as provided; only whitespace-only input is rejected, so the read path is unchanged. Satisfies FR-1 ("non-empty" name) and the human's decision to reject whitespace-only names.

### NB-2 — Recipe uniqueness per plan (ADR-5)

`backend/app/routes/plans.py` — `update_plan` now computes the set of recipe ids already in the plan before processing `add_meals`. For each id: a nonexistent recipe returns 404 naming the missing recipe (unchanged); an id already present in the plan is silently skipped (no duplicate, no error); otherwise the meal is appended at the end. The `existing_recipe_ids` set is updated as meals are appended, so duplicates within a single `add_meals` list are also deduped. `remove_meal_ids` semantics are unchanged (recipe ids; each removes the single matching meal; ids not present ignored). Per ADR-5 guard rails: no `meal_id`/row-id field added, no `UNIQUE(plan_id, recipe_id)` constraint or schema change, no 409, `PlanMeal` response shape unchanged.

### NB-3 — Commit the automated test suite to `backend/tests/`

Created `backend/tests/conftest.py` (a `client` fixture that re-imports the app per test against a fresh temp SQLite file via `FOODFLOW_DB_PATH`, giving each test an isolated database) and `backend/tests/test_foodflow.py` with 32 tests: the 28 tests named in `docs/tests/implementation-t1-t10.md` (AC-1..AC-6, all nine requirements edge cases, the ADR 404/422 error cases, the four-table schema, the WAL/busy_timeout/foreign_keys pragmas, `remove_meal_ids` semantics, shopping list alphabetical sort), two additional tests covering the report's scope section (name-substring filter, plan delete), and two new tests for the new behaviors: `test_validation_whitespace_recipe_name` (whitespace-only name → 422 on create and update, stored name preserved) and `test_add_meal_deduplicates_existing_recipe` (duplicate add silently deduped, 200, recipe appears once). Added `backend/dev-requirements.txt` (`-r requirements.txt` + `pytest==9.1.1` + `httpx==0.28.1`) so the suite is runnable without adding test tooling to the production image (the Dockerfile installs `requirements.txt` only).

---

## Deviations from the ADR

None.

---

## Validation performed

- `/tmp/opencode/foodflow-venv/bin/python -m pytest backend/tests` → 32 passed, 0 failed, 0 skipped (Python 3.14.4, pytest 9.1.1, fastapi 0.115.6, SQLAlchemy 2.0.36, pydantic 2.13.5). Deprecation warnings only, from fastapi/starlette internals on Python 3.14, not from the changed code.
- Manual check of the two new behaviors via the suite: whitespace-only recipe name → 422; duplicate recipe add to a plan → 200 with the recipe appearing once.
- Not validated: browser-based UI interaction (unchanged from the original implementation; no headless browser available).

---

## Follow-up issues discovered

None.

---

## Board updates

```text
Move T-1..T-10 In Progress -> Review — evidence: PR #1 (branch feat/meal-planner-core, commit addressing NB-1, NB-2, NB-3), backend/tests/ suite 32 passed
```

Note: the `In Progress -> Review` transition requires an open PR with tests run; PR #1 is already open on `feat/meal-planner-core` and the suite has run. The human applies the transition per `github-projects-policy.md`.

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** tester (+ reviewer after)