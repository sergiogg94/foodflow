# Implementation plan: FoodFlow — Frontend language switch (English ↔ Spanish)

**Date:** 2026-09-08  
**Project:** FoodFlow  
**Requested by:** human  
**Requirements:** `docs/requirements-language-switch.md`  
**Status:** ✅ approved

---

## Planning summary

The work is sliced into six tasks across a single frontend track. The first two tasks establish the i18n infrastructure and translation data; the third adds the language selector to the app header; the fourth through sixth replace hardcoded UI strings across the three existing views. The i18n mechanism (hand-rolled React Context + localStorage vs. external library) is an architecture decision constrained by ADR-2 guard rails (`docs/adr/2026-08-28_frontend-tooling-and-api-integration.md:124-126`); tasks that depend on this choice are marked **[requires architecture]**. No backend changes are needed. The plan preserves the mobile-first layout and introduces no regressions in existing view behavior.

**Assumptions:** Per-device persistence means `localStorage` (consistent with `docs/discovery-language-switch.md` and `docs/requirements-language-switch.md:21`). The selector is placed in the app header (`frontend/src/App.tsx:19-32`) as specified by the requirements. User-created data (recipe names, ingredient names, plan names) is never translated.

**Open questions:** none blocking. `docs/requirements-language-switch.md` has no open questions.

---

## Task breakdown

### T-1 — Design and implement i18n infrastructure [requires architecture]

**Traces to:** FR-1, FR-2, FR-5, NFR-3, AC-1, AC-3  
**Touches:** `frontend/src/` (new i18n module), `frontend/src/App.tsx`  
**[requires architecture]** — The i18n mechanism is an architecture decision. ADR-2 guard rails (`docs/adr/2026-08-28_frontend-tooling-and-api-integration.md:124-126`) forbid external state-management and data-fetching libraries. An external i18n library (e.g. `react-i18next`) would require amending ADR-2. The architect must choose between a hand-rolled React Context + `localStorage` solution (consistent with existing guard rails) or an external library (requires ADR amendment). This task creates the language context provider, a `useLanguage` hook, and `localStorage` read/write for persistence. The provider wraps the app in `App.tsx` and exposes `lang` and `setLang`. On mount, it reads from `localStorage`; absent a stored value, defaults to `"en"`.

### T-2 — Create translation dictionaries for English and Spanish

**Traces to:** FR-3, FR-4, AC-2, AC-4, AC-6  
**Touches:** `frontend/src/` (new translations module, proposed: `frontend/src/i18n/translations.ts`)  
Define the complete set of translation keys covering all UI strings across the three views and the app shell. Keys are organized by namespace (e.g. `nav`, `recipes`, `plans`, `shopping`). Includes pluralization support for ingredient and meal counts. The dictionaries are static TypeScript objects imported by the translation function. User-created data keys are excluded by design.

### T-3 — Add language selector to the app header

**Traces to:** FR-1, FR-5, NFR-1, AC-1, AC-2, AC-6  
**Touches:** `frontend/src/App.tsx`, `frontend/src/styles/global.css`  
Render a language selector in the app header (`frontend/src/App.tsx:19-32`) with two options labeled in their own language: "English" and "Español". The selector calls `setLang` from the language context. The selector must fit the existing mobile-first layout. The `document.documentElement.lang` attribute is updated reactively when the language changes (FR-5).

### T-4 — Replace hardcoded strings in RecipesView

**Traces to:** FR-3, FR-4, FR-5, AC-2, AC-4, AC-5, AC-6  
**Touches:** `frontend/src/views/RecipesView.tsx`  
Replace all hardcoded English strings with translation function calls: view heading ("Recipes"), form headings ("New recipe"/"Edit recipe"), labels ("Name", "Ingredients (optional)"), placeholders ("Ingredient name", "Filter by name"), buttons ("Remove", "Add ingredient", "Create recipe"/"Save changes", "Cancel", "Edit", "Delete"), empty states, loading text, fallback error messages ("Failed to load recipes", "Failed to save recipe", etc.), and the ingredient count pluralization at lines 192-193. Confirmation dialog messages (`window.confirm` at line 73) are also translated; the recipe name inside the dialog remains untranslated (AC-5).

### T-5 — Replace hardcoded strings in PlansView

**Traces to:** FR-3, FR-4, FR-5, AC-2, AC-5, AC-6  
**Touches:** `frontend/src/views/PlansView.tsx`  
Replace all hardcoded English strings with translation function calls: view heading ("Plans"), form headings and labels ("New plan", "Name", "Create plan"), placeholder ("e.g. This week"), empty states ("No plans yet…", "This plan has no meals yet", "No recipes yet…"), button labels ("Delete", "Remove", "Add selected meals"), heading ("Add meals", "All plans"), loading text, fallback error messages, the meal count pluralization at line 136, and the "no ingredients" tag at lines 162 and 196. Confirmation dialog messages (`window.confirm` at line 54) are also translated; the plan name inside the dialog remains untranslated (AC-5).

### T-6 — Replace hardcoded strings in ShoppingListView

**Traces to:** FR-3, FR-4, FR-5, AC-2, AC-5, AC-6  
**Touches:** `frontend/src/views/ShoppingListView.tsx`  
Replace all hardcoded English strings with translation function calls: view heading ("Shopping list"), section headings ("Select plans", "Ingredients"), empty states ("No plans yet…", "Select at least one plan…", "No ingredients in the selected plans"), loading text, fallback error messages, and the meal count pluralization at line 87.

---

## Suggested issue structure

