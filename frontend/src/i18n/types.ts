import { translations } from "./translations";

export type Language = "en" | "es";
export type Namespace = keyof typeof translations["en"];
export type TranslationKeys = {
  [NS in Namespace]: keyof (typeof translations["en"])[NS];
};