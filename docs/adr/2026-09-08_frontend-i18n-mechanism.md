# ADR-6: Frontend i18n mechanism

**Date:** 2026-09-08  
**Project:** FoodFlow  
**Requested by:** human  
**Requirements:** `docs/requirements-language-switch.md`  
**Implementation plan:** `docs/implementation-plan-language-switch.md`  
**Status:** ✅ approved  
**Supersedes:** N/A  
**Superseded by:** N/A

---

## Context

Task T-1 (`docs/implementation-plan-language-switch.md:23-27`) establishes the i18n infrastructure for the frontend language switch feature. It is marked `[requires architecture]` because the choice of mechanism is constrained by ADR-2 guard rails (`docs/adr/2026-08-28_frontend-tooling-and-api-integration.md:124-126`), which prohibit external state-management, data-fetching, CSS, or routing libraries. Introducing an external i18n library would require superseding or amending ADR-2. The requirements define exactly two languages (English and Spanish), approximately 50 UI strings across three views and the app shell, simple pluralization for ingredient and meal counts (FR-4), per-device persistence via `localStorage` (FR-2, AC-3), and a reactive `document.documentElement.lang` attribute (FR-5). The human has chosen a language selector with English default and per-device persistence.

---

## Decision

We will use a hand-rolled React Context + `localStorage` solution for frontend i18n, consistent with the ADR-2 guard rails that prohibit external state and data-fetching libraries.

---

## Options considered

### Option A — React Context + `localStorage` (hand-rolled)

A `LanguageContext` providing `lang` ("en" | "es") and `setLang`, backed by `localStorage` for persistence. A `t()` translation function reads from static TypeScript dictionaries. Pluralization handled by a small helper. No new npm dependencies.

**Pros:** Fully consistent with ADR-2 guard rails — no new dependencies introduced; zero bundle-size increase beyond the project's own code; trivial to reason about for two languages and ~50 strings; the `t()` function and context are the same pattern already used for React state in this project.  
**Cons:** The developer must write and maintain the translation dictionaries by hand; no built-in pluralization engine (but the project only needs a single ternary per count); no namespace/lazy-loading features (irrelevant at this scale).

### Option B — `react-i18next` (external library)

Add `i18next` and `react-i18next` as npm dependencies. Define translation JSON files per language. Use the `useTranslation` hook and `<Trans>` component. Supports pluralization, namespace splitting, and lazy loading out of the box.

**Pros:** Mature ecosystem; built-in pluralization; namespace-based organization; well-documented.  
**Cons:** Introduces two new npm dependencies that violate ADR-2 guard rails (`docs/adr/2026-08-28_frontend-tooling-and-api-integration.md:124-126`); requires superseding or amending ADR-2; adds ~15 kB gzipped to the bundle for a feature that only translates ~50 strings in two languages; the pluralization engine is overkill for four pluralizable strings (ingredient count × two languages, meal count × two languages).

### Option C — Inline conditional rendering (no context, no library)

Each component reads `localStorage` directly and uses inline ternaries (`lang === "es" ? "Recetas" : "Recipes"`) without a shared context.

**Pros:** No context provider needed; zero dependencies.  
**Cons:** Language state is not shared — every component reads `localStorage` independently, so switching language requires all components to re-read on the next render cycle; `document.documentElement.lang` updates become scattered; impossible to build a centralized selector that triggers a re-render of the entire app; duplicates the `localStorage` read logic in every view. Not viable because FR-1 requires an app-header selector that switches all strings immediately.

---

## Recommendation

Option A — React Context + `localStorage`. It is the only option consistent with the ADR-2 guard rails without requiring an ADR amendment, and it is sufficient for the project's scale: two languages, ~50 strings, four pluralizable counts. It satisfies AC-1 (default English on first visit — `localStorage` absent → `"en"`), AC-3 (persistence across reloads — `localStorage` read on mount), and AC-2/AC-6 (immediate switch — context re-render propagates to all consumers). No new dependency is introduced, so no human approval beyond this ADR is needed.

---

## Implementation guidance

### Data model

