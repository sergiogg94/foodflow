import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";
import { createPlan, deletePlan, listPlans, updatePlan } from "../api/plans";
import { listRecipes } from "../api/recipes";
import type { Plan, RecipeSummary } from "../api/types";
import { useLanguage, t, pluralize } from "../i18n";

export default function PlansView() {
  const { lang } = useLanguage();
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
      setError(e instanceof Error ? e.message : t(lang, "plans.error_load"));
    } finally {
      setLoading(false);
    }
  }, [lang]);

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
      setError(e instanceof Error ? e.message : t(lang, "plans.error_create"));
    }
  };

  const handleDeletePlan = async (id: number, name: string) => {
    if (!window.confirm(t(lang, "plans.confirm_delete", { name }))) return;
    setError(null);
    try {
      await deletePlan(id);
      if (selectedPlanId === id) setSelectedPlanId(null);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : t(lang, "plans.error_delete"));
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
      setError(e instanceof Error ? e.message : t(lang, "plans.error_add_meals"));
    }
  };

  const handleRemoveMeal = async (recipeId: number) => {
    if (!selectedPlan) return;
    setError(null);
    try {
      await updatePlan(selectedPlan.id, { remove_meal_ids: [recipeId] });
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : t(lang, "plans.error_remove_meal"));
    }
  };

  return (
    <section className="view">
      <h2>{t(lang, "plans.heading")}</h2>
      {error && <p className="error">{error}</p>}

      <form className="card" onSubmit={handleCreatePlan}>
        <h3>{t(lang, "plans.new_plan")}</h3>
        <label>
          {t(lang, "plans.name_label")}
          <input
            type="text"
            value={newPlanName}
            onChange={(e) => setNewPlanName(e.target.value)}
            placeholder={t(lang, "plans.placeholder")}
            required
          />
        </label>
        <button type="submit" className="button-primary">
          {t(lang, "plans.create")}
        </button>
      </form>

      {loading && <p>{t(lang, "plans.loading")}</p>}

      <div className="card">
        <h3>{t(lang, "plans.all_plans")}</h3>
        {!loading && plans.length === 0 && (
          <p className="empty-state">
            {t(lang, "plans.empty_list")}
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
                  {plan.meals.length}{" "}
                  {pluralize(
                    plan.meals.length,
                    t(lang, "plans.meal_singular"),
                    t(lang, "plans.meal_plural"),
                  )}
                </span>
              </button>
              <button
                className="button-danger"
                onClick={() => handleDeletePlan(plan.id, plan.name)}
              >
                {t(lang, "plans.delete")}
              </button>
            </li>
          ))}
        </ul>
      </div>

      {selectedPlan && (
        <div className="card">
          <h3>{selectedPlan.name}</h3>
          {selectedPlan.meals.length === 0 ? (
            <p className="empty-state">{t(lang, "plans.no_meals_yet")}</p>
          ) : (
            <ul className="meal-list">
              {selectedPlan.meals.map((meal, index) => (
                <li key={`${meal.recipe_id}-${index}`} className="meal-item">
                  <div className="meal-info">
                    <span className="meal-name">{meal.name}</span>
                    {meal.ingredient_count === 0 && (
                      <span className="tag">{t(lang, "plans.no_ingredients")}</span>
                    )}
                  </div>
                  <button
                    className="button-secondary"
                    onClick={() => handleRemoveMeal(meal.recipe_id)}
                  >
                    {t(lang, "plans.remove")}
                  </button>
                </li>
              ))}
            </ul>
          )}

          <div className="add-meals">
            <h4>{t(lang, "plans.add_meals_heading")}</h4>
            {recipes.length === 0 ? (
              <p className="empty-state">
                {t(lang, "plans.empty_recipes")}
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
                          <span className="tag">{t(lang, "plans.no_ingredients")}</span>
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
                  {t(lang, "plans.add_selected")}
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </section>
  );
}
