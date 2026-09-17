# Implementation plan: FoodFlow — AI ingredient suggestions

**Date:** 2026-09-14  
**Project:** FoodFlow  
**Requested by:** human  
**Requirements:** `docs/requirements-ai-suggestions.md`  
**Status:** ✅ approved (2026-09-14)

---

## Planning summary

The work is sliced into six tasks across three tracks: backend (HTTP client dependency + `POST /recipes/suggest-ingredients` endpoint with Gemini integration), frontend (typed API client function, suggest button + proposal UI in the shared recipe form, i18n keys), and DevOps (`GOOGLE_API_KEY` setup documentation). The backend track is gated on one architecture decision: the HTTP client library for calling the Gemini API — T-1 is marked **[requires architecture]**. The endpoint contract is fixed by FR-1, so the frontend client function (T-3) and the i18n keys (T-5) can be authored against the requirements without waiting for backend implementation. T-4 (UI) is the largest task and depends on T-3 and T-5. No new frontend dependencies (NFR-2, ADR-2); the API key stays server-side (NFR-1).

**Assumptions:** The requirements artifact header still reads "🟡 pending approval" (`docs/requirements-ai-suggestions.md:7`), but the human confirmed approval on 2026-09-14; the header is stale and the orchestrator updates it. The backend HTTP client choice (httpx vs requests vs the google-genai SDK) is an architecture decision; the requirements mandate a new dependency (`docs/requirements-ai-suggestions.md:139`). AC-3 is interpreted per FR-2/FR-8: the frontend calls the backend, the backend returns 503 with detail `"AI suggestions are not configured"` when the key is missing, and the frontend displays that detail; "no API call is made from the frontend that would result in a 503" means the frontend never calls Gemini directly (NFR-1). The proposal UI lives inside the shared recipe form (`frontend/src/views/RecipesView.tsx:113-168`), which covers both create and edit modes.

**Open questions:** none blocking. `docs/requirements-ai-suggestions.md:144-146` lists no open questions.

---

## Task breakdown

### T-1 — Add HTTP client dependency to backend requirements [requires architecture]

**Traces to:** FR-3, NFR-4, AC-4  
**Touches:** `backend/requirements.txt`  
**[requires architecture]** — The backend has no HTTP client (`backend/requirements.txt`: fastapi, uvicorn, SQLAlchemy). The requirements mandate a new dependency for calling the Gemini API (`docs/requirements-ai-suggestions.md:139`); the specific library (httpx vs requests vs the google-genai SDK) is an architecture decision. The architect must choose and pin the version. This task adds the chosen dependency to `backend/requirements.txt`.

### T-2 — Implement `POST /recipes/suggest-ingredients` endpoint with Gemini integration

**Traces to:** FR-1, FR-2, FR-3, FR-4, NFR-1, NFR-4, AC-3, AC-4, AC-6  
**Touches:** `backend/app/routes/recipes.py`, `backend/app/schemas.py`  
Add the endpoint to the existing recipe router (`backend/app/routes/recipes.py`). Request schema: `name` (required, non-blank) and `language` (required, one of `"en"`/`"es"`), validated with Pydantic per NFR-4. Reads `GOOGLE_API_KEY` via `os.environ.get()`, strips whitespace (edge case), and returns HTTP 503 with detail `"AI suggestions are not configured"` when missing or empty (FR-2). Builds a prompt containing the recipe name, the requested output language, and an instruction to return only a JSON array of ingredient name strings; calls Gemini through the T-1 client; parses the response into `{"suggestions": [...]}` (FR-3). Any Gemini failure (network error, invalid key, rate limit, non-200, malformed body) returns HTTP 502 with detail `"Failed to get AI suggestions"` (FR-4). Sync function pattern per NFR-4.

### T-3 — Add frontend API client function for suggest-ingredients

**Traces to:** FR-1, FR-6, NFR-2, NFR-4, AC-1, AC-4  
**Touches:** `frontend/src/api/recipes.ts`, `frontend/src/api/types.ts` (proposed)  
Add a typed `suggestIngredients(name: string, language: "en" | "es")` function that POSTs to `/recipes/suggest-ingredients` through the shared client (`frontend/src/api/client.ts` `post` helper) and returns `{ suggestions: string[] }`. No new npm packages (NFR-2). Follows the existing CRUD function pattern (`frontend/src/api/recipes.ts:4-25`).

