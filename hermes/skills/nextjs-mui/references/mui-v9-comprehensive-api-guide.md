---
name: mui-project-setup
description: "Scaffold a project with MUI (Material UI) v9+ — theme, Grid, icons, and known breaking changes from v5/v6"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mui, material-ui, react, theming, migration, breaking-changes]
    related_skills: [design-md, popular-web-designs, claude-design, nextjs-project-setup]
---

# MUI Project Setup

## Overview

When scaffolding a new project with MUI v9+ (the version bundled with `create-next-app` / `npm create vite` since late 2025), several APIs changed from MUI v5/v6. This skill documents those changes and the correct way to set up themes, grids, icons, and component overrides.

## Version Detection

Always check which MUI version is installed before writing code:

```bash
# Check MUI version
cat node_modules/@mui/material/package.json | grep '"version"'
```

- **MUI v9.x** — Installed with Next.js 16, React 19. BREAKING CHANGES below.
- **MUI v5/v6** — Older projects. Original API still applies.

## MUI v9 Breaking Changes

### 1. Grid Component — Major API Change

**MUI v5/v6 (old API):**
```tsx
import { Grid } from "@mui/material";

<Grid container spacing={2}>
  <Grid item xs={12} md={6}>content</Grid>
</Grid>
```

**MUI v9 (new API):**
```tsx
import { Grid } from "@mui/material";

// Grid2-style API — use `size` prop instead of `xs`/`sm`/`md` on items
// Use Box or manual flex layouts for containers with justifyContent/alignItems
<Grid container spacing={2}>
  <Grid size={{ xs: 12, md: 6 }}>content</Grid>
</Grid>

// For flex properties like justifyContent, use a Box wrapper instead
<Box sx={{ display: "flex", justifyContent: "center", flexWrap: "wrap", gap: 2 }}>
  {/* items */}
</Box>
```

**Key changes:**
- ✅ `container` prop works the same
- ❌ `item` prop is REMOVED — just use direct children
- ❌ `xs={N}` is REMOVED — use `size={{ xs: N }}`
- ❌ `justifyContent`/`alignItems` on Grid container is REMOVED — use Box with `display: "flex"` instead
- ✅ `spacing` works the same

### 2. Icon Names — Several Renamed

| Old Name (v5/v6) | New Name (v9) |
|---|---|
| `PersonOutline` | `Person` |
| `DeleteOutline` | `DeleteOutlined` |
| `CheckCircleOutline` | `CheckCircleOutlined` |
| `Search` | `Search` (unchanged) |
| `ShoppingCartOutlined` | `ShoppingCartOutlined` (unchanged) |

**Pattern:** Many `*Outline` icons were renamed to `*Outlined` or lost the "Outline" suffix entirely. When an icon import fails, try:
- Drop the "Outline" suffix entirely → `DeleteOutline` → `Delete`
- Add "d" → `DeleteOutline` → `DeleteOutlined` (most common for v9)
- Remove "Outline" and don't add anything → `PersonOutline` → `Person`
- Check the full export list in `node_modules/@mui/icons-material/esm/`

### 3. Theme — styleOverrides Variant Overrides Changed

**MUI v5/v6 (old):**
```ts
MuiButton: {
  styleOverrides: {
    root: { ... },
    containedPrimary: {  // This worked in v5/v6
      "&:hover": { backgroundColor: "#..." }
    }
  }
}
```

**MUI v9 (new):**
```ts
MuiButton: {
  styleOverrides: {
    root: {
      borderRadius: 8,
      padding: "0.6rem 1.5rem",
    },
    // containedPrimary, outlinedSecondary, etc. are NO LONGER valid keys
    // Use root only + custom variants, or sx on each instance
  }
}
```

**Key changes:**
- ❌ Variant-specific overrides (`containedPrimary`, `outlinedSecondary`, `textPrimary`) are REMOVED from `styleOverrides`
- ✅ `root` override still works
- ✅ `MuiButtonBase` defaultProps still works (e.g. `disableRipple: true`)
- ✅ Custom per-instance styling via `sx` prop still works

