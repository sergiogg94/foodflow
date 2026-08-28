# ADR-1: Backend project layout and SQLite schema

**Date:** 2026-08-28  
**Project:** FoodFlow  
**Requested by:** human  
**Requirements:** `docs/requirements.md`  
**Implementation plan:** `docs/implementation-plan.md`  
**Status:** 🟡 pending approval  
**Supersedes:** N/A  
**Superseded by:** N/A

---

## Context

T-1 (`docs/implementation-plan.md:23-27`) scaffolds the FastAPI backend with SQLite persistence. The plan proposes a `backend/` project with `main.py`, `db.py`, and `models.py`, but the concrete directory structure and the data model for recipes, meal plans, and the plan-to-meal relationship are architecture decisions. The requirements fix the stack (FastAPI + SQLite, `docs/requirements.md:86,157`) and the entities: recipes with a name and an optional list of ingredient names (`FR-1`), and meal plans as flexible lists of meals (`FR-6`). Data must survive container restarts (`NFR-2`). This is a greenfield project with no existing code or ADRs.

---

## Decision

We will use a `backend/` FastAPI project with a SQLAlchemy 2.0 persistence layer over SQLite, using four tables — `recipes`, `recipe_ingredients`, `plans`, `plan_meals` — where `plan_meals` is the join table expressing the plan-to-meal relationship.

---

## Options considered

### Option A — SQLAlchemy ORM over SQLite

Use SQLAlchemy 2.0 with declarative models and a `Session`-based data layer, storing ingredients and plan meals in separate join tables.

**Pros:** Idiomatic FastAPI companion; cleanly models the many-to-many plan-to-meal relationship and the ordered ingredient list; handles transactions and cascade deletes; well-tested and widely understood.  
**Cons:** Adds a dependency and some boilerplate; ORM is more machinery than a raw `sqlite3` layer for this small schema.

### Option B — Raw `sqlite3` with a thin data layer

Use the standard-library `sqlite3` module directly, with hand-written SQL and a small repository layer.

**Pros:** Zero extra dependencies; full control over SQL; smallest possible footprint.  
**Cons:** Manual relationship handling, manual cascade logic, and manual row-to-object mapping; more error-prone for the plan-to-meal join; less idiomatic with FastAPI's async/typed conventions.

### Option C — Store ingredients and meals as JSON columns

Keep `recipes` and `plans` as two tables, storing the ingredient list and the meal list as JSON text columns.

**Pros:** Simplest schema (two tables); no join tables.  
**Cons:** No referential integrity for plan meals (a plan could reference a deleted recipe); deleting a recipe requires scanning JSON in every plan; harder to reason about and test. Rejected because `FR-5` requires deleting a recipe to remove it from every plan.

---

## Recommendation

Option A — SQLAlchemy 2.0 over SQLite. It is the idiomatic FastAPI choice, models the plan-to-meal relationship and ordered ingredient list cleanly, and gives referential integrity with cascade deletes that directly satisfy `FR-5` (deleting a recipe removes it from every plan). It satisfies AC-1 (recipe CRUD end-to-end) and AC-3 (multiple plans and history) with a maintainable schema. The dependency is justified by the relationship modeling it provides. [requires human approval for the SQLAlchemy dependency]

---

## Implementation guidance

### Data model

| Table | Field | Type | Constraints | Description |
|---|---|---|---|---|
| `recipes` | `id` | INTEGER | PK, autoincrement | Recipe identifier |
| `recipes` | `name` | TEXT | NOT NULL | Recipe name (required, non-empty) |
| `recipes` | `created_at` | TEXT | NOT NULL, default UTC ISO-8601 | Creation timestamp |
| `recipe_ingredients` | `id` | INTEGER | PK, autoincrement | Ingredient row identifier |
| `recipe_ingredients` | `recipe_id` | INTEGER | FK → `recipes.id`, NOT NULL, ON DELETE CASCADE | Owning recipe |
| `recipe_ingredients` | `name` | TEXT | NOT NULL | Ingredient name (may repeat within a recipe) |
| `recipe_ingredients` | `position` | INTEGER | NOT NULL | Order of the ingredient within the recipe |
| `plans` | `id` | INTEGER | PK, autoincrement | Plan identifier |
| `plans` | `name` | TEXT | NOT NULL | Plan name (required, non-empty) |
| `plans` | `created_at` | TEXT | NOT NULL, default UTC ISO-8601 | Creation timestamp |
| `plan_meals` | `id` | INTEGER | PK, autoincrement | Meal row identifier |
| `plan_meals` | `plan_id` | INTEGER | FK → `plans.id`, NOT NULL, ON DELETE CASCADE | Owning plan |
| `plan_meals` | `recipe_id` | INTEGER | FK → `recipes.id`, NOT NULL, ON DELETE CASCADE | Meal (a recipe) |
| `plan_meals` | `position` | INTEGER | NOT NULL | Order of the meal within the plan |

