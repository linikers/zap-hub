# localStorage Portfolio CRUD Pattern (Trading/Position Tracking)

## When to Use

Any app that needs user-owned position/portfolio tracking without a backend — prediction markets, paper trading, investment simulators, bet tracking.

## Architecture

### 1. Pure Data Layer (lib/portfolio.ts)

Split into two parts: pure CRUD functions (server-safe, testable) and React hook (client-only).

#### Data Types

```ts
interface Position {
  id: string;           // generated: Date.now(36) + Math.random(36)
  marketSlug: string;
  marketTitle: string;
  side: "YES" | "NO";
  entryPrice: number;   // 0-1
  quantity: number;     // share count
  entryDate: number;    // unix ms
  status: "open" | "closed";
  exitPrice?: number;   // set on close
  exitDate?: number;
  category?: string;
  pnl?: number;         // realized P&L (computed on close)
}

interface PortfolioMetrics {
  totalInvested: number;
  currentValue: number;
  pnl: number;
  pnlPercent: number;
  winRate: number;
  totalTrades: number;
  winningTrades: number;
  openPositions: number;
}
```

#### CRUD Functions (server-safe)

```ts
const STORAGE_KEY = "app-portfolio";

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

export function loadPositions(): Position[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
  } catch { return []; }
}

export function savePositions(positions: Position[]): void {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(positions)); } catch {}
}

export function addPosition(pos: Omit<Position, "id" | "entryDate" | "status">): Position[] {
  const positions = loadPositions();
  positions.unshift({ ...pos, id: generateId(), entryDate: Date.now(), status: "open" });
  savePositions(positions);
  return positions;
}

export function closePosition(id: string, exitPrice: number): Position[] {
  const positions = loadPositions();
  const idx = positions.findIndex(p => p.id === id);
  if (idx === -1 || positions[idx].status === "closed") return positions;
  const pos = positions[idx];
  positions[idx] = {
    ...pos, status: "closed", exitPrice, exitDate: Date.now(),
    pnl: Math.round((exitPrice - pos.entryPrice) * pos.quantity * 100) / 100,
  };
  savePositions(positions);
  return positions;
}

export function removePosition(id: string): Position[] {
  const positions = loadPositions().filter(p => p.id !== id);
  savePositions(positions);
  return positions;
}
```

#### Metrics Calculation

```ts
export function calcMetrics(positions: Position[]): PortfolioMetrics {
  const open = positions.filter(p => p.status === "open");
  const closed = positions.filter(p => p.status === "closed");
  const totalInvested = open.reduce((s, p) => s + p.entryPrice * p.quantity, 0);
  const realizedPnl = closed.reduce((s, p) => s + (p.pnl ?? 0), 0);
  const totalTrades = closed.length;
  return {
    totalInvested,
    currentValue: totalInvested,
    pnl: realizedPnl,
    pnlPercent: totalInvested > 0 ? (realizedPnl / totalInvested) * 100 : 0,
    winRate: totalTrades > 0
      ? (closed.filter(p => (p.pnl ?? 0) > 0).length / totalTrades) * 100
      : 0,
    totalTrades,
    winningTrades: closed.filter(p => (p.pnl ?? 0) > 0).length,
    openPositions: open.length,
  };
}
```

#### React Hook

```ts
export function usePortfolio() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [metrics, setMetrics] = useState<PortfolioMetrics>(defaultMetrics);

  useEffect(() => {
    const p = loadPositions();
    setPositions(p);
    setMetrics(calcMetrics(p));
  }, []);

  const refresh = useCallback(() => {
    const p = loadPositions();
    setPositions(p);
    setMetrics(calcMetrics(p));
  }, []);

  const add = useCallback((pos) => {
    const updated = addPosition(pos);
    setPositions(updated);
    setMetrics(calcMetrics(updated));
  }, []);

  const close = useCallback((id: string, exitPrice: number) => {
    const updated = closePosition(id, exitPrice);
    setPositions(updated);
    setMetrics(calcMetrics(updated));
  }, []);

  const remove = useCallback((id: string) => {
    const updated = removePosition(id);
    setPositions(updated);
    setMetrics(calcMetrics(updated));
  }, []);

  return { positions, metrics, add, close, remove, refresh };
}
```

