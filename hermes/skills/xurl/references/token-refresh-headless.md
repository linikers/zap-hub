# Renovar token OAuth2 expirado sem browser (refresh_token grant)

Quando `~/.xurl` tem um `refresh_token` mas o `access_token` expirou (`expiration_time` no passado), dá pra renovar por curl — sem abrir browser, sem rodar `xurl auth oauth2`. Verificado funcionando (HTTP 200, novos tokens com todos os scopes).

```bash
CID=$(python3 -c "import yaml;d=yaml.safe_load(open('/root/.xurl'));print(d['apps']['APP']['client_id'])")
SEC=$(python3 -c "import yaml;d=yaml.safe_load(open('/root/.xurl'));print(d['apps']['APP']['client_secret'])")
RT=$(python3 -c "import yaml;d=yaml.safe_load(open('/root/.xurl'));print(d['apps']['APP']['oauth2_tokens']['USER']['oauth2']['refresh_token'])")

curl -s -X POST https://api.x.com/2/oauth2/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -u "$CID:$SEC" \
  -d "grant_type=refresh_token" -d "refresh_token=$RT"
```

Confidential clients (Web app, automated app or bot) exigem basic auth `client_id:client_secret`. Depois, gravar o novo par em `~/.xurl` no mesmo caminho (`apps.<app>.oauth2_tokens.<user>.oauth2`) com `type: oauth2` e `expiration_time = now + expires_in` (normalmente 7200s). Sempre fazer backup do arquivo antes (`cp ~/.xurl ~/.xurl.bak.$(date +%s)`).

Observações:
- O `refresh_token` novo também vem no response — gravar ele, o antigo pode ser invalidado.
- Renovar o token NÃO resolve saldo: leituras de tweets seguem retornando `402 credits depleted` (`/2/users/me` continua funcionando). Para postar/ler com a conta nesse estado, usar o browser logado.
- A flag global é `--app NAME` (não `-A`).
