import { del, get, patch, post } from "./client";
import type { Recipe, RecipeSummary } from "./types";

export function listRecipes(filter?: string): Promise<RecipeSummary[]> {
  const query = filter ? `?filter=${encodeURIComponent(filter)}` : "";
  return get<RecipeSummary[]>(`/recipes${query}`);
}

export function getRecipe(id: number): Promise<Recipe> {
  return get<Recipe>(`/recipes/${id}`);
}

export function createRecipe(name: string, ingredients: string[]): Promise<Recipe> {
  return post<Recipe>("/recipes", { name, ingredients });
}

export function updateRecipe(
  id: number,
  patchBody: { name?: string; ingredients?: string[] }
): Promise<Recipe> {
  return patch<Recipe>(`/recipes/${id}`, patchBody);
}

export function deleteRecipe(id: number): Promise<void> {
  return del<void>(`/recipes/${id}`);
}