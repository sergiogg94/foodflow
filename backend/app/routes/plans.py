"""Meal plan CRUD endpoints (T-3).

Each write runs inside a single SQLAlchemy transaction that commits atomically
(ADR-4). Plans are retained in history: creating or editing one plan never
overwrites another (FR-7).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Plan, PlanMeal, Recipe
from ..schemas import PlanCreate, PlanMealRead, PlanRead, PlanUpdate

router = APIRouter(prefix="/plans", tags=["plans"])


def _plan_to_read(plan: Plan) -> PlanRead:
    meals = [
        PlanMealRead(
            recipe_id=meal.recipe_id,
            name=meal.recipe.name,
            ingredient_count=len(meal.recipe.ingredients),
        )
        for meal in plan.meals
    ]
    return PlanRead(id=plan.id, name=plan.name, meals=meals)


@router.post("", response_model=PlanRead, status_code=201)
def create_plan(payload: PlanCreate, db: Session = Depends(get_db)) -> PlanRead:
    plan = Plan(name=payload.name)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return _plan_to_read(plan)


@router.get("", response_model=list[PlanRead])
def list_plans(db: Session = Depends(get_db)) -> list[PlanRead]:
    plans = db.scalars(select(Plan).order_by(Plan.created_at, Plan.id)).all()
    return [_plan_to_read(plan) for plan in plans]


@router.get("/{plan_id}", response_model=PlanRead)
def get_plan(plan_id: int, db: Session = Depends(get_db)) -> PlanRead:
    plan = db.get(Plan, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return _plan_to_read(plan)


@router.patch("/{plan_id}", response_model=PlanRead)
def update_plan(
    plan_id: int, payload: PlanUpdate, db: Session = Depends(get_db)
) -> PlanRead:
    plan = db.get(Plan, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    if payload.name is not None:
        plan.name = payload.name
    if payload.add_meals is not None:
        next_position = len(plan.meals)
        for recipe_id in payload.add_meals:
            recipe = db.get(Recipe, recipe_id)
            if recipe is None:
                raise HTTPException(
                    status_code=404, detail=f"Recipe {recipe_id} not found"
                )
            plan.meals.append(PlanMeal(recipe_id=recipe_id, position=next_position))
            next_position += 1
    if payload.remove_meal_ids is not None:
        remove_set = set(payload.remove_meal_ids)
        plan.meals = [meal for meal in plan.meals if meal.recipe_id not in remove_set]
        for position, meal in enumerate(plan.meals):
            meal.position = position
    db.commit()
    db.refresh(plan)
    return _plan_to_read(plan)


@router.delete("/{plan_id}", status_code=204)
def delete_plan(plan_id: int, db: Session = Depends(get_db)) -> None:
    plan = db.get(Plan, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(plan)
    db.commit()