| Task | Issue title | Type |
|---|---|---|
| T-1 | T-1 Design and implement i18n infrastructure | Spike |
| T-2 | T-2 Create translation dictionaries for English and Spanish | Feature |
| T-3 | T-3 Add language selector to the app header | Feature |
| T-4 | T-4 Replace hardcoded strings in RecipesView | Feature |
| T-5 | T-5 Replace hardcoded strings in PlansView | Feature |
| T-6 | T-6 Replace hardcoded strings in ShoppingListView | Feature |

Issue body outline for each:

- **T-1:** Purpose: establish the i18n mechanism and per-device persistence. Covers FR-1, FR-2, FR-5, NFR-3. Verify AC-1, AC-3. Files: `frontend/src/` (new i18n module), `frontend/src/App.tsx`. **Blocked on architecture decision:** hand-rolled vs. external library.
- **T-2:** Purpose: define all translation keys and English/Spanish values. Covers FR-3, FR-4. Verify AC-2, AC-4, AC-6. Files: `frontend/src/i18n/translations.ts` (proposed).
- **T-3:** Purpose: render the language selector in the app header. Covers FR-1, FR-5, NFR-1. Verify AC-1, AC-2, AC-6. Files: `frontend/src/App.tsx`, `frontend/src/styles/global.css`.
- **T-4:** Purpose: translate all UI strings in the recipes view. Covers FR-3, FR-4, FR-5. Verify AC-2, AC-4, AC-5, AC-6. Files: `frontend/src/views/RecipesView.tsx`.
- **T-5:** Purpose: translate all UI strings in the plans view. Covers FR-3, FR-4, FR-5. Verify AC-2, AC-5, AC-6. Files: `frontend/src/views/PlansView.tsx`.
- **T-6:** Purpose: translate all UI strings in the shopping list view. Covers FR-3, FR-4, FR-5. Verify AC-2, AC-5, AC-6. Files: `frontend/src/views/ShoppingListView.tsx`.

---

## Priority order

1. **P0** — T-1, T-2: The i18n infrastructure and translations are prerequisites for all other tasks. Without the context provider and dictionaries, no string can be replaced. T-1 is the highest-risk task (architecture decision required).
2. **P0** — T-3, T-4, T-5, T-6: The language selector and string replacements deliver the visible feature. All four depend on T-1 and T-2; T-4, T-5, T-6 are independent of each other and can run in parallel. All are P0 because the feature is non-functional without any one of them (a partially translated UI is broken UX).

---

## Dependencies and blockers

- T-1 depends on: architecture decision (hand-rolled i18n vs. external library, subject to ADR-2 guard rails).
- T-2 depends on: T-1 (translation keys and hook API must be defined before dictionaries can be authored against them).
- T-3 depends on: T-1 (the selector calls `setLang` from the language context).
- T-4 depends on: T-1 and T-2 (RecipesView needs both the hook and the translation keys).
- T-5 depends on: T-1 and T-2 (PlansView needs both the hook and the translation keys).
- T-6 depends on: T-1 and T-2 (ShoppingListView needs both the hook and the translation keys).
- T-4, T-5, T-6 are independent of each other and can run in parallel.

---

## GitHub Projects mapping

Items start in Backlog: moving to Ready requires approved architecture, which does not exist yet at planning time.

| Task | Status | Priority | Effort |
|---|---|---|---|
| T-1 | Backlog | P0 | M |
| T-2 | Backlog | P0 | S |
| T-3 | Backlog | P0 | S |
| T-4 | Backlog | P0 | S |
| T-5 | Backlog | P0 | S |
| T-6 | Backlog | P0 | XS |

---

## Suggested execution sequence

1. Human approves this plan; the architect produces an ADR (or amends ADR-2) resolving the i18n mechanism. Per `github-projects-policy.md`, the planner then moves items Backlog → Ready (requires human-approved architecture).
2. Then T-1 (i18n infrastructure) and T-2 (translation dictionaries) sequentially: T-1 first, then T-2 which depends on the hook API from T-1.
3. Then in parallel: T-3 (language selector), T-4 (RecipesView strings), T-5 (PlansView strings), T-6 (ShoppingListView strings). All four depend on T-1 and T-2 being complete.
4. Tester validates each task's acceptance criteria as it completes: AC-1 and AC-3 after T-1, AC-2 and AC-6 after T-3, AC-4 and AC-5 after T-4/T-5/T-6.

---

## Board updates

```text
Create issue "T-1 Design and implement i18n infrastructure" (type: Spike), add to project 2, set Status Backlog, set Priority P0, set Effort M, set Area Frontend
Create issue "T-2 Create translation dictionaries for English and Spanish" (type: Feature), add to project 2, set Status Backlog, set Priority P0, set Effort S, set Area Frontend
Create issue "T-3 Add language selector to the app header" (type: Feature), add to project 2, set Status Backlog, set Priority P0, set Effort S, set Area Frontend
Create issue "T-4 Replace hardcoded strings in RecipesView" (type: Feature), add to project 2, set Status Backlog, set Priority P0, set Effort S, set Area Frontend
Create issue "T-5 Replace hardcoded strings in PlansView" (type: Feature), add to project 2, set Status Backlog, set Priority P0, set Effort S, set Area Frontend
Create issue "T-6 Replace hardcoded strings in ShoppingListView" (type: Feature), add to project 2, set Status Backlog, set Priority P0, set Effort XS, set Area Frontend
```

---

**Approved by:** human  
**Approval date:** 2026-09-08  
**Next agent:** architect