No server-side data model. The frontend manages a single language preference as a string stored in `localStorage`.

| Storage key | Type | Constraints | Description |
|---|---|---|---|
| `"foodflow-lang"` | `string` | `"en"` or `"es"`; default `"en"` when absent or invalid | Per-device language preference persisted in `localStorage` |

### Interface contract

No API changes. The frontend exposes a React Context and hook consumed by components.

#### `LanguageContext`

```
type Language = "en" | "es";

interface LanguageContextValue {
  lang: Language;
  setLang: (lang: Language) => void;
}
```

- `lang`: the current language. Read from `localStorage` key `"foodflow-lang"` on mount; defaults to `"en"` if absent or not `"en"`/`"es"`.
- `setLang(lang)`: writes to `localStorage`, updates `document.documentElement.lang`, and triggers a re-render of all consumers.

#### `useLanguage()` hook

```
function useLanguage(): LanguageContextValue
```

Returns the context value. Must be called inside a `<LanguageProvider>`. Throws if used outside the provider (standard React Context pattern — `useContext` throws by default).

#### `t(key: string, params?: Record<string, string | number>): string`

Translation function. Looks up `key` in the dictionary for the current `lang`. Supports interpolation via `{{param}}` placeholders in dictionary values. Not a hook — it is a plain function that accepts a language parameter or reads from context internally.

#### `pluralize(count: number, singular: string, plural: string): string`

Helper function. Returns `singular` when `count === 1`, otherwise `plural`. Called as `pluralize(count, t("recipes.ingredient_singular"), t("recipes.ingredient_plural"))`.

### File and folder structure

```text
frontend/src/
  i18n/
    index.ts               ← re-exports LanguageProvider, useLanguage, t, pluralize, type Language
    LanguageContext.tsx     ← createContext, LanguageProvider component, useLanguage hook
    translations.ts        ← static dictionaries: { en: {...}, es: {...} } organized by namespace
    types.ts               ← Language type, TranslationKeys type
  App.tsx                  ← modified: wrap app in <LanguageProvider>, replace hardcoded nav labels with t() calls
  views/
    RecipesView.tsx         ← modified: replace hardcoded strings with t() calls
    PlansView.tsx           ← modified: replace hardcoded strings with t() calls
    ShoppingListView.tsx    ← modified: replace hardcoded strings with t() calls
  styles/
    global.css              ← modified: add minimal styles for the language selector
```

**No new files outside `frontend/src/i18n/`.** Existing files are modified, not replaced.

### Translation dictionary structure

The `translations.ts` file defines a flat-ish structure organized by namespace. Example shape:

```typescript
const translations = {
  en: {
    nav: { recipes: "Recipes", plans: "Plans", shopping: "Shopping" },
    recipes: {
      heading: "Recipes",
      new_recipe: "New recipe",
      edit_recipe: "Edit recipe",
      name_label: "Name",
      ingredients_label: "Ingredients (optional)",
      ingredient_placeholder: "Ingredient name",
      remove: "Remove",
      add_ingredient: "Add ingredient",
      create: "Create recipe",
      save: "Save changes",
      cancel: "Cancel",
      search_label: "Search",
      filter_placeholder: "Filter by name",
      loading: "Loading…",
      empty_search: "No recipes match your search.",
      empty_list: "No recipes yet. Create your first recipe above.",
      ingredient_singular: "ingredient",
      ingredient_plural: "ingredients",
      edit: "Edit",
      delete: "Delete",
      confirm_delete: 'Delete recipe "{{name}}"?',
      error_load: "Failed to load recipes",
      error_save: "Failed to save recipe",
      error_load_one: "Failed to load recipe",
      error_delete: "Failed to delete recipe",
    },
    plans: { /* ...similar structure... */ },
    shopping: { /* ...similar structure... */ },
  },
  es: {
    nav: { recipes: "Recetas", plans: "Planes", shopping: "Lista de la compra" },
    recipes: { /* ...Spanish translations... */ },
    plans: { /* ...Spanish translations... */ },
    shopping: { /* ...Spanish translations... */ },
  },
} as const;
```

### Concrete string mappings (English → Spanish)

