# E-Commerce Header Patterns (MUI v9 + Next.js App Router)

Complete, production-tested patterns for e-commerce headers: search bar, category navigation, mobile drawer, touch targets, and WhatsApp FAB. All code targets MUI v9 + Next.js App Router with `"use client"`.

## 1. Controlled Search Bar with Clear Button

Full-featured search: controlled input, clear/X button, active-state border highlight, keyboard shortcuts (Enter/Esc), clickable search icon.

```tsx
const [searchValue, setSearchValue] = useState("");
const searchInputRef = useRef<HTMLInputElement>(null);

// ⚠️ Do NOT wrap these in useCallback when onSearch comes from a parent inline arrow.
// Plain functions close over the latest render's props — no stale closure, simpler code.
const fireSearch = (term: string) => {
  setSearchValue(term);
  onSearch?.(term);
};

const handleSearchKeyDown = (e: React.KeyboardEvent) => {
  if (e.key === "Enter") {
    fireSearch(searchValue);
    searchInputRef.current?.blur();
  }
  if (e.key === "Escape") {
    fireSearch("");
    searchInputRef.current?.focus();
  }
};
```

```tsx
<Box component="form"
  onSubmit={(e) => { e.preventDefault(); fireSearch(searchValue); }}
  sx={{
    display: "flex", alignItems: "center",
    backgroundColor: "#ffffff", borderRadius: 1.5,
    border: "1px solid",
    borderColor: searchValue ? "#E65100" : "#e0e0e0",
    px: 1.5, py: 0.5, maxWidth: 600, mx: { xs: "auto" },
    transition: "border-color 0.2s ease, box-shadow 0.2s ease",
    boxShadow: searchValue ? "0 0 0 3px rgba(230, 81, 0, 0.1)" : "none",
    "&:focus-within": {
      borderColor: "#E65100",
      boxShadow: "0 0 0 3px rgba(230, 81, 0, 0.1)",
    },
  }}
>
  <IconButton size="small" type="submit"
    sx={{ color: searchValue ? "#E65100" : "#999", mr: 0.5, p: 0.5 }}
  >
    <SearchIcon sx={{ fontSize: 20 }} />
  </IconButton>
  <InputBase
    placeholder="O que deseja procurar?"
    value={searchValue}
    onChange={(e) => fireSearch(e.target.value)}
    onKeyDown={handleSearchKeyDown}
    inputRef={searchInputRef}
    sx={{ flex: 1, fontSize: { xs: "0.85rem", md: "0.925rem" } }}
    inputProps={{ "aria-label": "buscar" }}
  />
  {searchValue && (
    <IconButton size="small"
      onClick={() => { fireSearch(""); searchInputRef.current?.focus(); }}
      sx={{ color: "#999", ml: 0.5, p: 0.5 }}
    >
      <Close sx={{ fontSize: 18 }} />
    </IconButton>
  )}
</Box>
```

## 2. Category Navigation Bar (Dark Theme)

Centered category buttons on a dark background. WhatsApp is a FAB (Section 5), NOT in the nav bar.

**⚠️ Anti-patterns:**
1. NEVER put `overflowX: "auto"` on the outer sticky AppBar container → "loose menu" on scroll
2. NEVER use `<Box sx={{ flex: 1 }} />` spacer → pushes categories left, breaks centering
3. NEVER use hardcoded `pr: { md: 22 }` → clips categories on the left
4. NEVER put WhatsApp in the nav bar → use FAB instead

