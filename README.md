# FoodFlow

FoodFlow is a self-hosted weekly meal planner for two people who share a single recipe base. It runs as a Docker container on a homeserver and is used from a phone browser on the local network.

## What it does

- **Recipes** — create, read, update, and delete recipes. A recipe is a name plus an optional list of ingredient names; a recipe may have zero ingredients.
- **Meal plans** — create one or more plans as flexible lists of meals (not strict day-by-day slots). Plans are kept in a history: past plans remain viewable and are never overwritten by creating or editing another plan.
- **Shopping list** — select one or more plans and get a flat, deduplicated list of ingredient names, sorted alphabetically. An ingredient shared by several recipes appears only once. The list reflects the selected plans as they are edited.
- **"No ingredients" tag** — a recipe without ingredients is marked with a "no ingredients" tag in a plan view and contributes nothing to the shopping list.
- **Recipe uniqueness per plan** — each recipe appears at most once per plan; adding a recipe that is already in the plan is silently ignored (ADR-5).

## Stack

- **Backend** — FastAPI with SQLAlchemy 2.0 over SQLite. Four tables (`recipes`, `recipe_ingredients`, `plans`, `plan_meals`); WAL mode, busy timeout, and foreign keys enabled.
- **Frontend** — Vite + React + TypeScript, mobile-first, with three views (Recipes, Plans, Shopping list), plain React state, and a typed API client.
- **Deployment** — a single docker-compose service. The React app is built at image build time and served by the FastAPI backend; the SQLite database is persisted on a `./data` bind mount. The app listens on port 8000.

There is no authentication. The app is intended for the local network only; anyone who can reach it can read and modify the data. Concurrent edits follow a last-change-wins rule (ADR-4).

## Run it

Prerequisites: Docker and docker-compose on the host.

```bash
docker compose up -d --build
```

Then open `http://<host>:8000` in a browser. Data is stored in `./data/foodflow.db` and survives container recreation.

## Documentation

- `docs/requirements.md` — scope, functional requirements, and acceptance criteria
- `docs/architecture.md` — architecture summary and ADR index
- `docs/adr/` — architecture decision records (ADR-1..ADR-5)
- `docs/delivery-checklist.md` — delivery status and open risks