Navigation labels: "Recipes" → "Recetas", "Plans" → "Planes", "Shopping" → "Lista de la compra".  
Headings: "Recipes" → "Recetas", "Plans" → "Planes", "Shopping list" → "Lista de la compra".  
Pluralization: "ingredient"/"ingredients" → "ingrediente"/"ingredientes"; "meal"/"meals" → "comida"/"comidas".  
"no ingredients" tag → "sin ingredientes".  
"Loading…" → "Cargando…".  
Button/label translations follow the patterns in FR-3.

### Naming conventions

- Context file: `LanguageContext.tsx` (PascalCase, React convention for context files).
- Hook: `useLanguage` (camelCase, React hook convention).
- Translation function: `t` (short, conventional in i18n libraries).
- Helper: `pluralize` (camelCase, plain function).
- Dictionary namespaces: `nav`, `recipes`, `plans`, `shopping` (camelCase, matching view names).
- localStorage key: `"foodflow-lang"` (kebab-case, namespaced to the app).

### Guard rails for the developer

- Do not add any npm dependency (`i18next`, `react-i18next`, `formatjs`, or any other i18n library). This ADR explicitly chooses hand-rolled to respect ADR-2 guard rails.
- Do not add a state-management library to share the language state; React Context is sufficient for this single value.
- Do not translate user-created data (recipe names, ingredient names, plan names) — these are data, not UI strings (AC-5, `docs/requirements-language-switch.md:29-30`).
- Do not implement automatic browser-language detection; the language is set only by explicit user action via the selector (`docs/requirements-language-switch.md:31`).
- Do not add deep-linking or URL-based language routing (out of scope; no router exists per ADR-2 guard rail at line 126).
- Do not split translation files into separate JSON files or lazy-load them; the total dictionary size is small enough to import statically.
- Do not change the `PlanMeal` or `Recipe` TypeScript interfaces (ADR-2); only UI strings change.
- The selector options must always be labeled in their own language: "English" and "Español" regardless of the current `lang` value (`docs/requirements-language-switch.md:119`).

---

## Acceptance criteria satisfied

- AC-1 → Default English on first visit: `LanguageProvider` reads `"foodflow-lang"` from `localStorage`; if absent or invalid, `lang` defaults to `"en"`. All `t()` calls return English strings. The selector renders "English" as selected.
- AC-2 → Switch to Spanish: `setLang("es")` updates context state, causing all consuming components to re-render with Spanish `t()` output. `document.documentElement.lang` is set to `"es"` inside `setLang`.
- AC-3 → Persistence across reloads: `setLang` writes to `localStorage`; `LanguageProvider` reads from `localStorage` on mount, restoring the previous choice.
- AC-4 → Spanish pluralization: `pluralize(count, t("recipes.ingredient_singular"), t("recipes.ingredient_plural"))` produces "1 ingrediente" / "2 ingredientes" when `lang` is `"es"`. Same pattern for meal counts.
- AC-5 → User data is not translated: the `t()` function is never called with recipe names, ingredient names, or plan names. Only UI string keys are passed to `t()`.
- AC-6 → Switch back to English: `setLang("en")` updates context state; all consumers re-render with English strings. `document.documentElement.lang` is set to `"en"`.

---

## Consequences

**Easier:** No new dependency to maintain, audit, or upgrade; the i18n mechanism is fully within the project's own code and follows the same React patterns already in use; adding a third language later is a matter of adding a dictionary entry and a selector option.  
**Harder:** Translation dictionaries are maintained manually; there is no tooling to extract missing keys or detect untranslated strings (acceptable at this scale); the `t()` function does not support complex pluralization rules (but the project only needs singular/plural for four strings).  
**Technical debt introduced:** None. The hand-rolled approach is the simplest solution for two languages; if the project later scales to many languages or needs complex i18n features, this ADR can be superseded by one introducing a library.

---

## Board updates

None — items affected by this ADR become eligible for `Ready` upon human approval; planning applies the transition.

---

**Approved by:** human  
**Approval date:** 2026-09-08  
**Next agent:** developer (+ tester in parallel)
