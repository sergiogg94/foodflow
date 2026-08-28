# Implementation plan: FoodFlow — Weekly Meal Planner

**Date:** 2026-08-28  
**Project:** FoodFlow  
**Requested by:** human  
**Requirements:** `docs/requirements.md`  
**Status:** ✅ approved

---

## Planning summary

The work is sliced into ten tasks across three tracks: backend (FastAPI + SQLite), frontend (React, mobile-first), and deployment (docker-compose). Each track is split into a scaffold task, feature tasks, and cross-cutting concerns, following the requirements' functional areas: recipe management (FR-1..FR-5), meal plans (FR-6, FR-7, FR-9), shopping list generation (FR-8), the "no ingredients" tag (FR-10), plus the non-functional requirements (Docker, persistence, concurrency, mobile-first). Backend and frontend tracks are independent after their scaffolds exist, so developer and tester can work in parallel. Tasks whose definition depends on a technical choice not yet made are marked **[requires architecture]** and are left for the architect to resolve.

**Assumptions:** proposed paths (`backend/`, `frontend/`, `docker-compose.yml`) are placeholders for a greenfield repo; the architect confirms the final layout. The exact API contracts, database schema, frontend tooling, and container topology are architecture decisions, not decided here. Automated testing is not mandated by the requirements; the tester agent validates acceptance criteria per task per the pipeline.

**Open questions:** none blocking. `docs/requirements.md:161-163` lists no open questions.

---

## Task breakdown

### T-1 — Scaffold FastAPI backend with SQLite persistence [requires architecture]

**Traces to:** FR-1, FR-6, NFR-2, AC-1, AC-3  
**Touches:** `backend/` (new), `backend/app/main.py`, `backend/app/db.py`, `backend/app/models.py` (proposed)  
Create the Python/FastAPI backend project: application entry point, SQLite database initialization, and the persistence layer for recipes and meal plans (including the plan-to-meal relationship). Data must survive container restarts (NFR-2). The exact schema and project layout are architecture decisions.

### T-2 — Implement recipe CRUD API

**Traces to:** FR-1, FR-2, FR-3, FR-4, FR-5, AC-1  
**Touches:** `backend/app/routes/recipes.py` (proposed)  
REST endpoints: create recipe (name required, ingredient list optional and may be empty), read recipe by id, list all recipes with optional name-substring filter, partial update (name and/or ingredients), and delete (removes the recipe from any plan that includes it).

### T-3 — Implement meal plan API

**Traces to:** FR-6, FR-7, FR-9, AC-3  
**Touches:** `backend/app/routes/plans.py` (proposed)  
REST endpoints: create plan as a flexible list of meals, add/remove meals, delete plan, and list all plans including history. Plans are retained and never overwritten by creating or editing another plan.

### T-4 — Implement shopping list generation API

**Traces to:** FR-8, AC-2, AC-6  
**Touches:** `backend/app/routes/shopping_list.py` (proposed)  
Endpoint that takes one or more plan ids and returns a flat, deduplicated list of ingredient names aggregated from the recipes in those plans. Empty plans and recipes without ingredients contribute nothing. Duplicate ingredient names across recipes appear once.

### T-5 — Scaffold React frontend with app shell [requires architecture]

**Traces to:** NFR-5, AC-1  
**Touches:** `frontend/` (new), `frontend/src/App.tsx`, `frontend/src/api/` (proposed)  
Create the React project, the mobile-first layout shell, navigation between the three main views (recipes, plans, shopping list), and the API client that talks to the backend. Build tooling and state-management approach are architecture decisions.

### T-6 — Build recipe management UI

**Traces to:** FR-1, FR-2, FR-3, FR-4, FR-5, AC-1  
**Touches:** `frontend/src/` recipe views (proposed)  
Recipe list view with search/filter by name, create/edit form (name + ingredient names, ingredients optional), and delete with confirmation. Mobile-first layout.

### T-7 — Build meal plan UI

**Traces to:** FR-6, FR-7, FR-9, FR-10, AC-3, AC-4  
**Touches:** `frontend/src/` plan views (proposed)  
Plan list (active + history), create plan, add/remove meals by selecting recipes from the base, and the "no ingredients" tag next to recipes without ingredients in the plan view. An empty recipe base shows an empty state prompting the user to create recipes first.

### T-8 — Build shopping list UI

