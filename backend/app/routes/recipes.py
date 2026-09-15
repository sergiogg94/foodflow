"""Recipe CRUD endpoints (T-2) and AI ingredient suggestions (T-2, ADR-7).

Each write runs inside a single SQLAlchemy transaction that commits atomically
(ADR-4). All persistence goes through the SQLAlchemy data layer; no hand-written
SQL in route modules (ADR-1 guard rail). The suggest-ingredients endpoint calls
the Gemini API synchronously with httpx (ADR-7); the GOOGLE_API_KEY stays
server-side (NFR-1).
"""

import json
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Recipe, RecipeIngredient
from ..schemas import (
    RecipeCreate,
    RecipeRead,
    RecipeSummary,
    RecipeUpdate,
    SuggestIngredientsRequest,
    SuggestIngredientsResponse,
)

router = APIRouter(prefix="/recipes", tags=["recipes"])

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3.1-flash-lite:generateContent"
)


def _recipe_to_read(recipe: Recipe) -> RecipeRead:
    return RecipeRead(
        id=recipe.id,
        name=recipe.name,
        ingredients=[ingredient.name for ingredient in recipe.ingredients],
    )


@router.post("", response_model=RecipeRead, status_code=201)
def create_recipe(payload: RecipeCreate, db: Session = Depends(get_db)) -> RecipeRead:
    recipe = Recipe(name=payload.name)
    for position, name in enumerate(payload.ingredients):
        recipe.ingredients.append(RecipeIngredient(name=name, position=position))
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return _recipe_to_read(recipe)


@router.post("/suggest-ingredients", response_model=SuggestIngredientsResponse)
def suggest_ingredients(
    payload: SuggestIngredientsRequest,
) -> SuggestIngredientsResponse:
    """Suggest main ingredients for a recipe name via Gemini (FR-1..FR-4).

    Reads GOOGLE_API_KEY from the environment and strips whitespace; returns
    503 when it is missing or empty (FR-2). Calls the Gemini API synchronously
    with a per-request httpx.Client (ADR-7) and maps every Gemini failure —
    network, timeout, non-200, malformed body — to 502 (FR-4).
    """
    api_key = os.environ.get("GOOGLE_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=503, detail="AI suggestions are not configured"
        )

    language_name = "English" if payload.language == "en" else "Spanish"
    prompt = (
        f"Suggest the main ingredients for the recipe \"{payload.name}\".\n"
        f"Respond in {language_name}.\n"
        "Return only a JSON array of ingredient name strings, with no "
        "additional text or explanation.\n"
        "Exclude pantry staples such as salt, oil, spices, and other basic "
        "seasonings; include only the main ingredients that would commonly "
        "go on a weekly shopping list."
    )

    request_body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {"type": "ARRAY", "items": {"type": "STRING"}},
        },
    }

    try:
        client = httpx.Client(timeout=30.0)
        response = client.post(
            GEMINI_API_URL,
            json=request_body,
            headers={"x-goog-api-key": api_key},
        )
        response.raise_for_status()
        data = response.json()
        raw = data["candidates"][0]["content"]["parts"][0]["text"]
        suggestions = json.loads(raw)
        if not isinstance(suggestions, list):
            raise TypeError("Gemini response is not a JSON array")
        return SuggestIngredientsResponse(suggestions=suggestions)
    except (httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError):
        raise HTTPException(status_code=502, detail="Failed to get AI suggestions")


@router.get("", response_model=list[RecipeSummary])
def list_recipes(
    filter: str | None = None, db: Session = Depends(get_db)
) -> list[RecipeSummary]:
    stmt = select(Recipe).order_by(Recipe.name)
    if filter:
        stmt = stmt.where(Recipe.name.contains(filter))
    recipes = db.scalars(stmt).all()
    return [
        RecipeSummary(
            id=recipe.id,
            name=recipe.name,
            ingredient_count=len(recipe.ingredients),
        )
        for recipe in recipes
    ]


@router.get("/{recipe_id}", response_model=RecipeRead)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)) -> RecipeRead:
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return _recipe_to_read(recipe)


@router.patch("/{recipe_id}", response_model=RecipeRead)
def update_recipe(
    recipe_id: int, payload: RecipeUpdate, db: Session = Depends(get_db)
) -> RecipeRead:
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if payload.name is not None:
        recipe.name = payload.name
    if payload.ingredients is not None:
        recipe.ingredients.clear()
        for position, name in enumerate(payload.ingredients):
            recipe.ingredients.append(RecipeIngredient(name=name, position=position))
    db.commit()
    db.refresh(recipe)
    return _recipe_to_read(recipe)


@router.delete("/{recipe_id}", status_code=204)
def delete_recipe(recipe_id: int, db: Session = Depends(get_db)) -> None:
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    # ON DELETE CASCADE on plan_meals.recipe_id removes the recipe from every
    # plan that includes it (FR-5).
    db.delete(recipe)
    db.commit()