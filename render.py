"""Draw a newspaper front page summing up Monday 23 November 2026.

Fresh implementation written for the news-image-20261123 bounty from a prose
brief: warm paper, ink + deep-red accent, masthead naming the day, a lead
story on the Gulf with a drawn seascape, three story cards, and a briefs
strip. All text is drawn with Pillow; no AI image generation, no network.
Deterministic: same input -> same bytes (no randomness, no timestamps).
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 239, 221)
INK = (25, 23, 19)
RED = (140, 29, 24)
MUTED = (107, 99, 85)
SEA = (46, 74, 94)
SEA_DARK = (32, 54, 70)
SKY_TOP = (232, 228, 210)
SKY_BOT = (207, 224, 232)
GREEN = (58, 107, 63)
ORANGE = (214, 110, 44)

SERIF = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"

_warnings = []


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(text, f, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if f.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(d, x, y, text, f, fill, max_w, max_lines=None, leading=None):
    """Draw wrapped text; record a warning if it would overflow its box."""
    leading = leading if leading is not None else int(f.size * 1.22)
    lines = wrap(text, f, max_w)
    if max_lines is not None and len(lines) > max_lines:
        _warnings.append("overflow: %r needs %d lines, box allows %d"
                         % (text[:40], len(lines), max_lines))
        lines = lines[:max_lines]
    for i, line in enumerate(lines):
        d.text((x, y + i * leading), line, font=f, fill=fill)
    return y + len(lines) * leading


def rule(d, x, y, w, weight=2, fill=INK):
    d.rectangle([x, y, x + w, y + weight - 1], fill=fill)


def draw_seascape(d, x, y, w, h):
    """Strait of Hormuz: sky, sun, sea, tanker, smoke, waves."""
    # sky gradient
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(SKY_TOP[k] + (SKY_BOT[k] - SKY_TOP[k]) * t) for k in range(3))
        d.line([(x, y + i), (x + w, y + i)], fill=c)
    # sun
    sx, sy, sr = x + w - 62, y + 42, 26
    d.ellipse([sx - sr - 10, sy - sr - 10, sx + sr + 10, sy + sr + 10],
              fill=(244, 226, 170))
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(240, 205, 110))
    # birds
    for bx, by in ((x + 52, y + 46), (x + 88, y + 62)):
        d.arc([bx - 12, by - 8, bx, by + 8], 200, 340, fill=INK, width=2)
        d.arc([bx, by - 8, bx + 12, by + 8], 200, 340, fill=INK, width=2)
    # sea
    sea_y = y + int(h * 0.62)
    d.rectangle([x, sea_y, x + w, y + h], fill=SEA)
    for wy, ww in ((sea_y + 18, 3), (sea_y + 42, 2), (sea_y + 66, 3)):
        for k in range(4):
            wx = x + 18 + k * 92
            d.arc([wx, wy - 8, wx + 56, wy + 8], 180, 360,
                  fill=(150, 180, 198), width=ww)
    # tanker: hull, containers, bridge, funnel
    hx0, hx1 = x + 46, x + w - 46
    hy = sea_y + 6
    d.polygon([(hx0, hy), (hx1, hy), (hx1 - 14, hy + 34), (hx0 + 14, hy + 34)],
              fill=(34, 34, 36))
    d.rectangle([hx0 + 8, hy - 6, hx1 - 8, hy], fill=(120, 20, 16))
    # containers
    cw = (hx1 - hx0 - 90) // 3
    cols = [(168, 92, 60), (96, 120, 138), (150, 150, 148)]
    for i in range(3):
        cx = hx0 + 34 + i * (cw + 6)
        d.rectangle([cx, hy - 34, cx + cw, hy - 8], fill=cols[i])
        d.line([(cx, hy - 22), (cx + cw, hy - 22)], fill=(255, 255, 255), width=1)
    # bridge (white block) + funnel
    d.rectangle([hx1 - 62, hy - 58, hx1 - 22, hy - 34], fill=(232, 228, 216))
    for wy in range(hy - 54, hy - 38, 6):
        d.line([(hx1 - 58, wy), (hx1 - 26, wy)], fill=SEA_DARK, width=2)
    d.rectangle([hx0 + 18, hy - 52, hx0 + 34, hy - 34], fill=(60, 60, 62))
    d.rectangle([hx0 + 18, hy - 52, hx0 + 34, hy - 46], fill=RED)
    # smoke from the funnel
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    fx, fy = hx0 + 26, hy - 56
    for i, (dx, dy, r, a) in enumerate(((0, -12, 13, 110), (10, -34, 16, 85),
                                        (-4, -58, 19, 60), (8, -82, 22, 40))):
        od.ellipse([fx + dx - r, fy + dy - r, fx + dx + r, fy + dy + r],
                   fill=(120, 118, 112, a))
    return overlay


def draw_globe(d, x, y, s):
    """Small globe icon for the climate card."""
    d.ellipse([x, y, x + s, y + s], outline=INK, width=3)
    d.arc([x + 6, y + s * 0.28, x + s - 6, y + s * 0.72], 0, 360,
          fill=INK, width=2)
    d.ellipse([x + s * 0.5 - 2, y, x + s * 0.5 + 2, y + s],
              outline=INK, width=2)
    d.line([(x + 4, y + s * 0.5), (x + s - 4, y + s * 0.5)], fill=INK, width=2)
    # sprout
    lx, ly = x + s - 8, y + s - 6
    d.arc([lx - 10, ly - 14, lx + 10, ly + 6], 180, 360, fill=GREEN, width=3)
    d.line([(lx, ly), (lx, ly - 14)], fill=GREEN, width=3)


def draw_flame_ship(d, x, y, s):
    """Flame over a small hull, for the ship-fire card."""
    d.polygon([(x + s * 0.5, y + 2), (x + s * 0.78, y + s * 0.42),
               (x + s * 0.66, y + s * 0.62), (x + s * 0.5, y + s * 0.55),
               (x + s * 0.34, y + s * 0.62), (x + s * 0.22, y + s * 0.42)],
              fill=ORANGE)
    d.polygon([(x + s * 0.5, y + 14), (x + s * 0.66, y + s * 0.4),
               (x + s * 0.5, y + s * 0.52), (x + s * 0.34, y + s * 0.4)],
              fill=RED)
    d.polygon([(x + 4, y + s * 0.68), (x + s - 4, y + s * 0.68),
               (x + s - 14, y + s * 0.94), (x + 14, y + s * 0.94)], fill=INK)
    d.rectangle([x + s * 0.44, y + s * 0.52, x + s * 0.56, y + s * 0.68],
                fill=INK)


def draw_factory(d, x, y, s):
    """Factory silhouette with a flame, for the fire card."""
    d.rectangle([x + 4, y + s * 0.5, x + s - 4, y + s * 0.94], fill=INK)
    for i in range(3):
        bx = x + 8 + i * ((s - 16) // 3)
        d.polygon([(bx, y + s * 0.5), (bx + (s - 16) // 6, y + s * 0.3),
                   (bx + (s - 16) // 3, y + s * 0.5)], fill=INK)
    d.rectangle([x + s - 16, y + s * 0.18, x + s - 8, y + s * 0.5], fill=INK)
    d.polygon([(x + s * 0.5, y + 2), (x + s * 0.68, y + s * 0.26),
               (x + s * 0.5, y + s * 0.34), (x + s * 0.32, y + s * 0.26)],
              fill=ORANGE)


def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx, cw = 36, W - 72  # margin, content width

    # ---- masthead ----
    rule(d, mx, 26, cw, 3, RED)
    d.text((W // 2, 40), "THE WORLD TODAY", font=font(SERIF_B, 58),
           fill=INK, anchor="ma")
    d.text((W // 2, 108), "MONDAY 23 NOVEMBER 2026", font=font(SANS_B, 30),
           fill=RED, anchor="ma")
    rule(d, mx, 152, cw, 2, INK)
    rule(d, mx, 157, cw, 1, INK)

    # ---- lead story ----
    ly = 176
    d.text((mx, ly), "THE GULF  •  LEAD STORY", font=font(SANS_B, 17), fill=RED)
    hx = mx
    hy = ly + 30
    head_f = font(SERIF_B, 46)
    while (head_f.getlength("IRAN STRIKES BAHRAIN") > 560
           or head_f.getlength("AS HORMUZ ATTACKS SURGE") > 560):
        head_f = font(SERIF_B, head_f.size - 1)
    d.text((hx, hy), "IRAN STRIKES BAHRAIN", font=head_f, fill=INK)
    d.text((hx, hy + 52), "AS HORMUZ ATTACKS SURGE", font=head_f, fill=INK)
    deck = ("Tehran hits an industrial site in Bahrain, home of the US Fifth "
            "Fleet, as tanker attacks in the Strait reach their highest level. "
            "Tehran says its uranium stockpile stays in Iran.")
    text_block(d, hx, hy + 116, deck, font(SANS, 20), INK, 560,
               max_lines=4, leading=27)
    text_block(d, hx, hy + 232,
               "Saudi-led forces intercept a Houthi missile.",
               font(SERIF_I, 18), MUTED, 560, max_lines=1)

    # seascape, right column
    sx, sy, sw, sh = 624, ly + 6, 364, 288
    overlay = draw_seascape(d, sx, sy, sw, sh)
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([sx, sy, sx + sw, sy + sh], outline=INK, width=2)
    d.text((sx + sw // 2, sy + sh + 10),
           "A tanker in the Strait of Hormuz", font=font(SERIF_I, 15),
           fill=MUTED, anchor="ma")

    # ---- divider ----
    rule(d, mx, 522, cw, 2, INK)

    # ---- three story cards ----
    cards = [
        ("CLIMATE  •  ANTALYA", "COP31 ON THE BRINK",
         "Summit two days into overtime. The third draft still omits fossil "
         "fuels; the EU rejects it as greenwash. Some 130 nations push to "
         "restore the language.", draw_globe),
        ("UKRAINE  •  THE BALTIC", "SHIP ABLAZE OFF FINLAND",
         "Russian cargo ship Sparta II burns after a Ukrainian drone strike. "
         "A drone hits a building near Kyiv; at least 14 people missing.",
         draw_flame_ship),
        ("INDONESIA", "FACTORY FIRE KILLS SEVEN",
         "Seven bodies recovered and dozens missing after a blaze at a "
         "factory. Rescue teams keep searching through the wreckage.",
         draw_factory),
    ]
    col_w, gap = 300, 26
    cy = 542
    for i, (kicker, head, body, icon) in enumerate(cards):
        cx = mx + i * (col_w + gap)
        icon(d, cx, cy, 58)
        d.text((cx + 70, cy + 6), kicker, font=font(SANS_B, 15), fill=RED)
        d.text((cx + 70, cy + 28), "23 NOV", font=font(SANS_B, 13), fill=MUTED)
        text_block(d, cx, cy + 70, head, font(SERIF_B, 25), INK, col_w,
                   max_lines=2, leading=30)
        text_block(d, cx, cy + 134, body, font(SANS, 17), INK, col_w,
                   max_lines=5, leading=23)
        if i < 2:
            d.line([(cx + col_w + 13, cy), (cx + col_w + 13, cy + 252)],
                   fill=(200, 190, 165), width=1)

    # ---- divider ----
    rule(d, mx, 820, cw, 2, INK)

    # ---- briefs strip ----
    by = 838
    d.text((mx, by), "IN BRIEF", font=font(SANS_B, 16), fill=RED)
    briefs = [
        ("LISBON", "Thousands march as living costs fuel anger."),
        ("MYANMAR", "Army-backed government calls the ASEAN decision "
         "\u2018unfair and imbalanced\u2019."),
        ("NVIDIA", "US accounting probe amid turmoil over AI chips sent to China."),
        ("WASHINGTON", "Trump vows to work with Democrats to cap card interest at 10%."),
    ]
    bw = 226
    for i, (place, txt) in enumerate(briefs):
        bx = mx + i * (bw + 8)
        text_block(d, bx, by + 26, place + " \u2014 " + txt,
                   font(SANS, 15), INK, bw, max_lines=4, leading=20)
    by2 = by + 112
    d.text((mx, by2), "SEOUL \u2014 Education minister resigns in an AI-cheating scandal.",
           font=font(SANS, 15), fill=INK)
    d.text((mx, by2 + 24),
           "THE HAGUE \u2014 Rohingya hail the World Court\u2019s genocide ruling on Myanmar.",
           font=font(SANS, 15), fill=INK)

    # ---- footer ----
    rule(d, mx, 994, cw, 1, MUTED)
    d.text((W // 2, 1002), "Sources: AFP  •  Reuters  •  Al Jazeera  •  The Times",
           font=font(SANS, 13), fill=MUTED, anchor="ma")

    if _warnings:
        print("WARNINGS:")
        for w in _warnings:
            print(" -", w)
    return img


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    render().save(out, "PNG")
    print("wrote", out)
