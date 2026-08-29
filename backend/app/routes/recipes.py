"""Recipe CRUD endpoints (T-2).

Each write runs inside a single SQLAlchemy transaction that commits atomically
(ADR-4). All persistence goes through the SQLAlchemy data layer; no hand-written
SQL in route modules (ADR-1 guard rail).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Recipe, RecipeIngredient
from ..schemas import RecipeCreate, RecipeRead, RecipeSummary, RecipeUpdate

router = APIRouter(prefix="/recipes", tags=["recipes"])


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