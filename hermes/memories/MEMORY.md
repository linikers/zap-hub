User: direto pt-BR, admite erro, prático, solução simples. Resumo tabular 🔴🟡🟢. Análise arquitetural antes de grandes mudanças. Build+teste local OBRIGATÓRIO antes de push. Branch→PR→aprova→merge. Oferecer treinamento/config completa depois de implementar. Quer estado real do projeto (oq funciona/mock/falta).
§
Chat individual por user (userId). ADMIN ve todos historicos, outros veem so os seus.
§
MarketingOS: CI lint+type-check+build. Deploy VPS self-hosted runner. OpenCode Go, deepseek-v4-flash fallback reasoning_content→content. OPENCODE_API_KEY no systemd. Commerce: usuário SELLER na Shopee (app Open Platform Seller criado, credenciais pendentes); publicar exige confirmação explícita.
§
Lint empty catch: precisa eslint-disable-next-line. ML: ACCESS_TOKEN no systemd + self-healing 401.
§
MarketingOS Ads: Meta v21 OUTCOME_* + is_adset_budget_sharing_enabled=false; insights [] ok. Google API=v21; dev token TESTE. 413: nginx 10m + express 15mb. Places: tela /places, API key por user (tabela PlacesConfig), leads sem site = quente.
§
Relatorio HBS (deltasge): azkaban manda grupoNotas 'Base Nacional Comum'/'Parte Diversificada' (padrão modelo1Fundamental, NÃO áreas). historicoEscolar.css compartilhado c/ modelo1 → só regras aditivas escopadas #modelo-187-*. Texto vertical: .vertical-text + span (span herda 8pt global). Usuário: análise antes de alterar, mudanças cirúrgicas (só hbs+css), testa em outra máquina.
§
Foto: api.taiff-connect.com.br/uploads/... Sticky MERGED (S3, BLE 0xa2-0xba). Backend não fala BLE.
§
linikers.cloud (com 'ni', NÃO linkers). Verificação domínio (Google/FB) no _app.tsx (não _document.jsx). Meta app 1569613858007188 modo DEV bloqueia anúncio (1885183).
§
Dogama: ~2.100 produtos, SEM API/CSV. Coleta assistida via preview Hermes (usuário logado); automático bloqueado (anti-bot). 50 importados; cron 6h (8a42a03559d5); credenciais config/dogama-credentials.json.
§
CJ Dropshipping (2026-08): token em config/cj-credentials.json (fora do git); cron renova 15d (f5996e5eb231). API: getAccessToken(apiKey)/refresh/getCategory/product/list?productName=KW; QPS=1, USD. ML /products/{id}/items=dict.results.