"""Favicon matching modoo.or.kr palette — blue bg with white 모 character."""
from PIL import Image, ImageDraw, ImageFont

BLD = "C:/Windows/Fonts/malgunbd.ttf"

def make_icon(size, out):
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Rounded square bg — brand blue
    r = int(s * 0.22)
    d.rounded_rectangle([0, 0, s, s], radius=r, fill=(24, 119, 242))

    # Big "모" character in white
    font_size = int(s * 0.66)
    font = ImageFont.truetype(BLD, font_size)
    text = "모"
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (s - tw) // 2 - bbox[0]
    ty = (s - th) // 2 - bbox[1] - int(s * 0.03)
    d.text((tx, ty), text, fill=(255, 255, 255), font=font)

    # Coral accent dot (top-right)
    dot_r = int(s * 0.09)
    d.ellipse([s - int(s * 0.18) - dot_r, int(s * 0.15) - dot_r,
               s - int(s * 0.18) + dot_r, int(s * 0.15) + dot_r],
              fill=(255, 89, 94))

    img = img.resize((size, size), Image.LANCZOS)
    img.save(out, "PNG", optimize=True)
    print(f"saved {out} ({size}x{size})")

make_icon(32, "site/favicon-32.png")
make_icon(180, "site/apple-touch-icon.png")
make_icon(192, "site/icon-192.png")
make_icon(512, "site/icon-512.png")
