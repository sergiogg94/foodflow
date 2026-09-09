# Code review: Frontend language switch (English ↔ Spanish)

**Date:** 2026-09-08  
**Project:** FoodFlow  
**Requested by:** human  
**Task(s):** T-1, T-2, T-3, T-4, T-5, T-6  
**Requirements:** `docs/requirements-language-switch.md`  
**Implementation notes:** `docs/notes/2026-09-08_language-switch-implementation.md`  
**Test report:** `docs/tests/2026-09-08_language-switch.md`  
**Branch:** `feat/language-switch`  
**Status:** 🟡 pending human decision

---

## Review summary

This is the re-review of the frontend language switch (T-1..T-6) after the developer addressed the blocking finding B-1 of the initial review (`docs/reviews/2026-09-08_language-switch_review.md`). B-1 is resolved and verified: the `TranslationKeys` type now lives in `frontend/src/i18n/types.ts` per the ADR-6 file structure, `translations.ts` contains only the static dictionaries, and no broken references remain. The production build passes. NB-1 and NB-3 remain open by explicit human decision (non-blocking); NB-2 was resolved by the orchestrator (`docs/architecture.md` ADR-6 → ✅ approved); P-1 stands. Zero blocking findings remain, so the verdict is ✅ Approved — the merge decision belongs to the human.

---

## Scope reviewed

Reviewed completely (not just diffs):

- **Re-work commit** — `c09140b` ("fix: move TranslationKeys type to types.ts per ADR-6 (B-1)"), touching only `frontend/src/i18n/types.ts` and `frontend/src/i18n/translations.ts`.
- **i18n infrastructure** — `frontend/src/i18n/LanguageContext.tsx`, `translations.ts`, `types.ts`, `index.ts`.
- **App shell** — `frontend/src/App.tsx` (provider wrap, selector, nav labels).
- **Views** — `frontend/src/views/RecipesView.tsx`, `PlansView.tsx`, `ShoppingListView.tsx` (all `t()` call sites, `pluralize()` usage, user-data rendering).
- **Styles** — `frontend/src/styles/global.css` (`.app-header-top`, `.lang-selector`, media query).
- **Unchanged files verified** — `frontend/package.json` (no new dependencies), `frontend/src/api/types.ts` (`PlanMeal`/`Recipe` intact), `frontend/index.html` (`lang="en"`).
- **Docs** — `docs/requirements-language-switch.md`, `docs/adr/2026-09-08_frontend-i18n-mechanism.md` (ADR-6), `docs/architecture.md`, `docs/notes/2026-09-08_language-switch-implementation.md`, `docs/tests/2026-09-08_language-switch.md`, `AGENT_LOG.md`.
- **Build** — `npm run build` re-run independently in `frontend/` after the fix: `tsc` clean (`strict: true`) and Vite production build succeeds (158.87 kB JS, 3.48 kB CSS).
- **Branch diff** — `git diff main...feat/language-switch` re-checked: still exactly 10 files (4 new i18n files, 4 modified source files, 1 modified stylesheet, 1 implementation-notes doc). No scope creep.

Could not be reviewed from code alone: real browser-based UI interaction of the selector and the three views (no headless browser available). The reactive `document.documentElement.lang` update and the immediate string switch during user interaction were verified by code inspection only and require manual human confirmation, as the tester declared.

---

## Acceptance criteria cross-check

| AC | Tester status | Reviewer verification |
|---|---|---|
| AC-1 | ✅ Pass | ✅ Agrees. `LanguageContext.tsx:8-16` (`getInitialLang`) returns `"en"` when the key is absent or invalid; `App.tsx:30` renders `English` as the first option bound to `value={lang}`. Browser rendering of the default state needs manual confirmation. |
| AC-2 | ✅ Pass | ✅ Agrees. `LanguageContext.tsx:28-36` (`setLang`) updates context state (re-render of all consumers), writes `localStorage`, and sets `document.documentElement.lang = "es"`. DOM observation during interaction was not performed — needs manual confirmation. |
| AC-3 | ✅ Pass | ✅ Agrees. Read on mount (`LanguageContext.tsx:10`), write on set (`:31`); the stored preference is restored on the next load. |
| AC-4 | ✅ Pass | ✅ Agrees. `pluralize` at `LanguageContext.tsx:84-86`; Spanish singular/plural pairs at `translations.ts:97-98,116-117`; call sites `RecipesView.tsx:195-199`, `PlansView.tsx:139-143`, `ShoppingListView.tsx:90-94`. Zero counts use the plural form (`0 !== 1`), per FR-4. |
| AC-5 | ✅ Pass | ✅ Agrees. User data (`recipe.name`, `plan.name`, `meal.name`, ingredient strings) is rendered directly and never passed to `t()` (`RecipesView.tsx:192`, `PlansView.tsx:136,167,200`, `ShoppingListView.tsx:87,119`). |
| AC-6 | ✅ Pass | ✅ Agrees. Same mechanism as AC-2: `setLang("en")` re-renders all consumers with English output and sets `document.documentElement.lang = "en"`. |

