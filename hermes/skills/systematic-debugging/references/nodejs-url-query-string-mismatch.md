# Node.js HTTP Server: URL Query String Mismatch

## Symptom

Browser shows broken image / failed resource load. The endpoint works via `curl` but not from a browser `<img>` tag or `<script>` tag.

## Root Cause

The browser appends cache-busting query parameters (e.g., `?t=1234567890`) to resource URLs. The server's route handler uses exact string comparison (`req.url === "/path"`) which fails when the URL includes `?...`.

The request falls through to the default/fallback handler, which returns the wrong content type (e.g., HTML instead of PNG).

## Debugging Path (Systematic)

1. **Verify via curl (works):** `curl -s -o /dev/null -w "%{content_type}" http://localhost:3000/qr`
2. **Verify with query string (broken):** `curl -s -o /dev/null -w "%{content_type}" "http://localhost:3000/qr?t=123"`
3. **Check browser raw bytes:** In browser console: `fetch('/qr?t=...').then(r => r.arrayBuffer()).then(buf => { const b = new Uint8Array(buf); return Array.from(b.slice(0,8)).map(x=>x.toString(16).padStart(2,'0')).join(' '); })`
   - `89 50 4e 47 ...` = PNG (working)
   - `3c 21 44 4f 43 54 59 50` = `<!DOCTYP` = HTML fallback (broken)
4. **Trace to root cause:** The `req.url` includes query string; `===` comparison fails.

## Fix

```javascript
// BEFORE (broken)
function handler(req, res) {
  if (req.url === "/qr") {       // FAILS for /qr?t=123
    // serve image
  } else {
    // fallback: serves HTML to everyone
  }
}

// AFTER (fixed)
function handler(req, res) {
  const pathname = req.url.split("?")[0];  // strip query string
  if (pathname === "/qr") {
    // serve image
  } else if (pathname === "/health") {
    // health check
  } else {
    // fallback HTML
  }
}
```

## Why curl Works but Browser Doesn't

- `curl http://localhost:3002/qr` → no query string → matches `=== "/qr"` → returns PNG
- Browser `<img src="/qr?t=123456">` → query string → doesn't match → falls through to HTML

## Prevention

Always strip query strings before route matching in Node.js HTTP servers:

```javascript
const pathname = req.url.split("?")[0];
// or: new URL(req.url, `http://${req.headers.host}`).pathname
```

Apply to ALL route comparisons, not just the one that's broken.

## Also Applies To

- Any Node.js HTTP/HTTPS server (not just Express — Express handles this automatically via `req.path`)
- WebSocket upgrade handlers checking `req.url`
- Custom middleware doing path-based routing
- Health check endpoints that browsers or monitoring tools may call with query params
