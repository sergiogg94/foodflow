# ADR-5: Recipe uniqueness per plan

**Date:** 2026-08-30  
**Project:** FoodFlow  
**Requested by:** human  
**Requirements:** `docs/requirements.md`  
**Implementation plan:** `docs/implementation-plan.md`  
**Status:** 🔄 proposed  
**Supersedes:** ADR-2 (partially — the `updatePlan` contract semantics for `add_meals` and `remove_meal_ids`)  
**Superseded by:** N/A

---

## Context

The reviewer flagged NB-2 (`docs/reviews/2026-08-30_meal-planner-core_review.md:63-65`): in the plan update API, `remove_meal_ids` is interpreted as recipe ids, so removing a meal removes every occurrence of that recipe in the plan. This ambiguity arises from ADR-2's `PlanMeal` interface, which exposes `recipe_id` but no meal-row id, so the frontend cannot reference a `plan_meals` row id (`docs/notes/implementation-notes.md:31,85`). The human has now decided the desired behavior: **each recipe appears at most once per plan**. This decision resolves the ambiguity by making the `recipe_id`-based contract unambiguous: with uniqueness enforced, a recipe id identifies exactly one meal in a plan. The requirements do not constrain duplicate meals in a plan (`FR-6`, `FR-7`), so this is a new business rule that must be specified as an ADR change rather than an implementation change.

---

## Decision

We will enforce that each recipe appears at most once in a given meal plan. Adding a recipe that is already in the plan will be silently ignored (deduplicated), and `remove_meal_ids` will continue to carry recipe ids, which now unambiguously remove that single meal.

---

## Options considered

### Option A — Silently ignore duplicate adds (dedupe)

When `add_meals` contains a recipe id already present in the plan, the backend skips that id and adds only the recipes not already present. The request succeeds (200) and returns the resulting plan.

**Pros:** Forgiving for the phone browser (NFR-5): the frontend's checkbox picker lets a user check a recipe already in the plan, and no error UI is needed on a small screen; consistent with the low-friction, last-write-wins philosophy of ADR-4 (no conflict rejection); idempotent — re-sending the same add is harmless.  
**Cons:** The client is not told explicitly that a duplicate was ignored; a caller that relies on a strict add-or-fail contract gets no signal.

### Option B — Reject duplicate adds with 409 Conflict

When `add_meals` contains a recipe id already present in the plan, the backend returns `409 Conflict` and makes no change.

**Pros:** Explicitly surfaces the duplicate to the caller; a strict API contract.  
**Cons:** Requires the frontend to detect, render, and recover from a 409 on the phone browser, adding error-handling UI and friction for a natural interaction (checking an already-present recipe); contradicts the low-friction, last-write-wins design of ADR-4; the human's requirement is only that no duplicate exists, not that the client be told.

### Option C — Enforce uniqueness at the database level (unique constraint on `plan_meals(plan_id, recipe_id)`)

Add a `UNIQUE(plan_id, recipe_id)` constraint to the `plan_meals` table, in addition to route-level handling.

**Pros:** Strongest guarantee; prevents duplicates even under a concurrent-add race.  
**Cons:** Requires a schema change and migration to ADR-1's table; under ADR-4's last-write-wins model a race could surface as a constraint violation (500) rather than a clean dedupe; the route-level check inside the atomic write transaction already prevents duplicates at this scale (two users). Rejected as scope creep beyond the human's requirement.

---

## Recommendation

Option A — silently ignore duplicate adds. It is the minimal change consistent with the human's requirement (each recipe at most once per plan) and with the project's mobile-first and low-friction constraints: the phone browser (NFR-5) needs no error UI for a natural checkbox interaction, and the behavior matches ADR-4's last-write-wins, no-conflict-rejection philosophy. It satisfies AC-3 (multiple plans, each with its own meal list) and AC-6 (removing a meal removes its ingredients) without a schema change to ADR-1. Option B adds mobile error-handling friction the scope does not require; Option C changes the schema for a guarantee the route-level check already provides at this scale.

---

## Implementation guidance

### Data model

No schema change. The `plan_meals` table (ADR-1) and the `PlanMeal` interface (ADR-2) are unchanged. The `recipe_id` field remains the sole identifier of a meal within a plan; uniqueness makes it unambiguous.

### Interface contract

The `updatePlan` contract from ADR-2 is unchanged in shape; only its semantics are now specified.

#### `PATCH /plans/{plan_id}`

**Request:**  
```json
{
  "name": "optional string",
  "add_meals": [1, 2, 3],
  "remove_meal_ids": [2]
}
```

**Response (200):** the full updated `Plan` (`id`, `name`, `meals`), where each `meals` entry is a `PlanMeal` (`recipe_id`, `name`, `ingredient_count`) and no `recipe_id` appears more than once.

**Semantics:**
- `add_meals` is a list of recipe ids. For each id, if the recipe does not exist, return `404` with `detail` naming the missing recipe. If the recipe already exists in the plan, skip it (no duplicate created, no error). Otherwise append it as a new meal at the end of the list.
- `remove_meal_ids` is a list of recipe ids. Each id removes the single meal whose `recipe_id` matches. Ids not present in the plan are ignored. Because uniqueness is enforced, a recipe id identifies at most one meal, so removal is unambiguous.
- `name`, `add_meals`, and `remove_meal_ids` are each optional and independent; the request applies whichever are present.

**Error cases:**
- `404` — plan not found, or an `add_meals` id references a nonexistent recipe.
- `422` — malformed request body (Pydantic validation).

### File and folder structure

No new files. The change is confined to the plan update route:

```text
foodflow/
  backend/app/routes/plans.py    ← modify update_plan: dedupe add_meals against existing meals
```

### Naming conventions

No new naming conventions. Follow the existing conventions in ADR-1 and ADR-2.

### Guard rails for the developer

- Do not add a `meal_id`/row-id field to the `PlanMeal` interface or to `remove_meal_ids`; uniqueness makes the `recipe_id`-based contract sufficient and is the minimal change.
- Do not add a `UNIQUE(plan_id, recipe_id)` constraint or any other schema change to `plan_meals` (ADR-1 is unchanged).
- Do not return `409` for duplicate adds; silently skip duplicates and return the resulting plan.
- Do not change the `PlanMeal` response shape (`recipe_id`, `name`, `ingredient_count`); the frontend contract in ADR-2 is unchanged.
- Do not alter the behavior of `remove_meal_ids` beyond the now-unambiguous single-meal semantics.

---

## Acceptance criteria satisfied

- AC-3 → Multiple plans each retain their own meal list; uniqueness applies per plan, so the same recipe can appear in different plans while appearing at most once within any single plan.
- AC-6 → Removing a meal (by recipe id) removes that single meal and its ingredients from the shopping list; the recipe remains in the base.
- NFR-5 → The dedupe-on-add behavior needs no error UI on the phone browser, keeping the mobile interaction low-friction.

---

## Consequences

**Easier:** `remove_meal_ids` is now unambiguous (recipe id = one meal); the frontend can rely on a plan never containing duplicate recipes; no schema or interface change.  
**Harder:** The backend must check existing meals before appending each `add_meals` id; a caller that wants to be told about duplicates gets no signal.  
**Technical debt introduced:** None.

---

## Board updates

None — items affected by this ADR become eligible for `Ready` upon human approval; planning applies the transition.

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** developer (+ tester in parallel)
