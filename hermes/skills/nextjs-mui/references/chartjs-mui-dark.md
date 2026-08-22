# Chart.js Integration with MUI Dark Theme

## Setup

```bash
npm install chart.js react-chartjs-2
```

## Registration

Register Chart.js components once (shared module or component top-level):

```tsx
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler);
```

Only register what you use. Registration is global — do once per app.

## MUI Dark Theme Palette

| Token | Hex | Use |
|-------|-----|-----|
| Primary | `#7c3aed` | Line, active elements |
| Primary + alpha | `rgba(124, 58, 237, 0.1)` | Fill area |
| Secondary (green) | `#3fb950` | Positive/probability YES |
| Error (red) | `#f85149` | Negative/probability NO |
| Warning (orange) | `#f0883e` | Medium severity |
| Border/text secondary | `#8b949e` | Axis labels, tooltips |
| Surface | `#161b22` | Card/chart background |
| Border | `#30363d` | Grid lines |
| Canvas bg | `#0d1117` | Page background |

## Interval Selector Pattern

Use Chips (not buttons or Select) for interval switching — they match MUI dark theme naturally:

```tsx
const INTERVALS = [
  { id: "7d", label: "7d", fidelity: 50 },
  { id: "1m", label: "1m", fidelity: 100 },
  { id: "all", label: "Max", fidelity: 200 },
] as const;

// In component
const [interval, setInterval] = useState<"7d" | "1m" | "all">("1m");
const [history, setHistory] = useState([]);

useEffect(() => {
  fetchHistory(interval).then(setHistory);
}, [interval]);

// Render
<Box sx={{ display: "flex", gap: 0.5 }}>
  {INTERVALS.map((int) => (
    <Chip
      key={int.id}
      label={int.label}
      size="small"
      onClick={() => setInterval(int.id)}
      variant={interval === int.id ? "filled" : "outlined"}
      sx={{
        color: interval === int.id ? "#e6edf3" : "#8b949e",
        bgcolor: interval === int.id ? "#7c3aed" : "transparent",
        borderColor: "#30363d",
        height: 24,
        cursor: "pointer",
      }}
    />
  ))}
</Box>
```

## Line Chart Component Template

```tsx
<Box sx={{ height: 250 }}>
  <Line
    data={{
      labels: history.map((pt) => new Date(pt.t * 1000).toLocaleDateString()),
      datasets: [{
        label: "Price",
        data: history.map((pt) => Number(pt.p) * 100),
        borderColor: "#7c3aed",
        backgroundColor: "rgba(124, 58, 237, 0.1)",
        fill: true,
        tension: 0.3,
        pointRadius: 0,
        borderWidth: 2,
      }],
    }}
    options={{
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { enabled: true } },
      scales: {
        x: {
          ticks: { color: "#8b949e", maxTicksLimit: 8, font: { size: 10 } },
          grid: { color: "rgba(48, 54, 61, 0.5)" },
        },
        y: {
          min: 0,
          max: 100,
          ticks: {
            color: "#8b949e",
            callback: (v) => `${v}%`,
            font: { size: 10 },
          },
          grid: { color: "rgba(48, 54, 61, 0.5)" },
        },
      },
    }}
  />
</Box>
```

## Pitfalls

- **Chart.js registration is global**: If you register components in multiple files, it's fine (idempotent) but wasteful. Register once.
- **Responsive charts need explicit height**: `<Box sx={{ height: 250 }}>` wrapping the `<Line>` is required — Chart.js can't infer height from flex containers.
- **Re-renders**: Don't inline `data` or `options` objects — wrap in `useMemo` or define outside component if they don't depend on props. Otherwise every render recreates the chart.
- **Dark theme tooltips**: Chart.js default tooltip is white — add tooltip styling via `options.plugins.tooltip`.
