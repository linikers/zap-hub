#!/usr/bin/env python3
"""
WhatsApp Cloud API Bridge for Hermes Agent.

Handles webhook verification, message receiving via WhatsApp Cloud API,
and sends responses back through the Meta Graph API.

Usage:
  WHATSAPP_TOKEN=EAA... WHATSAPP_PHONE_NUMBER_ID=123... WHATSAPP_ACCOUNT_ID=456... \\
    python3 whatsapp-cloud-bridge.py

Environment variables:
  WHATSAPP_TOKEN           - Permanent access token from Meta
  WHATSAPP_PHONE_NUMBER_ID - Phone number ID from Meta
  WHATSAPP_ACCOUNT_ID      - WhatsApp Business Account ID (optional, for info)
  WHATSAPP_VERIFY_TOKEN    - Your own verify token for webhook setup (default: hermes_verify_123)
  WHATSAPP_BRIDGE_PORT     - Port to listen on (default: 3001)
  WHATSAPP_API_VERSION     - Graph API version (default: v22.0)
  HERMES_BIN               - Path to hermes binary (default: auto-detect)
"""

import os
import sys
import json
import logging
import asyncio
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

# Try to import aiohttp from Hermes venv first
_HERMES_VENV = Path("/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages")
if _HERMES_VENV.exists():
    sys.path.insert(0, str(_HERMES_VENV))

try:
    from aiohttp import web, ClientSession
except ImportError:
    print("ERROR: aiohttp is required. Install with: pip install aiohttp")
    sys.exit(1)

# ── Config ──────────────────────────────────────────────────────────────
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
WHATSAPP_ACCOUNT_ID = os.environ.get("WHATSAPP_ACCOUNT_ID", "")
WHATSAPP_VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "hermes_verify_123")
WHATSAPP_API_VERSION = os.environ.get("WHATSAPP_API_VERSION", "v22.0")
WHATSAPP_RESTRICTED_MODE = os.environ.get("WHATSAPP_RESTRICTED_MODE", "").lower() in ("1", "true", "yes")
PORT = int(os.environ.get("WHATSAPP_BRIDGE_PORT", "3001"))

# Find hermes binary
_HERMES_BIN = os.environ.get("HERMES_BIN", "")
if not _HERMES_BIN:
    _candidates = [
        "/usr/local/bin/hermes",
        "/usr/bin/hermes",
        str(Path.home() / ".local/bin/hermes"),
    ]
    for c in _candidates:
        if Path(c).exists():
            _HERMES_BIN = c
            break
if not _HERMES_BIN:
    _HERMES_BIN = "hermes"  # fallback to PATH

# ── NFe Assistant ──────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from whatsapp_nfe import (
    detectar_intencao_nfe,
    handle_nfe_message,
    formatar_whatsapp_resposta,
    extrair_info_xml,
    validar_chave_acesso,
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
    force=True,
)
log = logging.getLogger("whatsapp-cloud-bridge")

# Ensure output is unbuffered
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, "reconfigure") else None
sys.stderr.reconfigure(line_buffering=True) if hasattr(sys.stderr, "reconfigure") else None

# ── Graph API ────────────────────────────────────────────────────────────
GRAPH_API_URL = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"

async def send_whatsapp(to: str, text: str) -> bool:
    """Send a text message via WhatsApp Cloud API."""
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        log.error("WHATSAPP_TOKEN or WHATSAPP_PHONE_NUMBER_ID not set")
        return False

    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    }

    try:
        async with ClientSession() as session:
            async with session.post(GRAPH_API_URL, json=payload, headers=headers) as resp:
                body = await resp.text()
                if resp.status == 200:
                    log.info("Message sent to %s (status %d)", to, resp.status)
                    return True
                else:
                    log.error("Failed to send to %s: HTTP %d - %s", to, resp.status, body)
                    # Check for specific sandbox mode error
                    if "131030" in body and "allowed list" in body:
                        log.warning("⚠ NÚMERO EM MODO SANDBOX! Para enviar mensagens:")
                        log.warning("   1. Adicione o número destinatário no Meta Developer Dashboard")
                        log.warning("      (WhatsApp → Configuration → Edit → Recipients)")
                        log.warning("   2. Ou verifique o número e saia do modo sandbox")
                    return False
    except Exception as e:
        log.error("Error sending message to %s: %s", to, e)
        return False


