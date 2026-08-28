# Requirements: FoodFlow — Weekly Meal Planner

**Date:** 2026-08-28  
**Project:** FoodFlow  
**Requested by:** human  
**Discovery:** `docs/discovery.md`  
**Status:** ✅ approved

---

## Scope summary

A webapp where two people share a single recipe base (recipe name + ingredient names only, ingredients optional), build one or more flexible meal plans as lists of meals (not strict day-by-day slot assignment), keep a history of plans, and automatically receive a deduplicated shopping list derived from one or more selected plans. The app runs as a Docker container on the user's homeserver, accessible within the local network with no authentication, and is designed mobile-first because the phone browser is the primary device of use.

---

## In scope

1. **Recipe management** — Create, read, update, and delete recipes. Each recipe consists of a name (text, required) and an optional list of ingredient names (text). A recipe may have zero ingredients.
2. **Recipe listing** — View all recipes in a searchable/filterable list, with the ability to select recipes for a meal plan.
3. **Meal plan creation** — Create multiple meal plans. Each plan is a flexible list of meals (recipes selected from the recipe base) that can grow as needed; it is not a strict day-by-day slot assignment. Plans can coexist and are kept in a history.
4. **Meal plan editing** — Add or remove meals within a plan. View any plan (current or historical) at any time.
5. **"No ingredients" tag** — When a recipe with no ingredients is included in a plan, the plan view marks it with a label/tag such as "no ingredients".
6. **Shopping list generation** — From one or more selected plans, produce a flat list of ingredient names. Ingredients that appear in multiple recipes appear only once in the list. The list updates automatically when the plans change.
7. **Concurrent shared access** — Two users access the same data simultaneously without authentication. Both see the same recipe base and the same plans.
8. **Docker deployment** — The application runs as a docker-compose stack on the user's homeserver, accessible within the local network via browser.

---

## Out of scope

- User authentication, accounts, or access control.
- Ingredient quantities, units, or measurements.
- Rich recipe metadata: categories, photos, preparation times, step-by-step instructions, nutritional information.
- Multi-user data isolation or per-user profiles.
- Integration with stores, pricing, or online shopping services.
- Native mobile application.
- TLS/HTTPS configuration or reverse proxy setup.
- External network access beyond the local network.
- Data export/import functionality.
- Recipe versioning or history (plan history is in scope; recipe history is not).
- Sharing plans between users or collaborative plan ownership beyond the shared single data set.

---

## Functional requirements

**FR-1 — Create recipe**  
POST a new recipe with a name (string, non-empty) and an optional list of ingredient names (array of strings). The ingredient list may be empty. The system persists the recipe and returns it with a unique identifier.

**FR-2 — Read recipe**  
GET a recipe by its identifier. Returns the recipe name and the full list of ingredient names (which may be empty).

**FR-3 — List recipes**  
GET all recipes. Returns a list of all recipes with their names and ingredient counts. The user can optionally filter by name substring.

**FR-4 — Update recipe**  
PUT/PATCH an existing recipe by identifier. Allows changing the name and/or the list of ingredient names. Partial updates are supported (e.g., changing only the name). The ingredient list may be set to empty.

**FR-5 — Delete recipe**  
DELETE a recipe by identifier. Removes the recipe from the system. If the recipe is included in any plan, it is removed from those plans.

**FR-6 — Create meal plan**  
Create a new meal plan as a flexible list of meals (recipes selected from the recipe base). The list can grow as the user requires; there is no strict day-by-day slot assignment and the order of meals is not meant to be followed literally. Multiple plans can exist at the same time, and plans are retained in a history.

**FR-7 — Edit meal plan**  
Modify a plan by adding or removing meals from its list. The plan is always visible in its current state. Past plans remain available in the history and are not overwritten by creating or editing another plan.

**FR-8 — Generate shopping list**  
From one or more selected plans, produce a deduplicated flat list of ingredient names. The user selects which plan(s) the shopping list is generated for. If the selected plans have no recipes, or all their recipes have no ingredients, the shopping list is empty. The list reflects the selected plans in real time as they are edited.

**FR-9 — Delete meal plan**  
Remove a plan. The plan is no longer shown in the active list or history. Recipes remain in the recipe base.

**FR-10 — Mark recipes without ingredients in a plan**  
When a recipe with no ingredients is included in a plan, the plan view displays a label/tag such as "no ingredients" next to that recipe.

---

## Non-functional requirements

**NFR-1 — Docker deployment**  
The application must run as a docker-compose stack deployable with a single command. The stack must expose a web interface accessible via browser on the local network.

**NFR-2 — Data persistence**  
All data (recipes and plans) must persist across container restarts. Data must be stored in a volume or bind mount to survive container recreation. The database is SQLite (decision by the human).

