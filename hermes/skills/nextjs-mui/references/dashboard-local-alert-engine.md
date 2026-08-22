# Local Alert Engine (Configurable + Persistent)

Lightweight, DB-free alert/notification system for dashboards. Polls an external API at intervals, checks user-defined rules, and persists events to localStorage. No backend required.

## Architecture

```
src/lib/alerts.ts          ← Engine: rules, events, start/stop, localStorage
src/components/AlertCenter.tsx  ← Admin UI: rule config + event history
src/components/AdminLayout.tsx  ← Sidebar badge showing unread count
```

## Alert Types

Define the kinds of alerts your app supports:

```ts
export type AlertType = "whale" | "volume" | "odds" | "opportunity";
```

Each type maps to a detection rule the user can toggle and configure.

## Data Model

### Rule
```ts
export interface AlertRule {
  id: string;
  type: AlertType;
  label: string;              // Human-readable
  enabled: boolean;
  threshold: number;          // Configurable via slider
  marketId?: string;          // Specific or all
  lastTriggered?: number;
}
```

### Event (fired when a rule matches)
```ts
export interface AlertEvent {
  id: string;
  ruleId: string;
  type: AlertType;
  title: string;
  message: string;
  severity: "info" | "warning" | "high";
  timestamp: number;
  read: boolean;
  marketSlug?: string;
}
```

## Engine Pattern (polling)

```ts
let pollingInterval: ReturnType<typeof setInterval> | null = null;
let previousState: Map<string, { volume: number; price: number }> = new Map();

export function startAlertEngine(
  rules: AlertRule[],
  onAlert: (event: AlertEvent) => void
) {
  if (pollingInterval) clearInterval(pollingInterval);

  const tick = async () => {
    const enabled = rules.filter((r) => r.enabled);
    if (enabled.length === 0) return;

    const data = await fetchLatestData();

    for (const item of data) {
      const prev = previousState.get(item.id);
      // Compare current vs previous to detect changes...
      // If change exceeds threshold → onAlert(newEvent)
      previousState.set(item.id, { volume: item.volume, price: item.price });
    }
  };

  tick(); // Immediate first tick
  pollingInterval = setInterval(tick, 30000);

  return () => {
    clearInterval(pollingInterval);
    pollingInterval = null;
    previousState.clear();
  };
}
```

## localStorage Persistence

```ts
const RULES_KEY = "app-alert-rules";
const EVENTS_KEY = "app-alert-events";

export function loadRules(): AlertRule[] {
  if (typeof window === "undefined") return defaultRules();
  const raw = localStorage.getItem(RULES_KEY);
  return raw ? JSON.parse(raw) : defaultRules();
}

export function saveRules(rules: AlertRule[]) {
  localStorage.setItem(RULES_KEY, JSON.stringify(rules));
}

export function addEvent(event: Omit<AlertEvent, "id" | "timestamp" | "read">) {
  const events = loadEvents();
  events.unshift({ ...event, id: `${Date.now()}-${crypto.randomUUID().slice(0,8)}`, timestamp: Date.now(), read: false });
  saveEvents(events.slice(0, MAX_EVENTS));
}
```

## Pitfalls

- **Module-level interval**: `pollingInterval` is a module-level variable. Only one engine can run at a time. If `startAlertEngine` is called while another is running, the old interval is cleared.
- **Cleanup on unmount**: The `return` function from `startAlertEngine` must be called when the component unmounts. In React, store it in a ref and call it in the useEffect cleanup:
  ```tsx
  useEffect(() => {
    const cleanup = startAlertEngine(rules, onAlert);
    return () => cleanup?.();
  }, []);
  ```
- **Async tick**: The tick function is async. `setInterval` does not await it — if a tick takes longer than the interval, overlapping ticks can occur. Add a guard:
  ```tsx
  let ticking = false;
  const tick = async () => {
    if (ticking) return;
    ticking = true;
    try { await doWork(); } finally { ticking = false; }
  };
  ```
- **localStorage in SSR**: Always guard `localStorage` access with `typeof window === "undefined"`. During server-side rendering, `localStorage` does not exist.
- **Stale callbacks**: The `onAlert` callback captured by the interval closure may be stale. Use a ref to keep it fresh:
  ```tsx
  const onAlertRef = useRef(onAlert);
  onAlertRef.current = onAlert;
  // Inside tick: onAlertRef.current(ev)
  ```
