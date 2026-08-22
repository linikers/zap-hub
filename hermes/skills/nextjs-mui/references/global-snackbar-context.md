# Global Snackbar Context (Provider + Hook)

Replace `alert()` and per-page snackbar state with a global context that any component can access.

## Pattern

### 1. Create the context

```tsx
// src/contexts/SnackbarContext.tsx
import { createContext, useContext, useState, useCallback, ReactNode } from "react";
import { Snackbar, Alert, AlertColor } from "@mui/material";

interface SnackbarContextType {
  showSnackbar: (message: string, severity?: AlertColor) => void;
}

const SnackbarContext = createContext<SnackbarContextType>({
  showSnackbar: () => {},
});

export function SnackbarProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [severity, setSeverity] = useState<AlertColor>("info");

  const showSnackbar = useCallback((msg: string, sev: AlertColor = "info") => {
    setMessage(msg);
    setSeverity(sev);
    setOpen(true);
  }, []);

  return (
    <SnackbarContext.Provider value={{ showSnackbar }}>
      {children}
      <Snackbar
        open={open}
        autoHideDuration={3000}
        onClose={() => setOpen(false)}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert
          onClose={() => setOpen(false)}
          severity={severity}
          variant="filled"
          sx={{ borderRadius: 2, fontWeight: 500, width: "100%" }}
        >
          {message}
        </Alert>
      </Snackbar>
    </SnackbarContext.Provider>
  );
}

export function useSnackbar() {
  return useContext(SnackbarContext);
}
```

### 2. Wrap in `_app.tsx` or root layout

```tsx
// pages/_app.tsx (Pages Router)
import { SnackbarProvider } from "@/contexts/SnackbarContext";

function MyApp({ Component, pageProps }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider>
        <Component {...pageProps} />
      </SnackbarProvider>
    </ThemeProvider>
  );
}
```

```tsx
// app/layout.tsx (App Router)
import { SnackbarProvider } from "@/contexts/SnackbarContext";

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <ThemeProvider>
          <SnackbarProvider>
            {children}
          </SnackbarProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
```

### 3. Use anywhere

```tsx
import { useSnackbar } from "@/contexts/SnackbarContext";

function MyComponent() {
  const { showSnackbar } = useSnackbar();

  const handleSave = async () => {
    try {
      await api.save(data);
      showSnackbar("Salvo com sucesso!", "success");
    } catch (err) {
      showSnackbar("Erro ao salvar", "error");
    }
  };

  // ...
}
```

## Benefits over prop-drilling or per-page state

- No more `alert()` dialogs anywhere in the codebase
- Components don't need `onOpenSnackBar` props
- Works inside deeply nested components without drilling
- `showSnackbar` ref is stable (`useCallback`) — safe as a `useEffect` dependency (no infinite loops)
- Consistent styling (variant: filled, same duration, same position)

## Migration from alert()

1. Create `SnackbarContext.tsx` in a `contexts/` directory
2. Wrap root component in `_app.tsx` or layout
3. One by one, replace each `alert("msg")` with `showSnackbar("msg", "success"|"error"|"warning"|"info")`
4. Remove `onOpenSnackBar` props from components that no longer need them
5. Remove per-component snackbar state if any

## MUI version compatibility

- Works with MUI v5, v6, and v9 (Snackbar + Alert APIs are stable across these versions)
- For MUI v9: `TransitionComponent` on Snackbar is removed. Default fade transition is used. If you need a slide transition, use `slots={{ transition: Slide }}`.
