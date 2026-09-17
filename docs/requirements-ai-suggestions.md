# Requirements: AI ingredient suggestions

**Date:** 2026-09-14  
**Project:** FoodFlow  
**Requested by:** human  
**Discovery:** `docs/discovery-ai-suggestions.md`  
**Status:** ✅ approved (2026-09-14)

---

## Scope summary

When creating or editing a recipe, the user clicks a button to get AI-generated ingredient suggestions based on the recipe name. Suggestions are returned via a backend call to Google AI Studio (Gemini) and presented as a proposal the user reviews and confirms before they are added to the recipe form.

---

## In scope

1. **POST /recipes/suggest-ingredients backend endpoint** — accepts a recipe name and the current UI language (en/es); calls Google AI Studio (Gemini) with a prompt requesting ingredient suggestions; returns a JSON array of ingredient name strings.
2. **API key management** — the Google AI Studio API key is read from the `GOOGLE_API_KEY` environment variable on the server side; never exposed to the frontend.
3. **Frontend API client function** — a typed function in `frontend/src/api/recipes.ts` that calls the new backend endpoint.
4. **Suggest button in the recipe form** — a button in both create and edit modes (the form is shared, `RecipesView.tsx:113-168`) that triggers the AI suggestion flow.
5. **Proposal UI** — suggestions are displayed to the user as a reviewable list separate from the existing ingredient rows. The user can review, edit, or remove individual suggestions and then confirm which ones to add to the form's ingredient list.
6. **Loading and error states** — while the API call is in progress, a loading indicator is shown and the suggest button is disabled (double-click protection). On failure, a translatable error message is displayed.
7. **i18n** — all new UI strings (button label, loading text, error messages, proposal labels) are added to `frontend/src/i18n/translations.ts` in both en and es (ADR-6).

---

## Out of scope

- Generating recipe names, preparation instructions, or any other content beyond ingredients.
- Automatically saving or merging suggestions without user review.
- Normalizing or deduplicating suggestions against existing recipes or ingredients.
- Support for AI providers other than Google AI Studio (Gemini).
- Offline or fallback suggestions when the API is unavailable.
- Cost controls, rate limiting, or usage tracking for the Gemini API.
- Modifying the recipe name input field or adding a free-text description field.
- Streaming responses from Gemini (suggestions are returned as a complete list).

---

## Functional requirements

**FR-1**  
The backend exposes a `POST /recipes/suggest-ingredients` endpoint that accepts a JSON body with `name` (string, required, non-blank) and `language` (string, required, one of `"en"` or `"es"`). It returns a JSON object with a `suggestions` field containing an array of ingredient name strings (zero or more).

**FR-2**  
The endpoint reads the Google AI Studio API key from the `GOOGLE_API_KEY` environment variable. If the variable is not set or is empty, the endpoint returns HTTP 503 with a detail message: `"AI suggestions are not configured"`.

**FR-3**  
The endpoint sends a prompt to the Google AI Studio (Gemini) API that includes: (a) the recipe name, (b) the requested language for output, and (c) an instruction to return only a JSON array of ingredient name strings. The endpoint parses the Gemini response and extracts the ingredient names into the `suggestions` array.

**FR-4**  
If the call to the Gemini API fails (network error, invalid API key, rate limit, or any non-200 response), the endpoint returns HTTP 502 with a detail message: `"Failed to get AI suggestions"`.

**FR-5**  
A "Suggest ingredients" button appears in the recipe form in both create mode (when `editingId === null`) and edit mode (when `editingId !== null`). The button is positioned within the ingredient section of the form, after the existing ingredient rows and the "Add ingredient" button.

**FR-6**  
When the user clicks the suggest button, the frontend sends a `POST /recipes/suggest-ingredients` request with the current value of the recipe name field and the current UI language (`en` or `es`). While the request is in flight, a loading indicator is shown and the suggest button is disabled to prevent duplicate requests.

**FR-7**  
When suggestions are returned, they are displayed in a reviewable list within the form. Each suggestion is shown as an editable text field with a toggle (selected by default). The user can modify the text of any suggestion, deselect it, or deselect all. An "Add" button incorporates only the selected suggestions as new ingredient rows appended to the existing ingredient list.

