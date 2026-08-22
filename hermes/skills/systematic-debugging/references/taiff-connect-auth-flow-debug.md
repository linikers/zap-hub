# Taiff Connect Backend — Auth Flow Debugging Reference

## Architecture

Stack: Express 5 + TypeORM + PostgreSQL + Yup schemas
Naming: Portuguese (entities, columns, enums)
Pattern: Controller → Service → Repository (TypeORM)
Auth: JWT (jsonwebtoken) + bcrypt
Social: Firebase Admin SDK (Google, Apple)
SMS: Twilio Verify API
Email: NOT IMPLEMENTED (TODO in ForgotPasswordService)

## Provider Fallback Pattern

Both VerifyService and NotificationService use a facade pattern:

```
if (env.twilioAccountSid && env.twilioAuthToken && env.twilioVerifyServiceSid) {
  → TwilioVerifyProvider (real SMS)
} else {
  → ConsoleVerifyProvider (logs to console only, NO actual SMS)
}
```

Same for NotificationService: TwilioProvider vs ConsoleNotificationProvider.

**Common failure mode**: Environment variables not injected in K8s → falls back to console → user reports "SMS not sending". Check pod env vars first.

## Known Issues (as of 2026-06-20)

### 1. ForgotPasswordService — Email never sent
File: `src/services/auth/ForgotPasswordService.ts`
Line 35: `// TODO: Enviar e-mail com o token aqui (nodemailer / SES / etc.)`
The service generates token + saves to DB but never sends email. No email provider configured.

### 2. Firebase Social Login — Generic error hides root cause (FIXED 2026-06-23)
File: `src/services/auth/FirebaseAuthProvider.ts`
Line 82: Now includes `error.message` in brackets in the response.
Before: `throw new AppError("Token social invalido ou expirado...", 401)`
After: `throw new AppError("Token social invalido ou expirado. [${detail}]", 401)`

**Confirmed root cause (2026-06-23):** The mobile app was sending an expired Firebase idToken (>1 hour). Firebase idTokens expire after 1 hour and this CANNOT be changed. The fix is on the app side: force refresh before calling `/auth/social`.

**Testing without mobile app:** Use Firebase REST API to generate an idToken:
```bash
curl -s -X POST "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=WEB_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"senha","returnSecureToken":true}'
# Then use the returned idToken in POST /auth/social
```

**Confirmed working:** Backend Firebase Admin SDK, private key, project ID all correct. Test passed with email/password idToken.

### 3. Social Login — Only Google and Apple supported
Schema: socialLoginSchema → provider: oneOf(["google", "apple"])
Facebook is NOT in the allowed list.

### 4. SMS — Twilio Verify
Route: POST /notifications/verify/send (public, no auth)
Route: POST /notifications/verify/check (public, no auth)
Channel: hardcoded "sms" (was "auto", fixed in PR #65)

## Helm Environment Variables

All secrets in helm/taiff-connect/values.yaml under secrets: section.
Defaults are empty strings — MUST be overridden via --set at deploy.

Key variables:
- TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_VERIFY_SERVICE_SID
- FIREBASE_PROJECT_ID, FIREBASE_CLIENT_EMAIL, FIREBASE_PRIVATE_KEY
- JWT_SECRET

If Twilio vars empty → falls back to console provider (no real SMS).
If Firebase vars empty → throws 503 "Firebase nao configurado".

## Routes Without Authentication (public)

| Route | Purpose | Security Note |
|-------|---------|---------------|
| POST /auth/register | New user | Normal |
| POST /auth/login | Login | Normal |
| POST /auth/forgot-password | Password recovery | Only email, no SMS |
| POST /auth/reset-password | Reset with token | Normal |
| POST /auth/social | Google/Apple login | Firebase-dependent |
| POST /notifications/verify/send | Send OTP | Public — any phone |
| POST /notifications/verify/check | Check OTP | Public — any phone |

## Debugging Checklist

1. Check pod env vars: kubectl exec -n production pod -- env | grep -E "TWILIO|FIREBASE"
2. Check Helm values: helm get values -n production taiff-connect
3. Check logs for tagged errors: [FirebaseAuthProvider], [TwilioVerifyProvider]
4. Verify Twilio credentials: Twilio Console → Account Info
5. Verify Firebase credentials: Firebase Console → Project Settings → Service Accounts
