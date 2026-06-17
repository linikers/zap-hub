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
§
User runs VPS Hermes (backend) + Desktop client via remote dashboard gateway. Prefers client-server: engine no VPS, GUI no PC local. Dashboard auth basic, port 9119.
§
Taiff PRs merged/approved: #58 OTA, #59 Add Device, #60 Auth (aprovado apos conserto testes), #61 Swagger docs (aprovado). Rafa-ross contributor no repo taiff-connect-backend. Swagger em /api-docs. Projeto sem .env.example — README desatualizado.