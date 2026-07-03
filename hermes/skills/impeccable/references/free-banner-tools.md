# Free AI Banner Generation Tools

Discovered during Car Crew Garage banner creation session (2026-07-02).
Goal: generate e-commerce banners programmatically without paid APIs.

## tl;dr Ranking

| Tool | API | Key Required | Quality | Model | Best For |
|------|-----|-------------|---------|-------|----------|
| **Leonardo.ai** | Yes | Free account (150 credits/day) | ⭐⭐⭐⭐⭐ | Leonardo Lightning/XL | Professional banners with reference images |
| **Pollinations.ai** | Yes | None | ⭐⭐⭐ | SDXL-based | Quick banners, zero setup |
| **HuggingFace Serverless** | Yes | Free HF token | ⭐⭐⭐⭐ | SDXL, FLUX, SD3 | Highest quality free tier |
| **Ideogram** | Yes | Paid only ($) | ⭐⭐⭐⭐⭐ | Ideogram 4.0 | Best text-in-image, but paid |
| **Ideogram Web** | No (browser) | Google login | ⭐⭐⭐⭐⭐ | Ideogram 4.0 | Manual use, no automation |

## Pollinations.ai — Zero-Setup Banner Generation

**Endpoint:** `GET https://image.pollinations.ai/prompt/{PROMPT}?width=W&height=H&nologo=true`

**Features:**
- No API key, no account, no rate limit (as of 2026-07)
- CURL-friendly — one HTTP call, returns image bytes
- Configurable width/height via query params
- `nologo=true` removes their watermark
- `seed=42` for reproducible results

**Limitations:**
- Dimensions aren't exact — `?width=1600&height=600` might return 1254×470
- Quality is good but not Midjourney/Ideogram level
- No reference image upload (text-to-image only)
- Text rendering in images is hit-or-miss
- No aspect ratio control beyond W×H
- Can be slow under load (30-60s)

**Practical usage pattern:**
```bash
# Generate, then resize via PIL to exact dimensions
curl -s "https://image.pollinations.ai/prompt/CITY%20SUNSET%20BANNER?width=1600&height=600&nologo=true&seed=42" -o bg.jpg
python3 -c "
from PIL import Image
bg = Image.open('bg.jpg').resize((1600, 600), Image.LANCZOS)
bg.save('banner_base.png')
"
```

**Prompt tips for Pollinations:**
- Use URL-encoded prompts with `+` or `%20` for spaces
- Be specific about lighting ("golden hour", "dramatic lighting", "sunset orange")
- Mention "automotive photography" for car-related banners
- Include "banner format" or "wide format" to nudge composition
- "empty left side" to create space for text/logo overlay

## PIL Compositining Pattern

When the AI can't generate the full banner (logo + product + background in one shot),
use a two-step pipeline:

1. **Generate background** with Pollinations/HuggingFace
2. **Overlay logo + text** with Python Pillow

```python
from PIL import Image, ImageEnhance, ImageDraw

BANNER = (1600, 600)

# Load + resize background
bg = Image.open("bg.jpg").convert("RGBA")
bg = bg.resize(BANNER, Image.LANCZOS)

# Load logo, make white background transparent
logo = Image.open("logo.jpg").convert("RGBA")
logo = logo.resize((200, 200), Image.LANCZOS)
pixels = logo.load()
for y in range(logo.height):
    for x in range(logo.width):
        r, g, b, a = pixels[x, y]
        if r > 200 and g > 200 and b > 200:
            pixels[x, y] = (r, g, b, 0)  # white → transparent

# Compose
bg.paste(logo, (40, 30), logo)

# Dark gradient overlay at bottom for CTA readability
overlay = Image.new("RGBA", BANNER, (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)
for y in range(BANNER[1] - 120, BANNER[1]):
    alpha = int(160 * (y - (BANNER[1] - 120)) / 120)
    draw.rectangle([0, y, BANNER[0], y + 1], fill=(0, 0, 0, alpha))
bg = Image.alpha_composite(bg, overlay)

# Enhance contrast + color
bg = ImageEnhance.Contrast(bg.convert("RGB")).enhance(1.1)
bg = ImageEnhance.Color(bg).enhance(1.05)

bg.save("banner_final.png")
```

**Gotchas:**
- `rembg` (AI background removal) may fail to install on some Linux setups due to PEP 668 + system package conflicts. Fall back to manual mask compositing or use online background removers.
- Always resize AFTER generation to exact banner dimensions.
- Pollinations sometimes returns different aspect ratios than requested.

## When NOT to Use Free Tools

If the user needs:
- **Text in the image** (promo titles, prices) → Ideogram web (Google login, free tier)
- **Reference image compositing** (their photo + generated background) → Leonardo.ai free tier
- **Production-grade repeatable banners** → paid API (Ideogram $20/mo or Replicate pay-per-use)
- **Exact brand colors/logo rendering** → manual design (Canva, Figma) or HTML/CSS banner component

## Hugo Confirmed: Ideogram API is Paid

As of 2026-07, Ideogram's API (`POST https://api.ideogram.ai/v1/ideogram-v3/generate`) requires a paid subscription. The free tier (Google login) only works via the web UI at ideogram.ai — no API access. Their pricing page: https://ideogram.ai/api-pricing.
