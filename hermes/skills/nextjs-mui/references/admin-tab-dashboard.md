# Multi-Tab Admin Dashboard (MUI + Next.js)

Pattern for a consistent admin panel with sidebar navigation and lazy tab content switching.

## Structure

```
src/components/AdminLayout.tsx   ← Sidebar + content area + tab routing
src/components/FeatureComp.tsx   ← One component per tab
src/app/admin/page.tsx           ← Server component, delegates to AdminLayout
```

## Core Pattern — AdminLayout.tsx

```tsx
"use client";
import { useState } from "react";
import { Box, Container, Paper, List, ListItemButton, ListItemIcon, ListItemText, Badge } from "@mui/material";

const tabs = [
  { id: "dashboard", labelKey: "admin.dashboard", icon: <DashboardIcon /> },
  { id: "alerts",    labelKey: "admin.alerts",    icon: <NotificationsIcon /> },
  { id: "whales",    labelKey: "admin.whales",    icon: <WaterDropIcon /> },
  { id: "news",      labelKey: "admin.news",      icon: <NewReleasesIcon /> },
  { id: "settings",  labelKey: "admin.settings",   icon: <SettingsIcon /> },
];

export default function AdminLayout() {
  const [tab, setTab] = useState("dashboard");

  return (
    <Box sx={{ display: "flex", minHeight: "calc(100vh - 64px)" }}>
      {/* Sidebar — fixed 240px */}
      <Paper sx={{ width: 240, bgcolor: "#0d1117", borderRight: "1px solid #30363d", borderRadius: 0, display: { xs: "none", md: "block" } }}>
        <List sx={{ pt: 2 }}>
          {tabs.map((item) => (
            <ListItemButton
              key={item.id}
              selected={tab === item.id}
              onClick={() => setTab(item.id)}
              sx={{
                mx: 1, borderRadius: 1, mb: 0.5,
                "&.Mui-selected": {
                  bgcolor: "rgba(124, 58, 237, 0.12)",
                  "& .MuiListItemIcon-root": { color: "#7c3aed" },
                  "& .MuiListItemText-primary": { color: "#e6edf3", fontWeight: 600 },
                },
              }}
            >
              <ListItemIcon sx={{ color: "#8b949e", minWidth: 40 }}>
                <Badge badgeContent={unreadCount} color="error">
                  {item.icon}
                </Badge>
              </ListItemIcon>
              <ListItemText primary={t(item.labelKey)} />
            </ListItemButton>
          ))}
        </List>
      </Paper>

      {/* Content area — renders the active tab's component */}
      <Box sx={{ flex: 1, p: 3 }}>
        <Container maxWidth="lg">
          {tab === "alerts" ? <AlertCenter /> :
           tab === "whales" ? <WhaleDashboard /> :
           tab === "news"   ? <NewsDashboard /> :
           <DefaultDashboard />}
        </Container>
      </Box>
    </Box>
  );
}
```

## Key Design Decisions

1. **`"use client"` at top** — the entire layout is a client component. Server components can't manage `useState` for tab state.
2. **No React Router** — tab state is managed with simple `useState`. No URL changes needed for admin internal navigation.
3. **Conditional rendering** — `tab === X ? <Comp /> : Y` pattern lazy-loads each component. Unmounts when switching tabs.
4. **Badge on alerts tab** — `unreadCount` state passed from AlertCenter via callback prop `onUnreadChange`.
5. **Admin link in main navbar** — small icon button (SettingsIcon) in the main AppBar linking to `/admin`.

## Adding a New Tab

1. Add an icon + `{ id, labelKey, icon }` to the `tabs` array
2. Create the component file (e.g., `WhaleDashboard.tsx`)
3. Import and add a ternary branch in the content area
4. Add the i18n key `admin.xxx` to both language objects