### 2. UI Component Structure

```
┌─────────────────────────────────────────────┐
│  Portfolio                    [Nova Posição] │
├─────────────────────────────────────────────┤
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌────┐   │
│  │$500 │ │+$12 │ │+2.4%│ │ 60% │ │  5 │   │
│  │Invest│ │ P&L │ │ ROI │ │Win% │ │Trade│   │
│  └─────┘ └─────┘ └─────┘ └─────┘ └────┘   │
├─────────────────────────────────────────────┤
│  Abertas (2)                                │
│  ┌─────────────────────────────────────────┐│
│  │ Mercado │ Lado │ Entrada │ Valor │ ⋮    ││
│  │ Spain   │ YES  │ 16.4%   │ $16   │Fechar││
│  │ Brazil  │ NO   │ 92.7%   │ $92   │Fechar││
│  └─────────────────────────────────────────┘│
├─────────────────────────────────────────────┤
│  Fechadas (3)                               │
│  ┌─────────────────────────────────────────┐│
│  │ Mercado │ Lado │ Entrada │ Saída │ P&L  ││
│  │ Trump   │ YES  │ 58%     │ 72%   │+$14  ││
│  └─────────────────────────────────────────┘│
└─────────────────────────────────────────────┘
```

#### Dialog: Add Position

- Market Title (required, TextField)
- Side (YES/NO, Select)
- Entry Price (0-1, required, number)
- Quantity (shares, required, number)
- Category (optional, TextField)

#### Dialog: Close Position

- Exit Price (0-1, required, number)
- Cancel / Close buttons

### 3. Metrics Cards Grid

Use Grid2 for responsive layout:

```tsx
<Grid2 key={stat.label} size={{ xs: 6, sm: 4, md: 2 }}>
  <Card>
    <CardContent sx={{ textAlign: "center" }}>
      <Typography variant="h5" sx={{ fontWeight: 700, color: stat.color }}>
        {stat.value}
      </Typography>
      <Typography variant="caption" sx={{ color: "#8b949e" }}>
        {stat.label}
      </Typography>
    </CardContent>
  </Card>
</Grid2>
```

P&L color rule: green `#3fb950` for positive, red `#f85149` for negative, gray `#8b949e` for zero.

### 4. Table: Open Positions

Columns: Market | Side (colored chip) | Entry Price | Qty | Value | Date | Actions (Close + Delete)

Close button opens Dialog for exit price. Delete removes without tracking (for mistakes).

### 5. Table: Closed Positions

Columns: Market | Side | Entry Price | Exit Price | P&L (colored) | Date

## i18n Keys Convention

```
portfolio.add           → "Nova Posição" / "New Position"
portfolio.totalInvested → "Investido" / "Invested"
portfolio.pnl           → "P&L"
portfolio.winRate       → "Win Rate"
portfolio.openPositions → "Abertas" / "Open"
portfolio.noOpen        → "Nenhuma posição aberta..." / "No open positions..."
portfolio.entryPrice    → "Entrada" / "Entry"
portfolio.qty           → "Qtd" / "Qty"
portfolio.actions       → "Ações" / "Actions"
portfolio.close         → "Fechar" / "Close"
portfolio.exit          → "Saída" / "Exit"
```

## Key Lessons

- **Pure functions + hook = testable + reactive**: CRUD functions are pure (input → output), hook provides React reactivity
- **`typeof window === "undefined"` guard**: Prevents SSR crashes when calling localStorage
- **`unshift` for newest-first**: New positions appear at the top of the list
- **PnL calculation is symmetric**: `(exitPrice - entryPrice) * quantity` works for BOTH YES and NO tokens — just track the token price change
- **Close dialog pattern**: Two-step (click close → enter exit price → confirm) prevents accidental closes
- **Delete vs Close**: Delete removes entirely (for mistakes), Close records as a trade with realized P&L
- **Metrics update on every mutation**: add, close, remove all recompute metrics immediately from scratch
