#!/usr/bin/env bash
# Bot de Vendas — WhatsApp Cloud API
# Canal de vendas automatizado pelo Hermes Agent (personalidade vendas)
#
# Configuracao:
# 1. Copie .env.example para .env e preencha as credenciais
# 2. ./run.sh start
#
# Variaveis do .env:
#   WHATSAPP_TOKEN=           - Token permanente do Meta
#   WHATSAPP_PHONE_NUMBER_ID= - ID do numero de telefone
#   WHATSAPP_ACCOUNT_ID=      - ID da conta WhatsApp Business
#   WHATSAPP_VERIFY_TOKEN=    - Token de verificacao do webhook
#   WHATSAPP_BRIDGE_PORT=     - Porta (default: 3002)
#
# O Hermes responde com personalidade "vendas" automaticamente.
