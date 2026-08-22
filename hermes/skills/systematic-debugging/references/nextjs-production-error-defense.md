# Next.js Production Error Defense

## "e is not a function" in Minified Production Builds

### Symptom

Client-side exception on page load in production (not dev). Minified error like `Uncaught TypeError: e is not a function` in a page chunk. Full message in dev: "Application error: a client-side exception has occurred".

### Common Root Causes (in order of likelihood)

#### 1. Variable Shadowing of `useLang()` `t` in `.map()`

The #1 cause in practice. `useLang()` returns `{ t: translateFn }`. If a `.map()` callback uses `t` as the parameter name, it **shadows** the translation function. Calling `t("key")` inside the map tries to call the array element as a function:

```tsx
const { t } = useLang();  // t = translation function

{trades.map((t: any, i) => (  // t SHADOWS the outer t
  <Chip label={t("side")} />  // t here is the trade OBJECT, not a function!
  // → TypeError: e is not a function
))}
```

**Fix:** Never use `t` as a map parameter when `useLang()` is in scope:

```tsx
// GOOD
{trades.map((trade, i) => (
  <Chip label={trade.side === "BUY" ? t("trades.buy") : t("trades.sell")} />
))}

// ALSO FINE — single-letter is fine as long as it's not `t`
{trades.map((item, i) => (
  <Chip label={item.side === "BUY" ? t("trades.buy") : t("trades.sell")} />
))}
```

**Detection:** In the minified production chunk, look for `t.side` or `t.price` being accessed inside the same scope where `t` is expected to be a function. If the component renders a table/list with language-dependent labels and crashes at render time, suspect this first.

**Smoking gun in minified code:** When you see `label:t.side==="BUY"?` followed by a `(0,X.u)(...)` call for the label text, that confirms variable shadowing. The minifier renames the outer `t` (translation fn) to `X.u`, while inner `t` stays as the array element. The `(0, X.u)()` pattern proves `t` at that point is the trade object, not the function.

#### 2. IIFE (Immediately Invoked Function Expression) returning JSX

Anti-pattern example leading to cryptic errors:

```tsx
{(() => {
  if (!condition) return null;
  return <Chip label={score} />;
})()}
```

When minified, this compiles to something like `(0, n())()` where the inner function's parameter gets named `e`, and if the code inside throws, the minifier's error becomes "e is not a function".

**Fix:** Extract into a proper component:

```tsx
function ScoreBadge({ condition, score }: Props) {
  try {
    if (!condition) return null;
    return <Chip label={score} />;
  } catch {
    return null; // fail silently, never crash the parent
  }
}
```

#### 3. Unchecked API response shape

API returns data in unexpected format (object vs array, null vs defined field). Common when calling external APIs (Polymarket, etc.) without response validation.

**Fix:** Guard at every boundary:

```ts
// After fetch, validate before using
const data = await response.json();
const items = Array.isArray(data.events) ? data.events : [];

// In .map() calls, guard against null items
items.filter(Boolean).map(item => ...)
```

#### 4. Stale CDN chunks (Vercel-specific)

Vercel CDN edge nodes serve old JS chunks for new HTML. The HTML references new chunk hashes, but old chunks still get served for some users, causing function reference errors.

**Fix:** Configure `vercel.json` with aggressive cache headers:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "no-cache, no-store, must-revalidate" },
        { "key": "Pragma", "value": "no-cache" },
        { "key": "Expires", "value": "0" }
      ]
    },
    {
      "source": "/_next/static/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "public, max-age=0, must-revalidate" }
      ]
    }
  ]
}
```

---

## Multi-Layer Error Defense for Next.js App Router

### Layer 1: ErrorBoundary (component-level)

Class component that catches errors in children without crashing the page:

```tsx
"use client";
import { Component, type ReactNode, type ErrorInfo } from "react";

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      // Render fallback UI with retry button
      return <FallbackUI onRetry={this.handleRetry} />;
    }
    return this.props.children;
  }
}
```

**Where to wrap:**
- Entire app in `layout.tsx` (catches everything — but shows full-page fallback)
- **Each section of a complex page individually** (critical refinement)
- Each list item / card in grids (isolates failures)

**Per-section wrapping is strongly preferred over single top-level ErrorBoundary:**
A single ErrorBoundary around the entire page content shows a full-page fallback if ANY component fails. With per-section wrappers, a crashed chart only hides the chart section, while the rest of the page (stats, orderbook, trades) continues working. Combine both: one at layout level as last resort, then individual wraps around each data-fetching section.

```tsx
{/* Per-section ErrorBoundary — chart fails, rest of page still works */}
<ErrorBoundary fallback={<SectionFallback label="Chart unavailable" />}>
  <PriceChart conditionId={conditionId} />
