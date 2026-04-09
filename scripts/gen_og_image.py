"""OG image matching modoo.or.kr palette (light/blue)."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG = (255, 255, 255)
BG_SUB = (246, 247, 248)
BRAND = (24, 119, 242)      # #1877f2
BRAND_DARK = (15, 79, 176)
CORAL = (255, 89, 94)       # #ff595e
INK_900 = (15, 20, 25)
INK_500 = (142, 142, 147)
INK_200 = (222, 233, 245)

img = Image.new("RGB", (W, H), color=BG)
d = ImageDraw.Draw(img)

# Soft top-left brand glow
from PIL import ImageFilter
glow = Image.new("RGB", (W, H), color=BG)
gd = ImageDraw.Draw(glow)
for r in range(520, 0, -18):
    c = (min(255, 240 - r // 20), min(255, 246 - r // 30), 255)
    gd.ellipse([-180 - r, -180 - r, 380 + r, 380 + r], fill=c)
glow = glow.filter(ImageFilter.GaussianBlur(90))
img = Image.blend(img, glow, 0.6)
d = ImageDraw.Draw(img)

# Left brand bar
d.rectangle([40, 70, 46, H - 70], fill=BRAND)

REG = "C:/Windows/Fonts/malgun.ttf"
BLD = "C:/Windows/Fonts/malgunbd.ttf"

f_eyebrow = ImageFont.truetype(REG, 26)
f_title = ImageFont.truetype(BLD, 76)
f_sub = ImageFont.truetype(REG, 32)
f_stat_n = ImageFont.truetype(BLD, 56)
f_stat_l = ImageFont.truetype(REG, 20)
f_footer = ImageFont.truetype(REG, 22)
f_logo = ImageFont.truetype(BLD, 28)

# Logo chip
d.rounded_rectangle([80, 50, 132, 102], radius=12, fill=BRAND)
bbox = d.textbbox((0, 0), "모", font=f_logo)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
d.text((80 + (52 - tw) / 2, 50 + (52 - th) / 2 - 4), "모", fill=(255, 255, 255), font=f_logo)
d.text((148, 62), "MODOO STARTUP PREDICTOR  ·  v1  ·  2026.04.09", fill=INK_500, font=f_eyebrow)

# Title
d.text((80, 130), "모두의 창업 합격 예측", fill=INK_900, font=f_title)
d.text((80, 228), "AI vs 정부 심사위원, 누가 더 정확할까?", fill=INK_500, font=f_sub)

# Stat blocks
def stat_block(x, y, num, label, color):
    d.rounded_rectangle([x, y, x + 230, y + 130], radius=16, fill=BG, outline=INK_200, width=2)
    d.text((x + 20, y + 20), label, fill=INK_500, font=f_stat_l)
    d.text((x + 20, y + 50), num, fill=color, font=f_stat_n)

stat_block(80,  320, "3,797", "공개 풀", INK_900)
stat_block(330, 320, "5,000", "선발", BRAND)
stat_block(580, 320, "0.04", "좋아요-점수 상관", BRAND_DARK)
stat_block(830, 320, "D-36", "마감(5/15)", CORAL)

# Divider
d.rectangle([80, 490, W - 80, 491], fill=INK_200)

bullets = [
    "·  닉네임·좋아요·시각 모두 가린 블라인드 스코어링",
    "·  LOCAL 공식 3축 + TECH 정부 표준 추정 3축",
    "·  SHA256으로 잠근 예측 — 발표 후 정직하게 채점",
]
for i, b in enumerate(bullets):
    d.text((80, 510 + i * 32), b, fill=INK_900, font=f_footer)

url = "modoo-startup-predictor.pages.dev"
bbox = d.textbbox((0, 0), url, font=f_footer)
w = bbox[2] - bbox[0]
d.text((W - w - 80, 600), url, fill=BRAND, font=f_footer)

img.save("site/og.png", "PNG", optimize=True)
print(f"saved site/og.png ({W}x{H})")
