# Implementation notes: FoodFlow core implementation (T-1..T-10)

**Date:** 2026-08-29  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** T-1, T-2, T-3, T-4, T-5, T-6, T-7, T-8, T-9, T-10  
**Branch:** none — no branch created and no commits made, per the human's instruction to only create files  
**ADR(s):** `docs/adr/2026-08-28_backend-layout-and-sqlite-schema.md`, `docs/adr/2026-08-28_frontend-tooling-and-api-integration.md`, `docs/adr/2026-08-28_container-topology-and-persistence-mount.md`, `docs/adr/2026-08-28_concurrency-mechanism-last-change-wins.md`  
**Status:** 🟡 pending review

---

## Summary

Implemented the full FoodFlow stack per ADR-1..ADR-4: a FastAPI + SQLAlchemy 2.0 backend over SQLite (four tables, WAL mode, busy timeout, atomic write transactions), a Vite + React + TypeScript mobile-first SPA with a typed API client and three views (recipes, plans, shopping list), and a single-container docker-compose deployment that builds the React app at image build time and serves it from FastAPI with the SQLite file persisted on a `./data` bind mount. All ten tasks (T-1..T-10) are implemented; the backend was verified with a 44-check API smoke test, the frontend with a production build, and the deployment with a real `docker compose up` including a container-recreation persistence check.

---

## Implementation per task

### T-1 — Scaffold FastAPI backend with SQLite persistence

Created `backend/app/` with `main.py` (FastAPI entry point, CORS for `http://localhost:5173` only, static SPA mount), `db.py` (SQLite engine, session factory, `init_db`, WAL + `busy_timeout=5000` + `foreign_keys=ON` pragmas per ADR-4), `models.py` (SQLAlchemy 2.0 declarative models), `schemas.py` (Pydantic request/response schemas), and `routes/`. The schema is exactly the four tables from ADR-1 (`recipes`, `recipe_ingredients`, `plans`, `plan_meals`) with the specified columns, `ON DELETE CASCADE` on both foreign keys of `plan_meals`, and indexes on `recipe_ingredients(recipe_id)`, `plan_meals(plan_id)`, `plan_meals(recipe_id)`. `created_at` defaults to UTC ISO-8601. The database file defaults to `<repo>/data/foodflow.db` (matches the ADR-3 bind mount) and is overridable via `FOODFLOW_DB_PATH`. Satisfies FR-1, FR-6, NFR-2; foundation for AC-1, AC-3, AC-5.

### T-2 — Implement recipe CRUD API

Created `backend/app/routes/recipes.py` with `POST /recipes` (name required non-empty, ingredients optional and may be empty), `GET /recipes` (list with optional `filter` name-substring query), `GET /recipes/{id}`, `PATCH /recipes/{id}` (partial update of name and/or ingredients), and `DELETE /recipes/{id}` (204; the DB-level `ON DELETE CASCADE` on `plan_meals.recipe_id` removes the recipe from every plan, FR-5). Duplicate ingredient names within a recipe are stored as provided. All persistence goes through the SQLAlchemy data layer; no hand-written SQL in route modules. Satisfies FR-1..FR-5, AC-1.

### T-3 — Implement meal plan API

Created `backend/app/routes/plans.py` with `POST /plans` (name required non-empty), `GET /plans` (all plans, including history, ordered by creation), `GET /plans/{id}`, `PATCH /plans/{id}` (optional `name`, `add_meals` as recipe ids, `remove_meal_ids`), and `DELETE /plans/{id}`. Plans are retained in history: creating or editing one plan never overwrites another (FR-7). Each meal in the response carries `recipe_id`, `name`, and `ingredient_count` per the ADR-2 `PlanMeal` interface. Assumption (ADR-2 does not define the semantics of `remove_meal_ids`): the field contains **recipe ids** — the backend removes every meal row whose `recipe_id` is in the list. This is the only interpretation consistent with the ADR-2 `PlanMeal` interface, which exposes `recipe_id` but no meal-row id, so the frontend cannot reference a `plan_meals` row id. Consequence: removing a meal removes all occurrences of that recipe in the plan. Satisfies FR-6, FR-7, FR-9, AC-3.

### T-4 — Implement shopping list generation API

