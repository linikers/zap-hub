#!/usr/bin/env python3
"""Simple QR streaming server - reads latest QR from file, serves HTML that auto-refreshes."""

import http.server
import urllib.parse
import json
import sys
import os

QR_FILE = "/tmp/whatsapp-qr-data.txt"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8898

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="refresh" content="8">
<title>QR WhatsApp NF-e</title>
<style>
body{font-family:sans-serif;background:#0f0f0f;color:#eee;text-align:center;padding:20px;margin:0}
h1{color:#4CAF50;font-size:1.4em}
.phone{color:#888;font-size:1.1em;margin:4px 0 16px}
.qr{background:white;padding:16px;border-radius:16px;display:inline-block;max-width:90vw}
.qr img{width:320px;max-width:100%;height:auto;display:block}
.steps{background:#1a1a1a;padding:14px 20px;border-radius:8px;margin:16px auto;max-width:400px;text-align:left;line-height:2;font-size:0.95em}
.warn{background:#2a1500;border:1px solid #553300;padding:10px 14px;border-radius:8px;margin:12px auto;max-width:400px;color:#fa0;font-size:0.9em}
.ts{color:#666;font-size:0.8em;margin-top:8px}
</style>
</head>
<body>
<h1>📱 Conectar WhatsApp NF-e</h1>
<p class="phone">N\u00famero: <strong>+55 44 991670539</strong></p>
<div class="qr"><img src="https://api.qrserver.com/v1/create-qr-code/?size=340x340&data=QR_DATA_HERE" alt="QR Code"></div>
<div class="steps">
<b>Passo a passo:</b>
<ol>
<li>Abra o <b>WhatsApp</b> no celular</li>
<li><b>Configura\u00e7\u00f5es</b> \u2192 <b>Dispositivos conectados</b></li>
<li>Toque em <b>Conectar um dispositivo</b></li>
<li>Aponte a c\u00e2mera para o QR Code</li>
</ol>
</div>
<div class="warn">\u26a0\ufe0f QR atualizado automaticamente a cada 8s</div>
<p class="ts">\u00daltima atualiza\u00e7\u00e3o: TIMESTAMP</p>
</body>
</html>"""

class QRHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/qr' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            try:
                qr_data = open(QR_FILE).read().strip()
                if not qr_data:
                    html = "<html><body><h1>Aguardando QR Code...</h1><meta http-equiv='refresh' content='5'></body></html>"
                    self.wfile.write(html.encode())
                    return
                encoded = urllib.parse.quote(qr_data, safe='')
                import datetime
                ts = datetime.datetime.now().strftime('%H:%M:%S')
                html = HTML_TEMPLATE.replace('QR_DATA_HERE', encoded).replace('TIMESTAMP', ts)
                self.wfile.write(html.encode())
            except FileNotFoundError:
                html = "<html><body><h1>Aguardando QR Code...</h1><meta http-equiv='refresh' content='5'></body></html>"
                self.wfile.write(html.encode())
        elif self.path == '/raw':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            try:
                qr_data = open(QR_FILE).read().strip()
                self.wfile.write(qr_data.encode())
            except FileNotFoundError:
                self.wfile.write(b'')
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            try:
                qr_data = open(QR_FILE).read().strip()
                status = 'active' if qr_data else 'waiting'
            except:
                status = 'waiting'
            self.wfile.write(json.dumps({'status': status, 'updated_at': str(os.path.getmtime(QR_FILE) if os.path.exists(QR_FILE) else 0)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404')
    def log_message(self, format, *args):
        sys.stderr.write("[QR] %s - %s\n" % (self.client_address[0], format % args))

print(f"[QR] Server starting on port {PORT}")
print(f"[QR] Reading QR from: {QR_FILE}")
if os.path.exists(QR_FILE):
    print(f"[QR] Current QR data: {open(QR_FILE).read().strip()[:50]}...")
http.server.HTTPServer(('', PORT), QRHandler).serve_forever()
