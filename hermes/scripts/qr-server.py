#!/usr/bin/env python3
"""Super simple QR server - serves latest QR from file."""
import http.server, urllib.parse, sys

QR_FILE = "/tmp/whatsapp-qr-data.txt"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8898

class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/raw":
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            try:
                self.wfile.write(open(QR_FILE, "rb").read().strip())
            except:
                self.wfile.write(b"")
        elif self.path in ("/", "/qr"):
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            try:
                qr = open(QR_FILE).read().strip()
                if not qr:
                    self.wfile.write(b"<meta http-equiv=refresh content=5><h1>Aguardando QR...</h1>")
                    return
                enc = urllib.parse.quote(qr, safe="")
                html = '<!DOCTYPE html><html lang=pt-BR><head><meta charset=UTF-8><meta name=viewport content="width=device-width,initial-scale=1.0"><meta http-equiv=refresh content=7><title>QR NF-e</title><style>body{background:#111;color:#eee;text-align:center;font-family:sans-serif;padding:20px}img{max-width:90vw;width:320px;background:#fff;padding:10px;border-radius:12px}.s{text-align:left;max-width:380px;margin:16px auto;line-height:2;background:#1a1a1a;padding:12px 20px;border-radius:8px}</style></head><body><h2>\U0001f4f1 Conectar WhatsApp NF-e</h2><p>+55 44 991670539</p><img src="https://api.qrserver.com/v1/create-qr-code/?size=340x340&data=' + enc + '" alt=QR><div class=s><b>Passos:</b><ol><li>WhatsApp > Configurações > Dispositivos conectados<li>Toque em "Conectar um dispositivo"<li>Aponte a câmera para o QR</ol></div><p style=color:#fa0>\u23f3 Auto-refresh a cada 7s</p></body></html>'
                self.wfile.write(html.encode("utf-8"))
            except Exception as e:
                self.wfile.write(("<meta http-equiv=refresh content=5><h1>Erro: " + str(e) + "</h1>").encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404")
    def log_message(self, *a): pass

http.server.HTTPServer(("", PORT), H).serve_forever()
