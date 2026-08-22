# OpenCode Go API — DeepSeek via OpenAI-Compatible Endpoint

## Endpoint

```
Base URL: https://opencode.ai/zen/go/v1
API Key:  OPENCODE_GO_API_KEY (sk-... format, store in .env)
```

Or use `OPENCODE_API_KEY` as the env var name — the autohedge-bot project uses this. Either works.

## Supported Models

| Model | Notes |
|-------|-------|
| `deepseek-v4-flash` | Default, fast reasoning model. Tested and working. |
| `deepseek-chat` | ❌ **Not supported.** Returns `ModelError: Model deepseek-chat is not supported`. |

Only `deepseek-v4-flash` confirmed working as of June 2026. The model name may differ from what the provider's documentation lists — test with a minimal chat completion before wiring into any pipeline.

## Key Differences vs Standard OpenAI

### 1. Reasoning model — no `temperature` parameter

DeepSeek V4 Flash is a reasoning model. Remove `temperature` from `chat.completions.create()` — passing it causes no errors (it's silently ignored) but the model ignores it. Omitting it makes the intent clear.

```python
# ❌ Don't bother — reasoning models don't use temperature
resp = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[...],
    temperature=0.3,
)

# ✅ Clean call
resp = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[...],
)
```

### 2. `reasoning_tokens` consume from `max_tokens`

The model spends a significant portion of the token budget on internal reasoning before producing visible output. A `max_tokens=20` call with a simple prompt like "hello" may return an empty string because all 20 tokens were consumed by reasoning. Symptoms:

```
finish_reason: length   # hit token limit mid-reasoning
content: ''             # no visible output
usage.reasoning_tokens: 20  # all tokens went to reasoning
```

Set `max_tokens` generously (8000+) when the model needs to both reason and produce output. For a 4-step agent pipeline (Director → Quant → Risk → Execution), each step produces 1500-5000 chars of output.

### 3. The `reasoning_content` field

The response message includes `reasoning_content` alongside `content`. This field holds the model's chain-of-thought. It's not present on standard OpenAI responses — code that accesses `resp.choices[0].message.content` works normally; the reasoning is an additional field, not a replacement.

```python
resp = client.chat.completions.create(model="deepseek-v4-flash", messages=[...])
msg = resp.choices[0].message
print(msg.content)           # visible output (may be '' if tokens exhausted)
print(msg.reasoning_content) # chain-of-thought (if available)
```

## Python Client Setup

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://opencode.ai/zen/go/v1",
    api_key=os.getenv("OPENCODE_API_KEY"),
)

resp = client.chat.completions.create(
    model="deepseek-v4-flash",
    messages=[{"role": "user", "content": "Analyze the crypto market..."}],
    max_tokens=8000,
)
```

## .env

```
OPENCODE_API_KEY=sk-...
AUTOHEDGE_MODEL=deepseek-v4-flash
```

The `AUTOHEDGE_MODEL` env var is specific to the autohedge-bot project. For general use, pass the model name directly to the API call.

## Authentication Errors

401 with `ModelError: Model X is not supported` usually means the model name is wrong, not that the API key is invalid. Try `deepseek-v4-flash` — it's the only model confirmed working on this endpoint.
