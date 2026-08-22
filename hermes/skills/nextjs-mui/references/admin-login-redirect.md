# Login Redirect for Admin Users

## Problem

After `signIn("credentials", { ... redirect: false })`, the session JWT is not immediately ready.
Fetching `/api/auth/session` right after signIn may return null or trigger a 404 on `/_log`.

## Solution: Retry Pattern

```tsx
const result = await signIn("credentials", {
  email, password,
  redirect: false,
});

if (result?.error) {
  setError("Credenciais inválidas");
  return;
}

// Retry session fetch with backoff
let session = null;
for (let i = 0; i < 5; i++) {
  try {
    const res = await fetch("/api/auth/session");
    if (res.ok) {
      session = await res.json();
      if (session?.user) break;  // got valid session
    }
  } catch { /* retry */ }
  await new Promise(r => setTimeout(r, 200));
}

// Redirect based on role
if (session?.user?.admin) {
  router.push("/admin");
} else {
  router.push("/");
}
```

## Key Points

- Retry up to 5 times with 200ms delay (total max ~1s)
- Break early when `session.user` is populated (don't wait all 5 retries)
- Admin → `/admin` (dashboard), regular user → `/` (homepage)
- Same login UI for everyone — the redirect difference is invisible to the user
- Google login (`signIn("google", { callbackUrl: "/" })`) cannot do this check server-side, so Google login always goes to `"/"` for now
