# MUI Theme Standardization — Portfolio Session

## Context

Portfolio project (`linikers/portfolio`) — Next.js 13.4, MUI v6, Pages Router. Had hex colors scattered across every page with no unified theme.

## Discovery: User's UI Standard

The user's standard UI library is **MUI** (Material UI).
- Portfolio uses MUI v6 (`@mui/material@^6.1.1`)
- CarCrew uses MUI v9 with `slotProps`
- The user said "nosso padrão de ui que esqueci o nome" — it's MUI

## Theme File Created

`src/config/theme.ts` with:

```ts
import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    mode: "dark",
    primary: { main: "#22d3ee" },   // cyan accent
    background: {
      default: "#0a0a0f",
      paper: "#111827",
    },
    text: {
      primary: "#f0f0f0",
      secondary: "#64748b",
    },
    divider: "#1e293b",
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundImage: "none",
          backgroundColor: "#111827",
          border: "1px solid #1e293b",
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { textTransform: "none", borderRadius: 10, fontWeight: 600 },
        outlined: {
          borderColor: "#1e293b",
          color: "#64748b",
          "&:hover": {
            borderColor: "#22d3ee",
            color: "#22d3ee",
            background: "rgba(34, 211, 238, 0.08)",
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { fontFamily: "monospace" },
        outlined: {
          borderColor: "#1e293b",
          color: "#cbd5e1",
          backgroundColor: "rgba(255,255,255,0.03)",
          "&:hover": {
            borderColor: "#22d3ee",
            backgroundColor: "rgba(34, 211, 238, 0.08)",
          },
        },
      },
    },
  },
});
```

## _app.jsx Wrapping

```jsx
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import theme from "@/config/theme";

export default function MyApp({ Component, pageProps }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Component {...pageProps} />
    </ThemeProvider>
  );
}
```

## Hex → Token Substitutions Made

| Page | Before | After |
|------|--------|-------|
| contato.tsx | `backgroundColor: '#d4d0c4'` | (removed, inherits `background.default`) |
| contato.tsx | `text-green-600` | `text-cyan-400` |
| contato.tsx | `text-gray-800` | `text-white` |
| ferramentas.tsx | `bgcolor: "#d4d0c4"` | `bgcolor: "background.default"` |
| ferramentas.tsx | `backgroundColor: "#2e3440"` | `backgroundColor: "background.paper"` + `border: 1, borderColor: "divider"` |
| perfil.tsx | `backgroundColor: "#3b5998"` | `backgroundColor: "primary.main"` |
| perfil.tsx | `backgroundColor: "#f5f5f5"` (2x) | `backgroundColor: "action.hover"` |
| login.tsx | `backgroundColor: "gray"` | `backgroundColor: "background.default"` |
| login.tsx | `backgroundColor: "white"` | `backgroundColor: "background.paper"` |
| PropagandaLayout | `bgcolor: "#f8fafc"` | `bgcolor: "background.default"` |
| PropagandaLayout | `bgcolor: "white"` (2x) | `bgcolor: "background.paper"` |
| PropagandaLayout | `borderRight: "1px solid #e2e8f0"` | `borderRight: 1, borderColor: "divider"` |
| PropagandaLayout | `borderBottom: "1px solid #e2e8f0"` | `borderBottom: 1, borderColor: "divider"` |

## MUI v6 → v9 Migration Notes

Portfolio is on MUI v6, CarCrew on MUI v9. Key differences:
- v6: `Grid2` is in `@mui/material`
- v9: `slotProps` replaces many `props` patterns
- v6 `sx` API is the same
- v6 `ThemeProvider` import path: `@mui/material/styles`
