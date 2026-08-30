"""FastAPI application entry point.

Serves the REST API under /recipes, /plans, and /shopping-list, enables CORS
for the Vite dev origin only (ADR-2), and mounts the built React SPA as static
files when present (ADR-3).
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .routes import plans, recipes, shopping_list

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATIC_DIR = REPO_ROOT / "frontend" / "dist"


def _static_dir() -> Path:
    """Directory containing the built React SPA.

    Defaults to <repo>/frontend/dist for local development. In the container
    (ADR-3) FOODFLOW_STATIC_DIR points at /app/static.
    """
    return Path(os.environ.get("FOODFLOW_STATIC_DIR", str(DEFAULT_STATIC_DIR)))


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="FoodFlow API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recipes.router)
app.include_router(plans.router)
app.include_router(shopping_list.router)

# Mount the built SPA last so API routes take precedence. In production the
# SPA and the API share a single origin, so no CORS is needed there (ADR-3).
static_dir = _static_dir()
if static_dir.is_dir():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")