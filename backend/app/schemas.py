"""Pydantic request/response schemas for the FoodFlow API."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class RecipeCreate(BaseModel):
    name: str = Field(..., min_length=1)
    ingredients: list[str] = []

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        """Reject names that are empty or only whitespace (FR-1: non-empty).

        The stored value is preserved as provided; only whitespace-only input
        is rejected (review finding NB-1).
        """
        if value.strip() == "":
            raise ValueError("Recipe name must not be blank")
        return value


class RecipeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    ingredients: list[str] | None = None

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str | None) -> str | None:
        """Reject names that are empty or only whitespace (FR-1: non-empty)."""
        if value is not None and value.strip() == "":
            raise ValueError("Recipe name must not be blank")
        return value


class RecipeRead(BaseModel):
    id: int
    name: str
    ingredients: list[str]


class RecipeSummary(BaseModel):
    id: int
    name: str
    ingredient_count: int


class SuggestIngredientsRequest(BaseModel):
    name: str = Field(..., min_length=1)
    language: Literal["en", "es"]

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        """Reject names that are empty or only whitespace (FR-1: non-blank)."""
        if value.strip() == "":
            raise ValueError("Recipe name must not be blank")
        return value


class SuggestIngredientsResponse(BaseModel):
    suggestions: list[str]


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