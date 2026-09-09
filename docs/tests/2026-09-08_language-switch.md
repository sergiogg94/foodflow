# Test report: Frontend language switch (English ↔ Spanish)

**Date:** 2026-09-08  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** T-1, T-2, T-3, T-4, T-5, T-6  
**Requirements:** `docs/requirements-language-switch.md`  
**Implementation notes:** `docs/notes/2026-09-08_language-switch-implementation.md`  
**Branch:** `feat/language-switch`  
**Status:** 🟡 pending review

---

## Validation summary

Validated the frontend language switch (hand-rolled React Context + `localStorage` i18n) against AC-1..AC-6, all eight edge cases, and ADR-6 contract requirements. The frontend production build (`tsc + vite build`) passed clean with `strict: true`. The backend test suite (32 tests) passed with zero failures, confirming no regression. All acceptance criteria were verified by code inspection against the ADR-6 contract: the `LanguageProvider` reads `localStorage["foodflow-lang"]` on mount with default `"en"`, `setLang` writes to localStorage and updates `document.documentElement.lang`, `t()` and `pluralize()` are implemented, the selector options are hardcoded in their own language, and user-created data is never passed to `t()`. No automated frontend test suite exists (no test framework in `package.json`); no headless browser was available for DOM interaction testing.

---

## Scope tested

**Tested:** `LanguageContext` implementation (provider, `useLanguage`, `t()`, `pluralize()`); translation dictionaries for all four namespaces (`nav`, `recipes`, `plans`, `shopping`) in both languages; language selector in `App.tsx` (options, `onChange` handler, `value` binding); all `t()` call sites across `RecipesView.tsx`, `PlansView.tsx`, and `ShoppingListView.tsx`; `pluralize()` usage for ingredient and meal counts; `document.documentElement.lang` sync on mount and on language change; `localStorage` read on mount and write on language change; `window.confirm` dialog translation with user-data name interpolation; error fallback strings; "no ingredients" tag in both PlanView locations; selector option labels hardcoded in own language; ADR-2 guard rails (no new npm dependencies in `package.json`); frontend `tsc` type-check with `strict: true` and `noUnusedLocals`/`noUnusedParameters` enabled; production Vite build; backend test suite (32 tests, no regression).  
**Not tested:** Real browser-based UI interaction of the language selector and all three views — no headless browser available in this environment. The `document.documentElement.lang` reactive update during user interaction (clicking the selector) was verified only by code inspection of the `setLang` callback, not by DOM observation. The actual rendering of translated strings in a live DOM was not exercised.

---

## Acceptance criteria coverage

| AC | Status | Evidence |
|---|---|---|
| AC-1 | ✅ Pass | `LanguageContext.tsx:8-16`: `getInitialLang()` reads `localStorage["foodflow-lang"]`, returns `"en"` when key is absent or value is not `"en"`/`"es"`. `LanguageContext.tsx:26`: `useState<Language>(getInitialLang)` uses lazy initializer. `App.tsx:30`: first `<option>` is `<option value="en">English</option>`, bound to `value={lang}` (line 26). Default English on first visit is guaranteed by the absent-key fallthrough. |
| AC-2 | ✅ Pass | `LanguageContext.tsx:28-36`: `setLang` calls `setLangState(newLang)` (triggers React re-render of all consumers), writes `localStorage.setItem(STORAGE_KEY, newLang)`, and sets `document.documentElement.lang = newLang`. `App.tsx:27`: `onChange={(e) => setLang(e.target.value as "en" | "es")}`. All view components call `useLanguage()` and pass `lang` to every `t()` call, so changing `lang` causes all UI strings to switch immediately on re-render. |
| AC-3 | ✅ Pass | `LanguageContext.tsx:31`: `setLang` writes `localStorage.setItem(STORAGE_KEY, newLang)`. `LanguageContext.tsx:10`: `getInitialLang()` reads `localStorage.getItem(STORAGE_KEY)` on mount. The preference is restored on next page load. |
| AC-4 | ✅ Pass | `LanguageContext.tsx:84-86`: `pluralize(count, singular, plural)` returns `singular` when `count === 1`, else `plural`. `translations.ts:97-98`: `ingredient_singular: "ingrediente"`, `ingredient_plural: "ingredientes"`. `translations.ts:116-117`: `meal_singular: "comida"`, `meal_plural: "comidas"`. `RecipesView.tsx:195-199`: `pluralize(recipe.ingredient_count, t(lang, "recipes.ingredient_singular"), t(lang, "recipes.ingredient_plural"))`. `PlansView.tsx:139-143` and `ShoppingListView.tsx:90-94`: same pattern for meal counts. Zero counts use plural form (0 !== 1), producing "0 ingredientes" / "0 comidas" — correct per FR-4. |
| AC-5 | ✅ Pass | `RecipesView.tsx:192`: `{recipe.name}` rendered directly, not passed to `t()`. `RecipesView.tsx:126`: `{recipe.ingredient_count}` is a number, not translated. `PlansView.tsx:136,159,167,200`: plan names and meal names rendered as `{plan.name}`, `{meal.name}`, `{recipe.name}` — never passed to `t()`. `ShoppingListView.tsx:87,119`: `{plan.name}` and `{ingredient}` rendered directly. `window.confirm` dialogs (`RecipesView.tsx:75`, `PlansView.tsx:56`) pass `{ name }` for interpolation — the name value is user data and is not itself a translation key. |
| AC-6 | ✅ Pass | Same mechanism as AC-2: `setLang("en")` at `LanguageContext.tsx:28` updates context state, all consumers re-render with English `t()` output. `document.documentElement.lang` set to `"en"` at line 35. |

