# Free Banner Generation Workflow

Generate e-commerce banners programmatically using free tools — no API keys, no GPU required.

## Tools Used

| Tool | Purpose | Cost | Setup |
|------|---------|------|-------|
| **Pollinations.ai** | AI-generated background/scene | Free, no API key | None — HTTP GET |
| **rembg** (u2net) | Background removal from images | Free, local | `pip install "rembg[cpu]"` |
| **Pillow (PIL)** | Compositing, color grading, logo overlay | Free, built-in | `pip install Pillow` |

## Alternative: HuggingFace SDXL

For higher quality, use HuggingFace's free inference API with SDXL models. Requires a HuggingFace account (free) and API token.

## Workflow

### Step 1: Generate Background
```bash
curl -s "https://image.pollinations.ai/prompt/CITY%20STREET%20SUNSET%20MOTION%20BLUR?width=1600&height=600&nologo=true" -o bg.png
```
- Format: `https://image.pollinations.ai/prompt/{PROMPT}?width={W}&height={H}&nologo=true&seed={SEED}`
- Best results: descriptive prompts in English, specify mood/lighting/style
- Seed parameter ensures reproducibility
- Note: Pollinations may not respect exact dimensions — resize with PIL afterward

### Step 2: Remove Background from Subject
```python
from rembg import remove
from PIL import Image

img = Image.open("subject.jpg").convert("RGBA")
out = remove(img)  # u2net model auto-downloads on first use
out.save("subject_nobg.png")
```
- First run downloads ~176MB model to `~/.u2net/u2net.onnx`
- Works on CPU, 5-15 seconds per image
- Use `alpha_matting=True` for cleaner edges on complex subjects

### Step 3: Composite with PIL
```python
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw

bg = Image.open("bg.png").resize((1600, 600), Image.LANCZOS)
subject = Image.open("subject_nobg.png").convert("RGBA")
logo = Image.open("logo.png").convert("RGBA")

# Resize subject to ~50% of banner width
subject_w = int(1600 * 0.5)
ratio = subject.height / subject.width
subject = subject.resize((subject_w, int(subject_w * ratio)), Image.LANCZOS)

# Create shadow
shadow = Image.new("RGBA", (subject.width + 60, 50), (0,0,0,0))
# ... draw elliptical shadow with GaussianBlur

# Composite
composite = bg.copy()
composite.paste(shadow, (pos_x - 30, road_y), shadow)
composite.paste(subject, (pos_x, pos_y), subject)

# Logo overlay with transparency
# Make white/near-white pixels transparent in logo
for y in range(logo.height):
    for x in range(logo.width):
        r, g, b, a = logo.getpixel((x, y))
        if r > 210 and g > 210 and b > 210:
            logo.putpixel((x, y), (r, g, b, 0))
composite.paste(logo, (35, 25), logo)

composite.save("banner_final.png")
```

### Step 4: Deploy
- Place in project's `public/` folder
- Commit + push (Vercel auto-deploys)
- For CarCrew: register in `banners` table via Prisma or API

## Pitfalls

1. **Pollinations ignores exact dimensions** — always resize with PIL after download
2. **rembg needs ONNX runtime** — install with `pip install "rembg[cpu]"` (not just `rembg`)
3. **System Python may block pip** (PEP 668) — use `python3 -m venv` to isolate
4. **Logo transparency**: JPEG logos have white backgrounds — convert white pixels to alpha channel
5. **Subject positioning**: calculate `pos_y = road_y - subject_height + overlap` so the subject sits ON the road, not floating above it
6. **Shadow realism**: use `ImageFilter.GaussianBlur(radius=3-5)` on shadow layer, darken gradually toward edges
7. **Color grading**: apply `ImageEnhance.Contrast(1.1)` and `ImageEnhance.Color(1.05)` at the end to unify the composite

## Quality Tiers

| Method | Quality | Time | Cost |
|--------|---------|------|------|
| Pollinations + rembg + PIL | Decent (6/10) | ~1 min | Free |
| HuggingFace SDXL | Good (8/10) | ~5 min | Free |
| Ideogram / Midjourney | Excellent (9/10) | ~30 sec | Paid |
| Professional designer | Perfect (10/10) | Days | $$$ |
