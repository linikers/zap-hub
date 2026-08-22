# React i18n — Zero-Dependency Translation System (absorbed from react-i18n skill)

## Architecture

```
src/lib/lang.tsx          ← translations + context + hook
src/components/Navbar.tsx ← toggle button (PT / EN)
src/app/layout.tsx        ← LangProvider wrapping the app
```

## 1. Translation File (`src/lib/lang.tsx`)

**MUST be `.tsx`** (contains JSX). **`"use client"` MUST be the very first line** — before any comment or import.

```tsx
"use client";
import { createContext, useContext, useState, useEffect, type ReactNode } from "react";

export type Lang = "pt-BR" | "en";

const translations: Record<Lang, Record<string, string>> = {
  "pt-BR": {
    "hero.subtitle": "Dashboard em tempo real",
    "nav.admin": "Admin",
  },
  en: {
    "hero.subtitle": "Real-time dashboard",
    "nav.admin": "Admin",
  },
};

export function t(lang: Lang, key: string, fallback?: string): string {
  return translations[lang]?.[key] ?? fallback ?? key;
}

const LangCtx = createContext<{
  lang: Lang;
  setLang: (l: Lang) => void;
  t: (key: string, fallback?: string) => string;
}>({
  lang: "pt-BR",
  setLang: () => {},
  t: (key: string) => key,
});

export function LangProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>("pt-BR");

  useEffect(() => {
    const stored = localStorage.getItem("polylink-lang") as Lang | null;
    if (stored === "en" || stored === "pt-BR") setLangState(stored);
  }, []);

  const setLang = (l: Lang) => {
    setLangState(l);
    localStorage.setItem("polylink-lang", l);
  };

  return (
    <LangCtx.Provider
      value={{ lang, setLang, t: (key: string, fallback?: string) => t(lang, key, fallback) }}
    >
      {children}
    </LangCtx.Provider>
  );
}

export function useLang() {
  return useContext(LangCtx);
}
```

## 2. Wrapping the App (`layout.tsx`)

```tsx
import { LangProvider } from "@/lib/lang";

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body>
        <LangProvider>
          {children}
        </LangProvider>
      </body>
    </html>
  );
}
```

## 3. Using Translations

### Client components (hook)
```tsx
"use client";
import { useLang } from "@/lib/lang";

export default function MyComponent() {
  const { t } = useLang();
  return <p>{t("hero.subtitle")}</p>;
}
```

### Server components
Cannot use hooks. Pass translations as props from a parent client component, or use the pure `t()` function with a hardcoded lang.

## 4. Language Toggle (MUI)

```tsx
"use client";
import { useLang } from "@/lib/lang";
import { ToggleButton, ToggleButtonGroup } from "@mui/material";

export default function Navbar() {
  const { lang, setLang, t } = useLang();
  return (
    <ToggleButtonGroup
      value={lang}
      exclusive
      onChange={(_, v) => v && setLang(v)}
      size="small"
    >
      <ToggleButton value="pt-BR">{t("nav.lang.pt")}</ToggleButton>
      <ToggleButton value="en">{t("nav.lang.en")}</ToggleButton>
    </ToggleButtonGroup>
  );
}
```

## Pitfalls

- **`"use client"` position** — must be line 1, before any comment or import
- **File extension** — `.tsx` required when file contains JSX
- **Context in server components** — hooks only work in client components
- **Translation keys have no type safety** — misspelled keys silently render the key string
- **⚠️ Variable shadowing of `t` in `.map()`** — This is the #1 runtime crash. `useLang()` returns `{ t }`. If a `.map()` callback uses `t` as its parameter, the inner `t` shadows the translation function → `TypeError: e is not a function`:
  ```tsx
  // BAD — t SHADOWS the outer t
  {items.map((t: any) => (
    <p>{t("my.key")}</p>  // t here is the ITEM, not the function!
  ))}

  // GOOD
  {items.map((item: any) => (
    <p>{t("my.key")}</p>  // t is still the translation function
  ))}
  ```
