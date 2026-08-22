# OpenCode Provider Quirks

Base URL: `https://opencode.ai/zen/go/v1`
(Already includes `/v1` — do NOT append another one.)

## Response Format

OpenCode returns responses in **streaming/delta format** even for non-streaming requests:

```
// Standard OpenAI format (what most code expects):
choices[0].message.content = "..."

// OpenCode format:
choices[0].delta.content = "..."
```

**Fix**: Always read both formats:
```ts
const text = choice?.message?.content || choice?.delta?.content;
```

## Reasoning Model Behavior (deepseek-v4-flash)

The `deepseek-v4-flash` model is a **reasoning model** (R1-style). It returns responses differently:

```json
{
  "choices": [{
    "message": {
      "content": "",                    // ⚠️ EMPTY when max_tokens too low!
      "reasoning_content": "We analyze... finally answer: {\"probability\":65}",
      "role": "assistant"
    }
  }]
}
```

### Critical: max_tokens Sensitivity

The model needs tokens for BOTH reasoning and the final answer:
- **Reasoning**: consumes 300-1500+ tokens
- **Final answer**: needs 100-500+ tokens
- **If max_tokens is 300**: only reasoning fits → `content` returns EMPTY

**Fix in code** (read all three fields):
```ts
const choice = data?.choices?.[0];
let text = choice?.message?.content || choice?.delta?.content || "";

// Fallback: reasoning models put answer in reasoning_content
// when content is empty (max_tokens too low)
if (!text && choice?.message?.reasoning_content) {
  text = choice.message.reasoning_content;
}
```

**Configuration:**
```
AI_API_BASE_URL=https://opencode.ai/zen/go/v1
AI_MODEL=deepseek-v4-flash  # CORRECT — this model exists
```

### Prompt Tuning for Reasoning Models

When the answer needs to be parsed from `reasoning_content`:
- Add to system prompt: "Output the JSON as the LAST thing in your response — after any analysis"
- This way even if parsing from reasoning_content, the JSON is at the end
- The `parseEstimate` regex fallback can find `probability: 65` in the middle if needed

## Model Names

| Name in Hermes/Cursor | Name in OpenCode API |
|---|---|
| `deepseek-v4-flash` | `deepseek-v4-flash` |
| `deepseek-chat` | ❌ **Not supported** — OpenCode doesn't have this model |

Always use `deepseek-v4-flash` as the model name. The default `deepseek-chat` in polyLink's code was wrong for this provider.

### 🔍 Diagnostic: Reasoning Truncated

If the `reasoning_content` text **ends mid-sentence or mid-word** (e.g. `"...and the description d"`), this CONFIRMS that `max_tokens` is too low. The model was writing the final answer but got cut off.

**Fix**: Increase `max_tokens` to at least 2000.

### Debug Protocol for Empty Response

When debugging "Empty response from AI API":

1. Add `detail: JSON.stringify(data).slice(0, 500)` to the error response
2. Redeploy and retrigger the failing call
3. Read the `detail` field — it tells you:
   - Is `reasoning_content` present? → reasoning model, increase `max_tokens`
   - Is `delta.content` present but `message.content` not? → streaming format
   - Is `content` empty but no other field? → actual empty response from provider
   - What model name is actually being used? (check the `model` field)
4. Act on the pattern (see table below)

### Error Patterns

| Error | Meaning | Fix |
|---|---|---|
| `401 - Model X is not supported` | Model name doesn't exist on OpenCode | Use correct model name (deepseek-v4-flash, not deepseek-chat) |
| `Empty response from AI API` | Response format mismatch (delta vs message) | Read both `.message.content` and `.delta.content` |
| `Empty response` + `reasoning_content` has text | max_tokens too low for reasoning model | Increase max_tokens to 2000+ (check if reasoning_content ends mid-sentence) |
| `Empty response` + `reasoning_content` empty + `delta.content` present | OpenCode streaming format | Read `.delta.content` instead of `.message.content` |
| `Empty response` + absolutely nothing in response | Provider returned blank | Check API key validity, model availability, or try different model |

## Timeout

Models like `deepseek-v4-flash` can take 15-30 seconds to respond. Set `AbortSignal.timeout(30000)` minimum.

## Environment Variables for polyLink

```
AI_API_KEY=<same key used in Hermes>
AI_API_BASE_URL=https://opencode.ai/zen/go/v1
AI_MODEL=deepseek-v4-flash
```
