"""Generate favicon PNGs (32, 180) from a simple design."""
from PIL import Image, ImageDraw, ImageFont

BLD = "C:/Windows/Fonts/malgunbd.ttf"

def make_icon(size, out):
    img = Image.new("RGBA", (size * 4, size * 4), (0, 0, 0, 0))  # supersample
    d = ImageDraw.Draw(img)
    s = size * 4

    # Rounded square bg
    r = int(s * 0.22)
    d.rounded_rectangle([0, 0, s, s], radius=r, fill=(11, 18, 32))

    # Thin border
    d.rounded_rectangle([int(s * 0.045), int(s * 0.045), s - int(s * 0.045), s - int(s * 0.045)],
                        radius=int(r * 0.85), outline=(52, 211, 153, 90), width=int(s * 0.012))

    # Big "모" character
    font_size = int(s * 0.66)
    font = ImageFont.truetype(BLD, font_size)
    text = "모"
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (s - tw) // 2 - bbox[0]
    ty = (s - th) // 2 - bbox[1] - int(s * 0.03)
    d.text((tx, ty), text, fill=(52, 211, 153), font=font)

    # Small emerald dot (top-right accent)
    dot_r = int(s * 0.08)
    d.ellipse([s - int(s * 0.2) - dot_r, int(s * 0.14) - dot_r,
               s - int(s * 0.2) + dot_r, int(s * 0.14) + dot_r],
              fill=(52, 211, 153))

    # Downsample with antialiasing
    img = img.resize((size, size), Image.LANCZOS)
    img.save(out, "PNG", optimize=True)
    print(f"saved {out} ({size}x{size})")

make_icon(32, "site/favicon-32.png")
make_icon(180, "site/apple-touch-icon.png")
make_icon(192, "site/icon-192.png")
make_icon(512, "site/icon-512.png")
