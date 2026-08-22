# polyLink AI API Debugging Case Study

## The Symptoms

User's polyLink dashboard had two AI features broken:
1. **AI Estimate** (Edge Score) — `POST /api/ai/estimate` returned 502 "Empty response from AI API"
2. **AI Translate** — `POST /api/ai/translate` returned 502 "Empty response from AI API"

## Initial Error

First attempt returned 401 with:
```json
{
  "type": "error",
  "error": {
    "type": "ModelError",
    "message": "Model deepseek-chat is not supported"
  }
}
```

This came from **OpenCode** provider (`https://opencode.ai/zen/go/v1`), meaning the `AI_API_BASE_URL` was set correctly but `AI_MODEL=deepseek-chat` doesn't exist there.

## After Model Name Fix

After changing `AI_MODEL` to `deepseek-v4-flash`, the error changed to:
```json
{"error": "Empty response from AI API"}
```

## Root Cause

The response from the API was:
```json
{
  "model": "deepseek-v4-flash",
  "choices": [{
    "index": 0,
    "message": {
      "content": "",
      "reasoning_content": "We are asked to estimate the fair probability..."
    }
  }]
}
```

**Two problems:**
1. `deepseek-v4-flash` is a **reasoning model** (R1-style). It puts chain-of-thought in `reasoning_content` and the final answer in `content`. But `content` was empty.
2. `max_tokens: 300` was too low — the model consumed all 300 tokens on reasoning and had none left for the final answer JSON.

## Fix Applied

1. **Fallback to `reasoning_content`** when `content` is empty
2. **Increased `max_tokens`** from 300 → 2000 (enough for reasoning + JSON output)
3. **Increased timeout** from 15s → 30s (reasoning models are slower)
4. **System prompt tweak**: Added "Output the JSON as the LAST thing in your response — after any analysis"
5. **Debug**: Included the full response JSON in error detail for future debugging

## Code Changes

### Route handler (estimate)
```typescript
// Support both standard and streaming format
const choice = data?.choices?.[0];
let text = choice?.message?.content || choice?.delta?.content || "";

// Fallback for reasoning models
if (!text && choice?.message?.reasoning_content) {
  text = choice.message.reasoning_content;
}
```

### Config
```typescript
max_tokens: 2000,  // was 300
signal: AbortSignal.timeout(30000),  // was 15000
```

## Key Lessons

1. **Model naming is provider-specific**: `deepseek-chat` on DeepSeek ≠ `deepseek-v4-flash` on OpenCode
2. **Reasoning models need 2000+ max_tokens**: The reasoning phase consumes hundreds of tokens
3. **Always handle reasoning_content**: Even if the model doesn't advertise as "reasoning", some providers add it
4. **Always log the raw response**: Without the `detail` field, we'd never have seen the `reasoning_content` structure
5. **Prompt structure matters**: Tell reasoning models to put the JSON at the END of the response
