# Headless / Server Setup — xurl OAuth sem Browser

## Problema

`xurl auth oauth2 --app my-app` abre um browser pra fazer o fluxo OAuth 2.0 PKCE.
Em servidores headless (Linux sem display, SSH, Docker, WSL sem browser) ou quando
Cloudflare bloqueia a autenticação no X, isso não funciona.

## Solução: Gerar o ~/.xurl YAML manualmente

### 1. Criar o app no X Developer Portal (FAÇA ISSO NO SEU NOTEBOOK/DESKTOP)

1. Vá em https://developer.x.com/en/portal/dashboard
2. Crie um app ou use um existente
3. Em "User Authentication Settings":
   - App type: **Web App, Automated App or Bot** (NÃO "Native App")
   - Callback/Redirect URI: `http://localhost:8080/callback`
   - Website URL: qualquer URL válida (ex: `https://github.com/linikers`)
   - Permissions (OAuth 2.0): `app.read`, `tweet.read`, `tweet.write`, `users.read`, `dm.read`, `dm.write`, `offline.access`
4. Anote o **Client ID** e **Client Secret** (na página Keys and Tokens)

### 2. No servidor headless, registrar o app

```bash
xurl auth apps add my-app --client-id CLIENT_ID --client-secret CLIENT_SECRET
xurl auth default my-app
```

### 3. Gerar token OAuth 2.0 manualmente

Se não tem browser no servidor, gere o token em outro lugar e copie o arquivo:

**No seu desktop/notebook (com browser):**
```bash
xurl auth oauth2 --app my-app
# Isso abre o browser, faz login no X, autoriza
```

**Copie o arquivo de token gerado:**
```bash
# O token fica em ~/.xurl como YAML
# Copie o ~/.xurl do desktop para o servidor
```

O arquivo `~/.xurl` tem essa estrutura:
```yaml
default: my-app
apps:
  my-app:
    oauth2:
      liniker@deltasge.com.br:
        access_token: "..."
        refresh_token: "..."
        expires_at: "..."
```

### 4. Alternativa: Gerar token via curl (100% headless)

Se não tem acesso a uma máquina com browser:

1. Crie um app no X Developer Portal com as scopes certas
2. Gere um Bearer Token (das "Keys and Tokens" → "Bearer Token")
3. Use o app auth com Bearer Token pra testes:
   ```bash
   xurl auth apps add my-bearer-app --bearer-token SEU_BEARER_TOKEN
   xurl auth default my-bearer-app
   ```
4. Teste com `xurl whoami` (só funciona pra endpoints públicos)
5. Pra escrever (postar, etc.), precisa OAuth 2.0 com refresh_token — infelizmente
   não tem como pular o login via browser nesse caso. O X API exige o fluxo
   OAuth 2.0 PKCE interativo pelo menos uma vez pra gerar o refresh_token.

### 5. Se Cloudflare estiver bloqueando o login (headless server)

O X usa Cloudflare — sintomas típicos:
- Página de login não carrega ou redireciona pra CAPTCHA/desafio
- "Something went wrong" após autorizar o app
- Browser headless normal (Chromium/Puppeteer) é bloqueado antes de carregar

#### Solução A (recomendada): Desktop + copiar ~/.xurl
Fazer o login OAuth uma vez no desktop com browser real, copiar o `~/.xurl` pro servidor.

#### Solução B (headless, com Camoufox + Google SSO) — ✅ VALIDADO

