"""Generate 1200x630 OG image for the prediction site."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
img = Image.new("RGB", (W, H), color=(2, 6, 23))  # bg-gray-950
d = ImageDraw.Draw(img)

# Subtle dot grid
for x in range(0, W, 40):
    for y in range(0, H, 40):
        d.point((x, y), fill=(31, 41, 55))

# Top gradient bar (emerald)
for i in range(8):
    d.rectangle([0, i, W, i + 1], fill=(16, 185, 129 - i * 4))

REG = "C:/Windows/Fonts/malgun.ttf"
BLD = "C:/Windows/Fonts/malgunbd.ttf"

f_eyebrow = ImageFont.truetype(REG, 28)
f_title   = ImageFont.truetype(BLD, 76)
f_sub     = ImageFont.truetype(REG, 32)
f_stat_n  = ImageFont.truetype(BLD, 56)
f_stat_l  = ImageFont.truetype(REG, 22)
f_footer  = ImageFont.truetype(REG, 22)

# Eyebrow
d.text((60, 50), "v1 LOCKED · SHA256 · 2026-04-09", fill=(110, 231, 183), font=f_eyebrow)

# Title (2 lines)
d.text((60, 95), "모두의 창업 합격 예측", fill=(255, 255, 255), font=f_title)
d.text((60, 195), "AI vs 정부 심사위원, 누가 더 정확할까?", fill=(229, 231, 235), font=f_sub)

# Stat blocks
def stat_block(x, y, num, label, color):
    d.rounded_rectangle([x, y, x + 230, y + 130], radius=12, fill=(17, 24, 39), outline=(31, 41, 55), width=2)
    d.text((x + 20, y + 20), label, fill=(156, 163, 175), font=f_stat_l)
    d.text((x + 20, y + 50), num, fill=color, font=f_stat_n)

stat_block(60,  300, "3,797", "공개 풀", (255, 255, 255))
stat_block(310, 300, "5,000", "선발", (110, 231, 183))
stat_block(560, 300, "0.04",  "좋아요-점수 상관", (251, 191, 36))
stat_block(810, 300, "D-36",  "마감(5/15)", (252, 165, 165))

# Mid divider line
d.rectangle([60, 470, W - 60, 471], fill=(31, 41, 55))

# Method bullets
bullets = [
    "·닉네임·좋아요·시각 모두 가린 블라인드 스코어링",
    "·LOCAL 공식 3축 + TECH 정부 표준 추정 3축",
    "·SHA256으로 잠근 예측 — 발표 후 정직하게 채점",
]
for i, b in enumerate(bullets):
    d.text((60, 490 + i * 32), b, fill=(209, 213, 219), font=f_footer)

# URL bottom right
url = "modoo-startup-predictor.pages.dev"
bbox = d.textbbox((0, 0), url, font=f_footer)
w = bbox[2] - bbox[0]
d.text((W - w - 60, 580), url, fill=(110, 231, 183), font=f_footer)

img.save("site/og.png", "PNG", optimize=True)
print(f"saved site/og.png ({W}x{H})")
