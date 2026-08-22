# Headless OAuth Setup — xurl sem Browser

Quando o servidor não tem display (Linux headless, SSH, Docker), o xurl
não consegue abrir navegador para o fluxo OAuth 2.0. Este guia cobre
as alternativas testadas.

## Opção 1: Fake xdg-open + Camoufox (mais simples)

### 1. Fingir xdg-open para capturar URL

```bash
# Backup do real (se existir)
cp /usr/bin/xdg-open /usr/bin/xdg-open.real

# Criar fake que salva a URL em vez de abrir navegador
cat > /usr/bin/xdg-open << 'EOF'
#!/bin/bash
echo "$@" > /tmp/oauth_url.txt
exit 0
EOF
chmod +x /usr/bin/xdg-open
```

### 2. Iniciar OAuth

```bash
xurl auth oauth2 --app APP_NAME USERNAME &
sleep 5
cat /tmp/oauth_url.txt
```

### 3. Navegar URL no Camoufox

Com o Camoufox rodando (porta 9377):

```bash
# Criar tab com URL de autorizacao
OAUTH_URL=$(cat /tmp/oauth_url.txt)
curl -s -X POST http://localhost:9377/tabs \
  -H 'Content-Type: application/json' \
  -d "{\"userId\":\"xurl\",\"sessionKey\":\"oauth\",\"url\":\"$OAUTH_URL\"}"
```

### 4. Login via Google (se for o caso)

Se a conta X foi criada com Google:

```bash
# Pegar snapshot para ver elementos
curl -s "http://localhost:9377/tabs/TAB_ID/snapshot?userId=xurl"

# Clicar "Continue as NOME" no iframe do Google
# (ref varia, pegar do snapshot)
curl -s -X POST "http://localhost:9377/tabs/TAB_ID/click" \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e4"}'
```

### 5. Autorizar App

Depois de logado, a pagina de autorizacao aparece sozinha.
Clicar "Authorize app":

```bash
curl -s -X POST "http://localhost:9377/tabs/TAB_ID/click" \
  -H 'Content-Type: application/json' \
  -d '{"userId":"xurl","ref":"e3"}'
```

O X redireciona para `localhost:8080/callback` e o xurl completo
captura o código automaticamente.

### 6. Verificar

```bash
xurl auth status  # Deve mostrar oauth2: USERNAME
xurl whoami
```

## Opção 2: Desktop + Copiar ~/.xurl (mais robusta)

Se Camoufox nao funcionar (formulario React do X nao responde):

1. Fazer OAuth em uma maquina com browser (desktop/notebook)
2. Copiar o arquivo `~/.xurl` para o servidor

```bash
# No desktop (após xurl auth oauth2 com sucesso)
scp ~/.xurl servidor:~/.xurl
```

No servidor, o xurl ja reconhece as credenciais copiadas.

## Opção 3: Bearer Token (leitura apenas)

Para endpoints de leitura (sem postar), usar Bearer Token:

```bash
xurl auth apps add app-name --bearer-token SEU_BEARER_TOKEN
xurl auth default app-name
xurl whoami  # funciona para leitura
```

Nao funciona para postar — exige OAuth 2.0 com refresh token.

## Pitfalls

- **QR/URL expira rapido**: ~60 segundos. Se demorar pra navegar no Camoufox,
  o xurl regenera uma nova URL e o processo precisa ser reiniciado.
- **Camoufox sem sessao**: Se o browser desconectar, a sessao Google se perde.
  Tem que fazer login novamente.
- **device_removed (codigo 401)**: O WhatsApp/Baileys rejeita a conexao.
  Limpar sessao e tentar de novo.
- **xurl timeout**: Se o callback demorar mais que ~60 segundos, o xurl
  fecha o servidor. Reiniciar o `xurl auth oauth2` com URL fresca.
