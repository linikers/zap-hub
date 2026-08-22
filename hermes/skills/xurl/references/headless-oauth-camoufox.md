# Headless OAuth 2.0 PKCE Flow — xurl + Camoufox

Quando o servidor nao tem browser (headless) e o fluxo `xurl auth oauth2`
tenta abrir xdg-open, use esta tecnica para completar a autenticacao.

## Visao Geral

```
xurl auth oauth2 → xdg-open (falso) → captura URL de autorizacao
                → Camoufox navega ate URL
                → Login no X (Google SSO + 2FA via SMS se necessario)
                → Autoriza o app
                → X redireciona para localhost:8080/callback
                → xurl recebe o code e troca por tokens
```

## Passo a Passo

### 1. Fake xdg-open para capturar URL

```bash
# Backup real
cp /usr/bin/xdg-open /usr/bin/xdg-open.real

# Fake que salva URL
cat > /usr/bin/xdg-open << 'EOF'
#!/bin/bash
echo "$@" > /tmp/xurl-oauth-url.txt
exit 0
EOF
chmod +x /usr/bin/xdg-open

# Iniciar xurl em background
# (use terminal com background=true)
xurl auth oauth2 --app NOME_DO_APP

# URL capturada em /tmp/xurl-oauth-url.txt
```

### 2. Restaurar xdg-open depois

```bash
cp /usr/bin/xdg-open.real /usr/bin/xdg-open
```

### 3. Navegar com Camoufox

```bash
# Criar tab com a URL de autorizacao
curl -s -X POST http://localhost:9377/tabs \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","sessionKey":"oauth","url":"URL_CAPTURADA"}'

# Ver snapshot
curl -s "http://localhost:9377/tabs/TAB_ID/snapshot?userId=xurl&full=true"
```

### 4. Login Google SSO (headless)

Na pagina de autorizacao do X, clicar "Log in" [e1], depois:

```bash
# Clicar "Sign in with Google" (pode abrir nova aba)
curl -s -X POST "http://localhost:9377/tabs/TAB_ID/click" \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e3"}'
```

Na nova aba do Google:
- Digitar email no campo [e2]
- Clicar Next [e6]
- Digitar senha no campo [e1]
- Clicar Next [e5]

Se pedir 2FA:
- Clicar "Text" ou "Try another way"
- Usuario envia o codigo SMS
- Digitar codigo no campo e clicar Next

### 5. Autorizar app

Apos login Google completo, voltar a aba do X (ou usar o iframe
"Continuar como Liniker") e clicar "Authorize app".

### 6. Callback

O X redireciona para `http://localhost:8080/callback?code=...`
O xurl (rodando em background) captura e troca por tokens.

### 7. Verificar

```bash
xurl auth status
xurl whoami
xurl auth default NOME_DO_APP USERNAME
```

## Pitfalls

- **QR code do QR na sessao do Google expira** — se o fluxo demorar,
  o Google pode pedir 2FA novamente
- **React do X nao aceita texto injetado via JavaScript** — para postar
  pelo browser, use a API, que requer creditos
- **Camoufox sem proxy residencial** — algumas paginas podem detectar
  automacao (Cloudflare)
- **OAuth token expirado apos timeout** — se o xurl demorar muito no
  fluxo manual, pode expirar. Gerar novo fluxo.
