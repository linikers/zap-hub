---
name: nextjs-ai-routes
description: Build Next.js App Router API routes that proxy to external LLM/AI providers (OpenAI-compatible APIs). Covers provider format differences, timeout tuning, error logging, and response parsing patterns.
category: software-development
tags:
  - nextjs
  - ai
  - api-routes
  - openai-compatible
  - proxy
  - error-handling
---

# Next.js AI API Routes

Patterns for building Next.js App Router API routes that proxy requests to external LLM/AI providers (OpenAI-compatible APIs like OpenCode, DeepSeek, OpenRouter, etc.).

## Core Pattern

```ts
// src/app/api/ai/<endpoint>/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    const apiKey = process.env.AI_API_KEY;
    const baseUrl = (process.env.AI_API_BASE_URL || "https://api.deepseek.com").replace(/\/+$/, "");
    const model = process.env.AI_MODEL || "deepseek-chat";

    if (!apiKey) {
      return NextResponse.json(
        { error: "AI_API_KEY not configured" },
        { status: 500 }
      );
    }

    // Build URL — some providers include /v1 in base_url, others don't
    const url = `${baseUrl}${baseUrl.includes("/v1") ? "" : "/v1"}/chat/completions`;

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model,
        messages: [
          { role: "system", content: "..." },
          { role: "user", content: buildPrompt(body) },
        ],
        temperature: 0.3,
        max_tokens: 300,
      }),
      signal: AbortSignal.timeout(30000), // 30s for slow models
    });

    if (!response.ok) {
      const errBody = await response.text().catch(() => "Unknown error");
      return NextResponse.json(
        { error: `AI API error: ${response.status}`, detail: errBody.slice(0, 500) },
        { status: 502 }
      );
    }

    const data = await response.json();

    // ⚠️ Providers vary in response format:
    //   - Standard OpenAI: choices[0].message.content
    //   - OpenCode / streaming-style: choices[0].delta.content
    //   - Reasoning models (R1-style): choices[0].message.reasoning_content
    //   - Some providers: choices[0].text
    const choice = data?.choices?.[0];
    let text = choice?.message?.content || choice?.delta?.content || choice?.text || "";

    // Reasoning model fallback: content is empty when max_tokens too low
    // The answer is inside reasoning_content instead
    if (!text && choice?.message?.reasoning_content) {
      text = choice.message.reasoning_content;
    }

    if (!text) {
      return NextResponse.json(
        { error: "Empty response from AI API", detail: JSON.stringify(data).slice(0, 500) },
        { status: 502 }
      );
    }

    const result = parseResponse(text);
    return NextResponse.json({ success: true, ...result });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
```

## Provider Response Format Differences

| Format | Path | Providers |
|--------|------|-----------|
| Standard | `choices[0].message.content` | OpenAI, DeepSeek, OpenRouter, most OpenAI-compatible |
| Delta/streaming | `choices[0].delta.content` | OpenCode, some streaming-optimized endpoints |
| **Reasoning (R1-style)** | `choices[0].message.reasoning_content` | deepseek-v4-flash, DeepSeek-R1, Qwen-R1, reasoning models |
| Text | `choices[0].text` | Legacy OpenAI |
| Raw text | `response body itself` | Some minimalist providers |

**Always** read from `message.content || delta.content || text` to be provider-agnostic.

### Reasoning Model Quirk (⚠️ Critical)

Models like `deepseek-v4-flash` and DeepSeek-R1 are **reasoning models**. They return the chain-of-thought in a special field:

```json
{
  "choices": [{
    "message": {
      "content": "",        // ← EMPTY if max_tokens too low!
      "reasoning_content": "We need to analyze... therefore the probability is... {\"probability\": 65, ...}"
    }
  }]
}
```

**The trap**: `content` comes back EMPTY when `max_tokens` is too low — the model spends all available tokens on reasoning and never gets to write the final answer. The actual answer is inside `reasoning_content`.

**🔍 Diagnostic signal**: If `reasoning_content` ends mid-word or mid-sentence (e.g. `"...and the description d"`), it's CONFIRMED that `max_tokens` is too low. The reasoning was cut off before reaching the final answer.

