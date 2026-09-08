import { useState } from "react";
import RecipesView from "./views/RecipesView";
import PlansView from "./views/PlansView";
import ShoppingListView from "./views/ShoppingListView";
import { LanguageProvider, useLanguage, t } from "./i18n";

type View = "recipes" | "plans" | "shopping";

const NAV_ITEMS: { id: View; key: string }[] = [
  { id: "recipes", key: "nav.recipes" },
  { id: "plans", key: "nav.plans" },
  { id: "shopping", key: "nav.shopping" },
];

function AppShell() {
  const [view, setView] = useState<View>("recipes");
  const { lang, setLang } = useLanguage();

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header-top">
          <h1>FoodFlow</h1>
          <select
            className="lang-selector"
            value={lang}
            onChange={(e) => setLang(e.target.value as "en" | "es")}
            aria-label="Language"
          >
            <option value="en">English</option>
            <option value="es">Espa&#241;ol</option>
          </select>
        </div>
        <nav className="app-nav">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.id}
              className={`nav-button${view === item.id ? " active" : ""}`}
              onClick={() => setView(item.id)}
            >
              {t(lang, item.key)}
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

export default function App() {
  return (
    <LanguageProvider>
      <AppShell />
    </LanguageProvider>
  );
}
