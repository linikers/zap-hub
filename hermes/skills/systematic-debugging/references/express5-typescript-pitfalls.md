# Express 5 TypeScript Pitfalls

## Class of Problem

A TypeScript project using Express 5 (`express@^5.x` with `@types/express@^5.x`) fails to compile with type errors that wouldn't occur in Express 4. The root cause is that Express 5 changed several type definitions that break existing Express 4 patterns.

## Known Pitfalls

### 1. `req.params` values typed as `string | string[]`

**Error:**
```
error TS2345: Argument of type 'string | string[]' is not assignable to parameter of type 'string'.
  Type 'string[]' is not assignable to type 'string'.
```

**Cause:** In `@types/express@5.x`, `req.params` values are typed as `string | string[]` (to support Express 5's parameter array feature). In Express 4, they were `string`.

**Fix:** Add a type assertion where the value is passed to a function expecting `string`:

```ts
// ❌ Before (Express 4 — works)
const { cep } = req.params;
service.execute(cep);

// ✅ After (Express 5 — type assertion needed)
const { cep } = req.params;
service.execute(cep as string);

// ✅ Alternative — runtime conversion (safe but changes behavior on arrays)
const { cep } = req.params;
service.execute(String(cep));
```

**Note:** For named route params like `:param`, the runtime value is always a single `string`. The `string[]` variant exists for internal Express 5 use with route arrays. `as string` is safe here.

### 2. `req.query` typing (unchanged but worth noting)

Express 5 still uses `qs`'s `ParsedQs` for `req.query`, which gives `string | string[] | ParsedQs | ParsedQs[] | undefined`. This is the same as Express 4 and is **not** a new issue — but becomes more visible when also fixing `req.params` issues.

### 3. Request handler / middleware signatures

Express 5 may have stricter handler typing in some versions. If you see errors about handler signatures, check whether the handler has the right arity (4 params for error handlers).

## Prevention

- When upgrading from Express 4 to Express 5, do a full `tsc --noEmit` build to catch all type regressions.
- Use `req.params` values with a type assertion or a helper guard:
  ```ts
  function paramAsString(p: string | string[]): string {
    return Array.isArray(p) ? p[0] : p;
  }
  ```
- Consider adding a `RouteParams` interface for typed params in controllers.

## Verification

After fixing:
```bash
npx tsc --noEmit  # Should pass with zero errors
```
