import { useCallback, useEffect, useState } from "react";
import type { FormEvent } from "react";
import {
  createRecipe,
  deleteRecipe,
  getRecipe,
  listRecipes,
  updateRecipe,
} from "../api/recipes";
import type { Recipe, RecipeSummary } from "../api/types";
import { useLanguage, t, pluralize } from "../i18n";

interface RecipeFormState {
  name: string;
  ingredients: string[];
}

const EMPTY_FORM: RecipeFormState = { name: "", ingredients: [] };

export default function RecipesView() {
  const { lang } = useLanguage();
  const [recipes, setRecipes] = useState<RecipeSummary[]>([]);
  const [filter, setFilter] = useState("");
  const [form, setForm] = useState<RecipeFormState>(EMPTY_FORM);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setRecipes(await listRecipes(filter || undefined));
    } catch (e) {
      setError(e instanceof Error ? e.message : t(lang, "recipes.error_load"));
    } finally {
      setLoading(false);
    }
  }, [filter, lang]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      const ingredients = form.ingredients.filter((i) => i.trim() !== "");
      if (editingId === null) {
        await createRecipe(form.name, ingredients);
      } else {
        await updateRecipe(editingId, { name: form.name, ingredients });
      }
      setForm(EMPTY_FORM);
      setEditingId(null);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : t(lang, "recipes.error_save"));
    }
  };

  const handleEdit = async (id: number) => {
    setError(null);
    try {
      const recipe: Recipe = await getRecipe(id);
      setEditingId(id);
      setForm({ name: recipe.name, ingredients: recipe.ingredients });
    } catch (e) {
      setError(e instanceof Error ? e.message : t(lang, "recipes.error_load_one"));
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (!window.confirm(t(lang, "recipes.confirm_delete", { name }))) return;
    setError(null);
    try {
      await deleteRecipe(id);
      if (editingId === id) {
        setEditingId(null);
        setForm(EMPTY_FORM);
      }
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : t(lang, "recipes.error_delete"));
    }
  };

  const updateIngredient = (index: number, value: string) => {
    setForm((prev) => {
      const ingredients = [...prev.ingredients];
      ingredients[index] = value;
      return { ...prev, ingredients };
    });
  };

  const addIngredientRow = () => {
    setForm((prev) => ({ ...prev, ingredients: [...prev.ingredients, ""] }));
  };

  const removeIngredientRow = (index: number) => {
    setForm((prev) => ({
      ...prev,
      ingredients: prev.ingredients.filter((_, i) => i !== index),
    }));
  };

  return (
    <section className="view">
      <h2>{t(lang, "recipes.heading")}</h2>
      {error && <p className="error">{error}</p>}

      <form className="card" onSubmit={handleSubmit}>
        <h3>{editingId === null ? t(lang, "recipes.new_recipe") : t(lang, "recipes.edit_recipe")}</h3>
        <label>
          {t(lang, "recipes.name_label")}
          <input
            type="text"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
        </label>
        <div className="ingredient-list">
          <span className="label">{t(lang, "recipes.ingredients_label")}</span>
          {form.ingredients.map((ingredient, index) => (
            <div className="ingredient-row" key={index}>
              <input
                type="text"
                value={ingredient}
                onChange={(e) => updateIngredient(index, e.target.value)}
                placeholder={t(lang, "recipes.ingredient_placeholder")}
              />
              <button
                type="button"
                className="button-secondary"
                onClick={() => removeIngredientRow(index)}
              >
                {t(lang, "recipes.remove")}
              </button>
            </div>
          ))}
          <button
            type="button"
            className="button-secondary"
            onClick={addIngredientRow}
          >
            {t(lang, "recipes.add_ingredient")}
          </button>
        </div>
        <div className="form-actions">
          <button type="submit" className="button-primary">
            {editingId === null ? t(lang, "recipes.create") : t(lang, "recipes.save")}
          </button>
          {editingId !== null && (
            <button
              type="button"
              className="button-secondary"
              onClick={() => {
                setEditingId(null);
                setForm(EMPTY_FORM);
              }}
            >
              {t(lang, "recipes.cancel")}
            </button>
          )}
        </div>
      </form>

      <div className="card">
        <label>
          {t(lang, "recipes.search_label")}
          <input
            type="search"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder={t(lang, "recipes.filter_placeholder")}
          />
        </label>
        {loading && <p>{t(lang, "recipes.loading")}</p>}
        {!loading && recipes.length === 0 && (
          <p className="empty-state">
            {filter
              ? t(lang, "recipes.empty_search")
              : t(lang, "recipes.empty_list")}
          </p>
        )}
        <ul className="recipe-list">
          {recipes.map((recipe) => (
            <li key={recipe.id} className="recipe-item">
              <div className="recipe-info">
                <span className="recipe-name">{recipe.name}</span>
                <span className="recipe-count">
                  {recipe.ingredient_count}{" "}
                  {pluralize(
                    recipe.ingredient_count,
                    t(lang, "recipes.ingredient_singular"),
                    t(lang, "recipes.ingredient_plural"),
                  )}
                </span>
              </div>
              <div className="recipe-actions">
                <button
                  className="button-secondary"
                  onClick={() => handleEdit(recipe.id)}
                >
                  {t(lang, "recipes.edit")}
                </button>
                <button
                  className="button-danger"
                  onClick={() => handleDelete(recipe.id, recipe.name)}
                >
                  {t(lang, "recipes.delete")}
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
