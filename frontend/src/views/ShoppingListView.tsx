import { useCallback, useEffect, useState } from "react";
import { listPlans } from "../api/plans";
import { generateShoppingList } from "../api/shoppingList";
import type { Plan, ShoppingList } from "../api/types";
import { useLanguage, t, pluralize } from "../i18n";

export default function ShoppingListView() {
  const { lang } = useLanguage();
  const [plans, setPlans] = useState<Plan[]>([]);
  const [selectedPlanIds, setSelectedPlanIds] = useState<number[]>([]);
  const [shoppingList, setShoppingList] = useState<ShoppingList>({
    ingredients: [],
  });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const refreshPlans = useCallback(async () => {
    setError(null);
    try {
      setPlans(await listPlans());
    } catch (e) {
      setError(e instanceof Error ? e.message : t(lang, "shopping.error_load_plans"));
    }
  }, [lang]);

  useEffect(() => {
    refreshPlans();
  }, [refreshPlans]);

  // Refetch the shopping list whenever the plan selection changes, so the
  // list reflects plan edits in real time (FR-8).
  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (selectedPlanIds.length === 0) {
        setShoppingList({ ingredients: [] });
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const result = await generateShoppingList(selectedPlanIds);
        if (!cancelled) setShoppingList(result);
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : t(lang, "shopping.error_generate"));
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [selectedPlanIds, lang]);

  const togglePlan = (planId: number) => {
    setSelectedPlanIds((prev) =>
      prev.includes(planId)
        ? prev.filter((id) => id !== planId)
        : [...prev, planId]
    );
  };

  return (
    <section className="view">
      <h2>{t(lang, "shopping.heading")}</h2>
      {error && <p className="error">{error}</p>}

      <div className="card">
        <h3>{t(lang, "shopping.select_plans")}</h3>
        {plans.length === 0 ? (
          <p className="empty-state">
            {t(lang, "shopping.empty_plans")}
          </p>
        ) : (
          <ul className="plan-picker">
            {plans.map((plan) => (
              <li key={plan.id}>
                <label className="plan-picker-item">
                  <input
                    type="checkbox"
                    checked={selectedPlanIds.includes(plan.id)}
                    onChange={() => togglePlan(plan.id)}
                  />
                  <span>{plan.name}</span>
                  <span className="plan-count">
                    {plan.meals.length}{" "}
                    {pluralize(
                      plan.meals.length,
                      t(lang, "shopping.meal_singular"),
                      t(lang, "shopping.meal_plural")
                    )}
                  </span>
                </label>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="card">
        <h3>{t(lang, "shopping.ingredients_heading")}</h3>
        {loading && <p>{t(lang, "shopping.loading")}</p>}
        {!loading && selectedPlanIds.length === 0 && (
          <p className="empty-state">
            {t(lang, "shopping.select_plan_hint")}
          </p>
        )}
        {!loading &&
          selectedPlanIds.length > 0 &&
          shoppingList.ingredients.length === 0 && (
            <p className="empty-state">{t(lang, "shopping.empty_ingredients")}</p>
          )}
        {!loading && shoppingList.ingredients.length > 0 && (
          <ul className="shopping-list">
            {shoppingList.ingredients.map((ingredient) => (
              <li key={ingredient}>{ingredient}</li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}