O [Camoufox](https://github.com/jo-inc/camofox-browser) (Firefox fork com anti-detection C++) consegue **carregar o X sem Cloudflare** em servidor headless. A REST API dele permite automação completa.

Este fluxo foi testado e funciona com **conta X criada via Google SSO** (sem email/senha local):

**Setup:**
```bash
git clone https://github.com/jo-inc/camofox-browser.git
cd camofox-browser
npm install && npm start
# Servidor REST na porta 9377
```

**Fluxo OAuth completo (validado):**

1. Capture a URL de autorização OAuth com o truque do `xdg-open`:
   ```bash
   # Backup do xdg-open real
   cp /usr/bin/xdg-open /usr/bin/xdg-open.real
   
   # Substitua por um script que salva a URL em vez de abrir browser
   cat > /usr/bin/xdg-open << 'EOF'
   #!/bin/bash
   echo "$@" > /tmp/xurl-oauth-url.txt
   exit 0
   EOF
   chmod +x /usr/bin/xdg-open
   
   # Inicie o xurl auth em background (vai chamar xdg-open com a URL)
   xurl auth oauth2 --app my-app &
   sleep 5
   
   # A URL de autorização está em /tmp/xurl-oauth-url.txt
   OAUTH_URL=$(cat /tmp/xurl-oauth-url.txt)
   
   # Restaure o xdg-open original
   cp /usr/bin/xdg-open.real /usr/bin/xdg-open
   ```

2. Crie uma tab no Camoufox com a URL de autorização:
   ```bash
   curl -s -X POST http://localhost:9377/tabs \
     -H 'Content-Type: application/json' \
     -d "{\"userId\":\"xurl\",\"sessionKey\":\"oauth\",\"url\":\"$OAUTH_URL\"}"
   # Retorna: {"tabId": "b06328fd-..."}
   ```

3. Na página de autorização, clique **"Log in"**:
   ```bash
   curl -s -X POST http://localhost:9377/tabs/TAB_ID/click \
     -H 'Content-Type: application/json' \
     -d '{"userId":"xurl","ref":"e1"}'
   ```

4. Na página de login, clique no iframe do **Google SSO** ("Continue as ..." ou "Sign in with Google"):
   ```bash
   # Pegue o snapshot primeiro pra achar o ref do iframe
   curl -s "http://localhost:9377/tabs/TAB_ID/snapshot?userId=xurl&full=true"
   # Procure por "Continue as NOME" ou similar no iframe
   
   # Clique no elemento do iframe
   curl -s -X POST http://localhost:9377/tabs/TAB_ID/click \
     -H 'Content-Type: application/json' \
     -d '{"userId":"xurl","ref":"e11"}'
   ```

5. **Login Google via Camoufox (validado com 2FA SMS):**
   - O Google abre popup em nova aba
   - Digite email no campo "Email or phone"
   - Clique Next
   - Digite a senha
   - Se 2FA estiver ativo, escolha SMS ou ligação e digite o código recebido
   - O Google autentica e redireciona pra `/gsi/transform`

6. Após Google auth, o popup fecha e o **cookie de sessão Google persiste no navegador**. Volte ao fluxo:
   ```bash
   # Navegue de volta à URL de autorização original
   curl -s -X POST "http://localhost:9377/tabs/TAB_ID/navigate" \
     -H 'Content-Type: application/json' \
     -d "{\"userId\":\"xurl\",\"url\":\"$OAUTH_URL\"}"
   ```

7. O iframe do Google na página agora mostra **"Continuar como NOME"**. Clique nele para logar no X:
   ```bash
   # O snapshot vai mostrar "Continuar como Liniker" [e4]
   curl -s -X POST http://localhost:9377/tabs/TAB_ID/click \
     -H 'Content-Type: application/json' \
     -d '{"userId":"xurl","ref":"e4"}'
   ```

8. Aguarde o processamento SSO. Depois navegue novamente pra URL de autorização:
   ```bash
   sleep 5
   curl -s -X POST "http://localhost:9377/tabs/TAB_ID/navigate" \
     -H 'Content-Type: application/json' \
     -d "{\"userId\":\"xurl\",\"url\":\"$OAUTH_URL\"}"
   ```

9. A página agora mostra **"Authorize app"**. Clique:
   ```bash
   # Procure por "hermesBigAg wants to access your X account"
   # e clique "Authorize app" [e3]
   curl -s -X POST http://localhost:9377/tabs/TAB_ID/click \
     -H 'Content-Type: application/json' \
     -d '{"userId":"xurl","ref":"e3"}'
   ```

10. O X redireciona pra `http://localhost:8080/callback?code=...` e o `xurl auth oauth2` em background recebe o token:
    ```bash
    # Verifique
    xurl auth status
    # Deve mostrar: oauth2: NOME_DO_USUARIO
    xurl auth default my-app USERNAME
    xurl whoami
    ```

**Pitfalls do fluxo:**
- O popup do Google aberto como aba separada (não `window.open`) **NÃO TEM `window.opener`**. O ID token não é enviado de volta via postMessage. Mas a sessão Google persiste via cookie — por isso o passo 6 (navegar de volta) funciona.
- O formulário React do X pode não exibir botão "Next" como elemento acessível — usar Google SSO (iframe) em vez do formulário de email.
- O fluxo completo leva alguns minutos (Google 2FA incluso). O `xurl auth oauth2` em background pode **timeout** se o processo demorar. Solução: iniciar um novo `xurl auth oauth2` com a sessão Google já ativa no navegador — o fluxo vai direto pra tela de autorização, sem precisar de login.
- A API do X requer **créditos** para operações de escrita. Mesmo logado pelo browser, o React do X pode bloquear envios programáticos de post. Após o OAuth, testar com `xurl whoami` (leitura, geralmente gratuita). Postar requer créditos em `developer.x.com → Billing`.

### Solução C (headless) — Google SSO via Camoufox

Quando o email da conta X não tem senha (criada via Google/Apple), o login com email no formulário React redireciona pra cadastro por telefone. A saída é usar o **Google SSO**:

**Por que funciona:** O Camoufox compartilha cookies entre tabs. Quando o Google autentica numa tab popup, a sessão persiste pra todo o navegador — inclusive no iframe do Google embutido na página de login do X e na página de autorização OAuth. A popup não consegue comunicar o token de volta (sem `window.opener`), mas **a sessão Google sobrevive**, então navegar de volta pra URL OAuth já mostra o usuário logado.

**Fluxo completo (testado e funcional):**

```bash
# Fase 1: Capturar URL de autorização OAuth
cat > /tmp/fake-xdg-open << 'EOF'
#!/bin/bash
echo "$@" > /tmp/xurl-oauth-url.txt
exit 0
EOF
chmod +x /tmp/fake-xdg-open
cp /usr/bin/xdg-open /usr/bin/xdg-open.real
cp /tmp/fake-xdg-open /usr/bin/xdg-open

# Iniciar OAuth em background (importante: timeout generoso — 60s+)
xurl auth oauth2 --app my-app &
sleep 6
cat /tmp/xurl-oauth-url.txt  # ← URL capturada

# Restaurar xdg-open
cp /usr/bin/xdg-open.real /usr/bin/xdg-open

# Fase 2: Navegar pra URL OAuth no Camoufox
OAUTH_URL=$(cat /tmp/xurl-oauth-url.txt)
curl -s -X POST http://localhost:9377/tabs \
  -H 'Content-Type: application/json' \
  -d "{\"userId\":\"xurl\",\"sessionKey\":\"oauth\",\"url\":\"$OAUTH_URL\"}"

# A página OAuth mostra "Log in" [e1] e um iframe do Google.
# NÃO clique no iframe — clique no link "Log in" [e1]:
curl -s -X POST http://localhost:9377/tabs/TAB_ID/click \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e1"}'

# Fase 3: Na página de login do X, clicar "Sign in with Google"
# O snapshot mostra: button "Sign in with Google. Opens in new tab" [e3]
curl -s -X POST http://localhost:9377/tabs/TAB_ID/click \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e3"}'

# Isso abre uma nova tab do Google. Pegar o tabId:
curl -s http://localhost:9377/tabs?userId=xurl

# Fase 4: Login no Google (na tab do Google)
# 4a. Digitar email
curl -s -X POST http://localhost:9377/tabs/GOOGLE_TAB_ID/type \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e2","text":"email@example.com"}'

# 4b. Clicar "Next"
curl -s -X POST http://localhost:9377/tabs/GOOGLE_TAB_ID/click \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e6"}'

# 4c. Digitar senha
curl -s -X POST http://localhost:9377/tabs/GOOGLE_TAB_ID/type \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e1","text":"senha"}'

# 4d. Clicar "Next"
curl -s -X POST http://localhost:9377/tabs/GOOGLE_TAB_ID/click \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e5"}'

# 4e. Se 2FA aparecer, selecionar método e pedir código pro usuário
# Opções: SMS [e2], ligação [e3], ou "Try another way" [e4]
curl -s -X POST http://localhost:9377/tabs/GOOGLE_TAB_ID/click \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e2"}'  # SMS

# 4f. Aguardar código, digitar e confirmar
curl -s -X POST http://localhost:9377/tabs/GOOGLE_TAB_ID/type \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e2","text":"CODIGO_6_DIGITOS"}'
curl -s -X POST http://localhost:9377/tabs/GOOGLE_TAB_ID/click \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e4"}'

# Fase 5: Google autenticou. Voltar pra aba principal do X e recarregar
# a URL OAuth. Agora o X reconhece o login do Google e mostra
# a página "Authorize app" diretamente.
curl -s -X POST http://localhost:9377/tabs/TAB_ID/navigate \
  -H 'Content-Type: application/json' \
  -d "{\"userId\":\"xurl\",\"url\":\"$OAUTH_URL\"}"

# Fase 6: Clicar "Authorize app" [e3]
# O X redireciona pra http://localhost:8080/callback?code=...
# O xurl em background recebe e troca o código por tokens.
curl -s -X POST http://localhost:9377/tabs/TAB_ID/click \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e3"}'

# Fase 7: Verificar
xurl auth status
xurl whoami
```

**Pitfalls:**
- A popup do Google abre sem `window.opener`, então o token **não** retorna automaticamente pra página do X. Mas isso não importa — a sessão Google persiste nos cookies do Camoufox, e ao recarregar a URL OAuth o X detecta o login e vai direto pra página de autorização.
- O `xurl auth oauth2` tem timeout padrão (~60s). O fluxo com Google 2FA (SMS/call) pode ultrapassar esse limite, fazendo o callback server morrer antes do código de autorização chegar. **Solução:** reiniciar o xurl (matar o anterior) DEPOIS que o Google já autenticou. A sessão Google persiste, então a NOVA URL OAuth vai direto pra página de autorização sem pedir login de novo. Veja o passo a passo na seção "Timeout Recovery" abaixo.
- A URL OAuth tem um code_challenge diferente a cada execução. A cada `xurl auth oauth2` é gerado um novo par PKCE. Guardar URLs antigas não adianta — sempre usar a URL fresca.
- Após autorizar, o callback redireciona o browser pra `localhost:8080/callback`. Como browser headless não consegue renderizar isso, o xurl server precisa estar vivo pra receber a requisição. Verifique: `curl -s http://localhost:8080/` (deve dar 404 — sinal que o server tá de pé).

### Timeout Recovery (quando o xurl morre durante Google 2FA)

Se o `xurl auth oauth2` timeout durante o 2FA do Google:

```bash
# 1. Matar processo antigo (se ainda estiver rodando)
pkill -f "xurl auth" 2>/dev/null || true

# 2. Re-capturar URL de autorização com fake xdg-open
cat > /tmp/fake-xdg-open << 'EOF'
#!/bin/bash
echo "$@" > /tmp/xurl-oauth-url2.txt
exit 0
EOF
chmod +x /tmp/fake-xdg-open
cp /usr/bin/xdg-open.real /usr/bin/xdg-open 2>/dev/null || true
cp /tmp/fake-xdg-open /usr/bin/xdg-open

# 3. Iniciar NOVO xurl auth (gera novo code_challenge)
xurl auth oauth2 --app my-app &
sleep 6

# 4. Restaurar xdg-open e pegar a nova URL
cp /usr/bin/xdg-open.real /usr/bin/xdg-open
NEW_OAUTH_URL=$(cat /tmp/xurl-oauth-url2.txt)

# 5. Navegar pra nova URL no Camoufox — como Google já tá logado,
#    vai direto pra página "Authorize app" sem pedir login
curl -s -X POST http://localhost:9377/tabs/TAB_ID/navigate \
  -H 'Content-Type: application/json' \
  -d "{\"userId\":\"xurl\",\"url\":\"$NEW_OAUTH_URL\"}"

# 6. Autorizar
curl -s -X POST http://localhost:9377/tabs/TAB_ID/click \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e3"}'

# 7. Verificar
xurl auth status
xurl whoami
```

### Verificação

```bash
xurl auth status
# Deve mostrar: ▸ my-app (oauth2: @seu_usuario)
xurl whoami
# Deve retornar seus dados do perfil
```
