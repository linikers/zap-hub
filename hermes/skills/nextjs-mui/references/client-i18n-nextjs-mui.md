# Client-Side i18n for Next.js + MUI

Lightweight in-app translation system without external dependencies. Ideal for small-to-medium apps that need pt-BR + English (or similar dual-language support).

## Architecture

```
src/lib/lang.tsx          ← Language context + translation map + provider
src/components/Navbar.tsx ← ToggleButton PT | EN in the navbar
src/app/layout.tsx        ← Wrap with LangProvider
Every component            ← useLang() hook
```

## Implementation

### 1. Translation Map + Context (`src/lib/lang.tsx`)

```tsx
"use client";  // MUST be line 1 — no comments before it
import { createContext, useContext, useState, useEffect, type ReactNode } from "react";

export type Lang = "pt-BR" | "en";
const STORAGE_KEY = "app-lang";

const translations: Record<Lang, Record<string, string>> = {
  "pt-BR": {
    "nav.lang.pt": "PT",
    "nav.lang.en": "EN",
    "hero.subtitle": "Dashboard em tempo real...",
    "section.trending": "Mercados em Alta",
    // ...all keys
  },
  en: {
    "nav.lang.pt": "PT",
    "nav.lang.en": "EN",
    "hero.subtitle": "Real-time dashboard...",
    "section.trending": "Trending Markets",
    // ...all keys
  },
};

// Pure function (usable from both server and client)
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
    const stored = localStorage.getItem(STORAGE_KEY) as Lang | null;
    if (stored === "en" || stored === "pt-BR") setLangState(stored);
  }, []);

  const setLang = (l: Lang) => {
    setLangState(l);
    localStorage.setItem(STORAGE_KEY, l);
  };

  return (
    <LangCtx.Provider value={{
      lang, setLang,
      t: (key: string, fallback?: string) => t(lang, key, fallback)
    }}>
      {children}
    </LangCtx.Provider>
  );
}

export function useLang() { return useContext(LangCtx); }
```

### 2. LangProvider in layout.tsx

```tsx
import { LangProvider } from "@/lib/lang";

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body>
        <LangProvider>
          <Navbar />  ← can now use useLang()
          {children}
        </LangProvider>
      </body>
    </html>
  );
}
```

### 3. Using in Components

```tsx
"use client";
import { useLang } from "@/lib/lang";

export default function MyComponent() {
  const { t } = useLang();
  return <Typography>{t("some.key")}</Typography>;
}
```

## Toggle Button in Navbar (MUI)

```tsx
import { ToggleButton, ToggleButtonGroup } from "@mui/material";
import { useLang } from "@/lib/lang";

const { lang, setLang, t } = useLang();

<ToggleButtonGroup
  value={lang}
  exclusive
  onChange={(_, v) => v && setLang(v)}
  size="small"
  sx={{
    "& .MuiToggleButton-root": {
      color: "#8b949e",
      borderColor: "#30363d",
      px: 1, py: 0.3,
      fontSize: "0.75rem",
      fontWeight: 600,
      textTransform: "none",
      "&.Mui-selected": {
        color: "#e6edf3",
        bgcolor: "#21262d",
      },
    },
  }}
>
  <ToggleButton value="pt-BR">{t("nav.lang.pt")}</ToggleButton>
  <ToggleButton value="en">{t("nav.lang.en")}</ToggleButton>
</ToggleButtonGroup>
```

## Pitfalls

### `"use client"` MUST be the first line

```tsx
// BROKEN — comment before directive
// My i18n system
"use client";

// WORKS
"use client";
// My i18n system
```

Next.js parses the file top-down and looks for the directive as the very first expression. Any comment, blank line, or import before it breaks the directive.

### File extension must be `.tsx`, not `.ts`

JSX in a `.ts` file causes a "Syntax Error" at build time pointing at the JSX tag. **Fix:** rename `lang.ts` to `lang.tsx`. Next.js resolves imports without extension either way.

### Server components cannot use `useLang()`

An async server component using `useLang()` crashes:

```
Error: Attempted to call useLang() from the server but useLang is on the client.
```

**Fix:** Convert to a client component with useEffect:
```tsx
// BROKEN — async server component
export default async function MyComponent() {
  const { t } = useLang();  // ERROR
  let data = await fetchAPI();
}

// WORKS — client component
"use client";
import { useEffect, useState } from "react";
export default function MyComponent() {
  const { t } = useLang();
  const [data, setData] = useState(null);
  useEffect(() => { fetchAPI().then(setData); }, []);
}
```

Trade-off: you lose ISR/revalidate. Data fetches client-side.

### API Enum Values vs Translated Labels

When the API returns English enum values, compare against the raw value, not the translated label:
```tsx
label={t.side === "BUY" ? t("trades.buy") : t("trades.sell")}
//              raw API value ^^^        ^^^ translated label
```

### `t()` variable shadowing

Inside `map()` callbacks, the iteration variable can shadow `t` from `useLang()`:
```tsx
{trades.map((t, i) => (  // ← local t shadows translation t
  <Chip label={t.side === "BUY" ? ... } />
))}
```

This is fine as long as you only need `t("key")` outside the callback. Inside, the local `t` refers to the trade object. Either rename the parameter or call `t("key")` before the map.
