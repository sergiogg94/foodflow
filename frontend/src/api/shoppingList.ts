import { post } from "./client";
import type { ShoppingList } from "./types";

export function generateShoppingList(planIds: number[]): Promise<ShoppingList> {
  return post<ShoppingList>("/shopping-list", { plan_ids: planIds });
}