Created `backend/app/routes/shopping_list.py` with `POST /shopping-list` taking `{plan_ids: number[]}` and returning `{ingredients: string[]}`. Ingredients are aggregated from the recipes of all meals in the selected plans and deduplicated by case-sensitive exact match (architecture.md:62). Empty plans and recipes without ingredients contribute nothing. Assumption (order is unspecified by the ADRs): the returned list is sorted alphabetically for deterministic output. Satisfies FR-8, AC-2, AC-6.

### T-5 — Scaffold React frontend with app shell

Created `frontend/` as a Vite + React + TypeScript SPA: `package.json`, `tsconfig.json`, `vite.config.ts`, `index.html`, `src/main.tsx`, `src/App.tsx` (app shell with three-view navigation via plain React state — no router), `src/api/` (typed client), and `src/styles/global.css` (plain CSS, mobile-first with a `min-width: 768px` media query). The API client exposes exactly the functions from ADR-2 (`listRecipes`, `getRecipe`, `createRecipe`, `updateRecipe`, `deleteRecipe`, `listPlans`, `getPlan`, `createPlan`, `updatePlan`, `deletePlan`, `generateShoppingList`) with the ADR-2 TypeScript interfaces in `src/api/types.ts`. The API base URL is read from a single constant in `src/api/client.ts`, sourced from `VITE_API_BASE_URL` (`.env.development` → `http://localhost:8000`; `.env.production` → empty, same-origin). Two files beyond the ADR-2 listing were required for the tooling to work: `src/vite-env.d.ts` (standard Vite client-types reference, required for `import.meta.env` to type-check) and the `.env.development`/`.env.production` files (the mechanism the guard rail's "single constant" reads from). Satisfies NFR-5 and the AC-1 recipe-list viewing portion.

### T-6 — Build recipe management UI

Created `frontend/src/views/RecipesView.tsx`: searchable recipe list (name-substring filter), create/edit form (name + dynamic ingredient rows, ingredients optional), delete with `window.confirm` confirmation, and ingredient-count display. Satisfies FR-1..FR-5, AC-1.

### T-7 — Build meal plan UI

Created `frontend/src/views/PlansView.tsx`: plan list (all plans including history), create plan, select a plan to view/edit its meals, add meals by selecting recipes from the base (checkbox picker), remove meals, delete plan with confirmation, and the "no ingredients" tag next to recipes with `ingredient_count === 0` in the plan's meal list (FR-10, AC-4). An empty recipe base shows an empty state prompting the user to create recipes first. Satisfies FR-6, FR-7, FR-9, FR-10, AC-3, AC-4.

### T-8 — Build shopping list UI

Created `frontend/src/views/ShoppingListView.tsx`: checkbox selection of one or more plans, deduplicated shopping list, empty states for no selection / no ingredients, and automatic refetch whenever the selection changes so the list reflects plan edits in real time (FR-8). Satisfies FR-8, AC-2, AC-6.

### T-9 — Add docker-compose deployment stack

Created `docker-compose.yml` (single service `foodflow`, port `8000:8000`, bind mount `./data:/app/data`), `backend/Dockerfile` (multi-stage: builds the React app from `frontend/` at image build time, then serves `dist` as static files from the FastAPI image; `FOODFLOW_STATIC_DIR=/app/static`, `FOODFLOW_DB_PATH=/app/data/foodflow.db`), and `frontend/Dockerfile` (standalone build stage for the React app producing `/app/dist`). `backend/app/main.py` mounts `StaticFiles` at `/` after the API routers so the SPA and API share one origin (no CORS in production). `data/` is gitignored. Note: `backend/Dockerfile` embeds the frontend build stage inline rather than referencing `frontend/Dockerfile` via `COPY --from`, because Docker cannot reference a stage across Dockerfiles; `frontend/Dockerfile` is provided as the canonical standalone build stage producing the same artifact. Satisfies NFR-1, NFR-2, NFR-3, AC-1 end-to-end.

### T-10 — Harden concurrent access (last change wins)

Implemented per ADR-4 in `backend/app/db.py` and the existing write paths: SQLite is opened with WAL mode (`PRAGMA journal_mode=WAL`) and `PRAGMA busy_timeout=5000` on every connection, so concurrent readers work with a single serialized writer and concurrent writers wait rather than fail. Every write endpoint (`POST`/`PATCH`/`DELETE` on recipes and plans) commits a single atomic SQLAlchemy transaction. No version columns, no ETags, no `409` handling, no WebSockets — plain last-write-wins as decided. The frontend simply refetches on view refresh (no client-side merge or conflict UI). Satisfies NFR-4, AC-5.

---

## Deviations from the ADR

None.

---

## Validation performed

- `pip install -r backend/requirements.txt` (Python 3.14.4 venv) → installed fastapi 0.115.6, uvicorn 0.34.0, SQLAlchemy 2.0.36, pydantic 2.13.5.
- Backend smoke test via FastAPI `TestClient` (44 checks covering AC-1..AC-6, FR-1, FR-3, FR-5, FR-8, FR-9, edge cases, 404s, WAL/busy_timeout pragmas, four-table schema) → ALL CHECKS PASSED.
- `npm install` in `frontend/` → 68 packages added; `package-lock.json` generated.
- `npm run build` in `frontend/` (`tsc && vite build`) → type-check clean; production bundle built (152.88 kB JS, 3.22 kB CSS).
- Production topology check: `uvicorn app.main:app` with `FOODFLOW_STATIC_DIR` pointing at `frontend/dist` → `GET /` serves the SPA (200 text/html), static assets served (200), API works same-origin, CORS preflight from `http://localhost:5173` → 200, from another origin → 400 (rejected).
- `docker build -f backend/Dockerfile -t foodflow:test .` → Successfully built.
- `docker compose up -d --build` → stack started; SPA served at `http://localhost:8000`; recipe created via API; `docker compose down` + `docker compose up -d` → recipe still present after container recreation (NFR-2 persistence verified).
- Not validated: no browser-based UI interaction test (no headless browser available); the tester agent should exercise the three views in a browser. No automated test suite is committed (requirements do not mandate one).

---

## Follow-up issues discovered

- No automated test suite exists in the repository; the validation smoke test used here lives in `/tmp` and is not committed. Candidate issue for planning: add a committed backend test suite (pytest + TestClient) so regressions are caught without re-running manual checks.
- `remove_meal_ids` semantics (recipe ids, not `plan_meals` row ids) is an interpretation of an ambiguity in ADR-2, documented in T-3 above. If the human wants single-occurrence removal of duplicate meals in a plan, the `PlanMeal` response contract would need a meal-row id field — that is an ADR change, not an implementation change.

---

## Board updates

```text
Move T-1 Scaffold FastAPI backend with SQLite persistence Ready -> In Progress — evidence: docs/notes/implementation-notes.md, backend/app/
Move T-2 Implement recipe CRUD API Ready -> In Progress — evidence: docs/notes/implementation-notes.md, backend/app/routes/recipes.py
Move T-3 Implement meal plan API Ready -> In Progress — evidence: docs/notes/implementation-notes.md, backend/app/routes/plans.py
Move T-4 Implement shopping list generation API Ready -> In Progress — evidence: docs/notes/implementation-notes.md, backend/app/routes/shopping_list.py
Move T-5 Scaffold React frontend with app shell Ready -> In Progress — evidence: docs/notes/implementation-notes.md, frontend/
Move T-6 Build recipe management UI Ready -> In Progress — evidence: docs/notes/implementation-notes.md, frontend/src/views/RecipesView.tsx
Move T-7 Build meal plan UI Ready -> In Progress — evidence: docs/notes/implementation-notes.md, frontend/src/views/PlansView.tsx
Move T-8 Build shopping list UI Ready -> In Progress — evidence: docs/notes/implementation-notes.md, frontend/src/views/ShoppingListView.tsx
Move T-9 Add docker-compose deployment stack Ready -> In Progress — evidence: docs/notes/implementation-notes.md, docker-compose.yml, backend/Dockerfile, frontend/Dockerfile
Move T-10 Harden concurrent access (last change wins) Ready -> In Progress — evidence: docs/notes/implementation-notes.md, backend/app/db.py
```

Note: the `In Progress -> Review` transition requires an open PR with tests run. No PR was opened because the human instructed not to commit; the transition is suggested once the human requests a commit/PR. The `Backlog -> Ready` transition for these items belongs to the planner (per `github-projects-policy.md:90`), not the developer.

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** tester (+ reviewer after)