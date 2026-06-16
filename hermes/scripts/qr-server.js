#!/usr/bin/env node
const http = require('http');
const fs = require('fs');
const path = '/tmp/whatsapp-qr-data.txt';
const port = parseInt(process.argv[2] || '8898');

const html = (qr, enc) => `<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<meta http-equiv="refresh" content="7">
<title>QR NF-e</title>
<style>
body{background:#111;color:#eee;text-align:center;font-family:sans-serif;padding:20px;margin:0}
h2{color:#4CAF50}
img{max-width:90vw;width:320px;background:#fff;padding:10px;border-radius:12px}
.s{text-align:left;max-width:380px;margin:16px auto;line-height:2;background:#1a1a1a;padding:12px 20px;border-radius:8px}
</style>
</head>
<body>
<h2>📱 Conectar WhatsApp NF-e</h2>
<p>+55 44 991670539</p>
<img src="https://api.qrserver.com/v1/create-qr-code/?size=340x340&data=${enc}" alt="QR">
<div class="s"><b>Passos:</b><ol>
<li>WhatsApp > Configurações > Dispositivos conectados
<li>Toque em "Conectar um dispositivo"
<li>Aponte a câmera para o QR
</ol></div>
<p style="color:#fa0">⏳ Auto-refresh a cada 7s</p>
</body>
</html>`;

http.createServer((req, res) => {
  if (req.url === '/raw') {
    res.writeHead(200, {
      'Content-Type': 'text/plain; charset=utf-8',
      'Access-Control-Allow-Origin': '*',
      'Cache-Control': 'no-cache'
    });
    try {
      const data = fs.readFileSync(path, 'utf-8').trim();
      res.end(data);
    } catch { res.end(''); }
  } else if (req.url === '/' || req.url === '/qr') {
    res.writeHead(200, {
      'Content-Type': 'text/html; charset=utf-8',
      'Cache-Control': 'no-cache'
    });
    try {
      const qr = fs.readFileSync(path, 'utf-8').trim();
      if (!qr) { res.end('<meta http-equiv=refresh content=5><h1>Aguardando QR...</h1>'); return; }
      res.end(html(qr, encodeURIComponent(qr)));
    } catch(e) { res.end(`<meta http-equiv=refresh content=5><h1>Erro: ${e.message}</h1>`); }
  } else {
    res.writeHead(404); res.end('404');
  }
}).listen(port, '0.0.0.0', () => console.log(`QR server: http://0.0.0.0:${port}`));