```tsx
<Box sx={{
  backgroundColor: "#1A1A1A",
  display: { xs: "none", lg: "block" },  // lg=1200px, not md
}}>
  <Container maxWidth="xl">  {/* xl=1536px, not lg=1200px */}
    <Box sx={{
      display: "flex", alignItems: "center", minHeight: 44,
    }}>
      <Box sx={{
        flex: 1, display: "flex",
        justifyContent: "center",   // CENTERED
        flexWrap: "nowrap",
      }}>
        {categorias.map((cat) => (
          <Button key={cat.slug}
            onClick={() => onCategorySelect?.(activeCategory === cat.slug ? null : cat.slug)}
            sx={{
              color: activeCategory === cat.slug ? "#E65100" : "#ffffff",
              textTransform: "none", fontSize: "0.85rem",
              whiteSpace: "nowrap", flexShrink: 0,
              px: { lg: 1.25, xl: 2 }, py: 1.25, minHeight: 44,
              borderRadius: 0,
              fontWeight: activeCategory === cat.slug ? 600 : 400,
              borderBottom: activeCategory === cat.slug
                ? "2px solid #E65100" : "2px solid transparent",
              transition: "color 0.15s ease, border-color 0.15s ease",
              "&:hover": { backgroundColor: "rgba(255,255,255,0.08)", color: "#E65100" },
            }}
          >{cat.nome}</Button>
        ))}
        <Button
          onClick={(e) => setCategoriesMenuAnchor(e.currentTarget)}
          endIcon={<ExpandMore sx={{ fontSize: 18,
            transition: "transform 0.2s ease",
            transform: categoriesMenuAnchor ? "rotate(180deg)" : "rotate(0deg)" }} />}
          sx={{
            color: categoriesMenuAnchor ? "#E65100" : "#ffffff",
            textTransform: "none", fontSize: "0.85rem",
            whiteSpace: "nowrap", flexShrink: 0,
            px: { lg: 1.25, xl: 2 }, py: 1.25, minHeight: 44,
            borderRadius: 0, fontWeight: 600,
            borderBottom: categoriesMenuAnchor ? "2px solid #E65100" : "2px solid transparent",
            transition: "color 0.15s ease, background-color 0.15s ease",
            "&:hover": { backgroundColor: "rgba(255,255,255,0.08)", color: "#E65100" },
          }}
        >+ Categorias</Button>
        <Menu
          anchorEl={categoriesMenuAnchor}
          open={Boolean(categoriesMenuAnchor)}
          onClose={() => setCategoriesMenuAnchor(null)}
          anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
          transformOrigin={{ vertical: "top", horizontal: "left" }}
          slotProps={{ paper: { sx: {
            mt: 0.5, borderRadius: 1.5,
            boxShadow: "0 4px 20px rgba(0,0,0,0.15)",
            minWidth: 200, maxHeight: 360,
          }}}}
        >
          {categorias.map((cat) => (
            <MenuItem key={cat.slug}
              onClick={() => { onCategorySelect?.(cat.slug); setCategoriesMenuAnchor(null); }}
              selected={activeCategory === cat.slug}
              sx={{
                py: 1.25, px: 2.5, fontSize: "0.9rem",
                color: activeCategory === cat.slug ? "#E65100" : "text.primary",
                "&.Mui-selected": { backgroundColor: "rgba(230, 81, 0, 0.08)" },
              }}
            >{cat.nome}</MenuItem>
          ))}
        </Menu>
      </Box>
    </Box>
  </Container>
</Box>
```

**Key decisions:**
- `flex: 1` + `justifyContent: "center"` = categories centered in available space
- `Container maxWidth="xl"` (1536px): lg (1200px) doesn't fit 11 categories
- Breakpoint `lg` (1200px), not `md` (900px): 11 × ~100px = ~1100px
- Responsive padding: `px: { lg: 1.25, xl: 2 }` reduces on smaller screens
- NO overflow, NO scroll, NO spacers, NO hardcoded padding

## 3. Mobile Drawer with Expandable Categories

Shows below `lg` breakpoint (1200px). Categories, account, WhatsApp.

