# Composite Scoring Dashboard (Intelligence Score Pattern)

## When to Use

Any dashboard that needs to rank or score items based on multiple weighted metrics — prediction markets, investment screens, risk assessment, opportunity scoring.

## Architecture

### 1. Pure Calculation Function (testable, no hooks)

Separate scoring logic from presentation:

```ts
// lib/scoring.ts
interface ScoreInput {
  metrics: Record<string, number>;  // e.g., { liquidity, volume, volatility }
  weights: Record<string, number>;  // e.g., { liquidity: 0.10, volume: 0.10 }
  userEstimate?: number;            // optional manual input
  maxValues?: Record<string, number>; // for normalization
}

export function calcCompositeScore(input: ScoreInput): {
  composite: number;     // 0-100
  subScores: Record<string, number>;
  grade: "excellent" | "good" | "fair" | "poor";
} {
  // Normalize each metric against its max
  // Apply weights
  // Return composite + individual scores
}
```

**Benefits**: Pure function = unit-testable, no React dependency, can be used in both server and client.

### 2. Visual Components

#### Score Ring (circular progress)

```tsx
<Box sx={{
  width: 120, height: 120, borderRadius: "50%",
  background: `conic-gradient(${color} ${score * 3.6}deg, #21262d ${score * 3.6}deg)`,
  display: "flex", alignItems: "center", justifyContent: "center",
}}>
  <Box sx={{
    width: 90, height: 90, borderRadius: "50%", bgcolor: "#0d1117",
    display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
  }}>
    <Typography variant="h4" sx={{ fontWeight: 800, color, lineHeight: 1 }}>
      {score}
    </Typography>
  </Box>
</Box>
```

#### Sub-Score Bars

```tsx
{subScores.map(s => (
  <Box key={s.key}>
    <Box sx={{ display: "flex", justifyContent: "space-between", mb: 0.25 }}>
      <Typography variant="caption">{s.label} ({s.weight})</Typography>
      <Typography variant="caption">{s.value}</Typography>
    </Box>
    <Box sx={{ width: "100%", height: 6, borderRadius: 3, bgcolor: "#21262d", overflow: "hidden" }}>
      <Box sx={{
        width: `${s.value}%`, height: "100%", borderRadius: 3,
        bgcolor: s.value >= 70 ? "#3fb950" : s.value >= 40 ? "#f0883e" : "#f85149",
        transition: "width 0.5s ease",
      }} />
    </Box>
  </Box>
))}
```

#### Compact Badge (for card/list-item views)

```tsx
function ScoreBadge({ score, grade }: { score: number; grade: string }) {
  if (score < 40) return null; // only show notable scores
  return (
    <Chip
      label={`${icon} ${score}`}
      size="small"
      sx={{ height: 18, fontSize: 10, fontWeight: 700, bgcolor: `${color}18`, color }}
    />
  );
}
```

Always wrap in try/catch — a failed score shouldn't crash the parent card:
```tsx
try { return <Badge ... />; } catch { return null; }
```

### 3. Whale Activity Score (from Trade Data)

For dashboards that track trading activity per market/asset:

```tsx
async function calcWhaleScore(conditionId: string): Promise<number> {
  const trades = await getRecentTrades(100, conditionId);
  // Group by wallet address
  const makerMap = new Map<string, number>();
  for (const t of trades) {
    if (t.maker) {
      makerMap.set(t.maker.toLowerCase(), (makerMap.get(t.maker.toLowerCase()) ?? 0) + 1);
    }
  }
  // Calculate concentration: % of trades from top 3 wallets
  const sorted = Array.from(makerMap.values()).sort((a, b) => b - a);
  const top3Share = sorted.slice(0, 3).reduce((s, v) => s + v, 0) / sorted.reduce((s, v) => s + v, 0);
  // Score: moderate concentration = healthy whale interest
  if (top3Share >= 0.80) return 70;   // whales dominate (manipulation risk)
  if (top3Share >= 0.50) return 90;   // strong whale interest
  if (top3Share >= 0.30) return 75;   // moderate
  if (top3Share >= 0.15) return 50;   // some interest
  return 25;                          // low interest
}
```

## Key Lessons

- **Pure function + presentation** keeps scoring testable and components simple
- **try/catch at every badge** prevents a calculation failure from crashing the parent card
- **Weight ordering** matters: put the most important metric first in the composite formula, give it highest weight
- **Grade thresholds** should be tuned to your data distribution; what's "excellent" varies by domain
- **Normalization max values** can be dynamic (computed from current dataset) or static (domain-knowledge based)
- **Compact badges** should only show for notable scores (< threshold → render nothing)