**NFR-3 — Local network access**  
The application must be accessible within the user's local network without external internet connectivity. No authentication is required; the app is open to anyone who can reach it on the network.

**NFR-4 — Concurrent access**  
Two users must be able to view and modify the same recipe base and plans simultaneously without data corruption. When two users edit the same recipe or plan at the same time, the last change wins (decision by the human). This requirement defines the need and the chosen strategy; the implementation detail is an architecture decision.

**NFR-5 — Mobile-first responsive design**  
The web interface must be designed mobile-first, because the phone browser is the primary device of use. The layout must look good and remain usable on a mobile phone viewport, and must scale up gracefully to tablet and desktop viewports.

---

## Acceptance criteria

**AC-1 — Recipe CRUD end-to-end**  
Given the recipe base is empty  
When the user creates a recipe named "Pasta Carbonara" with ingredients ["pasta", "eggs", "bacon", "cheese"]  
Then the recipe appears in the recipe list with name "Pasta Carbonara" and 4 ingredients  
And reading the recipe by its identifier returns the same name and ingredient list.

**AC-2 — Flexible plan as a list of meals with shopping list**  
Given recipes "Pasta Carbonara" (pasta, eggs, bacon, cheese) and "Caesar Salad" (lettuce, cheese, croutons) exist in the recipe base  
When the user creates a plan whose meal list contains "Pasta Carbonara" and "Caesar Salad"  
Then the shopping list for that plan contains ["pasta", "eggs", "bacon", "cheese", "lettuce", "croutons"]  
And "cheese" appears only once despite being in both recipes.

**AC-3 — Multiple plans and plan history**  
Given a plan named "This week" exists with "Pasta Carbonara"  
When the user creates a second plan named "Next week" with "Caesar Salad"  
Then both plans are available simultaneously  
And the "This week" plan remains viewable in the history with its original contents.

**AC-4 — Recipe without ingredients is tagged in the plan**  
Given a recipe "Plain Rice" with no ingredients exists  
When the user includes "Plain Rice" in a plan  
Then the plan view shows a label/tag such as "no ingredients" next to "Plain Rice"  
And the shopping list for that plan does not include any ingredient for "Plain Rice".

**AC-5 — Concurrent access with last change wins**  
Given two users have the app open in separate browsers  
When one user creates a recipe while the other is viewing the recipe list  
Then both users see the new recipe after their view refreshes  
And no data is lost or corrupted.

**AC-6 — Plan editing cascades to shopping list**  
Given a plan with "Pasta Carbonara" and "Caesar Salad" exists  
When the user removes "Caesar Salad" from the plan  
Then the shopping list no longer contains "lettuce" or "croutons"  
And the recipe "Caesar Salad" still exists in the recipe base.

---

## Edge cases

- **Empty recipe base** — When no recipes exist, the meal plan creation screen shows an empty state prompting the user to create recipes first. The shopping list is empty.
- **Recipe with no ingredients** — A recipe may be saved with an empty ingredient list. Such a recipe contributes nothing to the shopping list and is tagged "no ingredients" in the plan view.
- **Duplicate ingredient names within a recipe** — If the user enters the same ingredient name twice in a single recipe (e.g., ["cheese", "cheese"]), the system stores them as provided. The shopping list deduplicates across all recipes.
- **Plan with no meals** — A plan may have an empty meal list (e.g., created but not yet filled). The shopping list is empty until meals are added.
- **Shopping list from multiple plans** — The user selects one or more plans to generate the shopping list. Ingredients are aggregated and deduplicated across all selected plans. If the same ingredient appears in recipes across different selected plans, it appears only once in the list.
- **Editing a recipe that is in a plan** — Changes to a recipe's ingredient list (e.g., removing or adding ingredients) immediately affect the shopping list of every plan that includes it.
- **Deleting a recipe that is in a plan** — Deleting a recipe removes it from every plan that includes it, and its ingredients no longer appear in those plans' shopping lists.
- **Concurrent recipe edits** — Two users editing the same recipe simultaneously: the last change wins (decision by the human).
- **Concurrent plan edits** — Two users modifying the same plan simultaneously: the last change wins (decision by the human).

---

## Dependencies

- No existing source code, architecture decisions, or ADRs exist. This is a greenfield project.
- The user's homeserver has Docker and docker-compose installed with sufficient resources (confirmed by the human).
- The Python backend and React frontend are declared constraints from the human. The backend framework is FastAPI and the database is SQLite (decisions by the human). Specific implementation details are architecture decisions.

---

## Open questions

None — all previously open questions (concurrent edit conflict resolution, database persistence model) have been resolved by the human.

---

## Board updates

None — planning owns item creation and state.

---

**Approved by:** human  
**Approval date:** 2026-08-28  
**Next agent:** planner
