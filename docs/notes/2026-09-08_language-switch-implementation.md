# Implementation notes: Frontend language switch (English ↔ Spanish)

**Date:** 2026-09-08  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** T-1, T-2, T-3, T-4, T-5, T-6  
**Branch:** `feat/language-switch`  
**ADR(s):** `docs/adr/2026-09-08_frontend-i18n-mechanism.md`  
**Status:** 🟡 pending review

---

## Summary

Implemented the frontend language switch per ADR-6: a hand-rolled React Context + `localStorage` i18n mechanism with no new npm dependencies. The app header now renders a language selector ("English"/"Español", always labeled in their own language) that switches all UI strings across the three views (recipes, plans, shopping list) immediately, persists the choice per device under the `"foodflow-lang"` localStorage key, defaults to English, and keeps `document.documentElement.lang` in sync. All hardcoded UI strings in the three views were replaced with `t()` calls; ingredient and meal counts use the `pluralize()` helper; user-created data (recipe names, ingredient names, plan names) is never translated.

---

## Implementation per task

### T-1 — Design and implement i18n infrastructure

Created `frontend/src/i18n/` with:

- `types.ts` — `type Language = "en" | "es"`.
- `LanguageContext.tsx` — `LanguageContext` (createContext), `LanguageProvider` component, `useLanguage()` hook, `t()` translation function, `pluralize()` helper. `LanguageProvider` reads `localStorage["foodflow-lang"]` on mount (default `"en"` when absent or invalid), writes it in `setLang`, updates `document.documentElement.lang`, and triggers a re-render of all consumers via context state. `useLanguage()` throws when used outside the provider.
- `translations.ts` — static dictionaries `{ en, es }` organized by namespace (`nav`, `recipes`, `plans`, `shopping`); skeleton at T-1, completed in T-2.
- `index.ts` — re-exports `LanguageProvider`, `useLanguage`, `t`, `pluralize`, and the `Language` type.

Modified `frontend/src/App.tsx` to wrap the app in `<LanguageProvider>` and replace hardcoded nav labels with `t()` calls.

Satisfies FR-1 (selector mechanism), FR-2 (persistence + default), FR-5 (document lang attribute), NFR-3 (no new dependencies), AC-1 (default English), AC-3 (persistence across reloads).

### T-2 — Create translation dictionaries for English and Spanish

Completed `frontend/src/i18n/translations.ts` with all UI strings across the three views and the app shell: navigation labels, view headings, form headings, labels, placeholders, buttons, empty states, loading text, fallback error messages, confirmation dialog templates with `{{name}}` interpolation, the "no ingredients" tag, and pluralization keys (`ingredient_singular`/`ingredient_plural`, `meal_singular`/`meal_plural`) for both languages. The `en` and `es` dictionaries match 1:1.

Satisfies FR-3 (UI string translation), FR-4 (pluralization), AC-2/AC-6 (switch languages), AC-4 (Spanish pluralization).

### T-3 — Add language selector to the app header

Modified `frontend/src/App.tsx` to render a `<select class="lang-selector">` in the header with exactly two options labeled in their own language: "English" and "Español" (hardcoded, never translated — per ADR-6 guard rail). The selector calls `setLang` from the language context and is visible on all three views. Added minimal styles in `frontend/src/styles/global.css` (`.app-header-top`, `.lang-selector`) that fit the mobile-first layout; the desktop media query keeps the existing header layout with the selector grouped with the title.

Satisfies FR-1 (selector visible on all views), FR-5 (document lang attribute updated reactively), NFR-1 (mobile-first), AC-1/AC-2/AC-6 (selector reflects and changes the language).

### T-4 — Replace hardcoded strings in RecipesView

Modified `frontend/src/views/RecipesView.tsx` to replace all hardcoded English strings with `t(lang, "recipes.*")` calls: heading, form headings ("New recipe"/"Edit recipe"), labels ("Name", "Ingredients (optional)"), placeholders ("Ingredient name", "Filter by name"), buttons ("Remove", "Add ingredient", "Create recipe"/"Save changes", "Cancel", "Edit", "Delete"), empty states, loading text, and fallback error messages. The `window.confirm` dialog at the delete handler uses `t(lang, "recipes.confirm_delete", { name })` — the recipe name inside the dialog is user data and is not translated (AC-5). The ingredient count at the recipe list uses `pluralize(recipe.ingredient_count, t(...singular), t(...plural))`.

Satisfies FR-3, FR-4, FR-5, AC-2, AC-4, AC-5, AC-6.

### T-5 — Replace hardcoded strings in PlansView

Modified `frontend/src/views/PlansView.tsx` to replace all hardcoded English strings with `t(lang, "plans.*")` calls: heading, form headings/labels ("New plan", "Name"), placeholder ("e.g. This week"), buttons ("Create plan", "Delete", "Remove", "Add selected meals"), headings ("All plans", "Add meals"), empty states, loading text, fallback error messages, and the "no ingredients" tag at both the meal list and the recipe picker. The `window.confirm` dialog at the delete handler uses `t(lang, "plans.confirm_delete", { name })` — the plan name is user data and is not translated (AC-5). The meal count uses `pluralize(plan.meals.length, t(...singular), t(...plural))`. Plan names, meal names, and recipe names in the picker remain untranslated.

Satisfies FR-3, FR-4, FR-5, AC-2, AC-5, AC-6.

### T-6 — Replace hardcoded strings in ShoppingListView

Modified `frontend/src/views/ShoppingListView.tsx` to replace all hardcoded English strings with `t(lang, "shopping.*")` calls: heading ("Shopping list"), section headings ("Select plans", "Ingredients"), empty states ("No plans yet…", "Select at least one plan…", "No ingredients in the selected plans"), loading text, and fallback error messages. The meal count in the plan picker uses `pluralize(plan.meals.length, t(...singular), t(...plural))`. Plan names and ingredient names remain untranslated (AC-5).

Satisfies FR-3, FR-4, FR-5, AC-2, AC-5, AC-6.

---

## Deviations from the ADR

None.

---

## Validation performed

- `npm run build` in `frontend/` (tsc + vite build) → passed, no errors (run after each task commit and on the complete branch).
- `python -m pytest backend/tests -q` (in a fresh venv with `backend/dev-requirements.txt`) → 32 passed, 0 failed, 0 skipped (1617 deprecation warnings from fastapi/starlette internals on Python 3.14, not from changed code).
- Not validated: real browser-based UI interaction (no headless browser available in this environment) — the language switch behavior is verified at the type-check/build level and by code inspection against AC-1..AC-6.

---

## Follow-up issues discovered

- None.

---

## Board updates

```text
Move T-1 In Progress -> Review — evidence: PR <url> (branch feat/language-switch)
Move T-2 In Progress -> Review — evidence: PR <url> (branch feat/language-switch)
Move T-3 In Progress -> Review — evidence: PR <url> (branch feat/language-switch)
Move T-4 In Progress -> Review — evidence: PR <url> (branch feat/language-switch)
Move T-5 In Progress -> Review — evidence: PR <url> (branch feat/language-switch)
Move T-6 In Progress -> Review — evidence: PR <url> (branch feat/language-switch)
```

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** tester (+ reviewer after)