### T-4 — Add suggest button and proposal UI to the recipe form

**Traces to:** FR-5, FR-6, FR-7, FR-8, NFR-3, AC-1, AC-2, AC-3, AC-4, AC-5, AC-6  
**Touches:** `frontend/src/views/RecipesView.tsx`  
In the shared form (`frontend/src/views/RecipesView.tsx:113-168`), add the "Suggest ingredients" button after the ingredient rows and the "Add ingredient" button (FR-5). On click: validate the recipe name is non-blank (edge case: empty name → validation message, no request), then call `suggestIngredients` with `form.name` and `lang` from `useLanguage()` (FR-6, NFR-3). While the request is in flight, show a loading indicator and disable the button (FR-6, AC-5). On success: render a proposal list — each suggestion is an editable text field with a toggle selected by default; an "Add" button appends only the selected suggestions as new ingredient rows and dismisses the proposal (FR-7, AC-2); an empty list shows a "no suggestions" message the user can dismiss (edge case). On failure: display the backend detail (503/502) through translatable keys (FR-8, AC-3, AC-4).

### T-5 — Add i18n keys for AI suggestions (en/es)

**Traces to:** FR-9, NFR-3, AC-1, AC-6  
**Touches:** `frontend/src/i18n/translations.ts`  
Add keys under the `recipes` namespace: suggest button label, loading indicator text, proposal heading, add button label, empty-suggestions message, and error messages (not configured / failed). Every key has values in both `en` and `es` (FR-9, ADR-6).

### T-6 — Document `GOOGLE_API_KEY` setup for deployment

**Traces to:** NFR-1, AC-3  
**Touches:** `docker-compose.yml`, `README.md`, `.env.example` (proposed)  
Pass `GOOGLE_API_KEY` to the docker-compose service via an `env` section referencing the host `.env` (gitignored, `.gitignore:15`), and document the setup in `README.md`: create `.env` with `GOOGLE_API_KEY=<key>`, never commit it (NFR-1). Optionally add a committed `.env.example` containing the variable name only, with no value.

---

## Suggested issue structure

| Task | Issue title | Type |
|---|---|---|
| T-1 | [AI suggestions] T-1: Add HTTP client dependency to backend requirements | Chore |
| T-2 | [AI suggestions] T-2: Implement POST /recipes/suggest-ingredients endpoint with Gemini integration | Feature |
| T-3 | [AI suggestions] T-3: Add frontend API client function for suggest-ingredients | Feature |
| T-4 | [AI suggestions] T-4: Add suggest button and proposal UI to the recipe form | Feature |
| T-5 | [AI suggestions] T-5: Add i18n keys for AI suggestions (en/es) | Feature |
| T-6 | [AI suggestions] T-6: Document GOOGLE_API_KEY setup for deployment | Chore |

Issue body outline for each:

- **T-1:** Purpose: add the HTTP client dependency the Gemini call needs. Covers FR-3, NFR-4. Verify AC-4. Files: `backend/requirements.txt`. **Blocked on architecture decision:** httpx vs requests vs google-genai SDK.
- **T-2:** Purpose: expose the suggest-ingredients endpoint with Gemini integration and env-var key handling. Covers FR-1, FR-2, FR-3, FR-4, NFR-1, NFR-4. Verify AC-3, AC-4, AC-6. Files: `backend/app/routes/recipes.py`, `backend/app/schemas.py`.
- **T-3:** Purpose: typed frontend function calling the new endpoint. Covers FR-1, FR-6, NFR-2, NFR-4. Verify AC-1, AC-4. Files: `frontend/src/api/recipes.ts`, `frontend/src/api/types.ts`.
- **T-4:** Purpose: suggest button, loading state, and reviewable proposal UI in the shared recipe form. Covers FR-5, FR-6, FR-7, FR-8, NFR-3. Verify AC-1, AC-2, AC-3, AC-4, AC-5, AC-6. Files: `frontend/src/views/RecipesView.tsx`.
- **T-5:** Purpose: en/es translations for all new UI strings. Covers FR-9, NFR-3. Verify AC-1, AC-6. Files: `frontend/src/i18n/translations.ts`.
- **T-6:** Purpose: document and wire the server-side API key for deployment. Covers NFR-1. Verify AC-3 (deployment context). Files: `docker-compose.yml`, `README.md`, `.env.example`.

