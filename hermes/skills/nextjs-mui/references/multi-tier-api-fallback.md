# Multi-Tier API Fallback Pattern

When building data dashboards that depend on third-party APIs, use this fallback chain to prevent blank screens when APIs fail.

## Pattern

```
Tier 1: Primary API (with API key) → Tier 2: Public fallback (RSS/no-auth endpoint) → Tier 3: Mock data
```

## Implementation Template

```typescript
export async function fetchMyData(): Promise<DataType[]> {
  // Tier 1: Primary API (requires API key)
  const apiKey = process.env.NEXT_PUBLIC_MYAPI_KEY;
  if (apiKey) {
    try {
      const res = await fetch(`https://api.example.com/data?apiKey=${apiKey}`);
      if (res.ok) return await res.json();
    } catch {
      // Fall through to next tier
    }
  }

  // Tier 2: Public/no-auth fallback
  try {
    const res = await fetch("https://public-api.example.com/data");
    if (res.ok) {
      const raw = await res.text();
      return parseRawResponse(raw); // Parse differently if format differs
    }
  } catch {
    // Fall through to mock
  }

  // Tier 3: Mock data (never fails)
  return getMockData();
}
```

## Where to place API keys

| Context | Where to set |
|---------|-------------|
| Local dev | `.env.local` |
| Vercel deploy | Vercel Dashboard > Settings > Environment Variables |
| GitHub forks | Can't set — app falls back to Tier 2 or 3 automatically |

## Detecting mock mode for UI

```tsx
const [showMockBadge, setShowMockBadge] = useState(false);
useEffect(() => {
  if (!process.env.NEXT_PUBLIC_MYAPI_KEY) setShowMockBadge(true);
}, []);

// In render:
{showMockBadge && (
  <Typography variant="caption" sx={{ color: "#f0883e" }}>
    ⚡ Modo simulado — configure NEXT_PUBLIC_MYAPI_KEY no .env para dados reais
  </Typography>
)}
```

## When to use

- News/newsletter dashboards (NewsAPI → RSS → Mock)
- Crypto/finance data (paid API → CoinGecko free → Mock)
- Social media analytics (Graph API → scraping → Mock)
- Weather/climate (WeatherAPI → OpenWeatherMap free → Mock)

## Pitfalls

- **Rate limiting**: Tier 1 may have daily/monthly request caps. Use polling intervals wisely (default: 2-5 min).
- **Error vs empty**: An API returning `[]` is not a failure — don't fall through. Only fall through on network errors or non-2xx status.
- **Type compatibility**: Tier 2/3 may return different JSON shapes than Tier 1. Normalize in each branch.
- **Badge visibility**: The mock badge should be outside the data fetch — it's a client-side check for the env var, not a server-side check.
