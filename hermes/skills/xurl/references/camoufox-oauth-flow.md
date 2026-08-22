# Camoufox OAuth Flow — Working Recipe

This reference documents the **proven working flow** for completing `xurl auth oauth2` on a headless server using Camoufox (anti-detection Firefox fork). This complements the general headless-setup.md.

## Prerequisites

- Camoufox server running on port 9377 (`/root/camofox-browser`)
- xurl CLI installed and app registered (`xurl auth apps add my-app --client-id ... --client-secret ...`)
- Target X account that uses **Google Sign-In** (NOT email/password — that redirects to phone signup for Google-linked accounts)

## Step-by-Step

### 1. Start xurl OAuth and intercept the authorization URL

```bash
# Replace xdg-open with a URL-capturing script
cp /usr/bin/xdg-open /usr/bin/xdg-open.real
cat > /usr/bin/xdg-open << 'EOF'
#!/bin/bash
echo "$@" > /tmp/xurl-oauth-url.txt
exit 0
EOF
chmod +x /usr/bin/xdg-open

# Start OAuth flow (background via terminal tool)
xurl auth oauth2 --app my-app

# Wait a few seconds, then capture
sleep 5
OAUTH_URL=$(cat /tmp/xurl-oauth-url.txt)

# Restore real xdg-open
cp /usr/bin/xdg-open.real /usr/bin/xdg-open
```

### 2. Navigate Camoufox tab to the OAuth URL

```bash
curl -s -X POST http://localhost:9377/tabs \
  -H 'Content-Type: application/json' \
  -d "{\"userId\":\"xurl\",\"sessionKey\":\"oauth\",\"url\":\"$OAUTH_URL\"}"
```

### 3. Handle the login page

The OAuth page shows "Log in" link. Click it.

```bash
# Get tab ID from step 2 response
TAB_ID="<tab-id>"

# Click "Log in"
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/click" \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e1"}'
```

On the login page, **do NOT enter email/password** — for Google-linked accounts, X redirects to phone signup. Instead:

### 4. Sign in with Google

```bash
# The login page has a "Sign in with Google" button
# It opens a popup tab for Google OAuth
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/click" \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e3"}'
```

This opens a new Google sign-in tab. Find it with `GET /tabs?userId=xurl`.

### 5. Complete Google authentication

In the Google sign-in tab:
1. Enter email → click Next
2. Enter password → click Next
3. Handle **2FA SMS** if Google requests it (send code to phone, user provides it)
4. Enter 2FA code → click Next

```bash
# Type email
curl -s -X POST "http://localhost:9377/tabs/$GOOGLE_TAB_ID/type" \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e2","text":"email@example.com"}'

# Click Next
curl -s -X POST "http://localhost:9377/tabs/$GOOGLE_TAB_ID/click" \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e6"}'

# Type password
curl -s -X POST "http://localhost:9377/tabs/$GOOGLE_TAB_ID/type" \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e1","text":"password"}'

# Click Next
curl -s -X POST "http://localhost:9377/tabs/$GOOGLE_TAB_ID/click" \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e5"}'

# Handle 2FA if needed (user provides SMS code)
curl -s -X POST "http://localhost:9377/tabs/$GOOGLE_TAB_ID/type" \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e2","text":"038499"}'

curl -s -X POST "http://localhost:9377/tabs/$GOOGLE_TAB_ID/click" \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e4"}'
```

### 6. Return to X tab and use the Google iframe

After Google authenticates, close the Google tabs and return to the X OAuth tab. **Key trick**: the X OAuth page has a Google iframe that now shows "Continue as <Name>" — click this to complete X login via Google.

```bash
# Go back to the X OAuth page (re-navigate with the captured URL)
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/navigate" \
  -H 'Content-Type: application/json' \
  -d "{\"userId\":\"xurl\",\"url\":\"$OAUTH_URL\"}"

# The Google iframe shows "Continue as <Name>" button
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/click" \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e4"}'
```

### 7. Authorize the app

After Google sign-in propagates to X, the **authorize app page** appears:
- Shows the X account name and the app requesting access
- Click "Authorize app"

```bash
curl -s -X POST "http://localhost:9377/tabs/$TAB_ID/click" \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e3"}'
```

X redirects to `http://localhost:8080/callback?code=...` which is xurl's local OAuth callback server. The xurl process receives the code and exchanges it for tokens.

### 8. Verify

```bash
xurl auth status
# Should show: oauth2: @username

xurl whoami
# Should return profile data
```

## Known Issues

- **Google popup tabs don't have `window.opener`** — Camoufox tabs opened via REST API are NOT JavaScript popups, so Google's postMessage to opener fails. The solution is the iframe approach (step 6): after Google auth, the iframe on the X page shows "Continue as <Name>".
- **Google 2FA SMS** — the phone number must be accessible. User receives the code and provides it mid-flow.
- **xurl timeout** — the xurl OAuth server has a timeout (~5 minutes). If the Google auth flow takes longer, xurl exits with "authentication timed out". Start a new `xurl auth oauth2` and retry (the Google session persists in Camoufox, so it's faster the second time).
- **Element refs change** — Camoufox refs (`e1`, `e2`, etc.) are DOM-dependent. Always get a fresh snapshot before clicking/typing to verify the correct ref.