---

## Edge case coverage

| Edge case / error case | Test | Result |
|---|---|---|
| First visit — no stored preference | Code inspection: `LanguageContext.tsx:8-16` (absent key → `"en"`) | ✅ Pass |
| Language switch with existing data | Code inspection: user data never passed to `t()` — `RecipesView.tsx:192`, `PlansView.tsx:136,167,200`, `ShoppingListView.tsx:87,119` | ✅ Pass |
| Persistence across reloads and browser restarts | Code inspection: `LanguageContext.tsx:10,31` (read on mount, write on set) | ✅ Pass |
| Spanish pluralization (1/2/0) | Code inspection: `LanguageContext.tsx:84-86` (`pluralize` ternary), `translations.ts:97-98,116-117` (singular/plural pairs), zero uses plural | ✅ Pass |
| "no ingredients" tag | Code inspection: `PlansView.tsx:169` (meal list), `PlansView.tsx:202` (recipe picker) — `t(lang, "plans.no_ingredients")` → `"sin ingredientes"` / `"no ingredients"` | ✅ Pass |
| Confirmation dialogs | Code inspection: `RecipesView.tsx:75` — `t(lang, "recipes.confirm_delete", { name })` → `Delete recipe "{{name}}"?` / `¿Eliminar receta "{{name}}"?`; plan name inside is user data, not translated. `PlansView.tsx:56` — same pattern. | ✅ Pass |
| API error messages | Code inspection: all catch blocks use `e instanceof Error ? e.message : t(lang, "...")` — backend error messages pass through via `e.message`, frontend fallback strings are translated (`RecipesView.tsx:35,59,70,85`, `PlansView.tsx:31,51,63,83,94`, `ShoppingListView.tsx:22,46`). | ✅ Pass |
| Selector labels always in own language | Code inspection: `App.tsx:30-31` — `<option value="en">English</option>` and `<option value="es">Español</option>` are hardcoded strings, not passed to `t()`. | ✅ Pass |
| localStorage unavailable (SSR, privacy settings) | Code inspection: `LanguageContext.tsx:12-13` — try/catch around `localStorage.getItem` falls through to default `"en"`. `LanguageContext.tsx:32-33` — try/catch around `setItem` ignores write failures silently. No crash. | ✅ Pass |
| Invalid localStorage value (not `"en"` or `"es"`) | Code inspection: `LanguageContext.tsx:11` — `if (stored === "en" || stored === "es") return stored` — any other value falls through to default `"en"`. | ✅ Pass |
| ADR-2 guard rails — no new npm dependencies | Code inspection: `frontend/package.json` — dependencies are `react` and `react-dom` only; no i18next, react-i18next, or any other i18n library. | ✅ Pass |
| `useLanguage` used outside provider | Code inspection: `LanguageContext.tsx:50-56` — throws `Error("useLanguage must be used within a LanguageProvider")`. | ✅ Pass |
| ADR-6 contract: file structure | Code inspection: `frontend/src/i18n/` contains `LanguageContext.tsx`, `translations.ts`, `types.ts`, `index.ts` — matches ADR-6 exactly. | ✅ Pass |
| ADR-6 contract: `t()` interpolation | Code inspection: `LanguageContext.tsx:77-80` — `replace(new RegExp(\`\\\{\\\{${param}\\\}\\\}\`, "g"), String(val))` handles `{{name}}` placeholders in `confirm_delete` templates. | ✅ Pass |
| `document.documentElement.lang` initial sync | Code inspection: `LanguageContext.tsx:38-41` — syncs on every render if `document.documentElement.lang !== lang`. `index.html:2` starts with `lang="en"`, matching the default. | ✅ Pass |

---

## Result summary

- `npm run build` in `frontend/` (`tsc && vite build`) → type-check clean (`strict: true`); production bundle built (158.87 kB JS, 3.48 kB CSS)
- `python -m pytest backend/tests -q` → 32 passed, 0 failed, 0 skipped

**Totals:** 32 passed · 0 failed · 0 skipped

---

## Defects observed

None.

---

## Test gaps

- **Automated frontend unit tests** — No test framework exists in `frontend/package.json` (no vitest, jest, or similar). The `t()`, `pluralize()`, `LanguageProvider`, and `useLanguage` functions cannot be exercised by automated tests without adding a test runner. The developer flagged this same limitation (`docs/notes/2026-09-08_language-switch-implementation.md:76`). This is a follow-up candidate, not a defect in the implementation.
- **Browser-based UI interaction** — The language selector click behavior, reactive DOM re-render with translated strings, `document.documentElement.lang` update during user interaction, and mobile viewport rendering of the selector were not validated. No headless browser was available in this environment. The developer flagged the same limitation (`docs/notes/2026-09-08_language-switch-implementation.md:76`). The human should exercise the selector in a real browser to confirm: (1) clicking "Español" switches all strings immediately, (2) the selector shows "Español" as selected after switching, (3) reloading the page restores Spanish, (4) clicking "English" switches back, (5) the selector fits the mobile layout, and (6) user data (recipe names, ingredient names, plan names) remains untranslated during the switch.
- **`document.documentElement.lang` reactive update** — The code at `LanguageContext.tsx:35` sets `document.documentElement.lang` inside `setLang`, and the mount sync at lines 38-41 covers the initial state. This was verified by code inspection only, not by DOM observation in a running browser.

---

## Board updates

None — the reviewer consumes this report.

---

**Approved by:** ________________  
**Approval date:** ________________  
**Next agent:** reviewer
