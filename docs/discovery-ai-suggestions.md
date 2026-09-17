# Discovery: AI ingredient suggestions when creating recipes

**Date:** 2026-09-14  
**Project:** FoodFlow  
**Requested by:** human  
**Status:** ✅ approved (2026-09-14)

---

## Problem statement

When creating a recipe, the user must manually type each ingredient in the form (`frontend/src/views/RecipesView.tsx:124-150`). The human's literal request: "Quiero agregar una nueva feature. A momento de crear una nueva receta quiero agregar un botón para que se sugieran ingredientes de la receta mediante una inteligencia artificial. Quiero usar una api key de google AI studio para ello". The underlying need: reduce the manual work of typing ingredients by generating them automatically from the recipe name via the Google AI Studio (Gemini) API.

---

## Goals

1. Let the user generate a list of suggested ingredients for a recipe with one click, using the recipe name as input, so that creating a recipe does not require typing every ingredient by hand.
2. Let the user review and edit the suggested ingredients before saving the recipe, so that the AI result does not become recipe data without confirmation.

---

## Non-goals

- Generating recipe names, preparation instructions, or any other content: ingredients only.
- Saving suggestions automatically without user review.
- Exposing the API key in the frontend or in the browser.
- Support for multiple AI providers: Google AI Studio (Gemini) only.
- Normalizing or deduplicating ingredients against existing recipes.
- Offline or fallback suggestions when the API is unavailable.

---

## Assumptions

- The recipe name is the only input available in the form (the form only has `name` and `ingredients`, `RecipesView.tsx:13-18`) → if incorrect (e.g. the user wants to describe the recipe in free text), scope expands with an additional field.
- The button appears in both create and edit modes (the form is shared, `RecipesView.tsx:113-168`). **Resolved by human (2026-09-14): the button also appears when editing a recipe.** → the endpoint must accept existing ingredients as context when editing.
- The API key is stored in the backend (environment variable), never in the frontend, because the SPA is served to any device on the local network without authentication (`README.md:20`) → if incorrect (key in frontend), any device on the network could read and use it.
- Suggestions are loaded into the form as a proposal that the user confirms before incorporating. **Resolved by human (2026-09-14): suggestions are added as a proposal for the user to confirm.** → the flow must let the user accept/reject before saving.
- The backend needs a new dependency to call the Google API (`backend/requirements.txt` only has fastapi, uvicorn, SQLAlchemy) → if incorrect (e.g. standard `urllib` is used), there is no dependency change.
- New UI strings (button, loading/error states) require translation in English and Spanish (ADR-6, `frontend/src/i18n/translations.ts`) → if incorrect, the UI stays in a single language.
- The user already has a Google AI Studio API key (stated in the request) → if incorrect, the feature cannot be tested end to end.

---

## Open questions (resolved)

1. ~~(Blocking) Should the suggestion button appear only when creating a new recipe, or also when editing an existing one?~~ **Resolved by human (2026-09-14): the button appears in both create and edit modes.**
2. ~~(Blocking) When the AI returns suggestions, should they replace the current ingredient list, be added to it, or be shown as a proposal the user confirms before incorporating?~~ **Resolved by human (2026-09-14): suggestions are added as a proposal for the user to confirm.**
3. ~~In which language should the AI suggest ingredients: the current interface language (en/es) or always a fixed one?~~ **Resolved by human (2026-09-14): the current interface language.**

---

## Constraints

- Fixed stack: FastAPI + SQLite backend, Vite + React + TypeScript frontend, single docker-compose container (ADR-3).
- No authentication; local network access only; anyone who can reach the app can read and modify data (`README.md:20`). An API key in the frontend would be exposed to every device on the network.
- ADR-2 guard rails (frontend): no external state, data-fetching, CSS, or router libraries.
- ADR-6: all UI strings live in `frontend/src/i18n/translations.ts` in en/es; new strings require both translations.
- The backend has no HTTP client dependency (`backend/requirements.txt`: fastapi, uvicorn, SQLAlchemy).
- `docker-compose.yml` does not currently pass environment variables; the existing pattern is `os.environ.get` (`backend/app/db.py:25`, `backend/app/main.py:29`).
- `.env` is in `.gitignore` (`.gitignore:15`); the frontend `.env.development`/`.env.production` files are committed. The local `.env` is already used for a secret (GITHUB_TOKEN), value not reproduced here.

---

## Initial risks

- API key exposure: if the key is placed in the frontend or committed, it is exposed to every device on the local network and in git history → storage must be server-side; the repo already has a precedent of `GOOGLE_API_KEY` as a CI secret, not as an app variable (`docs/notes/2026-08-29_opencode-review-google-ai-studio.md:15`).
- Cost: Gemini calls are metered; a repeatedly clickable button has unlimited cost → cost risk.
- Key not configured: if the environment variable does not exist, the feature must fail gracefully (hide/disable the button or show a clear error) → UX risk.
- New backend dependency: adding an HTTP client or the Google SDK requires an architecture decision; `requirements.txt` is minimal and pinned.
- Latency: Gemini calls take seconds; the UI needs a loading state and double-click protection.
- The form is shared between create and edit (`RecipesView.tsx:113`); adding the button affects both modes.
- i18n: new strings (button, loading, error) require en/es translations (ADR-6).

---

## Existing context

- `frontend/src/views/RecipesView.tsx` — shared create/edit recipe form; ingredient rows at `:124-150`; submit at `:45-61`.
- `frontend/src/api/client.ts` — typed `get`/`post`/`patch`/`del` helpers over fetch.
- `frontend/src/api/recipes.ts` — recipe CRUD functions.
- `backend/app/routes/recipes.py` — recipe CRUD endpoints.
- `backend/app/schemas.py` — `RecipeCreate`/`RecipeUpdate`/`RecipeRead`.
- `backend/app/main.py` — app entry; CORS only for `localhost:5173`.
- `backend/app/db.py:25` — environment variable pattern (`FOODFLOW_DB_PATH`).
- `frontend/src/i18n/translations.ts` — en/es dictionaries (ADR-6).
- `docs/notes/2026-08-29_opencode-review-google-ai-studio.md` — precedent: `GOOGLE_API_KEY` as a secret and `gemini-2.5-pro` in the CI workflow.
- `docker-compose.yml` — no `env` section; `backend/Dockerfile:17-18` — `ENV FOODFLOW_STATIC_DIR`/`FOODFLOW_DB_PATH`.
- `.gitignore:15` — `.env` ignored.

---

## Linked references

- Human request (verbatim): "Quiero agregar una nueva feature. A momento de crear una nueva receta quiero agregar un botón para que se sugieran ingredientes de la receta mediante una inteligencia artificial. Quiero usar una api key de google AI studio para ello"
- `frontend/src/views/RecipesView.tsx`
- `backend/app/routes/recipes.py`
- `frontend/src/i18n/translations.ts` (ADR-6)
- `docs/adr/2026-09-08_frontend-i18n-mechanism.md` (ADR-6)
- `docs/notes/2026-08-29_opencode-review-google-ai-studio.md`
- `docker-compose.yml`, `backend/Dockerfile`

---

## Board updates

None — planning owns item creation.

---

**Approved by:** human  
**Approval date:** 2026-09-14  
**Next agent:** scopper