Notes:
- Duplicate ingredient names within a recipe are preserved as provided (`docs/requirements.md:143`); deduplication happens only at shopping-list generation time.
- `ON DELETE CASCADE` on `plan_meals.recipe_id` implements `FR-5` (deleting a recipe removes it from every plan).
- Indexes: `recipe_ingredients(recipe_id)`, `plan_meals(plan_id)`, `plan_meals(recipe_id)`.

### Interface contract

This ADR defines the persistence layer and project layout; the HTTP contracts are specified in ADR-1's downstream tasks (T-2, T-3, T-4) and are not repeated here. The data layer must expose, at minimum, functions to create/read/update/delete recipes (with their ingredients) and plans (with their meals), and to resolve a plan's meals to their recipes.

### File and folder structure

```text
foodflow/
  backend/
    app/
      __init__.py
      main.py            ← FastAPI app entry point, CORS, static file mount (see ADR-3)
      db.py              ← SQLite engine, session factory, DB initialization
      models.py          ← SQLAlchemy ORM models (Recipe, RecipeIngredient, Plan, PlanMeal)
      schemas.py         ← Pydantic request/response schemas
      routes/
        __init__.py
        recipes.py       ← recipe CRUD endpoints (T-2)
        plans.py         ← plan CRUD endpoints (T-3)
        shopping_list.py ← shopping list endpoint (T-4)
    requirements.txt     ← pinned dependencies
    Dockerfile           ← see ADR-3
```

### Naming conventions

- Python modules and packages: `snake_case`.
- SQLAlchemy model classes: `PascalCase` singular nouns (`Recipe`, `RecipeIngredient`, `Plan`, `PlanMeal`).
- Route modules named after the resource they expose (`recipes.py`, `plans.py`, `shopping_list.py`).
- Pydantic schemas: `PascalCase` with a `Base`/`Create`/`Update`/`Read` suffix where applicable.

### Guard rails for the developer

- Do not add tables or columns beyond the four tables above; no user/account tables (out of scope, `docs/requirements.md:32`).
- Do not store ingredient quantities, units, or rich recipe metadata (out of scope, `docs/requirements.md:33-34`).
- Do not introduce a second database or a caching layer; SQLite is the only store.
- Do not implement recipe versioning or recipe history (out of scope, `docs/requirements.md:41`).
- Do not hand-write SQL in route modules; all persistence goes through the SQLAlchemy data layer.

---

## Acceptance criteria satisfied

- AC-1 → The `recipes` + `recipe_ingredients` schema and CRUD data layer support creating, reading, listing, updating, and deleting a recipe with its ingredient list end-to-end.
- AC-3 → The `plans` + `plan_meals` schema supports multiple coexisting plans retained in history, each with its own meal list.
- AC-5 → The schema and data layer provide the persistence foundation for concurrent access (write serialization is specified in ADR-4).

---

## Consequences

**Easier:** Clean relationship modeling and cascade deletes; idiomatic FastAPI code; straightforward testing against SQLite.  
**Harder:** Slightly more setup than raw `sqlite3`; the ORM adds a dependency to the stack.  
**Technical debt introduced:** None beyond the ORM dependency itself.

---

## Board updates

None — items affected by this ADR become eligible for `Ready` upon human approval; planning applies the transition.

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** developer (+ tester in parallel)
