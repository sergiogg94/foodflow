# Discovery: Frontend language switch to Spanish

**Date:** 2026-09-04  
**Project:** FoodFlow  
**Requested by:** human  
**Status:** ✅ approved

---

## Problem statement

The FoodFlow frontend is entirely in English: all UI strings are hardcoded in `frontend/src/App.tsx` and `frontend/src/views/*.tsx`. The human asked to "change the frontend language to Spanish"; the underlying need is to use the interface in Spanish. The request was ambiguous between (a) a language selector allowing the user to toggle between English and Spanish, or (b) simply translating the UI to Spanish. The human has confirmed interpretation (a): a language selector, with the choice persisting per device and English as the default.

---

## Goals

1. Allow the user to use the FoodFlow frontend in Spanish: all UI strings (navigation, forms, empty states, tags, confirmations) are displayed in Spanish.
2. Allow the user to toggle the UI language between English and Spanish via a selector, with the choice persisting per device and defaulting to English.

---

## Non-goals

- Translating user-created data (recipe names, ingredient names, plan names): these are data, not UI strings; the data model has no language concept (`docs/architecture.md:41`).
- Languages beyond English and Spanish.
- Automatic browser-language detection: the confirmed decision is an explicit user action (selector), not automatic detection.
- Backend or API changes: the API returns data, not interface text.
- Per-user language preference: no user concept or authentication exists (`docs/requirements.md:32`); persistence is per device/browser, not per user.

---

## Assumptions

- We assume the request covers only frontend UI strings, not user-entered data (recipe names, ingredients, plans) → if wrong, scope expands to data localization and requires data-model changes.
- We assume the scope covers only English and Spanish → if wrong, scope expands to a multi-language internationalization system.
- We assume the current frontend is the only affected surface: all UI strings are in `frontend/src/App.tsx`, `frontend/src/views/*.tsx`, and `frontend/index.html` (verified) → if wrong (e.g., translatable strings exist in the backend or documentation), the scope changes.
- We assume per-device persistence means the preference is stored locally on the device (e.g., browser storage) and is not shared across devices or users → if wrong (e.g., the human expects cross-device sync), the scope expands significantly and requires backend changes.
- We assume this feature is a new effort on top of the core already merged into `main` (PR #1 `f830444`, PR #2 `64e4546`), independent of the pending delivery acceptance (`docs/delivery-checklist.md:11`) → if wrong (e.g., the human wants to fold it into the pending delivery), sequencing changes.

---

## Open questions

1. (Resolved) **Selector vs. one-way translation?** — Option (a): a language selector allowing the user to toggle between English and Spanish (decision by the human).
2. (Resolved) **Persistence and default language?** — The choice persists per device (browser/device); the default language is English (decision by the human).

---

## Constraints

- Frontend Vite + React + TypeScript with plain React state and no external state library (ADR-2, `docs/adr/2026-08-28_frontend-tooling-and-api-integration.md:22`).
- ADR-2 guard rails: no state-management or data-fetching library, no CSS framework or component library, no react-router (`docs/adr/2026-08-28_frontend-tooling-and-api-integration.md:124-126`). Any new i18n dependency would require an architecture decision.
- Confirmed decision: a language selector toggling between English and Spanish, with the choice persisting per device and English as the default (decision by the human).
- No authentication or user concept; the app is shared by two people without accounts (`docs/requirements.md:32`, `docs/architecture.md:14`). A language preference cannot be per-user.
- All UI strings are hardcoded in English in `frontend/src/App.tsx:8-12`, `frontend/src/views/RecipesView.tsx`, `frontend/src/views/PlansView.tsx`, `frontend/src/views/ShoppingListView.tsx`, and `frontend/index.html:2` (`lang="en"` attribute).
- The core (T-1..T-10) is merged into `main`, but the delivery is 🟡 pending human acceptance (`docs/delivery-checklist.md:11`).

---

## Initial risks

- ADR-2 guard rail (no external libraries) leaves two paths — a hand-rolled mechanism or a new i18n dependency — and choosing a dependency requires modifying/superseding ADR-2 → architecture decision needed before implementation.
- Strings are spread across four files with inline JSX text; an incomplete translation pass leaves a mixed-language UI → completeness risk.
- Hardcoded English pluralization ("1 ingredient"/"2 ingredients" in `frontend/src/views/RecipesView.tsx:192-193`; "1 meal"/"2 meals" in `frontend/src/views/PlansView.tsx:136` and `frontend/src/views/ShoppingListView.tsx:87`): Spanish has different pluralization rules; naive string replacement produces incorrect grammar → quality risk.
- The core delivery is pending human acceptance with open follow-ups (NB-4, NB-5, manual checks of AC-1/AC-4/AC-5, `docs/delivery-checklist.md:83-88`); starting a new feature before accepting the core may interleave work → sequencing risk.

---

## Existing context

- `frontend/src/App.tsx:8-12` — navigation labels "Recipes", "Plans", "Shopping" hardcoded in English.
- `frontend/src/views/RecipesView.tsx` — recipe management UI strings (headings, labels, buttons, empty states, confirmation dialog, "ingredient(s)" pluralization at `:192-193`).
- `frontend/src/views/PlansView.tsx` — plan UI strings; "no ingredients" tag at `:162` and `:196`; "meal(s)" pluralization at `:136`.
- `frontend/src/views/ShoppingListView.tsx` — shopping list UI strings; "meal(s)" pluralization at `:87`.
- `frontend/index.html:2` — `lang="en"` attribute on the HTML document.
- `docs/adr/2026-08-28_frontend-tooling-and-api-integration.md` (ADR-2) — plain React state, no external libraries; guard rails at `:124-126`.
- `docs/requirements.md:32` — no authentication or accounts; no user concept.
- `docs/delivery-checklist.md:11` — core delivery 🟡 pending human acceptance.
- `AGENT_LOG.md` — exists at the repo root (created this session).

---

## Linked references

- Human's request (verbatim): "Quiero agregar la funcionalidad de poder cambiar el idioma del frontend a español".
- Human's decisions (verbatim): option (a) — English-Spanish language selector with per-device persistence and English as default; session language policy — repo files in English.
- `frontend/src/App.tsx`
- `frontend/src/views/RecipesView.tsx`
- `frontend/src/views/PlansView.tsx`
- `frontend/src/views/ShoppingListView.tsx`
- `frontend/index.html`
- `docs/adr/2026-08-28_frontend-tooling-and-api-integration.md` (ADR-2)
- `docs/delivery-checklist.md`

---

## Board updates

None — planning owns item creation.

---

**Approved by:** human  
**Approval date:** 2026-09-04  
**Next agent:** scopper