</ErrorBoundary>

<ErrorBoundary fallback={<SectionFallback label="Trades unavailable" />}>
  <RecentTrades conditionId={conditionId} />
</ErrorBoundary>
```

Use a compact fallback component that doesn't break the grid layout:

```tsx
function SectionFallback({ label }: { label: string }) {
  return (
    <Card sx={{ bgcolor: "#161b22", border: "1px solid #30363d", borderRadius: 2 }}>
      <CardContent sx={{ textAlign: "center", py: 4 }}>
        <ErrorOutlineIcon sx={{ fontSize: 24, color: "#484f58", mb: 1 }} />
        <Typography variant="body2" sx={{ color: "#484f58" }}>
          {label}
        </Typography>
      </CardContent>
    </Card>
  );
}
```

Then use per-section:

```tsx
<ErrorBoundary fallback={<SectionFallback label="Orderbook unavailable" />}>
  <OrderBook tokenId={tokenId} />
</ErrorBoundary>
```

This keeps the grid cell alive when one section fails — nearby sections stay in their correct positions.

### Layer 2: error.tsx (route-level)

Convention file at route level (e.g., `src/app/error.tsx`). Catches errors thrown during rendering of that route segment. Receives `error` and `reset` props.

```tsx
"use client";
export default function RouteError({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <Box>
      <Typography>Error message here</Typography>
      <Button onClick={() => reset()}>Try again</Button>
    </Box>
  );
}
```

### Layer 3: global-error.tsx (app-level)

Last line of defense. Must render its own `<html>` and `<body>` tags (runs outside the app layout). For truly catastrophic failures.

```tsx
"use client";
export default function GlobalError({ error, reset }: Props) {
  return (
    <html>
      <body>
        {/* Minimal standalone error page */}
        <Button onClick={() => reset()}>Try again</Button>
      </body>
    </html>
  );
}
```

### Layer 4: loading.tsx

Convention file for loading states. Shows during page transitions and data fetching.

```tsx
export default function Loading() {
  return <CircularProgress />;
}
```

---

## API Call Hardening for Serverless

Always use AbortController with timeout for `fetch` in serverless environments (Vercel Edge/Functions timeout at 10-60s):

```ts
async function fetchJson<T>(url: string): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 15000);
  try {
    const res = await fetch(url, { signal: controller.signal });
    clearTimeout(timeoutId);
    if (!res.ok) throw new Error(`API ${res.status}: ${res.statusText}`);
    const text = await res.text();
    if (!text || text.trim() === "") throw new Error("Empty response");
    return JSON.parse(text);
  } catch (e) {
    clearTimeout(timeoutId);
    if (e instanceof DOMException && e.name === "AbortError") {
      throw new Error("API timeout (15s)");
    }
    throw e;
  }
}
```

---

## Debugging Checklist for "e is not a function"

1. [ ] Check browser console for the original error + chunk hash
2. [ ] Compare chunk hash with latest build — stale chunk?
3. [ ] Search codebase for IIFEs in JSX (`{(() => {`)
4. [ ] Check all `.map()` calls for non-array input
5. [ ] Verify API response shape matches expected types
6. [ ] Check Vercel/vercel.json cache headers
7. [ ] Add ErrorBoundary around the suspect component(s)
8. [ ] Test in incognito / hard-refresh (Ctrl+Shift+R)
9. [ ] **Clear console between test iterations** — stale messages from old builds deceive

---

## Advanced Techniques

### Binary-Search Component Isolation

When "e is not a function" occurs in the **React reconciler** (shared chunk, not page chunk), the error tells you *that* a component type isn't a function — but NOT *which* component. The stack trace only shows the reconciler internals (`beginWork`, `performUnitOfWork`).

**Technique: Disable Components One by One**

```tsx
// STEP 1: Disable ALL suspect components
<Box>TEST MODE — all disabled</Box>

// Build, start production server, test
// If error goes away → one of them is the culprit

// STEP 2: Add them back one at a time
<IntelligenceScoreCard ... />         // Test → if OK...
<PriceChart conditionId={...} />      // Test → if OK...
<OrderBook tokenId={...} />           // Test → if still OK, next one is likely
<RecentTrades conditionId={...} />    // Test → crash → BINGO

// STEP 3: Narrow further
// Now you know which component. Look at ITS render output.
// Disable sub-components within it to find the exact element.
```

**Key rules:**
- Each test = full rebuild (`npx next build && npx next start`)
- **Never change multiple components between builds** — you lose the isolation
- The imports still bundle even when disabled; the error only triggers when the component is *rendered* in JSX
- Start with ALL extras disabled, add back one by one (not remove one by one)

### Reading Minified Chunks to Identify the Culprit Component

The stack trace for "e is not a function" only shows the minified function name (e.g., `at I (...page-xxx.js:1:5183)`). You can identify which component `I` is by reading the minified page chunk:

```python
with open(".next/static/chunks/app/market/[slug]/page-xxx.js", "r") as f:
    content = f.read()

pos = 5183  # from the stack trace column
# Get context around the error position
snippet = content[max(0, pos-50):pos+100]
# The function definition is usually a few chars before the error
# Look for `function X(e){` where X is the minified name
```

Look for patterns:
- `function I(e){let{conditionId:l}=e,{t:r}=(0,k.u)()...` — the component destructures `conditionId` and calls `useLang()` (`k.u`). The `conditionId` prop identifies this as RecentTrades.
- `function Z(e){let{tokenId:l}=e...` — destructures `tokenId`, this is OrderBook.
- Function names (`I`, `Z`, etc.) vary per build; what matters is the destructured props.

**Props-to-component mapping for common Polymarket components:**
| Destructured props | Likely Component |
|---|---|
| `conditionId` | RecentTrades or PriceHistoryChart |
| `tokenId` | OrderBook |
| `event` + `yesPrice` + `noPrice` | IntelligenceScoreCard |
| `marketPrice` | EdgeScore |

### Local Production Server

Dev mode (`next dev`) won't reproduce this error — it only happens in production builds:

```bash
# Terminal 1: Build + serve
npx next build && npx next start -p 3460

# Browser: Navigate to the failing route
open http://localhost:3460/market/suspect-slug
```

Use a different port per test iteration to avoid port conflicts with stale servers. Kill old servers between builds:

```bash
# Check for running next servers
lsof -i :3000

# Kill them before starting a new one
kill <PID>
```

### Common Red Herrings

- **`prices-history` returning empty data** → the chart component handles this gracefully (checks `history.length === 0`). Not the cause.
- **Chart.js `register()` at module level** → if it failed, the page chunk wouldn't load at all. Not the cause for render-time errors.
- **`use` import from React 19** → unused `import { ..., use } from "react"` doesn't cause runtime errors; the variable is tree-shaken.
- **Module-level errors** → crash the ENTIRE chunk, not individual pages.
- **Render-time errors** → caught by ErrorBoundary, show fallback UI.
- **Stale console messages** → the browser preserves console output across page loads. Always `browser_console(clear=true)` before testing a new build.

### Root Cause Identification Flow

```
Error: "e is not a function" in shared chunk
  │
  ├─ Only on one page? → Component isolation (disable one by one)
  │
  ├─ All pages? → Module-level issue (broken import, ChartJS register)
  │
  └─ Intermittent? → Race condition, data-dependent crash
                      (API returns unexpected shape for certain markets)
```

For **data-dependent crashes** (only certain markets/items crash), the root cause is almost always an unexpected API response shape for that specific item. Check:
- `item.markets[0]` being undefined when expected to exist
- `outcomePrices` being an empty string instead of JSON array
- `conditionId` being null/empty when expected to be truthy

### Distinguishing Browser Console Source

When testing multiple local builds on different ports, the browser console accumulates messages from ALL ports. If you see "e is not a function" but the page loads fine, check the stack trace URL:

```
at http://localhost:3462/...chunk.js:1:111612   ← from OLD server, not current
at http://localhost:3463/...chunk.js:1:111612   ← from current test
```

Always clear the console (`browser_console(clear=true)`) before testing a new build, and verify the port in the stack trace matches your current server.

---

## Direct Imports vs Barrel Imports (MUI / Large UI Libraries)

When Next.js tree-shakes barrel imports (`import { Box, Card } from "@mui/material"`), it can sometimes strip a component that IS used, causing React to find `undefined` as the component type during rendering → "e is not a function".

**Prefer direct imports for UI library components used in client components:**

```tsx
// BAD — barrel import, risk of tree-shaking ambiguity
import { Box, Card, Typography, Chip } from "@mui/material";

// GOOD — direct import, no tree-shaking ambiguity
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
```

This matters most in:
- Page chunks (dynamically loaded routes), not shared chunks
- Components rendered conditionally (`{condition && <Component />}`)
- Components that use many MUI elements (5+)
- Components where "e is not a function" happens *during render* (not module load)
The barrel import creates a single dependency web the tree-shaker can't safely prune. Direct imports give it clear per-component signals.
