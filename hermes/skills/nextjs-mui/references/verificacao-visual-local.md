# Verificação visual de UI local (antes de pedir aprovação)

O dono não aprova PR de UI sem ver a tela — quer **captura nos dois temas** e leitura crítica. Faça a revisão ANTES de pedir aprovação.

## Por que não usar o browser configurado

O backend de browser em nuvem não alcança `localhost` (endereço privado bloqueado). Para UI local, suba um **chromium headless na própria máquina** e dirija por CDP.

## Receita

```bash
# 1) chromium com porta de debug (headless novo)
chromium --headless=new --remote-debugging-port=9222 --no-sandbox --disable-gpu \
  --hide-scrollbars about:blank >/tmp/chr.log 2>&1 &
sleep 5
curl -s http://127.0.0.1:9222/json/version | head -c 120   # confirma que subiu
```

```js
// 2) cliente CDP — Node 22+ tem WebSocket global, não precisa de playwright/puppeteer
const fs = require('fs');
const tema = process.argv[2] || 'light';
const saida = `/tmp/ui-${tema}.png`;
// token de sessão lido de ARQUIVO (nunca digitar senha em formulário)
const tok = fs.readFileSync('/caminho/para/.tok', 'utf8').trim();

(async () => {
  const lista = await (await fetch('http://127.0.0.1:9222/json/list')).json();
  const aba = lista.find((t) => t.type === 'page');
  const ws = new WebSocket(aba.webSocketDebuggerUrl);
  let seq = 0; const pend = new Map();
  const send = (method, params = {}) => new Promise((res) => {
    const i = ++seq; pend.set(i, res);
    ws.send(JSON.stringify({ id: i, method, params }));
  });
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) { pend.get(m.id)(m.result); pend.delete(m.id); }
  };
  await new Promise((r) => (ws.onopen = r));

  await send('Page.enable');
  await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1300, deviceScaleFactor: 1, mobile: false });

  // precisa estar NA ORIGEM para poder gravar localStorage
  await send('Page.navigate', { url: 'http://localhost:3001/login' });
  await new Promise((r) => setTimeout(r, 3000));
  await send('Runtime.evaluate', {
    expression: `localStorage.setItem('token', ${JSON.stringify(tok)}); localStorage.setItem('tema','${tema}');`,
  });
  await send('Page.navigate', { url: 'http://localhost:3001/dashboard' });
  await new Promise((r) => setTimeout(r, 8000));

  // o texto renderizado volta no stdout — dá pra ler a tela sem abrir imagem
  const t = await send('Runtime.evaluate', { expression: 'document.body.innerText.slice(0,2500)', returnByValue: true });
  console.log(t.result?.value);

  const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  fs.writeFileSync(saida, Buffer.from(shot.data, 'base64'));
  ws.close(); process.exit(0);
})();
```

3) Rode uma vez por tema (`node shot.js light` / `node shot.js dark`) e **olhe as imagens** com `vision_analyze` — pergunte explicitamente por contraste do texto pequeno, divisor, sobreposição/corte e estados vazios. Sem o `vision_analyze` a captura não vale nada.

## Como descobrir as chaves de localStorage do app

Leia o layout/provider: normalmente `token` (auth), o tema (ex.: `tema` = `light`|`dark`) e às vezes o estado do menu. Grepe o `layout.tsx` por `localStorage.getItem` antes de montar o script.

O token: gere por script (assinando com o segredo do serviço via `systemctl show <serviço> -p Environment`) e **escreva num arquivo** que o script lê. Nunca passe senha por formulário nem pela conversa.

## Limpeza

`pkill -f "remote-debugging-port=9222"` e apague o arquivo do token no fim.

## O que a revisão precisa cobrir

- **Os DOIS temas.** Um card legível no claro pode sumir no escuro (ver a regra de contraste em `SKILL.md`).
- **Texto explicativo pequeno** (fórmula, fonte, ressalva): é o primeiro a ficar abaixo de contraste aceitável.
- **Estados que não são o mesmo:** carregando × falha de rede × vazio legítimo. Uma tela que diz "nada aqui" quando a API caiu esconde o problema.
- **Números reais na tela** — se um card mostra zero ou traço, confirme na API se é o valor certo ou ausência de leitura.
- Conteúdo sobreposto, coluna cortada, linha de divisor invisível.
