# Code review: Meal Planner Core (T-1..T-10)

**Date:** 2026-08-30  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** T-1..T-10  
**Requirements:** `docs/requirements.md`  
**Implementation notes:** `docs/notes/implementation-notes.md`  
**Test report:** `docs/tests/implementation-t1-t10.md`  
**Branch:** feat/meal-planner-core  
**Status:** 🟡 pending human decision

---

## Review summary

The FoodFlow core implementation (T-1..T-10) follows ADR-1..ADR-4 closely: the four-table SQLite schema, the FastAPI REST contracts, the Vite/React/TypeScript SPA, and the single-container docker-compose deployment all match the approved architecture. The tester's 29/29 pass is consistent with the code for the backend, build, and deployment layers. One blocking finding: the PR branch `feat/meal-planner-core` also carries six commits of unrelated CI/infrastructure work (INFRA-1, the `opencode-review` GitHub Actions provider swap) that are not in the requirements, plan, or any ADR — scope creep on the PR. The browser-based UI behavior of AC-1, AC-4, and AC-5 could not be verified from code alone and needs manual human confirmation.

---

## Scope reviewed

Reviewed completely (not just diffs):

- **Backend** — `backend/app/main.py`, `db.py`, `models.py`, `schemas.py`, `routes/recipes.py`, `routes/plans.py`, `routes/shopping_list.py`, `requirements.txt`, `backend/Dockerfile`.
- **Frontend** — `frontend/src/App.tsx`, `main.tsx`, `api/client.ts`, `api/recipes.ts`, `api/plans.ts`, `api/shoppingList.ts`, `api/types.ts`, `views/RecipesView.tsx`, `views/PlansView.tsx`, `views/ShoppingListView.tsx`, `styles/global.css`, `package.json`, `tsconfig.json`, `vite.config.ts`, `index.html`, `.env.development`, `.env.production`, `vite-env.d.ts`, `frontend/Dockerfile`.
- **Deployment** — `docker-compose.yml`, `.gitignore`.
- **Docs** — `docs/notes/implementation-notes.md`, `docs/tests/implementation-t1-t10.md`.

Could not be reviewed from code alone: real browser-based UI interaction of the three views (Recipes, Plans, Shopping list). The tester and developer both flagged that no headless browser was available; the views were verified only at the API and build level. The visual rendering of the "no ingredients" tag, the empty states, and the two-browser concurrent scenario therefore require manual human confirmation.

Also reviewed the full branch diff `main...feat/meal-planner-core`, which revealed the CI/infrastructure commits described in the blocking finding below.

---

## Acceptance criteria cross-check

| AC | Tester status | Reviewer verification |
|---|---|---|
| AC-1 | ✅ Pass | ✅ Agrees at the API and build level. `routes/recipes.py:27-90` implements create/list/read/update/delete; `RecipesView.tsx` implements the UI. The end-to-end browser interaction (create → see in list → read by id) was not browser-tested; the UI portion needs manual confirmation. |
| AC-2 | ✅ Pass | ✅ Agrees. `shopping_list.py:23-30` aggregates and deduplicates via a set; `plans.py` builds the meal list. The returned content matches the required 6 ingredients with "cheese" once. |
| AC-3 | ✅ Pass | ✅ Agrees. `plans.py:40-43` lists all plans (history retained); creating/editing one plan never overwrites another. |
| AC-4 | ✅ Pass | ✅ Agrees at the data level. `PlansView.tsx:161-163` renders the "no ingredients" tag when `ingredient_count === 0`; `shopping_list.py` contributes nothing for empty-ingredient recipes. The visual rendering of the tag was not browser-tested; needs manual confirmation. |
| AC-5 | ✅ Pass | ✅ Agrees at the data layer. `db.py:34-46` enables WAL, `busy_timeout=5000`, and `foreign_keys=ON`; writes commit atomically. The actual two-browser scenario was not browser-tested; needs manual confirmation. |
| AC-6 | ✅ Pass | ✅ Agrees. The shopping list is computed at request time from current recipe state (`shopping_list.py`), so removing a meal drops its ingredients; the recipe itself remains in the base. |

---

## Findings

### 🔴 Blocking