### 5. ListItemText — primaryTypographyProps → slotProps

**MUI v5/v6 (old):**
```tsx
<ListItemText
  primary="Item"
  primaryTypographyProps={{ fontSize: "0.9rem" }}  // This worked in v5/v6
/>
```

**MUI v9 (new):**
```tsx
// ❌ primaryTypographyProps is REMOVED — will NOT compile
// ✅ Use sx with CSS class selector instead
<ListItemText
  primary="Item"
  sx={{ "& .MuiListItemText-primary": { fontSize: "0.9rem" } }}
/>
```

**Key changes:**
- ❌ `primaryTypographyProps`, `secondaryTypographyProps` props are REMOVED
- ❌ `slotProps.primary.fontSize` does NOT work (TypographyProps doesn't accept fontSize directly)
- ✅ Use `sx` with the inner class selector (`"& .MuiListItemText-primary"`) for typography styling
- ✅ `slotProps.primary.sx` also works for more complex typography props

### 6. Dialog PaperProps → slotProps

**MUI v5/v6 (old):**
```tsx
<Dialog PaperProps={{ sx: { borderRadius: 3 } }} />
```

**MUI v9 (new):**
```tsx
<Dialog slotProps={{ paper: { sx: { borderRadius: 3 } } }} />
```

Affects: `Dialog`, `Menu`, `Popover`, `Drawer`, `Autocomplete`, `Select` — any component with a `PaperProps` prop.

### 7. Next.js SSR — @mui/material-nextjs Dependency

When using MUI v9 with Next.js App Router, the `AppRouterCacheProvider` from `@mui/material-nextjs` is needed for proper SSR:

```bash
npm install @mui/material-nextjs
```

```tsx
import { AppRouterCacheProvider } from "@mui/material-nextjs/v16-appRouter";
```

**Important:** This package is NOT included by default with `@mui/material`. If you see `Module not found: Can't resolve '@mui/material-nextjs/v16-appRouter'`, install it explicitly.

### 8. Theme — Export

`createTheme` import path is unchanged:
```ts
import { createTheme } from "@mui/material/styles";
```

## Recommended Setup Pattern

### Dependencies

```bash
npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
npm install @mui/material-nextjs  # for AppRouterCacheProvider in Next.js SSR
```

### Basic MuiProvider

```tsx
"use client";

import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import theme from "./theme";

export default function MuiProvider({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}
```

### Theme with Safe Overrides (MUI v9)

```tsx
"use client";

import { createTheme } from "@mui/material/styles";

const theme = createTheme({
  palette: {
    primary: { main: "#E65100" },
    // ...
  },
  typography: {
    fontFamily: '"Geist Sans", "Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    button: { textTransform: "none", fontWeight: 600 },
  },
  shape: { borderRadius: 8 },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 8, padding: "0.6rem 1.5rem" },
        // ❌ NO containedPrimary / outlinedSecondary here in v9
      },
    },
    MuiCard: {
      styleOverrides: {
        root: { borderRadius: 12, boxShadow: "0 2px 8px rgba(0,0,0,0.08)" },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: { boxShadow: "0 1px 4px rgba(0,0,0,0.1)" },
      },
    },
  },
});

export default theme;
```

## Layout Pattern (Box over Grid for complex layouts)

In MUI v9, prefer `Box` with flexbox properties over `Grid` when you need:
- `justifyContent` / `alignItems`
- Mixed column widths that don't fit the 12-col grid
- Simple 1D layouts

```tsx
// GOOD: Box + flex for info strips, category lists, footer columns
<Box sx={{ display: "flex", flexWrap: "wrap", gap: 2, justifyContent: "center" }}>
  <Box sx={{ flex: { xs: "1 1 100%", sm: "1 1 30%" } }}>column 1</Box>
  <Box sx={{ flex: { xs: "1 1 100%", sm: "1 1 30%" } }}>column 2</Box>
</Box>

// GOOD: Grid for product grids and 2D layouts
<Grid container spacing={3}>
  <Grid size={{ xs: 12, sm: 6, md: 4 }}>item</Grid>
  <Grid size={{ xs: 12, sm: 6, md: 4 }}>item</Grid>
</Grid>
```

## Error Pattern Reference

When hitting build or type errors with MUI v9, match these patterns:

| Error Pattern | Cause | Fix |
|---|---|---|
| `No overload matches this call... Property 'justifyContent' does not exist` | Using `justifyContent`/`alignItems` on `<Grid container>` | Replace with `<Box sx={{ display: "flex", justifyContent: "center" }}>` |
| `No overload matches this call... Property 'item' does not exist` | Using `<Grid item>` — `item` prop removed in v9 | Remove `item` prop, use `<Grid>` directly |
| `No overload matches this call... Property 'xs' does not exist. Did you mean 'sx'?` | Using `<Grid xs={12}>` — `xs`/`sm`/`md` removed | Use `<Grid size={{ xs: 12 }}>` |
| `Object literal may only specify known properties, and 'containedPrimary' does not exist` | Variant override inside `MuiButton.styleOverrides` | Remove `containedPrimary`/`outlinedSecondary` — only `root` override works in v9 |
| `'@mui/icons-material' has no exported member named 'DeleteOutline'. Did you mean 'DeleteOutlined'?` | Icon renamed in v9 | Use the suggested name or check `node_modules/@mui/icons-material/esm/` |
| `Property 'primaryTypographyProps' does not exist on type 'ListItemTextProps'` | MUI v9 removed primaryTypographyProps | Use `sx={{ '& .MuiListItemText-primary': { fontSize: '0.9rem' } }}` |
| `Property 'PaperProps' does not exist on type 'DialogProps'` | MUI v9 slotProps API | Use `slotProps={{ paper: { sx: ... } }}` |
| `Module not found: Can't resolve '@mui/material-nextjs/v16-appRouter'` | Missing @mui/material-nextjs dependency | Install: `npm install @mui/material-nextjs` |

### Icon Naming Resolution Strategy

When an icon import fails:
1. Read the TypeScript error — it usually tells you the correct name (`Did you mean 'DeleteOutlined'?`)
2. Try removing "Outline" suffix entirely → `DeleteOutline` → `Delete`
3. Try adding "d" → `DeleteOutline` → `DeleteOutlined`
4. Browse `ls node_modules/@mui/icons-material/esm/ | grep -i <keyword>` for the exact filename
5. Fallback: use a similar icon that you know exists (e.g. `Person` instead of `PersonOutline`)

## Pitfalls

- **Always check MUI version first** before writing theme overrides or Grid usage. `npm ls @mui/material` or check `node_modules/@mui/material/package.json`.
- **component prop required on Grid items?** If TypeScript complains about missing `component` prop on Grid, you're using the old Grid API — switch to `size` prop.
- **Icon not found?** Try the name without "Outline", with "Outlined" suffix, or browse `node_modules/@mui/icons-material/esm/` for the exact file.
- **Tailwind + MUI together:** MUI v9 works fine with Tailwind v4, but the Tailwind class-based approach may conflict with MUI's sx prop. Choose one primary styling system per component.
- **Next.js + MUI + "use client":** Any component that imports from `@mui/material` MUST be a Client Component (`"use client"` at the top) or imported into one.
- **Badge `badgeContent` with `color="primary"`:** Works the same in v9. For custom badge colors, use `sx={{ '& .MuiBadge-badge': { backgroundColor: '#E65100' } }}`.
- **Server components and MUI:** MUI components don't work in Server Components. Wrap them in a Client Component boundary (`"use client"`) and import from there.
