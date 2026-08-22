---
name: twitter-algorithm-optimizer
description: "Otimiza posts para X/Twitter usando algoritmos reais (Real-graph, SimClusters, TwHIN, Tweepcred). Maximiza alcance e engajamento seguindo as regras do sistema de recomendacao."
version: 1.2.0
author: Hermes Agent
tags: [twitter, x, algoritmo, engajamento, alcance, social-media]
---

# Twitter Algorithm Optimizer

Baseado na analise do codigo aberto do algoritmo do Twitter/X.

## Quando Usar

- Escrever posts para maximizar alcance
- Analisar por que um post nao performou
- Criar threads com alto engajamento
- Estrategia de conteudo para o @hermesBigAgent

## Como Funciona

### 1. Real-graph — Engajamento dos Seguidores
O algoritmo prioriza posts que os proprios seguidores do autor engajam.

**Regras:**
- Se seus seguidores nao engajam, o X nao mostra pra ninguem
- Perguntas diretas geram mais replies que afirmacoes
- Posts que geram replies nas primeiras horas tem prioridade

**Exemplo:**
- ❌ "Compre meu curso de token ERC20"
- ✅ "Passei 3 meses aprendendo Solidity sozinho pra descobrir que 90% do que ensinam e teoria inutil. Montei um curso so com o que realmente funciona. Quer ver o indice? 👇"

### 2. SimClusters — Ressonancia Comunitária
O algoritmo identifica comunidades (dev Web3, crypto BR, Solidity) e prioriza conteudo relevante pra elas.

**Regras:**
- Escolha UM topico claro por post
- Use linguagem da comunidade (jargao, memor interno)
- Consistencia de topico ajuda o algoritmo a te categorizar

### 3. TwHIN — Adequacao Conteudo-Usuario
Mapeia relacoes entre usuarios e topicos.

**Regras:**
- Posts consistentes num nicho fortalecem sua autoridade
- Mudancas bruscas de topico confundem o algoritmo
- Use terminologia especifica do seu dominio

### 4. Tweepcred — Autoridade/Credibilidade
Score de reputacao do usuario.

**Regras:**
- Responda creators de alto credibilidade (absorve autoridade)
- Engajamento consistente > viralizar de vez em quando
- Evite engagement bait (danifica credibilidade a longo prazo)

## Gatilhos de Engajamento

| Sinal | O que gera | Exemplo |
|-------|-----------|---------|
| Like | Insight novo, frase memoravel, validacao de crenca | "Descobri que 90% dos tokens ERC20 usam o mesmo contrato base" |
| Reply | Pergunta direta, debate, opiniao incompleta | "Qual foi seu maior erro aprendendo Solidity?" |
| Retweet | Utilidade, representacao, entretenimento | "Esse tutorial de Solidity me salvou 10h. Segue o fio 🧵" |
| Bookmark | Tutorial, dados uteis, inspiracao | "Os 5 padroes de contrato ERC20 que voce precisa conhecer" |

## Estrutura do Post Ideal

```
1. Hook (primeira linha prende atencao) — "afirmacao ousada" ou "dor compartilhada"
2. Desenvolvimento (2-3 linhas) — experiencia especifica, dados, historia
3. CTA (termina com pergunta) — "Qual a sua experiencia?" ou "Concorda?"
```

## Como Postar (Na Pratica)

### API do X (via xurl) — Requer Creditos
A API do X nao e gratuita para escrita. Cada post custa $0.015 via xurl
(erro `CreditsDepleted` = sem saldo). Para postar pela API:
1. Ir em https://developer.x.com/en/portal/dashboard → Billing
2. Adicionar creditos (min $5 USD)
3. Usar: `xurl post "texto"` ou `xurl post "texto" --media-id ID`

### Zernio (Alternativa a API)
Zernio (https://zernio.com) e uma API unificada para 15+ plataformas.
Cobre X, Instagram, LinkedIn, TikTok etc. Precisa de cartao de credito
para ativar (custa $0.015/post + taxa de plataforma).

### Via Browser (Gratis mas Limitado)
O usuario pode postar manualmente pelo navegador. Automacao via
Camoufox/Playwright e possivel mas o React do X dificulta (nao detecta
texto inserido por JavaScript).

### Recomendacao para @hermesBigAgent
1. Escrever o post seguindo as regras do algoritmo (acima)
2. Postar manualmente pelo navegador (0 tweets → 2 tweets)
3. Quando houver orcamento, configurar xurl + creditos para automatizar

## Referencias

| File | Description |
|------|-------------|
| `references/examples.md` | Exemplos praticos de tweets otimizados com estrutura e gatilhos |

## Tom do Post — Regra Rigorosa 🚨

O **tom** impacta tanto quanto o conteúdo. O usuário **corrigiu explicitamente** tom revoltado/negativo:

> "vc esta muito revoltado, paz no coração kkkk"

**Regra:** posts DEVEM ser **leves, curiosos, construtivos**. NUNCA revoltados, reclamões ou vitimistas.

### ✅ Tom Permitido
- **Curiosidade genuína** — "saiu o Mythos 5 e o bagulho é brabo, cê já testou?"
- **Interesse compartilhado** — "o mais doido é ver o ritmo que as coisas tão evoluindo"
- **Convite ao debate** — pergunta honesta no final, sem tom de desabafo
- **Humor leve** — usar girias, "kkkk", "paz no coração"

### ❌ Tom Proibido
- **Revolta/reclamação** — "odeio que X não funciona", "sofri pra fazer Y"
- **Vitimismo** — "ninguém me ajuda", "tô há dias tentando e nada"
- **Desabafo** — "isso aqui não funciona nunca"

### Teste de 3 segundos
Antes de finalizar, releia: **"Isso soa como reclamação?"** Se sim, reescreva como observação interessante.

### Exemplos de ajuste
| Errado (revoltado) ❌ | Certo (curioso) ✅ |
|---|---|
| "odeio integrar pagamento BR, sofri demais" | "integrar pagamento BR tem seus truques" |
| "Passei 3 dias com PagBank e nada funciona" | "Testei 4 formas de autenticar no PagBank" |
| "APIs BR são terríveis, ngm ajuda" | "Cada gateway BR tem sua personalidade" |

## Anti-Padroes (NAO FAZER)

- Post generico: "Hoje vou falar sobre blockchain" — ninguem liga
- Engagement bait: "RT se concorda" — danifica credibilidade
- Autopromocao pura: "Compre meu curso" — sem valor = sem alcance
- Mudanca de topico brusca: um dia NFT, outro dia politica — confunde o algoritmo
- Tom revoltado/negativo: posts com desabafo, reclamacao ou vitimismo (ver seção "Tom do Post" acima)
