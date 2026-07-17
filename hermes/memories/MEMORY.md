OBSIDIAN_VAULT_PATH=/root/hermesCabeca — vault do Obsidian chamado "hermesCabeca" com notas centralizadas de projetos, devops e ideias. Repositório git local.
§
WhatsApp: bridge 3000 (5544991528386, Baileys self-chat) agora responde NF-e automaticamente p/ qq chamador. Bridge 3003 (554491277833) = Escomar NF-e conectado. send-validated.py p/ envio. Routing: /root/whatsapp-routing.json (desatualizado). NUNCA cross-bridge.
§
User prefere que eu pergunte e ele define ('me pergunte que eu defino') em vez de eu assumir ou implementar do meu jeito. Perguntar primeiro, implementar depois.
§
Provedor LLM: OpenCode Go (opencode.ai/zen/go/v1). Prefere pt-BR direto, resultado concreto, testa imediatamente. Exige análise antes de mudanças grandes.
§
User exige análise arquitetural (Prompt 0) antes de implementar mudanças grandes — revisar SOLID, escalabilidade, duplicações, dependências circulares e aguardar aprovação. Relatórios estruturados obrigatórios. Não tolera retrabalho. Tech debt deve ser documentado como GitHub Issues para rastreamento.
§
Gosta que eu ofereça treinamento/configuracao completa depois de implementar. Quer entender o estado real do projeto (oq funciona, oq é mock, oq falta). Aprecia resumo tabular com prioridades (🔴🟡🟢).
§
Marketing OS: monorepo Turbo+Next+Prisma+PG. API 3002, Dash 3001, Nginx 80. Branches syncadas via fast-forward. DB: postgres docker (marketing_dev). Token ML seller 50816240 renovado via refresh_token (cron 5h, scripts/refresh-ml-token.py). Fluxos ML: direto (consultar) e agente IA (agent/analisar). Dash UI: auto-refresh com toggle (desligado padrão) + btn manual. Prompts criados: marketplace.md, analytics.md, lead.md, channel.md, optimizer.md.
§
Marketing OS — pacote @marketing-os/ads criado com Google Ads + Meta Ads mock clients, AdsService, tipos compartilhados, dashboard com gráficos Recharts (gasto, receita, ROAS, CTR, CPC, impressões, cliques). Schema Prisma adicionado: AdConta, AdCampanha, AdMetrica, AdCriativo. Google Ads Specialist + Meta Ads Specialist criados com prompts google-ads.md e meta-ads.md. Rota API /api/ads. Dashboard em /ads no Next.js.