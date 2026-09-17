# Implementation notes: AI ingredient suggestions — frontend (T-3, T-5, T-4)

**Date:** 2026-09-14  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** T-3, T-5, T-4  
**Branch:** `feat/ai-suggestions-frontend`  
**ADR(s):** `docs/adr/2026-09-08_frontend-i18n-mechanism.md` (ADR-6)  
**Status:** 🟡 pending review

---

## Summary

Implemented the frontend track of the AI ingredient suggestions feature per ADR-6 and the approved plan: a typed `suggestIngredients` client function (T-3), en/es i18n keys under the `recipes` namespace (T-5), and the "Suggest ingredients" button plus reviewable proposal UI in the shared recipe form (T-4). The button appears in both create and edit modes, validates a non-blank recipe name before requesting, disables itself and shows a loading indicator while the request is in flight, renders each suggestion as an editable text field with a selected-by-default toggle, appends only the selected suggestions as new ingredient rows on "Add", and maps the backend 503/502 details to translatable error messages. No new npm dependencies were added (NFR-2, ADR-2).

---

## Implementation per task

### T-3 — Add frontend API client function for suggest-ingredients

- `frontend/src/api/types.ts` — added `SuggestIngredientsResponse { suggestions: string[] }`, following the existing interface-per-response pattern.
- `frontend/src/api/recipes.ts` — added `suggestIngredients(name: string, language: "en" | "es"): Promise<SuggestIngredientsResponse>` that POSTs `{ name, language }` to `/recipes/suggest-ingredients` through the shared `post()` helper (`frontend/src/api/client.ts`), following the existing CRUD function pattern. No new npm packages (NFR-2).

Satisfies FR-1, FR-6, NFR-2, NFR-4, AC-1, AC-4.

### T-5 — Add i18n keys for AI suggestions (en/es)

- `frontend/src/i18n/translations.ts` — added 8 keys under the `recipes` namespace in both `en` and `es` (1:1): `suggest_ingredients`, `suggest_loading`, `suggest_proposal_heading`, `suggest_add`, `suggest_empty`, `suggest_name_required`, `error_suggest_not_configured`, `error_suggest_failed`. The `TranslationKeys` type in `frontend/src/i18n/types.ts` derives from the dictionary, so it picks up the new keys automatically (no manual type edit). Accented Spanish characters use the existing `\u` escape convention.

Satisfies FR-9, NFR-3, AC-1, AC-6.

### T-4 — Add suggest button and proposal UI to the recipe form

- `frontend/src/views/RecipesView.tsx`:
  - Added the "Suggest ingredients" button after the ingredient rows and the "Add ingredient" button, inside the shared form (FR-5). It renders in both create (`editingId === null`) and edit mode (D-8).
  - `handleSuggest`: clears prior errors, validates `form.name.trim() !== ""` (blank → `recipes.suggest_name_required`, no request), then calls `suggestIngredients(form.name.trim(), lang)` with `lang` from `useLanguage()` (FR-6, NFR-3). Sets `suggesting` true for the duration; the button is `disabled={suggesting}` and a loading indicator (`recipes.suggest_loading`) is shown (FR-6, AC-5).
  - On success: `proposal` state is set to `{ text, selected: true }[]`. Non-empty proposals render a heading, one editable text input per suggestion, a selected-by-default checkbox toggle, and an "Add" button. "Add" appends only the selected, non-blank suggestions as new ingredient rows and dismisses the proposal (FR-7, AC-2). An empty array renders the `recipes.suggest_empty` message with a dismiss button (edge case).
  - On failure: `ApiError` status 503 → `recipes.error_suggest_not_configured`; 502 → `recipes.error_suggest_failed`; any other error falls back to the backend/`Error` message (FR-8, AC-3, AC-4).
  - Proposal and suggest-error state are cleared on form reset paths (save success, cancel, edit load, delete of the edited recipe) so a stale proposal never leaks across recipes.
- `frontend/src/styles/global.css` — added minimal styles for `.suggest-button`, `.suggest-proposal`, `.suggest-row`, `.suggest-toggle`, following the existing plain-CSS, mobile-first conventions (no CSS framework, ADR-2).

Satisfies FR-5, FR-6, FR-7, FR-8, NFR-3, AC-1, AC-2, AC-3, AC-4, AC-5, AC-6.

---

## Deviations from the ADR

None.

---

## Validation performed

- `npm run build` in `frontend/` (tsc + vite build) → passed, no TypeScript errors; 41 modules transformed, built in ~0.5s.
- `git diff --stat main...HEAD` → exactly 5 files changed, all within the T-3/T-5/T-4 scope.
- Not validated: real browser-based UI interaction (no headless browser or frontend test framework in this repo) and a live Gemini call (no `GOOGLE_API_KEY` in this environment). The tester should verify the button/proposal flow manually and the 503/502 error paths against a running backend.

---

## Follow-up issues discovered

- None.

---

## Board updates

```text
Move #23 ([AI suggestions] T-3) Ready -> In Progress — evidence: branch feat/ai-suggestions-frontend
Move #25 ([AI suggestions] T-5) Ready -> In Progress — evidence: branch feat/ai-suggestions-frontend
Move #24 ([AI suggestions] T-4) Ready -> In Progress — evidence: branch feat/ai-suggestions-frontend
Move #23 ([AI suggestions] T-3) In Progress -> Review — evidence: PR https://github.com/sergiogg94/foodflow/pull/29, build passed
Move #25 ([AI suggestions] T-5) In Progress -> Review — evidence: PR https://github.com/sergiogg94/foodflow/pull/29, build passed
Move #24 ([AI suggestions] T-4) In Progress -> Review — evidence: PR https://github.com/sergiogg94/foodflow/pull/29, build passed
Set Linked PR on #23, #24, #25 — evidence: PR https://github.com/sergiogg94/foodflow/pull/29 (Closes #23, Closes #24, Closes #25)
```

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** tester (+ reviewer after)
