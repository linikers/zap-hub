#!/usr/bin/env python3
"""
WhatsApp NF-e Daemon — bridge entre o Baileys bridge e o whatsapp_nfe.py.

Funciona com uma instância separada do bridge.js (porta 3003, modo bot).
Polla /messages e processa via modulo NF-e (modo restrito + horario).
"""

import os
import sys
import json
import time
import logging
import urllib.request
import urllib.error

# Config
BRIDGE_URL = os.environ.get("NFE_BRIDGE_URL", "http://localhost:3003")
POLL_INTERVAL = int(os.environ.get("NFE_POLL_INTERVAL", "2"))
BUSINESS_HOUR_START = int(os.environ.get("NFE_BUSINESS_HOUR_START", "8"))
BUSINESS_HOUR_END = int(os.environ.get("NFE_BUSINESS_HOUR_END", "18"))
BUSINESS_DAYS_STR = os.environ.get("NFE_BUSINESS_DAYS", "1,2,3,4,5")
BUSINESS_TZ = os.environ.get("NFE_BUSINESS_TZ", "America/Sao_Paulo")

LOG_FILE = os.environ.get("NFE_LOG_FILE", os.path.join(os.path.dirname(__file__), "whatsapp-nfe-daemon.log"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
log = logging.getLogger("nfe-daemon")

# Import modulo NF-e
sys.path.insert(0, os.path.dirname(__file__))
from whatsapp_nfe import (
    detectar_intencao_nfe,
    handle_nfe_message,
    responder_fora_do_escopo,
    responder_fora_do_horario,
    dentro_do_horario,
)


def dentro_do_horario_wrapper() -> bool:
    """Wrapper pra funcao do modulo."""
    return dentro_do_horario()


async def send_whatsapp(to: str, text: str) -> bool:
    """Envia mensagem via bridge."""
    payload = json.dumps({"chatId": to, "message": text}).encode("utf-8")
    req = urllib.request.Request(
        f"{BRIDGE_URL}/send",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        result = json.loads(resp.read().decode("utf-8"))
        if result.get("success"):
            return True
        log.error("Falha ao enviar: %s", result)
        return False
    except Exception as e:
        log.error("Erro ao enviar mensagem: %s", e)
        return False


def poll_messages():
    """Polla /messages da bridge."""
    try:
        req = urllib.request.Request(f"{BRIDGE_URL}/messages?timeout=20")
        resp = urllib.request.urlopen(req, timeout=30)
        data = json.loads(resp.read().decode("utf-8"))
        return data if isinstance(data, list) else []
    except urllib.error.HTTPError as e:
        if e.code == 504:
            return []  # timeout, sem mensagens
        log.error("HTTP error: %s", e)
        return []
    except Exception as e:
        log.error("Erro ao pollar mensagens: %s", e)
        return []


def process_message(msg: dict):
    """Processa uma mensagem recebida."""
    chat_id = msg.get("chatId", "")
    text = msg.get("text", "").strip()
    msg_id = msg.get("id", "")
    from_me = msg.get("fromMe", False)

    if not text or from_me:
        return

    log.info("Mensagem de %s: %.80s", chat_id, text)

    # Verifica horario
    if not dentro_do_horario_wrapper():
        log.info("Fora do horario, respondendo offline para %s", chat_id)
        resposta = responder_fora_do_horario()
        send_whatsapp(chat_id, resposta)
        return

    # Detecta se e NF-e
    tem_intencao, acao, params = detectar_intencao_nfe(text)

    if not tem_intencao:
        # Modo restrito: recusa
        resposta = responder_fora_do_escopo()
        send_whatsapp(chat_id, resposta)
        return

    # Processa via handle_nfe_message
    log.info("Intencao NFe detectada: %s", acao)

    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(
            handle_nfe_message(
                texto=text,
                from_number=chat_id,
                nome_cliente="",
                send_func=send_whatsapp,
                restricted_mode=True,
            )
        )
    finally:
        loop.close()


def main():
    log.info("=" * 50)
    log.info("NF-e Daemon iniciado")
    log.info("Bridge: %s", BRIDGE_URL)
    log.info("Horario: %02dh-%02dh, Dias: %s", BUSINESS_HOUR_START, BUSINESS_HOUR_END, BUSINESS_DAYS_STR)
    log.info("=" * 50)

    while True:
        try:
            messages = poll_messages()
            for msg in messages:
                try:
                    process_message(msg)
                except Exception as e:
                    log.error("Erro processando mensagem: %s", e)
                    import traceback
                    log.error(traceback.format_exc())
        except KeyboardInterrupt:
            log.info("Encerrando...")
            break
        except Exception as e:
            log.error("Erro no loop principal: %s", e)
            time.sleep(5)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
