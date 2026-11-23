#!/usr/bin/env python3
"""Render the 23 November 2026 front page for news-image-20261123.

Draws a newspaper front page with Pillow and saves it as entry.png
(1024x1024, under 1 MiB). All stories are the verified events of
22-23 November 2026 from the entry brief: the Iran/Bahrain/Hormuz
lead, COP31, the Sparta II / Kyiv strikes, the Indonesia factory
fire, and the Lisbon / Myanmar / Nvidia / Trump briefs.

Run: python3 render.py  ->  writes entry.png next to this file.
The grading entrypoint is main.py (stdlib only), which copies the
finished PNG to /output/entry.png.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CW = W - 2 * MARGIN  # 952

PAPER = (247, 240, 221)
INK = (26, 26, 26)
RED = (139, 26, 26)
SEA = (40, 70, 95)
SKY = (238, 231, 210)
CLOUD = (226, 219, 198)
SMOKE_D = (120, 120, 118)
SMOKE_M = (150, 150, 148)
SMOKE_L = (178, 178, 174)
GREEN = (34, 90, 60)
ORANGE = (198, 88, 20)
YELLOW = (228, 178, 40)
GREY = (96, 92, 84)
WAVE = (240, 238, 230)
STEEL = (60, 60, 60)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def fnt(path, size):
    return ImageFont.truetype(path, size)


def tracked_width(text, font, tracking):
    total = 0
    for ch in text:
        total += font.getlength(ch) + tracking
    return total - tracking if text else 0


def draw_tracked(d, x, y, text, font, fill, tracking=2):
    cx = x
    for ch in text:
        d.text((cx, y), ch, font=font, fill=fill)
        cx += font.getlength(ch) + tracking


def draw_tracked_center(d, cx, y, text, font, fill, tracking=2):
    w = tracked_width(text, font, tracking)
    draw_tracked(d, cx - w / 2, y, text, font, fill, tracking)


def wrap(text, font, max_w):
    lines = []
    for para in text.split("\n"):
        words = para.split()
        cur = ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if font.getlength(trial) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
    return lines


def draw_block(d, x, y, lines, font, fill, leading, center_w=None):
    for ln in lines:
        if center_w is not None:
            d.text((x + (center_w - font.getlength(ln)) / 2, y), ln,
                   font=font, fill=fill)
        else:
            d.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def fit_font(text, path, start, max_w):
    size = start
    while size > 10:
        f = fnt(path, size)
        if f.getlength(text) <= max_w:
            return f
        size -= 1
    return fnt(path, 10)


def rule(d, x, y, w, weight=1, fill=INK):
    d.rectangle([x, y, x + w - 1, y + weight - 1], fill=fill)


def draw_tanker_scene(d, x, y, w, h):
    """Drawn tanker-and-smoke scene for the lead story.

    The waterline is at y+92: the hull sits on it with its deck at
    y+66, the superstructure and funnel stand on the deck, and the
    smoke rises above the funnel.
    """
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SKY, outline=INK, width=1)
    # clouds
    d.ellipse([x + 54, y + 16, x + 134, y + 32], fill=CLOUD)
    d.ellipse([x + 664, y + 24, x + 764, y + 38], fill=CLOUD)
    d.ellipse([x + 394, y + 10, x + 464, y + 22], fill=CLOUD)
    # distant small ship, left, sitting on the waterline
    d.rectangle([x + 100, y + 84, x + 172, y + 92], fill=(140, 136, 130))
    d.rectangle([x + 128, y + 74, x + 148, y + 84], fill=(140, 136, 130))
    # sea
    d.rectangle([x, y + 92, x + w - 1, y + h - 1], fill=SEA)
    # waves
    for wx in (x + 40, x + 300, x + 560, x + 800):
        d.arc([wx, y + 100, wx + 90, y + 116], 200, 340, fill=WAVE, width=2)
    for wx in (x + 160, x + 430, x + 690):
        d.arc([wx, y + 110, wx + 80, y + 122], 200, 340, fill=WAVE, width=2)
    # tanker hull: deck at y+66, bottom edge on the waterline y+92
    d.polygon([(x + 300, y + 66), (x + 730, y + 66), (x + 706, y + 92),
               (x + 324, y + 92)], fill=(32, 32, 32))
    d.line([x + 300, y + 66, x + 730, y + 66], fill=(90, 88, 84), width=2)
    # mast on the deck
    d.line([x + 430, y + 34, x + 430, y + 66], fill=INK, width=2)
    d.line([x + 420, y + 40, x + 440, y + 40], fill=INK, width=2)
    # superstructure with windows, standing on the deck
    d.rectangle([x + 470, y + 32, x + 560, y + 66], fill=(245, 242, 232),
                outline=INK, width=1)
    for wx in (482, 506, 530):
        d.rectangle([x + wx, y + 42, x + wx + 12, y + 54], fill=INK)
    # funnel, red with black cap, standing on the deck
    d.rectangle([x + 600, y + 28, x + 634, y + 66], fill=RED)
    d.rectangle([x + 600, y + 28, x + 634, y + 38], fill=INK)
    # smoke rising from the funnel
    d.ellipse([x + 596, y + 4, x + 640, y + 24], fill=SMOKE_L)
    d.ellipse([x + 586, y + 12, x + 624, y + 30], fill=SMOKE_M)
    d.ellipse([x + 604, y + 2, x + 646, y + 20], fill=SMOKE_D)
    d.ellipse([x + 570, y + 18, x + 600, y + 34], fill=SMOKE_L)


def icon_globe(d, bx, by):
    cx, cy = bx + 30, by + 30
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], outline=GREEN, width=3)
    d.ellipse([cx - 12, cy - 24, cx + 12, cy + 24], outline=GREEN, width=2)
    d.line([cx - 24, cy, cx + 24, cy], fill=GREEN, width=2)
    d.polygon([(bx + 44, by + 10), (bx + 56, by + 2), (bx + 58, by + 14),
               (bx + 48, by + 18)], fill=GREEN)


def icon_flame_ship(d, bx, by):
    d.polygon([(bx + 30, by + 2), (bx + 44, by + 24), (bx + 52, by + 38),
               (bx + 40, by + 52), (bx + 20, by + 52), (bx + 8, by + 38),
               (bx + 16, by + 24)], fill=ORANGE)
    d.polygon([(bx + 30, by + 20), (bx + 40, by + 34), (bx + 38, by + 48),
               (bx + 22, by + 48), (bx + 20, by + 34)], fill=YELLOW)
    d.polygon([(bx + 6, by + 52), (bx + 54, by + 52), (bx + 46, by + 60),
               (bx + 14, by + 60)], fill=INK)


def icon_factory(d, bx, by):
    d.rectangle([bx + 44, by + 14, bx + 52, by + 56], fill=STEEL)
    d.ellipse([bx + 42, by + 2, bx + 52, by + 12], fill=SMOKE_M)
    d.ellipse([bx + 48, by + 0, bx + 58, by + 10], fill=SMOKE_L)
    d.polygon([(bx + 8, by + 26), (bx + 16, by + 18), (bx + 24, by + 26),
               (bx + 32, by + 18), (bx + 40, by + 26)], fill=STEEL)
    d.rectangle([bx + 8, by + 26, bx + 40, by + 56], fill=STEEL)
    d.rectangle([bx + 14, by + 36, bx + 22, by + 44], fill=PAPER)
    d.rectangle([bx + 28, by + 36, bx + 36, by + 44], fill=PAPER)


def draw_card(d, x, y, w, icon, kicker, headline, body):
    icon(d, x + (w - 60) // 2, y)
    y += 66
    draw_tracked_center(d, x + w // 2, y, kicker, fnt(SANS_B, 17), RED, 2)
    y += 26
    hf = fnt(SERIF_B, 28)
    y = draw_block(d, x, y, headline, hf, INK, 34, center_w=w)
    y += 8
    bf = fnt(SERIF, 18)
    lines = wrap(body, bf, w - 8)
    y = draw_block(d, x + 4, y, lines, bf, INK, 22, center_w=w - 8)
    return y


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # outer frame
    d.rectangle([14, 14, W - 15, H - 15], outline=INK, width=2)
    d.rectangle([20, 20, W - 21, H - 21], outline=INK, width=1)

    y = 28
    draw_tracked_center(d, W // 2, y, "FRONT PAGE - WORLD NEWS",
                        fnt(SANS_B, 19), GREY, 3)
    y += 26
    mast = fit_font("MONDAY 23 NOVEMBER 2026", SERIF_B, 64, CW)
    d.text(((W - mast.getlength("MONDAY 23 NOVEMBER 2026")) / 2, y),
           "MONDAY 23 NOVEMBER 2026", font=mast, fill=INK)
    y += 68
    rule(d, MARGIN, y, CW, 4)
    rule(d, MARGIN, y + 7, CW, 1)
    y += 16

    # ---- lead: Iran / Bahrain / Hormuz ----
    draw_tracked_center(d, W // 2, y, "MIDDLE EAST", fnt(SANS_B, 22), RED, 3)
    y += 30
    hf = fnt(SERIF_B, 50)
    y = draw_block(d, MARGIN, y,
                   ["IRAN STRIKES BAHRAIN", "AS GULF WAR WIDENS"],
                   hf, INK, 56, center_w=CW)
    y += 8
    deck = ("An industrial site is hit in Bahrain, home of the US Navy's "
            "Fifth Fleet. Tanker attacks in the Strait of Hormuz are at "
            "their highest level; a Houthi missile is intercepted. "
            "Tehran says its enriched uranium stockpile stays in Iran.")
    df = fnt(SERIF, 22)
    y = draw_block(d, MARGIN, y, wrap(deck, df, CW - 40), df, INK, 26,
                   center_w=CW - 40)
    y += 10
    draw_tanker_scene(d, MARGIN, y, CW, 124)
    y += 124 + 10
    rule(d, MARGIN, y, CW, 1)
    y += 8

    # ---- three story cards ----
    card_w = 304
    gap = 20
    cards = [
        (icon_globe, "CLIMATE - ANTALYA",
         ["COP31 TALKS", "ON THE BRINK"],
         "The summit in Antalya is two days into overtime. A third draft "
         "still omits fossil fuels; the EU rejects it, and about 130 "
         "countries push to restore the language."),
        (icon_flame_ship, "UKRAINE",
         ["SHIP ABLAZE", "OFF FINLAND"],
         "Russian cargo ship Sparta II is ablaze after a Ukrainian drone "
         "strike. A Russian drone hits a building in the Kyiv region; "
         "at least 14 missing."),
        (icon_factory, "INDONESIA",
         ["FACTORY FIRE:", "SEVEN DEAD"],
         "Seven bodies are recovered and about 50 people are missing "
         "after a factory fire."),
    ]
    card_top = y
    for i, (icon, kicker, headline, body) in enumerate(cards):
        cx = MARGIN + i * (card_w + gap)
        draw_card(d, cx, card_top, card_w, icon, kicker, headline, body)
        if i < 2:
            d.line([cx + card_w + 10, card_top, cx + card_w + 10,
                    card_top + 308], fill=GREY, width=1)
    y = card_top + 308
    rule(d, MARGIN, y, CW, 1)
    y += 8

    # ---- briefs strip ----
    draw_tracked(d, MARGIN, y, "IN BRIEF", fnt(SANS_B, 18), RED, 2)
    y += 24
    briefs = [
        ("LISBON", "Thousands march as living costs fuel anger."),
        ("MYANMAR", "The army-backed government calls an ASEAN decision "
         "\"unfair and imbalanced\"."),
        ("NVIDIA", "The chipmaker faces a US accounting probe amid turmoil."),
        ("TRUMP", "Vows to work with Democrats to cap credit-card "
         "interest at 10%."),
    ]
    bw = 226
    bgap = 16
    bf = fnt(SERIF, 16)
    for i, (kick, text) in enumerate(briefs):
        bx = MARGIN + i * (bw + bgap)
        draw_tracked(d, bx, y, kick, fnt(SANS_B, 16), RED, 2)
        draw_block(d, bx, y + 22, wrap(text, bf, bw), bf, INK, 19)
    y += 22 + 4 * 19 + 12

    # ---- footer ----
    rule(d, MARGIN, y, CW, 1)
    y += 8
    draw_tracked_center(d, W // 2, y, "MONDAY 23 NOVEMBER 2026",
                        fnt(SANS, 15), GREY, 2)
    return img


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    build().save(out, "PNG")
    print("wrote", out)


if __name__ == "__main__":
    main()
