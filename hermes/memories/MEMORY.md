User: direto pt-BR, admite erro, prático, solução simples. Resumo tabular 🔴🟡🟢. Análise arquitetural antes de grandes mudanças. Build+teste local OBRIGATÓRIO antes de push. Branch→PR→aprova→merge. Oferecer treinamento/config completa depois de implementar. Quer estado real do projeto (oq funciona/mock/falta).
§
Chat individual por user (userId). ADMIN ve todos historicos, outros veem so os seus.
§
MarketingOS: CI lint+type-check+build. Deploy VPS self-hosted runner. OpenCode Go, deepseek-v4-flash fallback reasoning_content→content. OPENCODE_API_KEY no systemd. Commerce: usuário SELLER na Shopee (Open Platform Seller, credenciais pendentes); publicar exige confirmação explícita; taxas 14%+6%. Fornecedor SEXSHOP_ATACADAO (ATACADO, CNPJ atacadista) c/ 60 DISCOVERED.
§
Lint empty catch: precisa eslint-disable-next-line. ML: ACCESS_TOKEN no systemd + self-healing 401.
§
Relatorio HBS (deltasge): azkaban manda grupoNotas 'Base Nacional Comum'/'Parte Diversificada' (padrão modelo1Fundamental, NÃO áreas). historicoEscolar.css compartilhado c/ modelo1 → só regras aditivas escopadas #modelo-187-*. Texto vertical: .vertical-text + span (span herda 8pt global). Usuário: análise antes de alterar, mudanças cirúrgicas (só hbs+css), testa em outra máquina.
§
Taiff stick user completo: owner_hash=token assinado (não id); 1º dono register auth gera hash (PR#155); access/revoke/unlink/transfer/lock endpoints prontos. ble_protocol JÁ tem lock 0xA0-0xA5 (não precisa FW). Expiração 24h node-cron.
§
linikers.cloud (com 'ni'). Verificação domínio no _app.tsx; Meta app 1569613858007188 modo DEV bloqueia anúncio.
§
Dogama: ~2.1k prods sem API; coleta via preview (anti-bot); cron 6h (8a42a03559d5); creds config/dogama-credentials.json.
§
CJ Dropshipping: token config/cj-credentials.json; cron 15d (f5996e5eb231). QPS=1.
§
gh CLI: `gh pr edit` (GraphQL) falha se token sem scope read:org (erro 'login field requires read:org'). Usar REST: `gh api -X PATCH repos/O/R/pulls/N -f title=... -f base=...` p/ title/body/base de PR.
§
Taiff admin: elevação p/ ADMIN é SÓ no banco via create-admin.ts (register só cria EXTERNAL). dbPassword RDS prod não versionado (injetado no deploy) → sem ele não crio.