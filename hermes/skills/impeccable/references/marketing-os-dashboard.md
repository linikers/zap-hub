# Marketing OS Dashboard — Design System

## Product Register

Product (dashboard/management tool for SMBs). Design SERVES the product.

## Scene

Empresário de Maringá-PR gerenciando anúncios Google Ads + Meta Ads às 10h da manhã em escritório. Ferramenta de trabalho diária — precisa ser profissional, não chamativa.

## Color Strategy

**Committed** — one saturated color (Indigo) carries the identity; zinc neutrals do the heavy lifting.

### Palette

| Role | OKLCH | HEX | Usage |
|------|-------|-----|-------|
| Primary | oklch(55% 0.14 280) | #6366f1 | Accent, buttons, active states |
| Primary hover | oklch(50% 0.16 280) | #4f46e5 | Hover state |
| Surface (bg) | oklch(15% 0.005 280) | #18181b | Deepest canvas (zinc-900) |
| Surface (paper) | oklch(20% 0.005 280) | #27272a | Cards, panels (zinc-800) |
| Surface (elevated) | oklch(25% 0.005 280) | #3f3f46 | Hover surfaces (zinc-700) |
| Text primary | oklch(90% 0.01 280) | #fafafa | Body text |
| Text secondary | oklch(65% 0.01 280) | #a1a1aa | Labels, captions |
| Success | oklch(55% 0.15 150) | #22c55e | Positive metrics |
| Warning | oklch(65% 0.15 85) | #f59e0b | Alerts |
| Error | oklch(55% 0.2 25) | #ef4444 | Negative metrics, deletions |

## Typography

- **Font**: Inter (professional), loaded via next/font/google
- **Scale steps**: 1.25 ratio (minor third)
- **Data**: `font-variant-numeric: tabular-nums` on metric cards and tables
- **Code/user content**: JetBrains Mono (monospace)

### Hierarchy

```
h1 → 1.75rem / 600 weight
h2 → 1.5rem
h3 → 1.25rem
h4 → 1.125rem
body → 0.875rem
caption → 0.75rem / text.secondary
```

## Layout

### App Shell

```
┌─ AppBar (glass/blur backdrop) ─────────────────┐
│  [☰] Marketing OS          [Avatar] [Logout]   │
├──────────┬─────────────────────────────────────┤
│ Sidebar  │  Main Content Area                   │
│ (240px)  │                                      │
│          │                                      │
│ GESTÃO   │  Page content renders here           │
│  📊 Dash │                                      │
│  📢 Ads  │                                      │
│  📈 Ana  │                                      │
├──────────┤                                      │
│ CANAIS   │                                      │
│  👥 Cont │                                      │
│  📋 Camp │                                      │
│  📱 Chat │                                      │
├──────────┤                                      │
│ ...      │                                      │
└──────────┴──────────────────────────────────────┘
```

### Sidebar Sections

| Section | Purpose | Items |
|---------|---------|-------|
| GESTÃO | Core tools | Dashboard, Anúncios, Analytics, Chat IA |
| CANAIS | Communication | Contatos, Campanhas, Eventos |
| MONITOR | Observability | Workers, Agentes |
| IA | AI features | Prompts, Playground, Memória |

### Content area

- Max width: unconstrained (dashboard tool, not article)
- Cards: max 4 per row (metric cards), 1-2 per row (charts)
- Gutters: 24px between cards, 16px inside cards

## Components

### Cards
- No gradient text, no side-stripe borders
- Dark background (zinc-800), subtle border (zinc-700)
- Selected/active: indigo left border + tinted bg

### Metric Cards (KPI)
- Icon on top (large, colored by metric type)
- Value (large, bold)
- Label (small, text.secondary)
- Variation chip (green/red percentage)
- No supporting chart — that's below

### Data Tables
- MUI Table with `size="small"`
- Striped or single-color rows based on data density
- Numerical columns right-aligned with tabular-nums

### Empty States
- Centered content in Paper
- Icon + heading + description
- CTA button ("Criar primeira campanha", "Conectar Google Ads")

### Navigation
- ListItemButton with 8px borderRadius on hover
- Selected item: indigo background tint + left border
- Tooltip on all sidebar items (descriptive, not label repetition)
- Collapse transitions: 250ms ease-out

## Interaction Patterns

- **Loading**: Skeleton components matching card dimensions, not spinners
- **Editing**: Modal or inline edit based on context complexity
- **Delete**: Confirmation dialog, never instant
- **OAuth flow**: Open auth URL in new tab, user returns to dashboard

## Anti-Patterns (specific to Marketing OS)

- Don't use hacker-green (#00ff41) — that's the portfolio brand
- Don't use MUI default blue (#90caf9) — replace with indigo
- Don't use '#' hardcoded colors — always reference theme.palette
- Don't use default MUI typography (Roboto) — always Inter
- Don't use Grid2 size prop syntax — use classic Grid `item xs/md` (MUI v6 compat)
