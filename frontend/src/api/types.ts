export interface Recipe {
  id: number;
  name: string;
  ingredients: string[];
}

export interface RecipeSummary {
  id: number;
  name: string;
  ingredient_count: number;
}

export interface PlanMeal {
  recipe_id: number;
  name: string;
  ingredient_count: number;
}

export interface Plan {
  id: number;
  name: string;
  meals: PlanMeal[];
}

export interface ShoppingList {
  ingredients: string[];
}