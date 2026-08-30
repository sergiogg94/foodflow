# ADR-2: Frontend tooling and API integration

**Date:** 2026-08-28  
**Project:** FoodFlow  
**Requested by:** human  
**Requirements:** `docs/requirements.md`  
**Implementation plan:** `docs/implementation-plan.md`  
**Status:** ✅ approved  
**Supersedes:** N/A  
**Superseded by:** ADR-5 (partially — the `updatePlan` contract semantics for `add_meals` and `remove_meal_ids`)

---

## Context

T-5 (`docs/implementation-plan.md:47-51`) scaffolds the React frontend with a mobile-first app shell and an API client that talks to the FastAPI backend. The plan proposes a `frontend/` project with `frontend/src/App.tsx` and `frontend/src/api/`, but the build tooling, the choice of TypeScript vs. JavaScript, the state-management approach, and how the React app talks to the backend (API client, CORS) are architecture decisions. The frontend must be mobile-first because the phone browser is the primary device (`NFR-5`, `docs/requirements.md:94-95`). This is a greenfield project with no existing frontend code.

---

## Decision

We will use a Vite + React + TypeScript single-page application in `frontend/`, with plain React state (no external state-management library) and a typed API client module in `frontend/src/api/` that calls the FastAPI REST API. CORS is enabled on the backend for the local development origin only.

---

## Options considered

### Option A — Vite + React + TypeScript, plain React state, typed API client

Vite as the build/dev server, TypeScript for type safety, React hooks for state, and a small hand-written typed API client.

**Pros:** Vite is the current standard React tooling with fast dev server and simple build; TypeScript catches contract mismatches against the API; no extra state dependency keeps the bundle and mental model small; the API client is a thin typed wrapper over `fetch`.  
**Cons:** Requires writing the API client by hand; no global store means each view refetches its data.

### Option B — Vite + React + JavaScript (no TypeScript)

Same tooling but plain JavaScript.

**Pros:** Slightly less setup; no type annotations to maintain.  
**Cons:** No compile-time safety against API contract drift; more error-prone as the API grows; weaker editor support. Rejected because the API contract is a shared boundary worth type-checking.

### Option C — Vite + React + TypeScript with a state library (Zustand/Redux)

Adds a global state store on top of Option A.

**Pros:** Centralized shared state across the three views (recipes, plans, shopping list).  
**Cons:** Adds a dependency and complexity that the scope does not require; the three views are largely independent and can each fetch their own data. Rejected as scope creep for a two-user, three-view app.

---

## Recommendation

Option A — Vite + React + TypeScript with plain React state and a typed API client. It is the minimal tooling that satisfies `NFR-5` (mobile-first) and gives type safety on the API boundary without adding a state library the scope does not need. It satisfies AC-1 (viewing the recipe list) and supports the three-view navigation required by T-5. The API client is a thin typed wrapper over `fetch`, and CORS is only needed in local development because production serves the SPA from the same origin as the API (see ADR-3).

---

## Implementation guidance

### Data model

No new server-side data model. The frontend defines TypeScript interfaces mirroring the API responses:

| Interface | Fields | Description |
|---|---|---|
| `Recipe` | `id: number`, `name: string`, `ingredients: string[]` | A recipe as returned by the API |
| `RecipeSummary` | `id: number`, `name: string`, `ingredient_count: number` | A recipe list item |
| `Plan` | `id: number`, `name: string`, `meals: PlanMeal[]` | A meal plan |
| `PlanMeal` | `recipe_id: number`, `name: string`, `ingredient_count: number` | A meal within a plan (recipe reference + display data) |
| `ShoppingList` | `ingredients: string[]` | Deduplicated shopping list |

### Interface contract

The frontend consumes the backend REST API defined by T-2, T-3, and T-4. The API client module exposes typed functions, one per endpoint:

- `listRecipes(filter?: string): Promise<RecipeSummary[]>`
- `getRecipe(id: number): Promise<Recipe>`
- `createRecipe(name: string, ingredients: string[]): Promise<Recipe>`
- `updateRecipe(id: number, patch: { name?: string; ingredients?: string[] }): Promise<Recipe>`
- `deleteRecipe(id: number): Promise<void>`
- `listPlans(): Promise<Plan[]>`
- `getPlan(id: number): Promise<Plan>`
- `createPlan(name: string): Promise<Plan>`
- `updatePlan(id: number, patch: { name?: string; add_meals?: number[]; remove_meal_ids?: number[] }): Promise<Plan>`
- `deletePlan(id: number): Promise<void>`
- `generateShoppingList(planIds: number[]): Promise<ShoppingList>`

CORS: the backend enables CORS for the Vite dev origin (`http://localhost:5173`) only. In production the SPA is served from the same origin as the API (ADR-3), so no CORS is configured there.

### File and folder structure

```text
foodflow/
  frontend/
    index.html
    package.json
    tsconfig.json
    vite.config.ts
    src/
      main.tsx
      App.tsx              ← app shell + navigation between the three views
      api/
        client.ts          ← typed fetch wrapper (base URL, error handling)
        recipes.ts         ← recipe API functions
        plans.ts           ← plan API functions
        shoppingList.ts    ← shopping list API function
        types.ts           ← shared TypeScript interfaces
      views/
        RecipesView.tsx    ← recipe list + CRUD forms (T-6)
        PlansView.tsx      ← plan list, editing, history, no-ingredients tag (T-7)
        ShoppingListView.tsx ← plan selection + deduplicated list (T-8)
      styles/
        global.css         ← mobile-first responsive styles
```

### Naming conventions

- React components: `PascalCase` with a `View` suffix for top-level views (`RecipesView`).
- API client files: `camelCase` named after the resource (`recipes.ts`, `plans.ts`).
- TypeScript interfaces: `PascalCase` (`Recipe`, `Plan`, `ShoppingList`).
- CSS: plain global stylesheet; no CSS framework is introduced.

### Guard rails for the developer

- Do not add a state-management library (Redux, Zustand, MobX) or a data-fetching library (React Query, SWR); plain React state and `fetch` are sufficient.
- Do not add a CSS framework or component library; use plain CSS with mobile-first media queries.
- Do not introduce routing beyond the three-view navigation; no react-router unless a view requires deep linking (not in scope).
- Do not implement authentication or user-specific state (out of scope, `docs/requirements.md:32`).
- Do not hardcode the API base URL; read it from a single constant in `client.ts` (dev origin vs. same-origin in production).

---

## Acceptance criteria satisfied

- AC-1 → The recipe list view (T-5/T-6) displays recipes fetched through the API client, satisfying the "viewing the recipe list" portion of AC-1.
- NFR-5 → The app shell and views are built mobile-first with responsive CSS, satisfying the mobile-first requirement.

---

## Consequences

**Easier:** Fast Vite dev loop; type safety on the API boundary; small dependency footprint.  
**Harder:** Each view refetches its own data (no shared cache); the API client is hand-written.  
**Technical debt introduced:** None beyond the hand-written API client, which is small and typed.

---

## Board updates

None — items affected by this ADR become eligible for `Ready` upon human approval; planning applies the transition.

---

**Approved by:** human  
**Approval date:** 2026-08-28  
**Next agent:** developer (+ tester in parallel)
