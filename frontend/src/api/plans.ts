import { del, get, patch, post } from "./client";
import type { Plan } from "./types";

export function listPlans(): Promise<Plan[]> {
  return get<Plan[]>("/plans");
}

export function getPlan(id: number): Promise<Plan> {
  return get<Plan>(`/plans/${id}`);
}

export function createPlan(name: string): Promise<Plan> {
  return post<Plan>("/plans", { name });
}

export function updatePlan(
  id: number,
  patchBody: { name?: string; add_meals?: number[]; remove_meal_ids?: number[] }
): Promise<Plan> {
  return patch<Plan>(`/plans/${id}`, patchBody);
}

export function deletePlan(id: number): Promise<void> {
  return del<void>(`/plans/${id}`);
}