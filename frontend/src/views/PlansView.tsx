import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";
import { createPlan, deletePlan, listPlans, updatePlan } from "../api/plans";
import { listRecipes } from "../api/recipes";
import type { Plan, RecipeSummary } from "../api/types";

export default function PlansView() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [recipes, setRecipes] = useState<RecipeSummary[]>([]);
  const [selectedPlanId, setSelectedPlanId] = useState<number | null>(null);
  const [newPlanName, setNewPlanName] = useState("");
  const [selectedRecipeIds, setSelectedRecipeIds] = useState<number[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const selectedPlan = plans.find((p) => p.id === selectedPlanId) ?? null;

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [plansData, recipesData] = await Promise.all([
        listPlans(),
        listRecipes(),
      ]);
      setPlans(plansData);
      setRecipes(recipesData);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load plans");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleCreatePlan = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!newPlanName.trim()) return;
    setError(null);
    try {
      const plan = await createPlan(newPlanName.trim());
      setNewPlanName("");
      await refresh();
      setSelectedPlanId(plan.id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create plan");
    }
  };

  const handleDeletePlan = async (id: number, name: string) => {
    if (!window.confirm(`Delete plan "${name}"?`)) return;
    setError(null);
    try {
      await deletePlan(id);
      if (selectedPlanId === id) setSelectedPlanId(null);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to delete plan");
    }
  };

  const toggleRecipeSelection = (recipeId: number) => {
    setSelectedRecipeIds((prev) =>
      prev.includes(recipeId)
        ? prev.filter((id) => id !== recipeId)
        : [...prev, recipeId]
    );
  };

  const handleAddMeals = async () => {
    if (!selectedPlan || selectedRecipeIds.length === 0) return;
    setError(null);
    try {
      await updatePlan(selectedPlan.id, { add_meals: selectedRecipeIds });
      setSelectedRecipeIds([]);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to add meals");
    }
  };

  const handleRemoveMeal = async (recipeId: number) => {
    if (!selectedPlan) return;
    setError(null);
    try {
      await updatePlan(selectedPlan.id, { remove_meal_ids: [recipeId] });
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to remove meal");
    }
  };

  return (
    <section className="view">
      <h2>Plans</h2>
      {error && <p className="error">{error}</p>}

      <form className="card" onSubmit={handleCreatePlan}>
        <h3>New plan</h3>
        <label>
          Name
          <input
            type="text"
            value={newPlanName}
            onChange={(e) => setNewPlanName(e.target.value)}
            placeholder="e.g. This week"
            required
          />
        </label>
        <button type="submit" className="button-primary">
          Create plan
        </button>
      </form>

      {loading && <p>Loading…</p>}

      <div className="card">
        <h3>All plans</h3>
        {!loading && plans.length === 0 && (
          <p className="empty-state">
            No plans yet. Create your first plan above.
          </p>
        )}
        <ul className="plan-list">
          {plans.map((plan) => (
            <li key={plan.id} className="plan-item">
              <button
                className={`plan-select${selectedPlanId === plan.id ? " active" : ""}`}
                onClick={() => setSelectedPlanId(plan.id)}
              >
                <span className="plan-name">{plan.name}</span>
                <span className="plan-count">
                  {plan.meals.length} meal{plan.meals.length === 1 ? "" : "s"}
                </span>
              </button>
              <button
                className="button-danger"
                onClick={() => handleDeletePlan(plan.id, plan.name)}
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      </div>

      {selectedPlan && (
        <div className="card">
          <h3>{selectedPlan.name}</h3>
          {selectedPlan.meals.length === 0 ? (
            <p className="empty-state">This plan has no meals yet.</p>
          ) : (
            <ul className="meal-list">
              {selectedPlan.meals.map((meal, index) => (
                <li key={`${meal.recipe_id}-${index}`} className="meal-item">
                  <div className="meal-info">
                    <span className="meal-name">{meal.name}</span>
                    {meal.ingredient_count === 0 && (
                      <span className="tag">no ingredients</span>
                    )}
                  </div>
                  <button
                    className="button-secondary"
                    onClick={() => handleRemoveMeal(meal.recipe_id)}
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          )}

          <div className="add-meals">
            <h4>Add meals</h4>
            {recipes.length === 0 ? (
              <p className="empty-state">
                No recipes yet. Create recipes first, then add them to this
                plan.
              </p>
            ) : (
              <>
                <ul className="recipe-picker">
                  {recipes.map((recipe) => (
                    <li key={recipe.id}>
                      <label className="recipe-picker-item">
                        <input
                          type="checkbox"
                          checked={selectedRecipeIds.includes(recipe.id)}
                          onChange={() => toggleRecipeSelection(recipe.id)}
                        />
                        <span>{recipe.name}</span>
                        {recipe.ingredient_count === 0 && (
                          <span className="tag">no ingredients</span>
                        )}
                      </label>
                    </li>
                  ))}
                </ul>
                <button
                  type="button"
                  className="button-primary"
                  onClick={handleAddMeals}
                  disabled={selectedRecipeIds.length === 0}
                >
                  Add selected meals
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </section>
  );
}