**Traces to:** FR-8, AC-2, AC-6  
**Touches:** `frontend/src/` shopping list view (proposed)  
View where the user selects one or more plans and sees the deduplicated shopping list. The list reflects plan edits (refetch on change). Empty selection or no ingredients → empty list.

### T-9 — Add docker-compose deployment stack [requires architecture]

**Traces to:** NFR-1, NFR-2, NFR-3, AC-1  
**Touches:** `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile` (proposed)  
docker-compose stack deployable with a single command, exposing the web interface on the local network, with a volume or bind mount for the SQLite database so data survives container recreation. Container topology (one vs. two services) is an architecture decision. AC-1's end-to-end verification runs against the deployed stack.

### T-10 — Harden concurrent access (last change wins) [requires architecture]

**Traces to:** NFR-4, AC-5  
**Touches:** backend write paths (`backend/app/routes/recipes.py`, `backend/app/routes/plans.py`), frontend refresh behavior (proposed)  
Ensure two users can view and modify the same data simultaneously without corruption or lost data; when both edit the same recipe or plan, the last change wins. The mechanism (write serialization, versioning, or plain last-write-wins PUT semantics) is an architecture decision.

---

## Suggested issue structure

| Task | Issue title | Type |
|---|---|---|
| T-1 | T-1 Scaffold FastAPI backend with SQLite persistence | Chore |
| T-2 | T-2 Implement recipe CRUD API | Feature |
| T-3 | T-3 Implement meal plan API | Feature |
| T-4 | T-4 Implement shopping list generation API | Feature |
| T-5 | T-5 Scaffold React frontend with app shell | Chore |
| T-6 | T-6 Build recipe management UI | Feature |
| T-7 | T-7 Build meal plan UI | Feature |
| T-8 | T-8 Build shopping list UI | Feature |
| T-9 | T-9 Add docker-compose deployment stack | Chore |
| T-10 | T-10 Harden concurrent access (last change wins) | Feature |

Issue body outline for each: purpose (1 line), requirements covered (FR-N list), acceptance criteria to verify (AC-N list), files affected.

- T-1: Purpose: backend foundation with persistent storage. Covers FR-1, FR-6, NFR-2. Verify AC-1, AC-3. Files: `backend/`.
- T-2: Purpose: full recipe CRUD over HTTP. Covers FR-1..FR-5. Verify AC-1. Files: `backend/app/routes/recipes.py`.
- T-3: Purpose: flexible meal plans with history. Covers FR-6, FR-7, FR-9. Verify AC-3. Files: `backend/app/routes/plans.py`.
- T-4: Purpose: deduplicated shopping list from selected plans. Covers FR-8. Verify AC-2, AC-6. Files: `backend/app/routes/shopping_list.py`.
- T-5: Purpose: frontend foundation with mobile-first shell. Covers NFR-5. Verify AC-1 (viewing the recipe list). Files: `frontend/`.
- T-6: Purpose: recipe list and CRUD forms. Covers FR-1..FR-5. Verify AC-1. Files: `frontend/src/` recipe views.
- T-7: Purpose: plan list, editing, history, no-ingredients tag. Covers FR-6, FR-7, FR-9, FR-10. Verify AC-3, AC-4. Files: `frontend/src/` plan views.
- T-8: Purpose: plan selection and deduplicated shopping list. Covers FR-8. Verify AC-2, AC-6. Files: `frontend/src/` shopping list view.
- T-9: Purpose: single-command homeserver deployment. Covers NFR-1, NFR-2, NFR-3. Verify AC-1 end-to-end on the deployed stack. Files: `docker-compose.yml`, Dockerfiles.
- T-10: Purpose: safe concurrent shared access. Covers NFR-4. Verify AC-5. Files: backend write paths, frontend refresh behavior.

---

## Priority order

1. **P0** — T-1, T-2, T-3, T-4, T-5, T-6, T-7, T-8: the end-to-end use case (register recipes → build meal plans → generate shopping list) cannot function without any of these. Scaffolds (T-1, T-5) are enablers for their tracks; the feature tasks deliver the core flow.
2. **P1** — T-9: required for the homeserver deliverable (NFR-1..NFR-3) but not for exercising the core flow during development. T-10: required for the two-person concurrent scenario (NFR-4, AC-5) but not for the single-user flow; it must be delivered before the two-person scenario is considered complete.

