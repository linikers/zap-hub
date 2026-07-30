User: direto pt-BR, admite erro, prático, solução simples, sem over-engineering. Resumo tabular 🔴🟡🟢. Análise arquitetural antes de grandes mudanças. Build local + testar OBRIGATÓRIO antes de push. Branch→PR→aprova→merge.
§
Gosta que eu ofereça treinamento/configuracao completa depois de implementar. Quer entender o estado real do projeto (oq funciona, oq é mock, oq falta). Aprecia resumo tabular com prioridades (🔴🟡🟢).
§
Chat individual por user (userId). ADMIN ve todos historicos, outros veem so os seus.
§
MarketingOS: v1.7.0. Footer sidebar. MANAGER=ADMIN sem usuarios/whatsapp/pricing. CI: lint+type-check+build. Deploy VPS via self-hosted runner. Login admin@marketingos.com/admin123. OpenCode Go provider, deepseek-v4-flash com fallback reasoning_content→content. OPENCODE_API_KEY no systemd.
§
PUSH: lint+type-check+build+test LOCAL antes de push. CI vermelho = falha minha. ML token: MERCADO_LIVRE_REFRESH_TOKEN no systemd, não no ads-credentials.json. carregarConfig() merge JSON + env.
§
Workflow: branch → PR → CI verde → merge. NUNCA push direto pra main. SEMPRE verificar lint + type-check + build + testes ANTES de push. Build force (npm run build nos pacotes modificados) pra garantir sem cache. NUNCA reportar "pronto" com CI vermelho. Lint empty catch: comentario nao resolve no-empty, precisa de eslint-disable-next-line.
§
Taiff Connect: produto catálogo S3/CloudFront (taiff-produtos-midia, digsnzaapp4io.cloudfront.net). Campos: codigo_produto, nome_comercial, uso, status, descricao (products) + tipo_arquivo (imagem/ficha_tecnica/manual/logo/video), nome_arquivo_original (product_images). DevOps EKS. Migration segura: hasColumn() antes de addColumn().
§
Marketing OS landing page: HTML em public/ é servido em /nome.html (com extensão), não /nome. Para URL sem extensão, usar Next.js page em src/pages/nome.tsx. CSS inline >10KB no <style> tag pode quebrar build Vercel — preferir MUI sx props. Deploy hook Vercel pode ficar PENDING sem avançar → deploy manual pelo dashboard resolve.