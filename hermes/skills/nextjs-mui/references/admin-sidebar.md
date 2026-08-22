# Admin Panel Sidebar Navigation

## Structure

Two components: `AdminSidebar` (the sidebar itself) and `AdminLayout` (wrapper that handles layout).

## AdminSidebar

- Desktop: `variant="permanent"` — fixed sidebar, 250px wide
- Mobile: `variant="temporary"` — drawer that slides over content
- Props: `open: boolean`, `onClose: () => void`
- Uses `useMediaQuery(theme.breakpoints.up("md"))` to detect desktop

### Menu Items

```tsx
const menuItems = [
  { label: "Dashboard", icon: <Dashboard />, path: "/admin" },
  { label: "Produtos", icon: <Inventory2 />, path: "/admin/produtos" },
  { label: "Categorias", icon: <Category />, path: "/admin/categorias" },
  { label: "Banners", icon: <ViewCarousel />, path: "/admin/banners" },
  { label: "Pedidos", icon: <ShoppingBag />, path: "/admin/pedidos", disabled: true, tag: "Em breve" },
];
```

- `disabled: true` items show `tag: "Em breve"` in italic gray
- `selected` highlights the current page via `pathname === item.path || pathname.startsWith(item.path + "/")`
- Selected item gets brand-color background (rgba)
- Hover gets light background (rgba white)

### Footer

- "Ver Loja" button → navigates to `/`
- "Sair" button → `signOut({ callbackUrl: "/admin/login" })`
- Both use `ListItemText` with `sx={{ "& .MuiListItemText-primary": { fontSize: "0.9rem" } }}` for font size

### Styling

- Background: `#1A1A1A` (dark)
- Text: `#ccc` default, `#E65100` when selected
- Border radius on items: 8px
- Borders between sections: `rgba(255,255,255,0.1)`

## AdminLayout

```tsx
export default function AdminLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  return (
    <Box sx={{ display: "flex", minHeight: "100vh" }}>
      {/* Mobile hamburger */}
      <IconButton
        onClick={() => setSidebarOpen(true)}
        sx={{
          position: "fixed", top: 8, left: 8, zIndex: 1200,
          display: { md: "none" },
          backgroundColor: "#fff", boxShadow: "0 2px 8px rgba(0,0,0,0.1)"
        }}
      >
        <MenuIcon />
      </IconButton>

      <AdminSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <Box sx={{ flex: 1, ml: { md: "250px" }, display: "flex", flexDirection: "column", minHeight: "100vh" }}>
        {children}
      </Box>
    </Box>
  );
}
```

- Mobile toggle is fixed-positioned at top-left with white background
- Content area uses `ml: { md: "250px" }` to offset for the sidebar on desktop
- All admin pages wrap content in `<AdminLayout>` instead of `<Header>` (sidebar replaces the site header)

## Usage in Pages

```tsx
import AdminLayout from "@/components/admin/AdminLayout";

export default function AdminPage() {
  return (
    <AdminLayout>
      <Container maxWidth="lg" sx={{ py: 4, mt: { xs: 6, md: 0 } }}>
        {/* page content */}
      </Container>
    </AdminLayout>
  );
}
```

- `mt: { xs: 6, md: 0 }` adds top margin on mobile to avoid overlap with the hamburger button.