**B-1** — `.github/workflows/opencode-review.yml`, `.opencode/agent/ci-review.md`, `docs/notes/2026-08-29_opencode-review-google-ai-studio.md` (commits `e2948c5`, `11ee89c`, `31a5b44`, `c741dc5`, `7e0c40e`, `8573b99`)  
The PR branch `feat/meal-planner-core` carries six commits of CI/infrastructure work (INFRA-1 — switching the `opencode-review` GitHub Actions workflow to Google AI Studio and adding a non-interactive `ci-review` agent) in addition to the FoodFlow implementation commit `95d9a89`. This work is not in `docs/requirements.md`, `docs/implementation-plan.md`, or any ADR; it has its own notes file marked "🟡 pending review" with no ADR and no human approval. Bundling unrelated, unapproved infrastructure changes into the FoodFlow PR is scope creep on the branch.  
**Fix:** Remove the CI/infrastructure commits from the `feat/meal-planner-core` branch (e.g., rebase the branch onto `95d9a89` or move the INFRA-1 work to a separate branch/PR) so PR #1 contains only the FoodFlow implementation. The INFRA-1 work should be tracked and reviewed as its own task with its own approval gate.

### 🟡 Non-blocking

**NB-1** — `backend/app/schemas.py:7`  
A recipe name of only whitespace (e.g., `"   "`) is accepted (HTTP 201) because `min_length=1` counts a whitespace string as length ≥ 1. FR-1 (`docs/requirements.md:49`) requires a "non-empty" name. The tester flagged this as an observation, not a confirmed defect, because a whitespace string is non-empty by length. The human decides whether to tighten validation.  
**Fix:** If the human wants whitespace-only names rejected, strip the name and re-check non-emptiness (e.g., a Pydantic validator that rejects names where `name.strip() == ""`).

**NB-2** — `backend/app/routes/plans.py:73-77`  
The `remove_meal_ids` field is interpreted as **recipe ids**, so removing a meal removes every occurrence of that recipe in the plan. This is a documented assumption (`docs/notes/implementation-notes.md:31`) arising from an ambiguity in ADR-2: the `PlanMeal` interface exposes `recipe_id` but no meal-row id, so the frontend cannot reference a `plan_meals` row id. The interpretation is consistent with the ADR-2 interface, but the consequence (all occurrences removed) may not match user expectations if a plan can contain the same recipe more than once. The human decides whether this behavior is acceptable.  
**Fix:** If single-occurrence removal is required, this is an ADR change (add a meal-row id to the `PlanMeal` response contract and reference it in `remove_meal_ids`), not an implementation change. Otherwise, document the all-occurrences behavior as the accepted semantics.

**NB-3** — No committed automated test suite  
The 29-test pytest suite that produced `docs/tests/implementation-t1-t10.md` lives in `/tmp` and is not committed to the repository. The requirements and implementation plan do not mandate automated tests, so this is not a blocking defect, but it leaves the implementation without regression protection. Both the developer and tester flagged this as a follow-up candidate.  
**Fix:** Add a committed pytest + FastAPI `TestClient` suite (e.g., `backend/tests/`) covering the ACs and error cases, as a follow-up task for planning.

### 🟢 Positive

**P-1** — `backend/app/db.py:34-46`  
The WAL mode, `busy_timeout=5000`, and `foreign_keys=ON` pragmas are applied on every connection via a SQLAlchemy `connect` event listener, which correctly implements ADR-4's write serialization and makes `ON DELETE CASCADE` (required by FR-5) work reliably. This is a clean, correct realization of the concurrency decision.

**P-2** — `frontend/src/views/ShoppingListView.tsx:30-54`  
The shopping list refetch effect uses a `cancelled` flag to guard against stale responses when the plan selection changes rapidly, and correctly handles the empty-selection case. This is a correct, race-safe implementation of the "list reflects plan edits in real time" requirement (FR-8).

---

## Final recommendation

🔄 **Changes requested** — The FoodFlow implementation itself matches the ADRs and passes the tester's suite, but the PR branch carries unrelated, unapproved CI/infrastructure commits (B-1), which is blocking scope creep. The developer must remove those commits from the branch before the human can merge.

---

## Board updates

```text
Hold T-1..T-10 in Review pending the developer removing the INFRA-1 CI commits from feat/meal-planner-core (B-1).
After B-1 is resolved and the human re-reviews, move T-1..T-10 Review -> Done (human applies the transition).
The INFRA-1 CI workflow work should be tracked as its own item and reviewed separately, not bundled into PR #1.
```

---

**Decision by:** ________________ *(human)*  
**Date:** ________________  
**Next step:** ✅ → documenter + merge · 🔄 → developer re-work · ⛔ → architect/human decision