**FR-8**  
When the API call fails or the API key is not configured, a translatable error message is displayed in the form. The message matches the detail from the backend response.

**FR-9**  
New i18n keys are added under the `recipes` namespace in `frontend/src/i18n/translations.ts` for: suggest button label, loading indicator text, suggestion proposal heading, add button label, and error messages. All keys have values in both `en` and `es`.

---

## Non-functional requirements

**NFR-1 — Security**  
The `GOOGLE_API_KEY` environment variable must never be included in the frontend build, served to the browser, or committed to the repository. The API key flows exclusively: environment → backend endpoint → Google API.

**NFR-2 — No new frontend dependencies**  
The feature is implemented using only React, TypeScript, and the existing API client (`frontend/src/api/client.ts`). No new npm packages are added (ADR-2).

**NFR-3 — i18n compliance**  
Every user-facing string introduced by this feature exists in both `en` and `es` entries of `frontend/src/i18n/translations.ts`. The `language` parameter sent to the backend matches the current `lang` value from `useLanguage()` (ADR-6).

**NFR-4 — Existing patterns**  
The backend endpoint follows the existing route pattern in `backend/app/routes/recipes.py`: sync function, Pydantic schema validation, `os.environ.get()` for environment variables. The frontend function follows the pattern in `frontend/src/api/recipes.ts`: typed `post()` call through the shared client.

---

## Acceptance criteria

**AC-1**  
Given the user is in create or edit mode with a recipe name entered  
When they click the "Suggest ingredients" button  
Then the button becomes disabled, a loading indicator appears, and after the API responds, a list of editable ingredient suggestions is shown within the form.

**AC-2**  
Given AI suggestions are displayed in the proposal list  
When the user clicks "Add" with some suggestions selected  
Then only the selected suggestions are appended as new ingredient rows in the form, and the proposal list is dismissed.

**AC-3**  
Given the `GOOGLE_API_KEY` environment variable is not set  
When the user clicks the "Suggest ingredients" button  
Then an error message is displayed indicating that AI suggestions are not configured, and no API call is made from the frontend that would result in a 503.

**AC-4**  
Given the Gemini API returns an error (e.g. invalid key, rate limit)  
When the backend processes the request  
Then the endpoint returns HTTP 502 and the frontend displays the error message to the user.

**AC-5**  
Given the user clicks the suggest button while a request is already in flight  
Then the button is disabled and no duplicate request is sent.

**AC-6**  
Given the UI language is set to Spanish (`es`)  
When the user requests ingredient suggestions  
Then the suggestions are returned in Spanish.

---

## Edge cases

- **Empty recipe name**: if the user clicks the suggest button with an empty or blank recipe name, the frontend does not send the request and shows a validation message or disables the button.
- **Gemini returns an empty list**: the proposal section shows a message indicating no suggestions were found, and the user can dismiss it.
- **Gemini returns non-JSON or malformed response**: the backend returns HTTP 502 with a clear error, and the frontend displays the error.
- **Existing ingredients in edit mode**: suggestions are appended to the existing list; the user decides whether to keep the originals or the suggestions.
- **Rapid repeated clicks**: the button is disabled during the request, preventing duplicate API calls.
- **API key with extra whitespace**: the backend strips whitespace from the `GOOGLE_API_KEY` value before using it.

---

## Dependencies

- `backend/app/routes/recipes.py` — new endpoint added to the existing recipe router.
- `frontend/src/api/recipes.ts` — new function added alongside existing CRUD functions.
- `frontend/src/views/RecipesView.tsx` — form modified to include the suggest button and proposal UI.
- `frontend/src/i18n/translations.ts` — new keys added under the `recipes` namespace.
- `backend/requirements.txt` — a new dependency is required for making HTTP requests to the Gemini API (the backend currently has no HTTP client; the specific library is an architecture decision).
- Google AI Studio API — the feature is non-functional without a valid `GOOGLE_API_KEY`.

---

## Open questions

None.

---

## Board updates

None — planning owns item creation and state.

---

**Approved by:** human  
**Approval date:** 2026-09-14  
**Next agent:** planner
