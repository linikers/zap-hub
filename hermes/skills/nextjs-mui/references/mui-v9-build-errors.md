# MUI v9 Build Error Reference

Collection of actual TypeScript build errors encountered when migrating from MUI v5/v6 to v9, with the exact fixes.

## Grid API

### Error: `Property 'justifyContent' does not exist`
```
Type '{ children: Element[]; container: true; spacing: number; justifyContent: string; }'
is not assignable to type 'GridBaseProps & ...'
  Property 'justifyContent' does not exist on type 'IntrinsicAttributes & GridBaseProps & ...'
```
**Fix:** Replace `<Grid container justifyContent="center">` with `<Box sx={{ display: "flex", flexWrap: "wrap", justifyContent: "center" }}>`.

### Error: `Property 'item' does not exist`
```
Property 'item' does not exist on type 'IntrinsicAttributes & GridBaseProps & ...'
```
**Fix:** Replace `<Grid item xs={12} md={4}>` with `<Grid size={{ xs: 12, md: 4 }}>` (or use `<Box sx={{ flex: ... }}>`).

## Dialog

### Error: `Property 'PaperProps' does not exist`
```
Property 'PaperProps' does not exist on type 'IntrinsicAttributes & DialogProps'
```
**Fix:** 
```tsx
// ❌ OLD
<Dialog PaperProps={{ sx: { borderRadius: 3 } }}>
// ✅ NEW
<Dialog slotProps={{ paper: { sx: { borderRadius: 3 } } }}>
```

## Icon Names

### Error: `No exported member named 'DeleteOutline'`
```
'"@mui/icons-material"' has no exported member named 'DeleteOutline'.
Did you mean 'DeleteOutlined'?
```
**Fix:** Rename to `DeleteOutlined`.

### Error: `No exported member named 'CheckCircleOutline'`
```
'"@mui/icons-material"' has no exported member named 'CheckCircleOutline'.
Did you mean 'CheckCircleOutlined'?
```
**Fix:** Rename all instances (import + JSX usage) to `CheckCircleOutlined`.

### Error: `No exported member named 'PersonOutline'`
```
'"@mui/icons-material"' has no exported member named 'PersonOutline'.
Did you mean 'PersonOutlined'?
```
**Fix:** Use `Person` or `PersonOutlined`.

## ListItemText

### Error: `Property 'primaryTypographyProps' does not exist`
```
Property 'primaryTypographyProps' does not exist on type 'IntrinsicAttributes & ListItemTextProps'
```
**Fix:**
```tsx
// ❌ OLD
<ListItemText primaryTypographyProps={{ fontSize: "0.9rem" }}>
// ✅ NEW option 1 (safest)
<ListItemText sx={{ "& .MuiListItemText-primary": { fontSize: "0.9rem" } }}>
// ✅ NEW option 2
<ListItemText slotProps={{ primary: { sx: { fontSize: "0.9rem" } } }}>
```

Note: Option 2 `slotProps.primary` accepts TypographyProps but `fontSize` must be inside `sx`, not at the top level.

## MUI Button styleOverrides

### Error: `'containedPrimary' does not exist in type`
```
Object literal may only specify known properties, and 'containedPrimary' does not
exist in type 'Partial<OverridesStyleRules<keyof ButtonClasses, "MuiButton", ...>>'
```
**Fix:** In MUI v9 theme, `containedPrimary` is no longer a valid key under `MuiButton.styleOverrides.root`. Remove variant-specific overrides from root, or use the theme's palette to control variant colors.

## TextField

### Error: `Property 'inputProps' does not exist on type`
```
Property 'inputProps' does not exist on type
'IntrinsicAttributes & { variant?: TextFieldVariants | undefined; } & Omit<...>'
```
**Fix:** In MUI v9, `inputProps` moved under `slotProps.htmlInput`:
```tsx
// ❌ OLD
<TextField inputProps={{ maxLength: 9 }} />

// ✅ NEW
<TextField slotProps={{ htmlInput: { maxLength: 9 } }} />
```

### Error: `'endAdornment' does not exist in type slotProps`
```
Object literal may only specify known properties, and 'endAdornment' does not exist
in type '{ root?: ...; input?: ...; htmlInput?: ...; }'
```
**Fix:** Use `slotProps.input.endAdornment` instead — or put the unit in the label:
```tsx
// ❌ OLD — endAdornment as a top-level slot key
<TextField slotProps={{ htmlInput: { min: 0 }, endAdornment: <InputAdornment>%</InputAdornment> }} />

// ✅ NEW — wrap in slotProps.input
<TextField slotProps={{ input: { endAdornment: <InputAdornment position="end">%</InputAdornment> } }} />
// or simpler: put indication in the label text
<TextField label="Margem (%)" />
```

## JSX

### Error: `JSX elements cannot have multiple attributes with the same name`
```
error TS17001: JSX elements cannot have multiple attributes with the same name.
```
**Fix:** Duplicate prop on the same JSX element — check that a prop (e.g. `label`, `placeholder`, `onClick`) wasn't declared twice. This happens when `patch` merges two versions of a component that both define the same prop. Remove the duplicate copy.

## Missing Dependency

### Error: `Can't resolve '@mui/material-nextjs/v16-appRouter'`
```
Module not found: Can't resolve '@mui/material-nextjs/v16-appRouter'
```
**Fix:** Install the separate package:
```bash
npm install @mui/material-nextjs
```
This package is NOT included in `@mui/material` and must be installed explicitly.
