# React Infinite Re-Render Loop

## Diagnosis

**Symptom:** Repeated identical network requests to the same API endpoint (`GET /api/xxx 304` firing every few milliseconds). The page works but the network tab is a firehose.

**Root cause:** A `useEffect` dependency that changes every render, creating an infinite cycle:

```
Function defined inline in component body
  → new reference on every render
    → useEffect fires (dep changed)
      → setState() called
        → re-render
          → new function reference again
            → useEffect fires again... ∞
```

## Common Triggers

### 1. Plain function as useEffect dep

```tsx
// ❌ BAD — recriated every render
function notify(msg: string) { ... }
useEffect(() => { fetch(); }, [notify]);
```

**Fix:** Use `useCallback` or remove from deps:

```tsx
// ✓ useCallback
const notify = useCallback((msg: string) => { ... }, [deps]);
useEffect(() => { fetch(); }, [notify]);

// ✓ Or stable context reference
const { showSnackbar } = useSnackbar();  // stable, memoized by provider
useEffect(() => { fetch(); }, [showSnackbar]);
```

### 2. Inline arrow function as dep (always a new ref)

```tsx
// ❌ BAD — anonymous function, new every render
useEffect(() => { fetch(); }, [() => {}]);
```

### 3. Object/array literal as dep (new ref every render)

```tsx
// ❌ BAD — new object every render
useEffect(() => { fetch(); }, [{ key: 'value' }]);
```

## Tell-Tale Signs

- Browser tab slows down or crashes after a few seconds
- Network tab shows the same request repeating every ~50ms
- `console.log` inside the effect fires on every render (way more than expected)
- Component re-renders without any user interaction

## How to Verify

1. Open browser DevTools → Network tab
2. Filter to XHR/Fetch requests
3. Watch for repeating `GET /api/... 304` at sub-second intervals
4. If it's looping: open the component source
5. Check the `useEffect` dependency array for:
   - Functions defined above it in the component
   - Objects/arrays created inline
   - Values from `useState` that are being set inside the effect

## Quick Fix Pattern

If the effect should only run once (on mount):

```tsx
useEffect(() => {
  fetchUsers();
}, []);  // empty deps — runs once
```

But if the function inside the effect needs external values (like a snackbar), either:
- Use a **context hook** (context providers memoize their values)
- Wrap the function in `useCallback` with the right deps
- Use a `ref` to hold the callback without it being a dep

## Context Hook Stability

Hooks from a well-built context provider are safe as useEffect deps:

```tsx
const { showSnackbar } = useSnackbar();  // stable reference
useEffect(() => { fetch().catch(() => showSnackbar("erro")); }, [showSnackbar]);
// ^ This will NOT loop because showSnackbar never changes between renders
```

## Real Session Example

PR #31 introduced `notify()` as an inline function in Vote.tsx, used as a useEffect dep. Result: `GET /api/list 304` firing every render. Fix: replaced with `useSnackbar().showSnackbar` (stable context reference) and removed the inline function entirely. PR #32.
