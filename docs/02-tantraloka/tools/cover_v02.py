#!/usr/bin/env python3
"""v02 series cover + emblem art (original geometry, no stock, no text in image).

Concept: restrained classical-Indian manuscript/yantra-inspired line geometry —
concentric orbits, paired triangles (upward/downward), twelve radial ticks
(dvādaśa hint), central bindu. Warm ivory field, deep maroon + antique gold
linework. ALL lettering is set in Word (proper shaping, selectable text);
the PNG carries geometry only so no broken Indic text can occur inside art.
Outputs:
  assets/cover_emblem.png  (emblem, transparent-ivory square, for cover/title)
  assets/cover_full_A4.png (full-bleed A4 frame art, optional backdrop)
"""
import math
import os

from PIL import Image, ImageDraw

BASE = "/root/tantraloka_ml"
ASSETS = os.path.join(BASE, "assets")

IVORY = (250, 244, 230)
GOLD = (166, 124, 46)
MAROON = (74, 20, 12)
GOLD_LT = (196, 158, 80)


def emblem(size=1600):
    im = Image.new("RGB", (size, size), IVORY)
    d = ImageDraw.Draw(im)
    cx = cy = size // 2
    # concentric orbits
    for i, r in enumerate((180, 300, 430, 560)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=GOLD if i % 2 else MAROON, width=6 if i % 2 == 0 else 3)
    # twelve radial ticks between orbit 2 and 3
    for k in range(12):
        a = math.radians(k * 30 - 90)
        x1, y1 = cx + 300 * math.cos(a), cy + 300 * math.sin(a)
        x2, y2 = cx + 430 * math.cos(a), cy + 430 * math.sin(a)
        d.line([x1, y1, x2, y2], fill=MAROON, width=5)
        mx, my = cx + 365 * math.cos(a), cy + 365 * math.sin(a)
        d.ellipse([mx - 12, my - 12, mx + 12, my + 12], fill=GOLD)
    # paired triangles (shadkona) inscribed in inner orbit
    R = 300
    up = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a)))
          for a in (-90, 30, 150)]
    dn = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a)))
          for a in (90, 210, 330)]
    d.polygon(up, outline=MAROON, width=6)
    d.polygon(dn, outline=MAROON, width=6)
    # petal arcs: small circles at triangle vertices
    for (x, y) in up + dn:
        d.ellipse([x - 26, y - 26, x + 26, y + 26], outline=GOLD, width=4)
    # central bindu
    d.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], fill=MAROON)
    d.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], outline=GOLD, width=4)
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=GOLD_LT)
    # corner diamonds (manuscript-frame hint)
    m = 60
    for (qx, qy) in ((m, m), (size - m, m), (m, size - m), (size - m, size - m)):
        d.polygon([(qx, qy - 26), (qx + 26, qy), (qx, qy + 26), (qx - 26, qy)],
                  outline=MAROON, width=4)
        d.ellipse([qx - 7, qy - 7, qx + 7, qy + 7], fill=GOLD)
    return im


def full_frame(w=2480, h=3508):
    """A4 @300dpi frame art: ivory field, maroon outer + gold inner rules,
    emblem centred in upper third; lower two-thirds left clear for Word text."""
    im = Image.new("RGB", (w, h), IVORY)
    d = ImageDraw.Draw(im)
    d.rectangle([90, 90, w - 90, h - 90], outline=MAROON, width=10)
    d.rectangle([130, 130, w - 130, h - 130], outline=GOLD, width=4)
    em = emblem(1500)
    im.paste(em, ((w - 1500) // 2, 320))
    # baseline ornament for lower page: thin gold rule + central diamond
    y = h - 420
    d.line([420, y, w - 420, y], fill=GOLD, width=4)
    d.polygon([(w // 2, y - 30), (w // 2 + 30, y), (w // 2, y + 30),
               (w // 2 - 30, y)], outline=MAROON, width=5)
    d.ellipse([w // 2 - 9, y - 9, w // 2 + 9, y + 9], fill=GOLD)
    return im


def main():
    os.makedirs(ASSETS, exist_ok=True)
    emblem(1600).save(os.path.join(ASSETS, "cover_emblem.png"))
    full_frame().save(os.path.join(ASSETS, "cover_full_A4.png"))
    print("cover art written to", ASSETS)


if __name__ == "__main__":
    main()