---

## Dependencies and blockers

- T-2 depends on T-1 because the recipe API needs the backend scaffold and persistence layer.
- T-3 depends on T-2 because plans reference recipes from the base.
- T-4 depends on T-3 because the shopping list aggregates ingredients from recipes in selected plans.
- T-6 depends on T-5 and T-2 because the recipe UI needs the app shell and the recipe API.
- T-7 depends on T-5 and T-3 because the plan UI needs the app shell and the plan API; selecting meals uses the recipe list API from T-2.
- T-8 depends on T-5 and T-4 because the shopping list UI needs the app shell and the shopping list API; plan selection uses the plan list API from T-3.
- T-9 depends on T-1 and T-5 because the Dockerfiles need both projects to exist.
- T-10 depends on T-2 and T-3 because it hardens the write paths those tasks create.

---

## GitHub Projects mapping

Items start in Backlog: moving to Ready requires approved architecture, which does not exist yet at planning time.

| Task | Status | Priority | Effort |
|---|---|---|---|
| T-1 | Backlog | P0 | M |
| T-2 | Backlog | P0 | M |
| T-3 | Backlog | P0 | M |
| T-4 | Backlog | P0 | S |
| T-5 | Backlog | P0 | M |
| T-6 | Backlog | P0 | M |
| T-7 | Backlog | P0 | M |
| T-8 | Backlog | P0 | S |
| T-9 | Backlog | P1 | S |
| T-10 | Backlog | P1 | S |

---

## Suggested execution sequence

1. Human approves this plan; the architect produces `docs/architecture.md` and ADRs. Per `github-projects-policy.md`, the planner then moves items Backlog → Ready (requires human-approved scope + ADRs).
2. Then in parallel, two tracks, each sequential within the track:
   - Backend: T-1 → T-2 → T-3 → T-4.
   - Frontend: T-5 → T-6 → T-7 → T-8.
3. T-10 (concurrency hardening) runs after T-2 and T-3, in parallel with the frontend track.
4. T-9 (Docker) runs after T-1 and T-5 exist, in parallel with the remaining UI work.
5. Tester validates each task's acceptance criteria as it completes: backend ACs (AC-1, AC-2, AC-3, AC-4, AC-5, AC-6) can be validated while the developer works on the frontend track; frontend ACs are validated as UI tasks land. Final end-to-end validation (AC-1 end-to-end, NFR-1..NFR-5) runs on the deployed stack after T-9.

---

## Board updates

```text
Create issue "T-1 Scaffold FastAPI backend with SQLite persistence" (type: Chore), add to project 2, set Status Backlog, set Priority P0, set Effort M, set Area Backend
Create issue "T-2 Implement recipe CRUD API" (type: Feature), add to project 2, set Status Backlog, set Priority P0, set Effort M, set Area Backend
Create issue "T-3 Implement meal plan API" (type: Feature), add to project 2, set Status Backlog, set Priority P0, set Effort M, set Area Backend
Create issue "T-4 Implement shopping list generation API" (type: Feature), add to project 2, set Status Backlog, set Priority P0, set Effort S, set Area Backend
Create issue "T-5 Scaffold React frontend with app shell" (type: Chore), add to project 2, set Status Backlog, set Priority P0, set Effort M, set Area Frontend
Create issue "T-6 Build recipe management UI" (type: Feature), add to project 2, set Status Backlog, set Priority P0, set Effort M, set Area Frontend
Create issue "T-7 Build meal plan UI" (type: Feature), add to project 2, set Status Backlog, set Priority P0, set Effort M, set Area Frontend
Create issue "T-8 Build shopping list UI" (type: Feature), add to project 2, set Status Backlog, set Priority P0, set Effort S, set Area Frontend
Create issue "T-9 Add docker-compose deployment stack" (type: Chore), add to project 2, set Status Backlog, set Priority P1, set Effort S, set Area DevOps
Create issue "T-10 Harden concurrent access (last change wins)" (type: Feature), add to project 2, set Status Backlog, set Priority P1, set Effort S, set Area Backend
```

After the architect's ADR is approved, the planner moves all ten items Backlog → Ready (per `github-projects-policy.md:90`, planner-only transition, requires approved scope + ADRs).

---

**Approved by:** human  
**Approval date:** 2026-08-28  
**Next agent:** architect