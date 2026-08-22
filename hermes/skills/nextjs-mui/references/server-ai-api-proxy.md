# Server-Side AI API Proxy (Next.js Route Handler)

## When to Use

Any Next.js app that needs to call LLM APIs (OpenAI, DeepSeek, Claude, OpenRouter, etc.) from the frontend without exposing the API key.

## Architecture

```
Browser                    Next.js API Route (server)     LLM Provider
   │  POST /api/ai/estimate  │                              │
   │ ──────────────────────► │  POST /v1/chat/completions    │
   │                         │ ────────────────────────────► │
   │                         │  { choices: [...] }          │
   │  { estimate }           │ ◄──────────────────────────── │
   │ ◄────────────────────── │                              │
```

## Implementation

### 1. Environment Variables
```bash
AI_API_KEY=sk-your-key
AI_API_BASE_URL=https://api.deepseek.com
AI_MODEL=deepseek-chat
```

### 2. Route Handler Pattern
```ts
// src/app/api/ai/estimate/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const apiKey = process.env.AI_API_KEY;
    if (!apiKey) return NextResponse.json({ error: "Not configured" }, { status: 500 });

    const baseUrl = process.env.AI_API_BASE_URL || "https://api.deepseek.com";
    const model = process.env.AI_MODEL || "deepseek-chat";

    const response = await fetch(`${baseUrl}/v1/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` },
      body: JSON.stringify({
        model,
        messages: [
          { role: "system", content: "Return JSON only." },
          { role: "user", content: JSON.stringify(body) },
        ],
        temperature: 0.3,
        max_tokens: 300,
      }),
      signal: AbortSignal.timeout(15000),
    });

    if (!response.ok) {
      const errText = await response.text().catch(() => "");
      return NextResponse.json({ error: `API ${response.status}`, detail: errText.slice(0, 500) }, { status: 502 });
    }

    const data = await response.json();
    const text = data?.choices?.[0]?.message?.content;
    return NextResponse.json({ success: true, result: text });
  } catch (err) {
    return NextResponse.json({ error: err instanceof Error ? err.message : "Unknown" }, { status: 500 });
  }
}
```

### 3. LLM Response Parsing
```ts
export function parseLLMResponse(text: string) {
  const cleaned = text.replace(/```json\s*/gi, "").replace(/```\s*/g, "").trim();
  try { return JSON.parse(cleaned); } catch {
    const p = text.match(/probability[:\s"]+(\d+)/i);
    const c = text.match(/confidence[:\s"]+(\d+)/i);
    return { probability: Number(p?.[1]) || 50, confidence: Number(c?.[1]) || 0 };
  }
}
```

## Providers
All OpenAI-compatible: DeepSeek, OpenAI, OpenRouter, Qwen. Switch via .env only.

## Key Lessons
- API key lives server-side only, never sent to browser
- Always timeout (AbortSignal.timeout(15s)) for serverless
- Temperature 0.3 for consistent estimates
- Max 300 tokens for JSON responses
- Cache per-market to avoid duplicate calls
