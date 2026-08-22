# OAuth Setup Patterns

## Problem
Getting OAuth tokens in a headless CLI/server environment where `open`/`xdg-open` can't launch a browser for user authorization.

## The xurl Trick

When a CLI tool (like `xurl auth oauth2`) tries to open the browser via `xdg-open` in a headless environment:

1. **Identify the browser-call command**: `strace -f -e trace=execve tool 2>&1 | grep xdg-open`
2. **Temporarily replace xdg-open** with a capture script:
```bash
cp /usr/bin/xdg-open /usr/bin/xdg-open.bak
cat > /usr/bin/xdg-open << 'EOF'
#!/bin/bash
echo "$@" > /tmp/oauth_url.txt
EOF
chmod +x /usr/bin/xdg-open
```
3. **Run the OAuth command** — the URL gets written to `/tmp/oauth_url.txt`
4. **Navigate to that URL** in the Hermes browser: `browser_navigate(url=...)`
5. **Complete the auth flow** in the browser
6. **Restore xdg-open**: `cp /usr/bin/xdg-open.bak /usr/bin/xdg-open`

## Alternative: Run in background, check port
Some tools start a local server first (port 8080 for xurl):
```bash
# Start in background
terminal(background=true, command="xurl auth oauth2 --app myapp")
# Wait for server
sleep 3
# Check server
ss -tlnp | grep 8080
# The tool may have printed the URL to stderr — capture via process log
```

## OAuth Routes Pattern (Next.js App Router)

For custom OAuth flows (Melhor Envio, Mercado Livre, etc.):

```
src/app/api/admin/<provider>/
  auth/route.ts       # GET — redirect to provider's authorize URL
  callback/route.ts   # GET — receive code, exchange for token, save config
```

### Auth Route
```typescript
export async function GET() {
  const params = new URLSearchParams({
    response_type: "code",
    client_id: config.clientId,
    redirect_uri: `${BASE_URL}/api/admin/<provider>/callback`,
    scope: "...",
  });
  return NextResponse.redirect(`${authUrl}?${params.toString()}`);
}
```

### Callback Route
```typescript
export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");
  // Exchange code for token
  const res = await fetch(tokenUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      grant_type: "authorization_code",
      client_id: config.clientId,
      client_secret: config.clientSecret,
      redirect_uri: `${BASE_URL}/api/admin/<provider>/callback`,
      code,
    }),
  });
  // Save token to config file
  // Redirect back to admin page
}
```

## Pitfalls

- **xdg-open replacement only works if caught before the browser call** — some tools cache the browser path at startup
- **Cloudflare blocks headless browser login** — X/Twitter, Reddit, and other sites with CF protection will challenge automated logins even for OAuth
- **OAuth redirect URIs must match exactly** — trailing slash, protocol (http vs https), and port all matter
- **XDG_OPEN env variable doesn't override xdg-open** — you must replace the binary itself
