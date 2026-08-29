# Architecture: FoodFlow — Weekly Meal Planner

**Date:** 2026-08-28  
**Project:** FoodFlow  
**Requested by:** human  
**Requirements:** `docs/requirements.md` (✅ approved)  
**Implementation plan:** `docs/implementation-plan.md` (✅ approved)  
**Status:** ✅ approved

---

## Technical summary

FoodFlow is a greenfield webapp for two people who share a single recipe base, build flexible meal plans as lists of meals, keep a plan history, and get a deduplicated shopping list from one or more selected plans. It runs as a docker-compose stack on the user's homeserver, is reachable only on the local network, requires no authentication, and is designed mobile-first.

The stack is fixed by the human: **Python + FastAPI** backend, **SQLite** database, **React** frontend, **docker-compose** deployment. The architecture resolves the four `[requires architecture]` tasks from the implementation plan:

- **T-1** — Backend project layout and SQLite schema (ADR-1).
- **T-5** — Frontend tooling and API integration (ADR-2).
- **T-9** — Container topology and persistence mount (ADR-3).
- **T-10** — "Last change wins" concurrency mechanism (ADR-4).

The design is deliberately minimal: two core entities (recipes, plans) with two join tables, a thin FastAPI REST layer, a plain React SPA with no external state library, and a single container that serves the built React app from the FastAPI backend.

---

## Existing context

- Greenfield project: no source code, no ADRs, no `AGENT_LOG.md` (`docs/discovery.md:39`, `docs/requirements.md:155`).
- Homeserver has Docker and docker-compose installed with sufficient resources (`docs/requirements.md:156`).
- Local-network-only access, no authentication, no TLS/proxy (`docs/requirements.md:88-90`, `docs/discovery.md:41`).
- `docs/architecture.md` was a scaffold with an empty decision index; this document replaces it.
- `docs/adr/` is empty (only `.gitkeep`).

---

## Proposed changes

Four independent decisions, each captured in its own ADR. Dependency order: ADR-1 (backend layout + schema) and ADR-2 (frontend tooling) are independent of each other; ADR-3 (container topology) depends on both; ADR-4 (concurrency) depends on ADR-1's write paths.

1. **ADR-1 — Backend layout and SQLite schema.** A `backend/` FastAPI project with a SQLAlchemy persistence layer over SQLite. Four tables: `recipes`, `recipe_ingredients`, `plans`, `plan_meals`. The plan-to-meal relationship is a join table so a plan is a flexible, ordered list of meals.
2. **ADR-2 — Frontend tooling.** A Vite + React + TypeScript SPA in `frontend/`, using plain React state (no external state library) and a typed API client in `frontend/src/api/`. CORS enabled on the backend for the dev origin.
3. **ADR-3 — Container topology.** A single docker-compose service: the React app is built at image build time and served as static files by the FastAPI backend. SQLite is persisted via a bind mount.
4. **ADR-4 — Concurrency.** Plain last-write-wins PUT/PATCH semantics with SQLite write serialization (WAL mode, transactions, busy timeout). No versioning, no conflict rejection.

---

## Components or modules affected

- **Backend** (`backend/`): FastAPI app entry point, SQLAlchemy models, DB initialization, and three route modules — recipes, plans, shopping list.
- **Frontend** (`frontend/`): Vite/React/TypeScript app with three views — recipes, plans, shopping list — plus a typed API client.
- **Deployment**: `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`, and a data bind mount.

---

## Data flow or interaction notes

- The React SPA calls the FastAPI REST API exclusively. In production the SPA is served from the same origin as the API (single container), so no CORS is needed in production; CORS is only configured for local development.
- Recipe CRUD writes flow through the recipes route into the `recipes` and `recipe_ingredients` tables.
- Plan CRUD writes flow through the plans route into the `plans` and `plan_meals` tables.
- The shopping list endpoint reads the selected plans, resolves each meal to its recipe, aggregates ingredient names across all selected plans, and deduplicates them (case-sensitive exact match).
- Deleting a recipe removes it from every plan that includes it (cascade), which immediately affects those plans' shopping lists.
- Editing a recipe's ingredients immediately affects the shopping list of every plan that includes it, because the shopping list is computed from the current recipe state at request time (no cached list).

---

## Interfaces or API changes

The backend exposes a REST API consumed by the frontend. Full contracts are specified per ADR:

- **Recipes** — `POST /recipes`, `GET /recipes`, `GET /recipes/{id}`, `PATCH /recipes/{id}`, `DELETE /recipes/{id}`.
- **Plans** — `POST /plans`, `GET /plans`, `GET /plans/{id}`, `PATCH /plans/{id}` (add/remove meals), `DELETE /plans/{id}`.
- **Shopping list** — `POST /shopping-list` (takes one or more plan ids, returns a deduplicated ingredient list).

---

## Risks and tradeoffs

- **Single container serving both app and API** — simplest deployment and no CORS in production, but couples frontend and backend lifecycle. Acceptable for a single homeserver with no scaling needs.
- **Plain last-write-wins** — matches the human's decision and avoids conflict-rejection UX, but a user can silently overwrite another user's concurrent edit. Accepted per the human's explicit decision (`docs/requirements.md:92`).
- **SQLite single-writer** — write serialization prevents corruption but limits concurrent writes; at this scale (two users) it is not a bottleneck.
- **No external state library** — keeps the frontend minimal, but shared data across views is refetched per view rather than held in a global store. Acceptable at this scale.

---

## Open technical questions

None blocking. The four `[requires architecture]` tasks are resolved by the ADRs below. No unresolved questions remain from the requirements (`docs/requirements.md:161-163`) or the plan (`docs/implementation-plan.md:17`).

---

## ADR references

| ADR | Title | Status | Date |
|---|---|---|---|
| ADR-1 | Backend project layout and SQLite schema | ✅ approved | 2026-08-28 |
| ADR-2 | Frontend tooling and API integration | ✅ approved | 2026-08-28 |
| ADR-3 | Container topology and persistence mount | ✅ approved | 2026-08-28 |
| ADR-4 | Concurrency mechanism (last change wins) | ✅ approved | 2026-08-28 |

---

## Decision index

| ADR | Title | Status | Date |
|---|---|---|---|
| ADR-1 | Backend project layout and SQLite schema | ✅ approved | 2026-08-28 |
| ADR-2 | Frontend tooling and API integration | ✅ approved | 2026-08-28 |
| ADR-3 | Container topology and persistence mount | ✅ approved | 2026-08-28 |
| ADR-4 | Concurrency mechanism (last change wins) | ✅ approved | 2026-08-28 |

---

## Board updates

None — items affected by these ADRs become eligible for `Ready` upon human approval; planning applies the transition.

---

**Approved by:** human  
**Approval date:** 2026-08-28  
**Next agent:** developer (+ tester in parallel)