# ── WhatsApp Media Download ────────────────────────────────────────────────
MEDIA_API_URL = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/"

async def download_media(media_id: str) -> Optional[str]:
    """Download a media file (XML, image, etc.) from WhatsApp Cloud API.
    Returns the local file path, or None on failure.
    """
    if not WHATSAPP_TOKEN or not media_id:
        return None

    try:
        # Step 1: Get media URL
        async with ClientSession() as session:
            async with session.get(
                f"{MEDIA_API_URL}{media_id}",
                headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
            ) as resp:
                if resp.status != 200:
                    log.error("Failed to get media URL for %s: %s", media_id, await resp.text())
                    return None
                data = await resp.json()
                media_url = data.get("url", "")
                mime_type = data.get("mime_type", "")

            if not media_url:
                log.error("No media URL for %s", media_id)
                return None

            # Step 2: Download the file
            async with session.get(
                media_url,
                headers={"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
            ) as resp:
                if resp.status != 200:
                    log.error("Failed to download media %s: %s", media_id, await resp.text())
                    return None
                content = await resp.read()

        # Step 3: Save to temp file
        ext = ".xml" if "xml" in mime_type else ".pdf" if "pdf" in mime_type else ".bin"
        suffix = f"_media_{media_id}{ext}"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="/tmp")
        tmp.write(content)
        tmp.close()
        log.info("Downloaded media %s -> %s (%d bytes, %s)", media_id, tmp.name, len(content), mime_type)
        return tmp.name

    except Exception as e:
        log.error("Error downloading media %s: %s", media_id, e)
        return None


async def send_whatsapp_mark_seen(to: str) -> bool:
    """Mark message as read."""
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        return False
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": to,  # takes message_id, not phone number
    }
    try:
        async with ClientSession() as session:
            async with session.post(GRAPH_API_URL, json=payload, headers=headers) as resp:
                return resp.status == 200
    except Exception:
        return False


async def send_typing_indicator(to: str) -> bool:
    """Send typing indicator (not supported in all API versions)."""
    # Business API doesn't have a direct typing endpoint via messages API
    # This is a stub for potential future use
    return True