**Debug protocol**: When getting "Empty response", always include the raw API response in the error detail to see what the provider actually returned:
```ts
return NextResponse.json(
  { error: "Empty response from AI API", detail: JSON.stringify(data).slice(0, 500) },
  { status: 502 }
);
```

**Fix** — read ALL three fields and use reasoning_content as fallback:

```ts
const choice = data?.choices?.[0];
let text = choice?.message?.content || choice?.delta?.content || "";

// Fallback: reasoning models put answer in reasoning_content
// when content is empty (max_tokens too low)
if (!text && choice?.message?.reasoning_content) {
  text = choice.message.reasoning_content;
}
```

**max_tokens rules for reasoning models:**
- Set at least **1000+**, ideally **2000+**
- Reasoning consumes 300-1500 tokens before the answer starts
- The system prompt should say: "Output the JSON as the LAST thing in your response — after any analysis"
- This ensures the JSON is at the end of reasoning_content and parseEstimate fallback (regex) can find it

## Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `AI_API_KEY` | Provider API key | `sk-...` |
| `AI_API_BASE_URL` | Provider endpoint | `https://opencode.ai/zen/go/v1` |
| `AI_MODEL` | Model name | `deepseek-v4-flash`, `gpt-4o-mini` |

## Timeout Tuning

- **15s** — OK for fast models (GPT-4o-mini, Claude Haiku)
- **30s** — Recommended for slower models (deepseek-v4-flash, large open models)
- **60s+** — For complex reasoning tasks or rate-limited providers
- Use `AbortSignal.timeout(N)` on the fetch call
- On timeout, the catch block returns a 500 with the timeout message

## Error Handling Checklist

1. **401/403** — Wrong API key or model not in your plan
2. **ModelError** — Model name doesn't exist on this provider
3. **Empty response** — Format mismatch (delta vs message), actual empty response, or reasoning model with insufficient max_tokens
   - **Debug**: Add `detail: JSON.stringify(data).slice(0, 500)` to the error response to see what the provider returned
   - If `reasoning_content` is present but `content` is empty → reasoning model, increase `max_tokens`
   - If `delta.content` is present but `message.content` is not → provider uses streaming format
4. **502 Bad Gateway** — Provider unreachable or returned error
5. **Timeout** — Increase timeout or use faster model
6. **CORS in browser** — This is a server-side route, CORS doesn't apply to server-to-server calls

## Typical Debugging Flow

When an AI API route returns errors, follow this systematic sequence:

1. Check if the API returns HTTP 200 or error status
2. If 200, examine the full JSON response via the `detail` field in the error
3. Check if `message.content` is empty but `reasoning_content` is filled → reasoning model
4. Check if `max_tokens` is insufficient (especially for reasoning models)
5. Check if timeout is too short for the model being used
6. Verify `AI_API_BASE_URL` has the correct `/v1` path
7. Verify `AI_MODEL` name matches what the provider expects

## Model Name Mapping Across Providers

Models have **different names on different providers**. A model available on one provider may have a completely different name on another.

| Logical Model | DeepSeek | OpenCode | OpenAI |
|-------------|----------|----------|--------|
| DeepSeek V3 | `deepseek-chat` | `deepseek-v3` | — |
| DeepSeek R1 | `deepseek-reasoner` | `deepseek-r1` | — |
| DeepSeek V4 Flash | — | `deepseek-v4-flash` | — |
| GPT-4o mini | — | — | `gpt-4o-mini` |

**Always keep the model name in an environment variable** so it can be changed per provider without code changes:
```typescript
const model = process.env.AI_MODEL || "deepseek-chat";
```

When you get **401 "Model not supported"** with a valid API key, it almost always means the model name doesn't exist on that provider. Check the provider's model list.

## Prompt Engineering for Structured Output

When extracting JSON from a reasoning model's output, the prompt structure is critical:

```typescript
const systemPrompt = `You are a prediction market analyst. Estimate the fair probability.

Rules:
1. Return ONLY valid JSON — no markdown, no extra text
2. Format: {"probability": 0-100, "confidence": 0-100}
...
9. Output the JSON as the LAST thing in your response — after any analysis`;
```

