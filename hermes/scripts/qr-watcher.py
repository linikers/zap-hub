#!/usr/bin/env python3
"""Watch QR data file and regenerate PNG every time it changes"""
import sys, time, os, hashlib

sys.path.insert(0, "/usr/local/lib/hermes-agent/venv/lib/python3.11/site-packages")
import qrcode

QR_DATA_FILE = "/tmp/whatsapp-qr-data.txt"
QR_IMAGE_FILE = "/root/.hermes/scripts/whatsapp-qr.png"
last_hash = ""

print("[qr-watcher] Monitoring QR data file...")

while True:
    try:
        if os.path.exists(QR_DATA_FILE):
            data = open(QR_DATA_FILE).read().strip()
            current_hash = hashlib.md5(data.encode()).hexdigest()
            
            if current_hash != last_hash:
                qr = qrcode.QRCode(box_size=10, border=4)
                qr.add_data(data)
                img = qr.make_image(fill_color='black', back_color='white')
                img.save(QR_IMAGE_FILE)
                last_hash = current_hash
                print(f"[qr-watcher] QR updated! ({len(data)} chars)")
                
                # Also update HTML
                import base64
                img_data = open(QR_IMAGE_FILE, "rb").read()
                b64 = base64.b64encode(img_data).decode()
                html = f'''<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>WhatsApp QR - Hermes</title>
<style>
body{{background:#111;color:#fff;font-family:sans-serif;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;margin:0;padding:20px;text-align:center}}
img{{max-width:350px;border-radius:12px;box-shadow:0 0 40px rgba(0,150,255,0.3)}}
.steps{{background:#1a1a2e;padding:20px;border-radius:12px;max-width:400px;text-align:left;margin:20px auto;color:#ccc}}
.steps li{{margin:10px 0}}
h1{{color:#4ade80}}
</style></head>
<body>
<h1>📱 Hermes WhatsApp</h1>
<p>Escaneie o QR Code com seu WhatsApp</p>
<img src="data:image/png;base64,{b64}" alt="QR Code">
<div class="steps">
<strong>Passos:</strong>
<ol>
<li>Abra o WhatsApp no celular</li>
<li>Vá em <strong>Configurações → Dispositivos Conectados</strong></li>
<li>Toque em <strong>Conectar um Dispositivo</strong></li>
<li>Aponte a câmera para o QR Code acima</li>
</ol>
</div>
<p>⚠ Abra esta página no CELULAR para escanear</p>
<p style="color:#4ade80">✅ QR Code atualizado em tempo real!</p>
</body></html>'''
                open("/root/.hermes/scripts/qr-scan.html", "w").write(html)
                print("[qr-watcher] HTML page updated!")
                
    except Exception as e:
        print(f"[qr-watcher] Error: {e}")
    
    time.sleep(2)
