import { useState } from "react";
import RecipesView from "./views/RecipesView";
import PlansView from "./views/PlansView";
import ShoppingListView from "./views/ShoppingListView";

type View = "recipes" | "plans" | "shopping";

const NAV_ITEMS: { id: View; label: string }[] = [
  { id: "recipes", label: "Recipes" },
  { id: "plans", label: "Plans" },
  { id: "shopping", label: "Shopping" },
];

export default function App() {
  const [view, setView] = useState<View>("recipes");

  return (
    <div className="app">
      <header className="app-header">
        <h1>FoodFlow</h1>
        <nav className="app-nav">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              className={`nav-button${view === item.id ? " active" : ""}`}
              onClick={() => setView(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </header>
      <main className="app-main">
        {view === "recipes" && <RecipesView />}
        {view === "plans" && <PlansView />}
        {view === "shopping" && <ShoppingListView />}
      </main>
    </div>
  );
}