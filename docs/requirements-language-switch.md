# Requirements: FoodFlow — Frontend language switch (English ↔ Spanish)

**Date:** 2026-09-04  
**Project:** FoodFlow  
**Requested by:** human  
**Discovery:** `docs/discovery-language-switch.md`  
**Status:** 🟡 pending approval

---

## Scope summary

Once this is done, the FoodFlow frontend shows a language selector in the app header that lets the user toggle the interface between English and Spanish. All existing UI strings — navigation, headings, labels, buttons, placeholders, empty states, tags, confirmations, and pluralized counts — render in the selected language. The choice persists per device (browser) and defaults to English on first visit. User-created data (recipe names, ingredient names, plan names) is never translated.

---

## In scope

1. A language selector in the app header, visible on all three views (recipes, plans, shopping list), offering exactly two options labeled in their own language: "English" and "Español".
2. Per-device persistence of the selected language: the choice survives page reloads and browser restarts; the default on first visit (no stored preference) is English.
3. Translation of all existing frontend UI strings to Spanish when Spanish is selected: navigation labels, view headings, form labels, buttons, placeholders, empty states, the "no ingredients" tag, confirmation dialogs, and loading text.
4. Correct pluralization of counts in both languages: "1 ingredient"/"2 ingredients" and "1 meal"/"2 meals" in English; "1 ingrediente"/"2 ingredientes" and "1 comida"/"2 comidas" in Spanish.
5. The HTML document `lang` attribute reflects the selected language ("en" or "es").

---

## Out of scope

- Translating user-created data: recipe names, ingredient names, and plan names are data, not UI strings, and are never translated.
- Languages beyond English and Spanish.
- Automatic browser-language detection — the language is chosen only by explicit user action.
- Backend or API changes: the API returns data, not interface text; API-provided error messages are not translated.
- Per-user language preference — no user concept or authentication exists; persistence is per device/browser.
- Cross-device sync of the language preference.
- Selection of the i18n mechanism (hand-rolled vs. external library) — an architecture decision subject to ADR-2 guard rails.

---

## Functional requirements

**FR-1 — Language selector**  
The app header displays a language selector with exactly two options, labeled in their own language: "English" and "Español". The selector is visible on all three views. Selecting an option switches all UI strings to that language immediately, without reloading the page.

**FR-2 — Persistence and default**  
The selected language is stored per device (browser). On subsequent visits, the previously selected language is restored. On first visit, when no stored preference exists, the UI is displayed in English.

**FR-3 — UI string translation**  
When Spanish is selected, all existing frontend UI strings render in Spanish: navigation labels ("Recipes" → "Recetas", "Plans" → "Planes", "Shopping" → "Lista de la compra"), view headings, form labels, buttons, placeholders, empty states, the "no ingredients" tag ("sin ingredientes"), confirmation dialogs, and loading text. When English is selected, the same strings render in English as they do today.

**FR-4 — Pluralization**  
Counts render with correct pluralization in the selected language: English "1 ingredient"/"2 ingredients" and "1 meal"/"2 meals"; Spanish "1 ingrediente"/"2 ingredientes" and "1 comida"/"2 comidas". Zero counts use the plural form in both languages ("0 ingredients", "0 ingredientes").

**FR-5 — Document language attribute**  
The `lang` attribute of the HTML document reflects the selected language: "en" when English is selected, "es" when Spanish is selected.

---

## Non-functional requirements

**NFR-1 — Mobile-first**  
The language selector must fit the existing mobile-first layout and remain usable on a mobile phone viewport, consistent with NFR-5 of the core requirements (`docs/requirements.md:94-95`).

**NFR-2 — No regression in existing views**  
The language switch must not change existing behavior of the recipes, plans, and shopping list views: data handling, API calls, and view structure remain as they are today. Only the displayed UI strings change.

**NFR-3 — ADR-2 guard rails**  
The implementation must respect the ADR-2 guard rails (`docs/adr/2026-08-28_frontend-tooling-and-api-integration.md:124-126`): no state-management, data-fetching, CSS, or routing libraries. Introducing an external i18n dependency requires an architecture decision that supersedes or amends ADR-2.

---

## Acceptance criteria

**AC-1 — Default English on first visit**  
Given a device with no stored language preference  
When the user opens the app for the first time  
Then all UI strings are displayed in English  
And the language selector shows "English" as the selected option.

**AC-2 — Switch to Spanish**  
Given the app is open with the UI in English  
When the user selects "Español" in the language selector  
Then all UI strings switch to Spanish immediately, without reloading the page  
And the document `lang` attribute becomes "es".

**AC-3 — Persistence across reloads**  
Given the user selected "Español"  
When the user reloads the page or closes and reopens the browser  
Then the UI is still displayed in Spanish  
And the language selector shows "Español" as the selected option.

**AC-4 — Spanish pluralization**  
Given the app is set to Spanish and recipes with 1 and 2 ingredients exist  
When the user views the recipe list  
Then the counts are displayed as "1 ingrediente" and "2 ingredientes" respectively.

**AC-5 — User data is not translated**  
Given the app is set to Spanish and a recipe named "Pasta Carbonara" with ingredient "pasta" exists  
When the user views the recipe list  
Then the recipe name and ingredient names are displayed exactly as entered ("Pasta Carbonara", "pasta")  
And only the UI strings are in Spanish.

**AC-6 — Switch back to English**  
Given the app is set to Spanish  
When the user selects "English" in the language selector  
Then all UI strings switch back to English  
And the document `lang` attribute becomes "en".

---

## Edge cases

- **First visit** — No stored preference exists: the UI defaults to English (AC-1).
- **Language switch with existing data** — Recipe names, ingredient names, and plan names are never translated; only UI strings change (AC-5).
- **Persistence across reloads and browser restarts** — The selected language is restored on the next visit (AC-3).
- **Spanish pluralization** — "1 ingrediente"/"2 ingredientes", "1 comida"/"2 comidas"; zero counts use the plural form ("0 ingredientes", "0 comidas").
- **"no ingredients" tag** — Renders as "sin ingredientes" in Spanish and "no ingredients" in English, in both the plan meal list (`frontend/src/views/PlansView.tsx:162,196`) and the recipe picker.
- **Confirmation dialogs** — `window.confirm` messages ("Delete recipe "X"?", "Delete plan "X"?") are translated; the recipe/plan name inside the dialog is user data and is not translated.
- **API error messages** — Error text returned by the backend (`e.message`) is not translated (no backend changes per discovery non-goals); frontend fallback strings ("Failed to load recipes", etc.) are translated.
- **Selector labels** — The options are always labeled in their own language ("English", "Español") regardless of the selected language.

---

## Dependencies

- `frontend/src/App.tsx` — app shell and navigation; hosts the header where the selector is placed; navigation labels at `:8-12`.
- `frontend/src/views/RecipesView.tsx` — recipe UI strings; "ingredient(s)" pluralization at `:192-193`.
- `frontend/src/views/PlansView.tsx` — plan UI strings; "meal(s)" pluralization at `:136`; "no ingredients" tag at `:162` and `:196`.
- `frontend/src/views/ShoppingListView.tsx` — shopping list UI strings; "meal(s)" pluralization at `:87`.
- `frontend/index.html:2` — `lang="en"` attribute on the HTML document.
- ADR-2 guard rails (`docs/adr/2026-08-28_frontend-tooling-and-api-integration.md:124-126`) — constrain the implementation; any new i18n dependency requires an architecture decision.
- Discovery decisions (`docs/discovery-language-switch.md`) — option (a) selector, per-device persistence, English default.

---

## Board updates

None — planning owns item creation and state.

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** planner