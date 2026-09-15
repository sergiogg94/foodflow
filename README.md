# FoodFlow

FoodFlow is a self-hosted weekly meal planner for two people who share a single recipe base. It runs as a Docker container on a homeserver and is used from a phone browser on the local network.

## What it does

- **Recipes** — create, read, update, and delete recipes. A recipe is a name plus an optional list of ingredient names; a recipe may have zero ingredients.
- **Meal plans** — create one or more plans as flexible lists of meals (not strict day-by-day slots). Plans are kept in a history: past plans remain viewable and are never overwritten by creating or editing another plan.
- **Shopping list** — select one or more plans and get a flat, deduplicated list of ingredient names, sorted alphabetically. An ingredient shared by several recipes appears only once. The list reflects the selected plans as they are edited.
- **"No ingredients" tag** — a recipe without ingredients is marked with a "no ingredients" tag in a plan view and contributes nothing to the shopping list.
- **Recipe uniqueness per plan** — each recipe appears at most once per plan; adding a recipe that is already in the plan is silently ignored (ADR-5).
- **Language switch (English ↔ Spanish)** — a selector in the app header toggles the interface between English and Spanish. All UI strings (navigation, headings, labels, buttons, placeholders, empty states, tags, confirmations, and pluralized counts) render in the selected language. The choice persists per device via `localStorage` and defaults to English. User-created data (recipe names, ingredient names, plan names) is never translated (ADR-6).

## Stack

- **Backend** — FastAPI with SQLAlchemy 2.0 over SQLite. Four tables (`recipes`, `recipe_ingredients`, `plans`, `plan_meals`); WAL mode, busy timeout, and foreign keys enabled.
- **Frontend** — Vite + React + TypeScript, mobile-first, with three views (Recipes, Plans, Shopping list), plain React state, a typed API client, and hand-rolled i18n (English ↔ Spanish, ADR-6).
- **Deployment** — a single docker-compose service. The React app is built at image build time and served by the FastAPI backend; the SQLite database is persisted on a `./data` bind mount. The app listens on port 8000.

There is no authentication. The app is intended for the local network only; anyone who can reach it can read and modify the data. Concurrent edits follow a last-change-wins rule (ADR-4).

## Run it

Prerequisites: Docker and docker-compose on the host.

```bash
docker compose up -d --build
```

Then open `http://<host>:8000` in a browser. Data is stored in `./data/foodflow.db` and survives container recreation.

### AI ingredient suggestions (optional)

The "Suggest ingredients" button in the recipe form calls Google AI Studio (Gemini) through the backend endpoint `POST /recipes/suggest-ingredients`. The API key is read server-side from the `GOOGLE_API_KEY` environment variable and is never exposed to the frontend or committed to the repository (NFR-1).

To enable the feature:

1. Create a `.env` file in the repository root (it is gitignored, `.gitignore:15` — never commit it):
   ```bash
   GOOGLE_API_KEY=<your-key>
   ```
2. `docker compose up -d --build` picks the key up automatically; docker-compose passes it to the container via the `env` section in `docker-compose.yml`.

If `GOOGLE_API_KEY` is not set, the endpoint returns HTTP 503 with detail `"AI suggestions are not configured"` and the form shows the corresponding error message. The rest of the app works normally without the key.

## Documentation

- `docs/requirements.md` — scope, functional requirements, and acceptance criteria
- `docs/architecture.md` — architecture summary and ADR index
- `docs/adr/` — architecture decision records (ADR-1..ADR-6)
- `docs/delivery-checklist.md` — delivery status and open risks