**Rule #9 is critical for reasoning models:** it ensures the JSON appears at the end of the `reasoning_content`, where the fallback parser can find it via regex.

## Parsing Structured Output from AI Responses

When the AI response includes extra text around the target JSON (common with reasoning models), use a two-phase parser:

```typescript
export function parseJSONResponse<T>(text: string): T | null {
  // Phase 1: Try direct JSON parse (works when model outputs pure JSON)
  try {
    const cleaned = text
      .replace(/```json\s*/gi, "")
      .replace(/```\s*/g, "")
      .trim();
    return JSON.parse(cleaned);
  } catch {
    // Phase 2: Extract JSON via regex (works when text wraps JSON)
    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      try {
        return JSON.parse(jsonMatch[0]);
      } catch { /* fall through */ }
    }
    // Phase 3: Key-value regex extraction (last resort)
    const probMatch = text.match(/probability[:\\s\"]+(\d+)/i);
    const confMatch = text.match(/confidence[:\\s\"]+(\d+)/i);
    if (probMatch) {
      return {
        probability: clamp(Number(probMatch[1]), 0, 100),
        confidence: clamp(Number(confMatch?.[1] || 0), 0, 100),
      } as T;
    }
    return null;
  }
}
```

This is useful for prediction market estimates, classification, or any structured output task where the AI's reasoning precedes the JSON answer.

## Translation Route Pattern

For AI-powered translation routes, these same patterns apply but with:
- **Lower temperature** (`0.1`) — for consistency across translations
- **Single-turn prompt** — no system prompt with rules, just a direct instruction
- **Output instruction**: "Translate the following text to {lang}. Output ONLY the translation, no explanations"

## Template

A complete, reusable Next.js API route template is available at `templates/nextjs-route.ts`. Copy it and adapt to your use case — it includes all the patterns covered in this skill (URL construction, response format handling, error handling, timeout management).

## Reference Files

| File | Description |
|------|-------------|
| `references/opencode-provider.md` | OpenCode provider-specific notes (API endpoints, model names) |
| `references/polylink-ai-debug-transcript.md` | Real debugging case study: reasoning model returning empty content, model name mismatch, and full fix walkthrough |

## Pitfalls

- **Trailing slash in base_url**: The `baseUrl.replace(/\/+$/, "")` pattern strips trailing slashes before adding `/v1/chat/completions`
- **/v1 already in base_url**: Some providers (OpenCode, OpenRouter) include `/v1` in their base URL; the `baseUrl.includes("/v1")` check prevents double `/v1/v1/`
- **Model name mismatches**: The same provider may use different model names than what you use in Hermes/Cursor — check provider docs
- **Reasoning models need room to think**: deepseek-v4-flash and similar R1-style models consume 300-1500+ tokens just for reasoning before the final answer. `max_tokens: 300` means `content` comes back EMPTY. Set `max_tokens: 2000+` for reasoning models.
- **reasoning_content is NOT the same as content**: Standard code reads `choices[0].message.content`. Reasoning models populate `choices[0].message.reasoning_content` instead. Always check BOTH fields. See "Reasoning Model Quirk" above.
- **Diagnostic: include raw API response in error**: When returning "Empty response" errors, include `detail: JSON.stringify(data).slice(0, 500)` in the response. This single field tells you: (a) if the format is delta vs message, (b) if reasoning_content is populated, (c) if max_tokens needs increasing, (d) the actual model name used. Without it you're debugging blind.
- **Serverless timeouts**: Vercel Hobby plan limits serverless functions to 10s — 30s timeout may trigger Vercel's hard limit. Upgrade to Pro or cache responses
- **Sensitive keys**: AI_API_KEY is server-side only (NEXT_PUBLIC_* would expose it to the client)

## Vercel-Specific Notes

- Set env vars in Vercel Dashboard → Settings → Environment Variables
- After changing env vars, **redeploy** (env changes don't take effect on existing deployments)
- Vercel Hobby: max 10s function execution time → use faster/smaller models
- Vercel Pro: max 60s (sufficient for 30s timeout)
- Use Incremental Static Regeneration or client-side caching to reduce API calls
