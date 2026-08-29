"""Pydantic request/response schemas for the FoodFlow API."""

from pydantic import BaseModel, Field


class RecipeCreate(BaseModel):
    name: str = Field(..., min_length=1)
    ingredients: list[str] = []


class RecipeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    ingredients: list[str] | None = None


class RecipeRead(BaseModel):
    id: int
    name: str
    ingredients: list[str]


class RecipeSummary(BaseModel):
    id: int
    name: str
    ingredient_count: int


class PlanCreate(BaseModel):
    name: str = Field(..., min_length=1)


class PlanUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    add_meals: list[int] | None = None
    remove_meal_ids: list[int] | None = None


class PlanMealRead(BaseModel):
    recipe_id: int
    name: str
    ingredient_count: int


class PlanRead(BaseModel):
    id: int
    name: str
    meals: list[PlanMealRead]


class ShoppingListRequest(BaseModel):
    plan_ids: list[int]


class ShoppingListRead(BaseModel):
    ingredients: list[str]