The tester's declared gaps (no frontend test framework, no headless browser, DOM observation not performed) are reasonable and consistent with the developer's notes (`docs/notes/2026-09-08_language-switch-implementation.md:76`). The ACs are verified at the code-inspection and build level, which is the strongest evidence available without a browser; the human should exercise the selector manually before final acceptance.

---

## Findings

### Re-review outcome of the original findings

| Finding | Status | Verification |
|---|---|---|
| B-1 — `TranslationKey` type in `translations.ts` instead of `types.ts`, unused | ✅ Resolved | `frontend/src/i18n/types.ts:3-6` now defines `Language`, `Namespace`, and `TranslationKeys` (renamed per ADR-6); `frontend/src/i18n/translations.ts:148` exports only the dictionaries and defines no types. Grep confirms no reference to the old `TranslationKey` name remains anywhere in `frontend/src`. The type remains unused (as in the initial review), which the ADR permits — the ADR's `t()` contract takes a plain `string` key. |
| NB-1 — `aria-label="Language"` hardcoded, not translated | 🟡 Open (human decision) | Not fixed. The human decided not to correct NB-1 in this pass. Remains non-blocking; the human decides whether to address it later. |
| NB-2 — `docs/architecture.md` ADR-6 recorded as "🔄 proposed" | ✅ Resolved | `docs/architecture.md:101,114` now record ADR-6 as "✅ approved | 2026-09-08". Resolved by the orchestrator, not by the PR. |
| NB-3 — `t()` interpolation `$`-pattern edge case | 🟡 Open (human decision) | Not fixed. The human decided not to correct NB-3 in this pass. Remains non-blocking; the human decides whether to address it later. |
| P-1 — robust `localStorage` try/catch handling | 🟢 Stands | `LanguageContext.tsx:8-16` unchanged and still valid. |

### 🔴 Blocking

None.

### 🟡 Non-blocking

**NB-1** — `frontend/src/App.tsx:28`  
The selector's `aria-label="Language"` is a hardcoded English string that is not translated. When Spanish is selected, a screen-reader user hears the selector labeled "Language" in English, which contradicts the FR-3 requirement that all UI strings render in the selected language. Open by explicit human decision; does not prevent merge.  
**Fix (when addressed):** Add a `nav.language` key to both dictionaries (`"Language"` / `"Idioma"`) and use `aria-label={t(lang, "nav.language")}`.

**NB-3** — `frontend/src/i18n/LanguageContext.tsx:77-80`  
The `t()` interpolation uses `result.replace(new RegExp(...), String(val))`. When the interpolated value is user data (recipe/plan name in the `confirm_delete` dialogs) and contains a `$` replacement pattern (`$&`, `$'`, `` $` ``, `$1`-`$99`), the value is interpreted as a replacement pattern and renders incorrectly. Verified: a recipe named `Pasta $&` produces `Delete recipe "Pasta {{name}}"?` instead of `Delete recipe "Pasta $&"?`. Open by explicit human decision; does not prevent merge.  
**Fix (when addressed):** Use a replacer function instead of a string replacement: `result.replace(regex, () => String(val))`.

### 🟢 Positive

**P-1** — `frontend/src/i18n/LanguageContext.tsx:8-16`  
`getInitialLang()` wraps the `localStorage` read in a try/catch and falls back to `"en"` when storage is unavailable (SSR, privacy settings) or holds an invalid value. This defensive handling goes beyond the ADR's minimum requirement ("defaults to `"en"` if absent or not `"en"`/`"es"`") and prevents a crash in restricted browser contexts.

---

## Final recommendation

✅ **Approved** — B-1 is resolved and verified (the `TranslationKeys` type now lives in `types.ts` per the ADR-6 file structure, with no broken references), the production build passes, and the branch diff still contains only T-1..T-6 plus the implementation-notes doc. The two remaining non-blocking findings (NB-1, NB-3) are open by explicit human decision and do not prevent merge. The merge decision belongs to the human.

---

## Board updates

```text
Move T-1..T-6 Review -> Done after the human merges PR #3 (branch feat/language-switch) — evidence: B-1 resolved and verified in re-review, npm run build passes, docs/reviews/2026-09-08_language-switch_review.md (human applies the transition).
NB-1 and NB-3 remain open as non-blocking follow-ups by human decision; NB-2 resolved by the orchestrator (docs/architecture.md ADR-6 -> approved).
```

---

**Decision by:** ________________ *(human)*  
**Date:** ________________  
**Next step:** ✅ → documenter + merge · 🔄 → developer re-work · ⛔ → architect/human decision