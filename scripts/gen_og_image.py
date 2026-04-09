"""Generate OG image (v2) — poster style, provocative, human-feeling."""
from PIL import Image, ImageDraw, ImageFilter

W, H = 1200, 630
BG = (8, 12, 24)
FG = (237, 242, 247)
MUTED = (148, 163, 184)
EMERALD = (52, 211, 153)
CORAL = (251, 113, 133)
AMBER = (251, 191, 36)

img = Image.new("RGB", (W, H), color=BG)
d = ImageDraw.Draw(img)

# Atmospheric gradient: radial-ish glow top left
glow = Image.new("RGB", (W, H), color=BG)
gd = ImageDraw.Draw(glow)
for r in range(600, 0, -20):
    alpha = 1 - (r / 600)
    c = (int(16 + 20 * alpha), int(40 + 35 * alpha), int(55 + 50 * alpha))
    gd.ellipse([-200 - r, -200 - r, 400 + r, 400 + r], fill=c)
glow = glow.filter(ImageFilter.GaussianBlur(80))
img.paste(glow, (0, 0))
d = ImageDraw.Draw(img)

# Subtle grain dots
import random
random.seed(42)
for _ in range(400):
    x, y = random.randint(0, W), random.randint(0, H)
    d.point((x, y), fill=(40, 55, 80))

# Accent vertical line on left
d.rectangle([40, 70, 44, H - 70], fill=EMERALD)

from PIL import ImageFont
BLD = "C:/Windows/Fonts/malgunbd.ttf"
REG = "C:/Windows/Fonts/malgun.ttf"

f_tag = ImageFont.truetype(REG, 22)
f_mega = ImageFont.truetype(BLD, 112)
f_body = ImageFont.truetype(REG, 30)
f_card_label = ImageFont.truetype(REG, 20)
f_card_id = ImageFont.truetype(BLD, 28)
f_small = ImageFont.truetype(REG, 20)
f_url = ImageFont.truetype(BLD, 26)

# Top tag
d.text((80, 70), "MODOO-STARTUP-PREDICTOR  /  v1  /  2026.04.09", fill=MUTED, font=f_tag)

# Giant question (main headline) — left aligned
d.text((74, 140), "5,000명 중", fill=FG, font=f_mega)
d.text((74, 262), "누가 뽑힐까?", fill=EMERALD, font=f_mega)

# Subheadline
d.text((80, 400), "심사위원이 뽑기 전에, AI가 먼저 뽑아봤다.", fill=MUTED, font=f_body)

# Right-side mock prediction cards (stacked, tilted)
def mock_card(x, y, label, idn, score, status, rotate=0):
    cw, ch = 280, 88
    card = Image.new("RGBA", (cw + 40, ch + 40), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([20, 20, 20 + cw, 20 + ch], radius=14,
                         fill=(15, 23, 42), outline=(51, 65, 85), width=2)
    cd.text((38, 34), label, fill=MUTED, font=f_card_label)
    cd.text((38, 58), idn, fill=FG, font=f_card_id)
    color = EMERALD if status == "통과" else CORAL
    bw, bh = 70, 34
    cd.rounded_rectangle([20 + cw - bw - 18, 20 + ch - bh - 18,
                          20 + cw - 18, 20 + ch - 18], radius=8, fill=color)
    from PIL import ImageFont as IF
    f_b = IF.truetype(BLD, 22)
    # center text in badge
    tb = cd.textbbox((0, 0), status, font=f_b)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    cd.text((20 + cw - bw - 18 + (bw - tw) / 2, 20 + ch - bh - 18 + (bh - th) / 2 - 3),
            status, fill=(8, 12, 24), font=f_b)
    # score tiny bar
    cd.text((180, 34), f"{score}/30", fill=MUTED, font=f_card_label)
    if rotate:
        card = card.rotate(rotate, resample=Image.BICUBIC, expand=False)
    img.paste(card, (x - 20, y - 20), card)

# Stack three cards on right
mock_card(800, 140, "TECH  ·  상위 4%",    "#10652",  "26", "통과", rotate=-2)
mock_card(800, 250, "TECH  ·  상위 61%",   "#11759",  "12", "탈락", rotate=1.5)
mock_card(800, 360, "LOCAL ·  상위 2%",    "#5489",   "23", "통과", rotate=-1)

# Bottom strip — URL + credibility
d.rectangle([0, H - 82, W, H - 80], fill=(30, 41, 59))
d.text((80, H - 62), "발표 전 SHA256 lock  ·  블라인드 스코어링 검증 r=0.04", fill=MUTED, font=f_small)
d.text((80, H - 36), "3,797개 공개 아이디어  ·  분야별 3축 평가  ·  코드 전면 공개", fill=MUTED, font=f_small)

url = "modoo-startup-predictor.pages.dev"
bbox = d.textbbox((0, 0), url, font=f_url)
w = bbox[2] - bbox[0]
d.text((W - w - 80, H - 50), url, fill=EMERALD, font=f_url)

img.save("site/og.png", "PNG", optimize=True)
print(f"saved site/og.png ({W}x{H})")