```tsx
<Drawer anchor="left" open={mobileMenuOpen}
  onClose={() => setMobileMenuOpen(false)}
  slotProps={{ paper: { sx: { width: 280 } } }}
>
  <Box sx={{ pt: 2 }}>
    <Box sx={{ px: 2, pb: 2 }}>
      <Link href="/" onClick={() => setMobileMenuOpen(false)}>
        <CarCrewLogoText />
      </Link>
    </Box>
    <Divider />
    <List>
      <ListItemButton onClick={() => setCategoriesOpen(!categoriesOpen)}>
        <ListItemIcon><MenuIcon /></ListItemIcon>
        <ListItemText primary="Categorias" />
        {categoriesOpen ? <ExpandLess /> : <ExpandMore />}
      </ListItemButton>
      <Collapse in={categoriesOpen}>
        <List disablePadding>
          {categorias.map((cat) => (
            <ListItemButton key={cat.slug} sx={{ pl: 4 }}
              onClick={() => { onCategorySelect?.(cat.slug); setMobileMenuOpen(false); }}
            >
              <ListItemText primary={cat.nome}
                sx={{ color: activeCategory === cat.slug ? "#E65100" : "inherit" }} />
            </ListItemButton>
          ))}
        </List>
      </Collapse>
      <Divider />
      <ListItemButton onClick={() => { router.push("/conta"); setMobileMenuOpen(false); }}>
        <ListItemIcon><Person /></ListItemIcon>
        <ListItemText primary="Minha Conta" />
      </ListItemButton>
      <ListItemButton onClick={() => {
        window.open("https://wa.me/5544998133182", "_blank");
        setMobileMenuOpen(false);
      }}>
        <ListItemIcon><WhatsApp /></ListItemIcon>
        <ListItemText primary="Fale no WhatsApp" sx={{ color: "#25D366" }} />
      </ListItemButton>
    </List>
  </Box>
</Drawer>
```

## 4. Touch Target & Spacing Standards

| Element | minHeight | px | py | whiteSpace | flexShrink |
|---------|-----------|----|----|------------|------------|
| Nav buttons (desktop) | 44px | 10-16px (responsive) | 10px | nowrap | 0 |
| ListItemButton (mobile) | 48px | 16px | 12px | — | — |
| IconButton (toolbar) | 40px | — | — | — | — |
| MenuItem (dropdown) | 40px | 20px | 10px | — | — |

## 5. WhatsApp FAB (Floating Action Button)

Standard e-commerce pattern: WhatsApp icon fixed to bottom-right, always visible during scroll.

```tsx
<IconButton
  href="https://wa.me/5544998133182"
  target="_blank"
  aria-label="Fale no WhatsApp"
  sx={{
    position: "fixed",
    bottom: { xs: 16, md: 24 },
    right: { xs: 16, md: 24 },
    zIndex: 1300,
    backgroundColor: "#25D366",
    color: "#fff",
    width: { xs: 56, md: 64 },
    height: { xs: 56, md: 64 },
    boxShadow: "0 4px 12px rgba(37, 211, 102, 0.4)",
    transition: "background-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease",
    "&:hover": {
      backgroundColor: "#20ba5a",
      boxShadow: "0 6px 16px rgba(37, 211, 102, 0.5)",
      transform: "scale(1.05)",
    },
  }}
>
  <WhatsApp sx={{ fontSize: { xs: 28, md: 32 } }} />
</IconButton>
```

**Why FAB:** Standard in BR e-commerce (Kabum, Pichau, ML, Terabyte). Always visible during scroll. Doesn't compete with categories for nav space. Uses `IconButton` (no `Fab` import needed).

## 6. Full Header Architecture

```
Row 1: [Hamburger(mobile)]  [===== LOGO =====]  [UserIcon] [CartBadge]
       position:sticky, white bg
Row 2: [================ SEARCH BAR ================]
       light gray bg (#fafafa)
Row 3: [Cat1] [Cat2] ... [+ Categorias ▼]
       dark bg (#1A1A1A), desktop only (lg+)

       💬 ← WhatsApp FAB (position: fixed, bottom-right)
```

Row 1: `position: relative` on Toolbar + `position: absolute` on hamburger/icons → logo stays centered.
Row 3: `display: { xs: "none", lg: "block" }` → hidden below 1200px, drawer handles mobile.
