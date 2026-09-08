const translations = {
  en: {
    nav: {
      recipes: "Recipes",
      plans: "Plans",
      shopping: "Shopping",
    },
    recipes: {},
    plans: {},
    shopping: {},
  },
  es: {
    nav: {
      recipes: "Recetas",
      plans: "Planes",
      shopping: "Lista de la compra",
    },
    recipes: {},
    plans: {},
    shopping: {},
  },
} as const;

export type Namespace = keyof typeof translations["en"];
export type TranslationKey = {
  [NS in Namespace]: keyof (typeof translations["en"])[NS];
};

export { translations };
