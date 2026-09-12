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
Taiff stick user: owner_hash=token assinado (não id); 1º dono register auth gera hash; access/revoke/unlink/transfer/lock prontos. ble lock 0xA0-0xA5 já existe. Expiração 24h node-cron.
§
linikers.cloud (com 'ni'). Verificação domínio no _app.tsx; Meta app 1569613858007188 modo DEV bloqueia anúncio.
§
Dogama: ~2.1k prods sem API; coleta via preview (anti-bot); cron 6h (8a42a03559d5); creds config/dogama-credentials.json.
§
CJ Dropshipping: token config/cj-credentials.json; cron 15d (f5996e5eb231). QPS=1.
§
gh CLI: `gh pr edit` (GraphQL) falha sem scope read:org → editar via REST `gh api -X PATCH repos/O/R/pulls/N -f title=...`.
§
Taiff admin: elevação p/ ADMIN é SÓ no banco via create-admin.ts (register só cria EXTERNAL). dbPassword RDS prod não versionado (injetado no deploy) → sem ele não crio.
§
Taiff: hair_type/tipoFio (liso/ondulado/crespo) + device_events.temperatura_c; PG local p/ validar migration: taiff-pg-tmp:5434.