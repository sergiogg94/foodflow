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

interface RecipeFormState {
  name: string;
  ingredients: string[];
}

const EMPTY_FORM: RecipeFormState = { name: "", ingredients: [] };

export default function RecipesView() {
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
      setError(e instanceof Error ? e.message : "Failed to load recipes");
    } finally {
      setLoading(false);
    }
  }, [filter]);

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
      setError(e instanceof Error ? e.message : "Failed to save recipe");
    }
  };

  const handleEdit = async (id: number) => {
    setError(null);
    try {
      const recipe: Recipe = await getRecipe(id);
      setEditingId(id);
      setForm({ name: recipe.name, ingredients: recipe.ingredients });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load recipe");
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (!window.confirm(`Delete recipe "${name}"?`)) return;
    setError(null);
    try {
      await deleteRecipe(id);
      if (editingId === id) {
        setEditingId(null);
        setForm(EMPTY_FORM);
      }
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to delete recipe");
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
      <h2>Recipes</h2>
      {error && <p className="error">{error}</p>}

      <form className="card" onSubmit={handleSubmit}>
        <h3>{editingId === null ? "New recipe" : "Edit recipe"}</h3>
        <label>
          Name
          <input
            type="text"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            required
          />
        </label>
        <div className="ingredient-list">
          <span className="label">Ingredients (optional)</span>
          {form.ingredients.map((ingredient, index) => (
            <div className="ingredient-row" key={index}>
              <input
                type="text"
                value={ingredient}
                onChange={(e) => updateIngredient(index, e.target.value)}
                placeholder="Ingredient name"
              />
              <button
                type="button"
                className="button-secondary"
                onClick={() => removeIngredientRow(index)}
              >
                Remove
              </button>
            </div>
          ))}
          <button
            type="button"
            className="button-secondary"
            onClick={addIngredientRow}
          >
            Add ingredient
          </button>
        </div>
        <div className="form-actions">
          <button type="submit" className="button-primary">
            {editingId === null ? "Create recipe" : "Save changes"}
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
              Cancel
            </button>
          )}
        </div>
      </form>

      <div className="card">
        <label>
          Search
          <input
            type="search"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Filter by name"
          />
        </label>
        {loading && <p>Loading…</p>}
        {!loading && recipes.length === 0 && (
          <p className="empty-state">
            {filter
              ? "No recipes match your search."
              : "No recipes yet. Create your first recipe above."}
          </p>
        )}
        <ul className="recipe-list">
          {recipes.map((recipe) => (
            <li key={recipe.id} className="recipe-item">
              <div className="recipe-info">
                <span className="recipe-name">{recipe.name}</span>
                <span className="recipe-count">
                  {recipe.ingredient_count} ingredient
                  {recipe.ingredient_count === 1 ? "" : "s"}
                </span>
              </div>
              <div className="recipe-actions">
                <button
                  className="button-secondary"
                  onClick={() => handleEdit(recipe.id)}
                >
                  Edit
                </button>
                <button
                  className="button-danger"
                  onClick={() => handleDelete(recipe.id, recipe.name)}
                >
                  Delete
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}