---

## Priority order

1. **P0** — T-1, T-2: the backend track is the core of the feature. Without the HTTP client (T-1) and the endpoint (T-2), no suggestion can be generated. T-1 is the highest-risk task (architecture decision required).
2. **P0** — T-3, T-4, T-5: the frontend track delivers the visible feature (button + proposal UI). T-4 depends on T-3 and T-5; all three are P0 because the feature is non-functional without any one of them.
3. **P1** — T-6: deployment documentation. The feature works during development without it, but the homeserver deliverable (NFR-1) requires the env var to be wired and documented.

---

## Dependencies and blockers

- T-1 depends on: architecture decision (HTTP client library: httpx vs requests vs google-genai SDK).
- T-2 depends on T-1 because the endpoint needs the HTTP client to call Gemini.
- T-3 depends on T-2 because the client function must be exercised against the real endpoint (contract fixed by FR-1).
- T-4 depends on T-3 and T-5 because the UI calls `suggestIngredients` and renders the keys defined by T-5.
- T-5 depends on nothing (keys are authored against the string list in FR-9).
- T-6 depends on T-2 because it documents the env var the endpoint reads.
- T-3, T-5, T-6 are independent of each other and can run in parallel after T-2.

---

## GitHub Projects mapping

Items start in Backlog: moving to Ready requires approved architecture, which does not exist yet at planning time.

| Task | Status | Priority | Effort |
|---|---|---|---|
| T-1 | Backlog | P0 | XS |
| T-2 | Backlog | P0 | M |
| T-3 | Backlog | P0 | XS |
| T-4 | Backlog | P0 | M |
| T-5 | Backlog | P0 | S |
| T-6 | Backlog | P1 | S |

---

## Suggested execution sequence

1. Human approves this plan; the architect produces an ADR resolving the HTTP client decision (T-1). Per `github-projects-policy.md`, the planner then moves items Backlog → Ready (requires human-approved architecture).
2. Then T-1 (dependency) and T-2 (endpoint) sequentially: T-1 first, then T-2 which depends on the chosen client.
3. Then in parallel: T-3 (client function), T-5 (i18n keys), T-6 (devops docs). All three depend on T-2 being complete.
4. Finally T-4 (button + proposal UI), which depends on T-3 and T-5.
5. Tester validates each task's acceptance criteria as it completes: AC-3 and AC-4 after T-2, AC-1/AC-5/AC-6 after T-4, AC-2 after T-4, AC-6 (Spanish output) after T-2 + T-4.

---

## Board updates

```text
Create issue "[AI suggestions] T-1: Add HTTP client dependency to backend requirements" (type: Chore), add to project 2, set Status Backlog, set Priority P0, set Effort XS, set Issue Type Chore, set Area Backend
Create issue "[AI suggestions] T-2: Implement POST /recipes/suggest-ingredients endpoint with Gemini integration" (type: Feature), add to project 2, set Status Backlog, set Priority P0, set Effort M, set Issue Type Feature, set Area Backend
Create issue "[AI suggestions] T-3: Add frontend API client function for suggest-ingredients" (type: Feature), add to project 2, set Status Backlog, set Priority P0, set Effort XS, set Issue Type Feature, set Area Frontend
Create issue "[AI suggestions] T-4: Add suggest button and proposal UI to the recipe form" (type: Feature), add to project 2, set Status Backlog, set Priority P0, set Effort M, set Issue Type Feature, set Area Frontend
Create issue "[AI suggestions] T-5: Add i18n keys for AI suggestions (en/es)" (type: Feature), add to project 2, set Status Backlog, set Priority P0, set Effort S, set Issue Type Feature, set Area Frontend
Create issue "[AI suggestions] T-6: Document GOOGLE_API_KEY setup for deployment" (type: Chore), add to project 2, set Status Backlog, set Priority P1, set Effort S, set Issue Type Chore, set Area DevOps
```

After the architect's ADR is approved, the planner moves the items Backlog → Ready (per `github-projects-policy.md:90`, planner-only transition, requires approved scope + ADRs).

---

**Approved by:** human  
**Approval date:** 2026-09-14  
**Next agent:** architect