# ── Hermes Integration ────────────────────────────────────────────────────
async def call_hermes(message: str, from_number: str) -> str:
    """Call Hermes CLI to process a message and return the response."""
    log.info("Calling Hermes for message from %s: %.60s...", from_number, message)

    try:
        proc = await asyncio.create_subprocess_exec(
            _HERMES_BIN, "chat", "-q", message, "--yolo",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
        except asyncio.TimeoutError:
            proc.kill()
            log.warning("Hermes timed out for message from %s", from_number)
            return "⏳ Desculpe, a resposta está demorando mais que o esperado. Tente novamente em instantes."

        response = stdout.decode("utf-8", errors="replace").strip()

        # If hermes produced no output, check stderr
        if not response:
            stderr_text = stderr.decode("utf-8", errors="replace").strip()
            if stderr_text:
                log.warning("Hermes stderr for %s: %.200s", from_number, stderr_text)
            response = "✅ Mensagem recebida e processada!"

        log.info("Hermes responded for %s: %.100s...", from_number, response[:100])
        return response

    except FileNotFoundError:
        log.error("Hermes binary not found at %s", _HERMES_BIN)
        return "❌ Erro: Hermes não encontrado. Contate o administrador."
    except Exception as e:
        log.error("Error calling Hermes for %s: %s", from_number, e)
        return "❌ Erro ao processar mensagem. Tente novamente."


# ── Webhook Handlers ──────────────────────────────────────────────────────
async def handle_get(request: web.Request) -> web.Response:
    """Handle webhook verification (GET) - required by Meta."""
    mode = request.query.get("hub.mode")
    token = request.query.get("hub.verify_token")
    challenge = request.query.get("hub.challenge")

    log.info("Webhook verification request: mode=%s, token=%s", mode, token)

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        log.info("Webhook verified successfully!")
        return web.Response(text=challenge)
    
    log.warning("Webhook verification failed: mode=%s, expected_mode=subscribe, token_match=%s",
                mode, token == WHATSAPP_VERIFY_TOKEN)
    return web.Response(status=403, text="Verification failed")


async def handle_post(request: web.Request) -> web.Response:
    """Handle incoming WhatsApp messages (POST)."""
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.Response(status=400, text="Invalid JSON")

    log.debug("Received webhook payload: %s", json.dumps(data, indent=2)[:500])

    # Process messages in background
    asyncio.create_task(process_incoming(data))

    # Return 200 OK immediately as required by Meta
    return web.json_response({"status": "ok"})


async def handle_health(request: web.Request) -> web.Response:
    """Health check endpoint."""
    return web.json_response({
        "status": "ok",
        "phone_number_id": WHATSAPP_PHONE_NUMBER_ID,
        "has_token": bool(WHATSAPP_TOKEN),
        "has_account_id": bool(WHATSAPP_ACCOUNT_ID),
    })


async def handle_send(request: web.Request) -> web.Response:
    """Manual send endpoint (for testing)."""
    try:
        data = await request.json()
        to = data.get("to", "")
        text = data.get("text", "")
        if not to or not text:
            return web.json_response({"error": "Missing 'to' or 'text'"}, status=400)
        ok = await send_whatsapp(to, text)
        return web.json_response({"sent": ok})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def process_incoming(data: dict):
    """Process incoming WhatsApp webhook data."""
    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                # Check for incoming messages
                for msg in value.get("messages", []):
                    await handle_message(msg, value)

                # Check for message status updates
                for status_update in value.get("statuses", []):
                    status = status_update.get("status", "")
                    msg_id = status_update.get("id", "")
                    if status == "read":
                        log.debug("Message %s read by recipient", msg_id)
                    elif status == "failed":
                        log.warning("Message %s failed: %s", msg_id, status_update)

    except Exception as e:
        log.error("Error processing incoming data: %s", e, exc_info=True)


async def handle_message(msg: dict, value: dict):
    """Handle a single WhatsApp message - routes NFe messages to the NFe assistant."""
    msg_type = msg.get("type", "")
    from_number = msg.get("from", "")
    msg_id = msg.get("id", "")
    metadata = value.get("metadata", {})
    display_phone = metadata.get("display_phone_number", "unknown")

    log.info("Message from %s (type=%s): %.80s", from_number, msg_type, json.dumps(msg)[:100])

    # Extract text based on message type
    text = ""
    attachment_path = None

    if msg_type == "text":
        text = msg.get("text", {}).get("body", "")
    elif msg_type == "interactive":
        # Handle button/list replies
        interactive = msg.get("interactive", {})
        if interactive.get("type") == "button_reply":
            text = interactive.get("button_reply", {}).get("title", "")
        elif interactive.get("type") == "list_reply":
            text = interactive.get("list_reply", {}).get("title", "")
    elif msg_type == "document":
        doc = msg.get("document", {})
        filename = doc.get("filename", "documento")
        mime_type = doc.get("mime_type", "")
        media_id = doc.get("id", "")

        # Se for XML, baixa e processa como nota fiscal
        if "xml" in mime_type.lower() or filename.lower().endswith(".xml"):
            log.info("XML document received from %s: %s", from_number, filename)
            attachment_path = await download_media(media_id)
            if attachment_path:
                text = f"validar xml anexado: {filename}"
            else:
                text = "📄 [Erro ao baixar XML]"
        else:
            text = f"📄 [Documento recebido: {filename}]"
    elif msg_type == "audio":
        text = "🎤 [Mensagem de áudio recebida]"
    elif msg_type == "image":
        text = "🖼️ [Imagem recebida]"
    elif msg_type == "video":
        text = "🎬 [Vídeo recebido]"
    else:
        text = f"[Mensagem tipo '{msg_type}' recebida]"

    if not text.strip():
        log.debug("Empty message from %s, skipping", from_number)
        return

    # ── NFe intent detection ──────────────────────────────────────────
    tem_intencao, acao, params = detectar_intencao_nfe(text)

    if tem_intencao:
        log.info("NFe intent detected from %s: action=%s params=%s",
                 from_number, acao, json.dumps(params, ensure_ascii=False))

        # Send typing indicator
        await send_whatsapp_mark_seen(msg_id)

        await handle_nfe_message(
            texto=text,
            from_number=from_number,
            nome_cliente="",
            send_func=send_whatsapp,
            attachment_path=attachment_path,
        )

        # Clean up temp file
        if attachment_path and os.path.exists(attachment_path):
            try:
                os.unlink(attachment_path)
            except Exception:
                pass

        return

    # ── Non-NFe: restricted mode or normal ────────────────────────────
    if WHATSAPP_RESTRICTED_MODE:
        from whatsapp_nfe import responder_fora_do_escopo
        response = responder_fora_do_escopo()
        log.info("Restricted mode: refusing non-NFe message from %s", from_number)
    else:
        response = await call_hermes(text, from_number)

    # Send response back
    sent = await send_whatsapp(from_number, response)
    if sent:
        log.info("Response sent to %s", from_number)
    else:
        log.error("Failed to send response to %s", from_number)


# ── Main ──────────────────────────────────────────────────────────────────
async def main():
    if not WHATSAPP_TOKEN:
        log.error("WHATSAPP_TOKEN environment variable is required")
        sys.exit(1)
    if not WHATSAPP_PHONE_NUMBER_ID:
        log.error("WHATSAPP_PHONE_NUMBER_ID environment variable is required")
        sys.exit(1)

    app = web.Application()

    # WhatsApp webhook endpoints
    app.router.add_get("/webhook", handle_get)
    app.router.add_post("/webhook", handle_post)

    # Management endpoints
    app.router.add_get("/health", handle_health)
    app.router.add_post("/send", handle_send)

    log.info("─" * 50)
    log.info(" WhatsApp Cloud API Bridge for Hermes")
    log.info("─" * 50)
    log.info(" Phone Number ID: %s", WHATSAPP_PHONE_NUMBER_ID)
    if WHATSAPP_ACCOUNT_ID:
        log.info(" Account ID:      %s", WHATSAPP_ACCOUNT_ID)
    log.info(" Token set:       %s", "✅ YES" if WHATSAPP_TOKEN else "❌ NO")
    log.info(" Listening on:    http://0.0.0.0:%d", PORT)
    log.info(" Webhook URL:     http://<YOUR_PUBLIC_IP>:%d/webhook", PORT)
    log.info(" Verify Token:    %s", WHATSAPP_VERIFY_TOKEN)
    log.info(" Hermes binary:   %s", _HERMES_BIN)
    log.info("─" * 50)
    log.info("")
    log.info(" NGROK (se for teste local):")
    log.info("   ngrok http %d", PORT)
    log.info("")
    log.info(" META CONFIGURAÇÃO:")
    log.info('   Callback URL:  https://SEU_DOMINIO/webhook')
    log.info('   Verify Token:  %s', WHATSAPP_VERIFY_TOKEN)
    log.info("")
    log.info(" Para testar o envio manual:")
    log.info('   curl -X POST http://localhost:%d/send \\', PORT)
    log.info('     -H "Content-Type: application/json" \\')
    log.info('     -d \'{"to":"5511999999999","text":"Ola!"}\'')
    log.info("─" * 50)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    log.info("Bridge started! Waiting for messages...")

    # Keep running
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
