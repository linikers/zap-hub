// Next.js API Route — OpenAI-Compatible Chat Completion
// Copy this template and adapt to your use case.

import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // === 1. Validate input ===
    if (!body.prompt) {
      return NextResponse.json({ error: "Missing prompt" }, { status: 400 });
    }

    // === 2. Read config from env ===
    const apiKey = process.env.AI_API_KEY;
    const baseUrl = (process.env.AI_API_BASE_URL || "https://api.deepseek.com").replace(/\/+$/, "");
    const model = process.env.AI_MODEL || "deepseek-chat";

    if (!apiKey) {
      return NextResponse.json({ error: "AI_API_KEY not configured" }, { status: 500 });
    }

    // === 3. Build request URL (handle /v1 suffix) ===
    const suffix = baseUrl.includes("/v1") ? "" : "/v1";
    const url = `${baseUrl}${suffix}/chat/completions`;

    // === 4. Call the API ===
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model,
        messages: [
          { role: "system", content: body.systemPrompt || "You are a helpful assistant." },
          { role: "user", content: body.prompt },
        ],
        temperature: body.temperature ?? 0.3,
        max_tokens: body.maxTokens ?? 2000, // 2000+ for reasoning models
      }),
      signal: AbortSignal.timeout(body.timeout ?? 30000), // 30s+ for reasoning models
    });

    // === 5. Handle HTTP errors ===
    if (!response.ok) {
      const errBody = await response.text().catch(() => "Unknown error");
      return NextResponse.json(
        { error: `AI API error: ${response.status}`, detail: errBody.slice(0, 500) },
        { status: 502 }
      );
    }

    // === 6. Parse response (handle all formats) ===
    const data = await response.json();
    const choice = data?.choices?.[0];

    // Try message.content, then delta.content (streaming), then reasoning_content (R1-style)
    let text = choice?.message?.content || choice?.delta?.content || "";

    if (!text && choice?.message?.reasoning_content) {
      // Reasoning model (DeepSeek-R1, deepseek-v4-flash, QwQ, etc.)
      text = choice.message.reasoning_content;
    }

    if (!text) {
      return NextResponse.json(
        { error: "Empty response from AI API", detail: JSON.stringify(data).slice(0, 500) },
        { status: 502 }
      );
    }

    // === 7. Return result ===
    return NextResponse.json({ success: true, result: text });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
