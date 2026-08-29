"""Shopping list generation endpoint (T-4).

Takes one or more plan ids and returns a flat, deduplicated list of ingredient
names aggregated from the recipes in those plans. Deduplication is a
case-sensitive exact match (architecture.md:62). Empty plans and recipes
without ingredients contribute nothing.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Plan
from ..schemas import ShoppingListRead, ShoppingListRequest

router = APIRouter(prefix="/shopping-list", tags=["shopping-list"])


@router.post("", response_model=ShoppingListRead)
def generate_shopping_list(
    payload: ShoppingListRequest, db: Session = Depends(get_db)
) -> ShoppingListRead:
    ingredients: set[str] = set()
    for plan_id in payload.plan_ids:
        plan = db.get(Plan, plan_id)
        if plan is None:
            raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
        for meal in plan.meals:
            for ingredient in meal.recipe.ingredients:
                ingredients.add(ingredient.name)
    return ShoppingListRead(ingredients=sorted(ingredients))