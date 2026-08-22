# Cloudinary Image Integration

## Setup

1. Create free account at cloudinary.com
2. Note your **Cloud Name** from the dashboard
3. Create an **Unsigned Upload Preset**: Settings → Upload → Upload Presets → Add preset → Mode: Unsigned
4. Set env var: `NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME=your_cloud_name`

## Widget Script

Add to `src/app/layout.tsx` body:
```tsx
<script src="https://upload-widget.cloudinary.com/global/all.js" async />
```

## Upload Component

```tsx
// src/components/CloudinaryUpload.tsx
export default function CloudinaryUpload({ onUpload, label = "Upload" }) {
  const widgetRef = useRef(null);

  const openWidget = () => {
    if (widgetRef.current) { widgetRef.current.open(); return; }
    widgetRef.current = window.cloudinary?.createUploadWidget(
      {
        cloudName: process.env.NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME || "your_cloud",
        uploadPreset: "your_preset",
        sources: ["local", "camera", "url"],
        multiple: false,
        maxFileSize: 5_000_000,
        styles: {
          palette: {
            window: "#ffffff",
            windowBorder: "#E65100",
            tabIcon: "#E65100",
            action: "#E65100",
            error: "#d32f2f",
            inProgress: "#E65100",
            complete: "#2e7d32",
          },
        },
      },
      (error, result) => {
        if (!error && result?.event === "success") {
          onUpload(result.info.secure_url, result.info.public_id);
        }
      }
    );
    widgetRef.current?.open();
  };

  return <Button onClick={openWidget}>{label}</Button>;
}
```

## URL Transformations

```tsx
// src/lib/cloudinary.ts
const CLOUD = process.env.NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME;

// Base URL builder
export function cloudinaryUrl(publicId: string, transforms?: Record<string, any>) {
  const base = `https://res.cloudinary.com/${CLOUD}/image/upload`;
  if (!transforms) return `${base}/f_auto,q_auto/${publicId}`;
  const params = Object.entries(transforms).map(([k, v]) => `${k}_${v}`).join(",");
  return `${base}/${params},f_auto,q_auto/${publicId}`;
}

// Pre-built sizes — crop: "pad" mostra o produto inteiro com fundo, sem cortar
export function thumbUrl(publicId: string)  { return cloudinaryUrl(publicId, { w: 300, h: 300, c: "pad" }); }
export function detailUrl(publicId: string) { return cloudinaryUrl(publicId, { w: 600, h: 600, c: "pad" }); }
export function miniUrl(publicId: string)   { return cloudinaryUrl(publicId, { w: 80, h: 80, c: "pad" }); }

export function isCloudinaryUrl(url: string) { return url.includes("cloudinary.com"); }
export function extractPublicId(url: string) {
  if (!url.includes("cloudinary")) return url;
  const match = url.match(/\/upload\/(?:v\d+\/)?(.+?)(?:\.\w+)?$/);
  return match ? match[1] : url;
}
```

## Usage

```tsx
// ProductCard — use thumbUrl for card grid
import { isCloudinaryUrl, thumbUrl, extractPublicId } from "@/lib/cloudinary";

<CardMedia
  image={isCloudinaryUrl(imgUrl) ? thumbUrl(extractPublicId(imgUrl)) : imgUrl}
/>

// Product detail — use detailUrl for large image
<img src={isCloudinaryUrl(imgUrl) ? detailUrl(extractPublicId(imgUrl)) : imgUrl} />

// Admin form — show preview after upload
<CloudinaryUpload onUpload={(url) => setForm({ ...form, imgUrl: url })} />
{form.imgUrl?.includes("cloudinary") && <img src={form.imgUrl} width={100} />}
```

## CLI Batch Upload (Unsigned Preset)

For bulk-uploading product images from the filesystem to Cloudinary, use `curl` with the unsigned upload preset:

```bash
# Upload a single image
curl -s -X POST "https://api.cloudinary.com/v1_1/YOUR_CLOUD_NAME/image/upload" \
  -F "file=@/path/to/image.jpg" \
  -F "upload_preset=YOUR_UPLOAD_PRESET" \
  -F "public_id=carcrew/produtos/category/product-name" \
  -F "folder=carcrew/produtos"

# Response includes secure_url:
# {"secure_url":"https://res.cloudinary.com/.../v1/carcrew/produtos/category/product-name.webp", ...}
```

**Requirements:**
- An **Unsigned Upload Preset** (Settings → Upload → Upload Presets → Add preset → Mode: Unsigned)
- The preset name (e.g., `carcrew`) — no API key/secret needed

**Batch script pattern (Python):**

```python
import subprocess, json

def upload_to_cloudinary(local_path, public_id):
    cmd = [
        "curl", "-s", "-X", "POST",
        "https://api.cloudinary.com/v1_1/drvnlgib2/image/upload",
        "-F", f"file=@{local_path}",
        "-F", "upload_preset=carcrew",
        "-F", f"public_id={public_id}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    data = json.loads(result.stdout)
    return data.get("secure_url")

# Usage:
image_map = {
    1: "/path/to/image1.jpg",
    2: "/path/to/image2.jpg",
}
for pid, local_path in image_map.items():
    cloud_id = f"carcrew/produtos/category/product-{pid}"
    url = upload_to_cloudinary(local_path, cloud_id)
    if url:
        print(f"✅ {pid} → {url}")
```

**Pitfalls:**
- The unsigned preset must be created in the Cloudinary dashboard first — it's not automatic
- Rate limits: Google Drive shared links can throttle after ~50 downloads, but Cloudinary upload itself has generous free limits (25GB storage)
- The `public_id` determines the Cloudinary URL path. Use a consistent folder structure like `carcrew/produtos/<category>/<product-name>`
- After uploading, update the product's `imgUrl` in `produtos.json` with the returned `secure_url`

## Why Cloudinary

- **25GB free** storage + 25GB/mo bandwidth
- **URL-based transformations**: one source image serves thumbnails, detail, mini via URL params
- **CDN** worldwide delivery
- **Upload widget** is a ready-made React-compatible component — no backend upload API needed
- **Auto-format**: `/f_auto` serves WebP when the browser supports it, JPEG otherwise

## Cleaning Up Local Images After Cloudinary Upload

After uploading all images to Cloudinary, remove them from git tracking to keep the repo clean:

```bash
# 1. Add image directories to .gitignore
echo -e "\n# Product images - stored on Cloudinary\npublic/produtos/compressors/\npublic/produtos/shocks/\npublic/produtos/bandejas/\npublic/produtos/bolsas/\n" >> .gitignore

# 2. Remove from git tracking (keep on disk)
git rm -r --cached public/produtos/compressors/ public/produtos/shocks/ public/produtos/bandejas/ public/produtos/bolsas/

# 3. Commit
git commit -m "chore: remove local images - hosted on Cloudinary"

# 4. Update produtos.json imgUrl fields to point to Cloudinary secure_url
# (the URLs returned from the upload response)
```

The SVGs in `public/produtos/` can stay as development-time placeholders for products without real photos yet. Products without real images should have `ativo: false` in their JSON entry to hide them from customers until photos are ready.
