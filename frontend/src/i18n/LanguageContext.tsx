import { createContext, useContext, useState, useCallback } from "react";
import type { ReactNode } from "react";
import type { Language } from "./types";
import { translations } from "./translations";

const STORAGE_KEY = "foodflow-lang";

function getInitialLang(): Language {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "en" || stored === "es") return stored;
  } catch {
    // localStorage unavailable (SSR, privacy settings) — fall back to default.
  }
  return "en";
}

interface LanguageContextValue {
  lang: Language;
  setLang: (lang: Language) => void;
}

const LanguageContext = createContext<LanguageContextValue | null>(null);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Language>(getInitialLang);

  const setLang = useCallback((newLang: Language) => {
    setLangState(newLang);
    try {
      localStorage.setItem(STORAGE_KEY, newLang);
    } catch {
      // Ignore write failures silently.
    }
    document.documentElement.lang = newLang;
  }, []);

  // Keep document.lang in sync on mount.
  if (document.documentElement.lang !== lang) {
    document.documentElement.lang = lang;
  }

  return (
    <LanguageContext.Provider value={{ lang, setLang }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage(): LanguageContextValue {
  const ctx = useContext(LanguageContext);
  if (!ctx) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return ctx;
}

/**
 * Translation function. Looks up `key` (dot-separated, e.g. "recipes.heading")
 * in the dictionary for the given `lang`. Supports `{{param}}` interpolation.
 */
export function t(
  lang: Language,
  key: string,
  params?: Record<string, string | number>,
): string {
  const dotIndex = key.indexOf(".");
  if (dotIndex === -1) return key;
  const namespace = key.slice(0, dotIndex);
  const subKey = key.slice(dotIndex + 1);

  const dict = translations[lang]?.[namespace as keyof (typeof translations)["en"]];
  if (!dict) return key;
  const value = dict[subKey as keyof (typeof dict)];
  if (typeof value !== "string") return key;
  if (!params) return value;
  return Object.entries(params).reduce<string>(
    (result, [param, val]) =>
      result.replace(new RegExp(`\\{\\{${param}\\}\\}`, "g"), String(val)),
    value,
  );
}

export function pluralize(count: number, singular: string, plural: string): string {
  return count === 1 ? singular : plural;
}
