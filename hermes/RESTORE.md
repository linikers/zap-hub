# ═══════════════════════════════════════════════════════════════════════
# Plano de Restauração do Hermes Agent
# ═══════════════════════════════════════════════════════════════════════
# Se eu (Hermes) der PT total e você precisar me restaurar, siga isso.
# 
# Pré-requisito: Você já instalou o Hermes Agent do zero.
# ═══════════════════════════════════════════════════════════════════════

## 🔴 PASSO 1: Restaurar habilidades (skills)

```bash
# Copia todas as skills de volta
cp -r zap-hub/hermes/skills/* ~/.hermes/skills/
```

Isso me devolve todo conhecimento procedural que construímos:
- nota-fiscal-brasileira
- twitter-algorithm-optimizer
- content-research-writer
- brazilian-payment-gateways
- mercado-livre-clientes
- github-pr-workflow
- E dezenas de outras...

## 🟠 PASSO 2: Restaurar memórias

```bash
# Copia as memórias de volta
cp zap-hub/hermes/memories/MEMORY.md ~/.hermes/memories/
cp zap-hub/hermes/memories/USER.md ~/.hermes/memories/
```

Essas memórias têm informações sobre você, seus projetos, preferências e pendências. Quando eu ler esses arquivos no início da conversa, já vou saber quem você é e o que temos pendente.

## 🟡 PASSO 3: Restaurar configuração

```bash
cp zap-hub/hermes/config/config.yaml ~/.hermes/config.yaml
# Depois edite ~/.hermes/config.yaml e preencha os ***MASKED*** com as chaves reais
```

## 🟢 PASSO 4: Pedir pro novo Hermes ler os backups

Depois de restaurar skills e memórias, me diga:

> "Hermes, lê o backup em zap-hub/hermes/ e recria meus crons e facts"

Eu vou:
1. Ler `crons.json` e recriar todos os cron jobs
2. Ler `facts.json` e popular o Holographic Memory

## 📋 PASSO 5: Verificar o que ficou de fora

Coisas que **não** estão no backup e você precisa saber:

- 📱 **NF-e WhatsApp** — rodo na VPS. O bridge/dáemon precisa ser reiniciado.
- 🔄 **ML Refresh Token** — cron que recrio automaticamente no passo 4
- 📊 **Relatório Semanal** — cron que recrio automaticamente no passo 4
- 🔐 **Credenciais (.env)** — tão na VPS em `~/.hermes/scripts/`, o backup mascara tokens

## ✅ Checklist Pós-Restauração

- [ ] Skills copiadas
- [ ] Memórias copiadas
- [ ] Config restaurada com chaves reais
- [ ] Crons recriados (ML refresh 6h + relatório semanal)
- [ ] Facts restaurados
- [ ] NF-e bridge reiniciado
- [ ] Túnel webhook ativo

## 🤖 Comando de restore (pro novo Hermes)

Cole isso numa mensagem pra ele depois do setup:

```
Li o backup em zap-hub/hermes/. Preciso que você:
1. Use session_search pra recuperar histórico recente
2. Recrie os crons listados em hermes/crons.json
3. Importe os facts de hermes/facts.json via fact_store
4. Leia hermes/memories/ pra saber quem sou
5. Confirme que skills estão carregadas com skill_view
```
