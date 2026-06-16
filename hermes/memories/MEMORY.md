autohedge-bot (linikers/autohedge-bot): CLI pipeline Director→Quant→Risk→Execution. Cron cada 6h desde 12/06. Pendente: configurar key Binance + API Key.
§
zap-hub (linikers): repositorio de conexoes WhatsApp + backup Hermes. NF-e Baileys (55 44 991670539, "Escomar Emissor") usa modo bot (allowed_users=*). QR vivo servido via Node.js (qr-server.js, port 8898) + ngrok tunnel.
§
Nunca fazer force push sem perguntar antes. A branch pode já ter sido mergeada e force push quebra o histórico do merge. Sempre verificar e perguntar antes.
§
CarCrewCommerce (carcrew.com.br) — Next.js + Prisma + PostgreSQL (Vercel). `produtos.json` é fonte de dados mas site/admin lê do banco. Sincronizar: push main → Vercel build roda `prisma generate && npx prisma db seed && next build` com tsx. Cloudinary drvnlgib2/preset carcrew. Google Drive com pastas por produto (fotos + .txt). Fluxo: baixar drive → Cloudinary → update JSON → git push → deploy automático.
§
Skill "pit-investimento" (business/) criada — PIT financeiro padronizado com custos por aluno, projeção 3 anos, valuation. Primeiro uso: gSimulados (10k alunos).
§
Taiff: Twilio SMS ativo (PR#53). Creds em values-production.yaml. Jira MCP via mcp-atlassian (API token) pendente config no config.yaml.
§
OBSIDIAN_VAULT_PATH=/root/hermesCabeca — vault do Obsidian chamado "hermesCabeca" com notas centralizadas de projetos, devops e ideias. Repositório git local.
§
gsimulados (github.com/linikers/gSimulados) — potencial projeto pré-vestibular com personas professores. Possivelmente melhor levar para outro servidor separado. Só PIT financeiro feito via pit-investimento (10k alunos base).
§
Taiff branches ordem: 1º firmware-update-ota, 2º connect-device-flow, 3º auth-registration (alinhar front). Register campos novos (confirmacaoSenha, termosAceitos) opcionais no Yup. Dashboard uso dispositivo ≠ dash admin.
§
NUNCA modificar rotas existentes que o front possa consumir. Preferir rotas NOVAS. Se precisar mudar schema/resposta, tornar campos opcionais (Yup) pra não quebrar front. Sempre analisar impacto antes de implementar.