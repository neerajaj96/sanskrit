#!/usr/bin/env python3
"""v02 curated figure system — refined grammar, one figure per doctrinal section.

Keeps the successful v01 concept (pure geometry, no in-figure text; verse
reference lives in the Malayalam caption) but unifies and restrains it:
- 36 curated figures (one per doctrinal H2 + appendix), replacing 334
  near-duplicate per-verse variants (redundancy elimination per spec F).
- Refined palette: warm ivory, antique gold hairlines, deep maroon, slate,
  muted red highlight (no bright presentation-slide red).
- Consistent line weights (4px primary / 2px secondary), double-rule frame,
  smaller aspect (1400x900) to reduce empty frame (spec F+G).
Output: assets/figs_v02/fig_V{nnn}.png + fig_APP1.png
"""
import json
import math
import os

from PIL import Image, ImageDraw

BASE = "/root/tantraloka_ml"
OUT = os.path.join(BASE, "assets", "figs_v02")

IVORY = (255, 251, 240)
GOLD = (166, 124, 46)
MAROON = (90, 26, 16)
SLATE = (46, 64, 87)
HL = (142, 47, 33)
WHITE = (255, 255, 255)

W, H = 1400, 900

MLD = "൦൧൨൩൪൫൬൭൮൯"


def ml(n):
    return "".join(MLD[int(d)] for d in str(n))


def canvas():
    im = Image.new("RGB", (W, H), IVORY)
    d = ImageDraw.Draw(im)
    d.rectangle([6, 6, W - 6, H - 6], outline=GOLD, width=3)
    d.rectangle([16, 16, W - 16, H - 16], outline=GOLD, width=1)
    return im, d


def motif(seed=0):
    im, d = canvas()
    cx, cy = W // 2, H // 2
    for i, r in enumerate(range(100, 340, 60)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=GOLD if i % 2 else MAROON, width=4 if i % 2 == 0 else 2)
    for k in range(12):
        a = math.radians(k * 30 + seed * 7)
        x1, y1 = cx + 100 * math.cos(a), cy + 100 * math.sin(a)
        x2, y2 = cx + 320 * math.cos(a), cy + 320 * math.sin(a)
        d.line([x1, y1, x2, y2], fill=GOLD, width=2)
    d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=MAROON)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=GOLD)
    return im


def triad(h=0):
    im, d = canvas()
    pts = [(W // 2 - 260, H // 2 + 150), (W // 2 + 260, H // 2 + 150),
           (W // 2, H // 2 - 200)]
    d.polygon(pts, outline=MAROON, width=4)
    for i, (x, y) in enumerate(pts):
        fill = HL if i == h % 3 else WHITE
        d.ellipse([x - 105, y - 105, x + 105, y + 105],
                  fill=fill, outline=MAROON, width=4)
    cx, cy = W // 2, H // 2 - 15
    d.ellipse([cx - 58, cy - 58, cx + 58, cy + 58], fill=GOLD, outline=MAROON, width=4)
    return im


def wheel(n=12, h=0):
    im, d = canvas()
    cx, cy = W // 2, H // 2
    R = 300
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=MAROON, width=4)
    d.ellipse([cx - R + 34, cy - R + 34, cx + R - 34, cy + R - 34],
              outline=GOLD, width=2)
    for k in range(n):
        a = math.radians(k * 360.0 / n - 90)
        x, y = cx + (R - 6) * math.cos(a), cy + (R - 6) * math.sin(a)
        wdt = 6 if k == h % n else 2
        col = HL if k == h % n else SLATE
        d.line([cx, cy, x, y], fill=col, width=wdt)
    d.ellipse([cx - 50, cy - 50, cx + 50, cy + 50], fill=MAROON)
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=GOLD)
    return im


def ladder(steps=3, pos=0):
    im, d = canvas()
    bw, bh, gap = 460, 92, 30
    total = steps * (bh + gap)
    y0 = (H - total) // 2 + 30
    for k in range(steps):
        y = y0 + k * (bh + gap)
        fill = HL if k == pos % steps else WHITE
        d.rounded_rectangle([W // 2 - bw // 2, y, W // 2 + bw // 2, y + bh],
                            radius=20, fill=fill, outline=MAROON, width=4)
        if k < steps - 1:
            d.line([W // 2, y + bh, W // 2, y + bh + gap], fill=GOLD, width=4)
            d.polygon([(W // 2 - 12, y + bh + gap - 14),
                       (W // 2 + 12, y + bh + gap - 14),
                       (W // 2, y + bh + gap)], fill=GOLD)
    return im


def flow(stages=4, pos=0):
    im, d = canvas()
    stages = max(2, min(stages, 6))
    bw, bh, gap = 180, 170, 32
    total = stages * bw + (stages - 1) * gap
    x0 = (W - total) // 2
    y = H // 2 - bh // 2
    for k in range(stages):
        x = x0 + k * (bw + gap)
        fill = HL if k == pos % stages else WHITE
        d.rounded_rectangle([x, y, x + bw, y + bh], radius=22,
                            fill=fill, outline=MAROON, width=4)
        if k < stages - 1:
            ax = x + bw
            d.line([ax, H // 2, ax + gap, H // 2], fill=GOLD, width=4)
            d.polygon([(ax + gap - 16, H // 2 - 12),
                       (ax + gap - 16, H // 2 + 12),
                       (ax + gap, H // 2)], fill=GOLD)
    return im


def mirror(mode=0):
    im, d = canvas()
    lw, lh = 340, 460
    y = H // 2 - lh // 2
    x1 = W // 2 - lw - 50
    x2 = W // 2 + 50
    d.rounded_rectangle([x1, y, x1 + lw, y + lh], radius=26,
                        fill=MAROON, outline=MAROON, width=4)
    d.ellipse([x1 + lw // 2 - 72, y + lh // 2 - 72,
               x1 + lw // 2 + 72, y + lh // 2 + 72], fill=GOLD)
    style = mode % 3
    if style == 0:
        d.rounded_rectangle([x2, y, x2 + lw, y + lh], radius=26,
                            outline=MAROON, width=4)
    elif style == 1:
        d.rounded_rectangle([x2 + 50, y + 50, x2 + lw - 50, y + lh - 50],
                            radius=26, outline=HL, width=4)
    else:
        for off in (0, 22, 44):
            d.rounded_rectangle([x2 + off, y + off, x2 + lw - off, y + lh - off],
                                radius=26, outline=MAROON if off < 44 else HL,
                                width=3)
    d.line([W // 2 - 16, y - 50, W // 2 - 16, y + lh + 50], fill=GOLD, width=3)
    return im


def chain(links=5, pos=0):
    im, d = canvas()
    bw, bh, gap = 420, 80, 28
    total = links * (bh + gap)
    y0 = (H - total) // 2 + 30
    for k in range(links):
        y = y0 + k * (bh + gap)
        fill = HL if k == pos % links else WHITE
        d.rounded_rectangle([W // 2 - bw // 2, y, W // 2 + bw // 2, y + bh],
                            radius=40, fill=fill, outline=MAROON, width=4)
        if k < links - 1:
            d.line([W // 2 - 50, y + bh, W // 2 - 50, y + bh + gap],
                   fill=GOLD, width=3)
            d.line([W // 2 + 50, y + bh, W // 2 + 50, y + bh + gap],
                   fill=GOLD, width=3)
    return im


def sound(pos=0):
    im, d = canvas()
    n = 12
    bw, bh, gap = 760, 34, 22
    total = n * (bh + gap)
    y0 = (H - total) // 2 + 16
    for k in range(n):
        y = y0 + k * (bh + gap)
        wdt = bw - k * 32
        x0 = (W - wdt) // 2
        fill = HL if k == pos % n else None
        d.rounded_rectangle([x0, y, x0 + wdt, y + bh], radius=16,
                            fill=fill, outline=MAROON, width=3)
    return im


FAM_ML = {
    "motif": "അലങ്കാരം",
    "triad": "ത്രിതയം",
    "wheel": "ചക്രം",
    "ladder": "സോപാനം",
    "flow": "പ്രവാഹം",
    "mirror": "ദർപ്പണം",
    "chain": "പരമ്പര",
    "sound": "നാദതലം",
}

# Curated: one representative verse per doctrinal H2 (+ appendix figure).
# verse -> (family, section-label, kwargs). Order follows the book.
CURATED = [
    (1, "motif", "മംഗളം", {}),
    (2, "triad", "ദേവീസ്തുതി", {}),
    (7, "chain", "ഗുരുസ്തുതി", {"links": 5}),
    (14, "flow", "ഗ്രന്ഥോദ്ദേശ്യം", {"stages": 4}),
    (22, "mirror", "സ്വാതന്ത്ര്യം", {"mode": 0}),
    (36, "triad", "അറിയുന്നവൻ", {}),
    (39, "flow", "നിർവചനം", {"stages": 4}),
    (52, "mirror", "സ്വതഃസിദ്ധി", {"mode": 1}),
    (60, "wheel", "സർവവ്യാപി", {"n": 6}),
    (67, "wheel", "സ്വാതന്ത്ര്യശക്തി", {"n": 8}),
    (81, "wheel", "സമൂഹധർമ്മം", {"n": 5}),
    (90, "ladder", "ഭേദം", {"steps": 3}),
    (94, "triad", "നാമനിർവചനം", {}),
    (106, "wheel", "ദ്വാദശീസംഘം", {"n": 12}),
    (116, "flow", "കല്പനാശക്തി", {"stages": 4}),
    (125, "mirror", "വിധിനിഷേധം", {"mode": 2}),
    (134, "flow", "മറവുതെളിവ്", {"stages": 3}),
    (140, "ladder", "ഇച്ഛാജ്ഞാനക്രിയ", {"steps": 3}),
    (150, "flow", "അറിവുക്രിയ", {"stages": 4}),
    (156, "flow", "സർവശക്തിമയം", {"stages": 3}),
    (161, "ladder", "മോക്ഷോപായം", {"steps": 4}),
    (167, "ladder", "സമാവേശത്രയം", {"steps": 3}),
    (171, "flow", "ശാംഭവം", {"stages": 5}),
    (202, "wheel", "ദേവീശക്തി", {"n": 12}),
    (211, "ladder", "ശാക്തം", {"steps": 3}),
    (214, "ladder", "ശാക്താണവം", {"steps": 3}),
    (219, "ladder", "ആണവം", {"steps": 3}),
    (226, "chain", "ഫലം", {"links": 5}),
    (232, "chain", "ഗുരുപരമ്പര", {"links": 5}),
    (239, "chain", "മലനീക്കം", {"links": 5}),
    (247, "flow", "സംശയനിശ്ചയം", {"stages": 4}),
    (274, "chain", "സംബന്ധം", {"links": 5}),
    (279, "flow", "മുൻപറച്ചിൽ", {"stages": 4}),
    (288, "ladder", "വിസ്തൃതനിർദ്ദേശം", {"steps": 6}),
    (331, "motif", "സമാപനം", {"seed": 2}),
]


def render_fam(fam, v, kw):
    if fam == "motif":
        return motif(seed=kw.get("seed", 0) + v)
    if fam == "triad":
        return triad(h=(v - 1) % 3)
    if fam == "wheel":
        n = kw.get("n", 12)
        return wheel(n=n, h=(v - 1) % n)
    if fam == "ladder":
        st = kw.get("steps", 3)
        return ladder(steps=st, pos=(v - 1) % st)
    if fam == "flow":
        st = kw.get("stages", 4)
        return flow(stages=st, pos=(v - 1) % st)
    if fam == "mirror":
        return mirror(mode=kw.get("mode", 0) + (v % 2))
    if fam == "chain":
        lk = kw.get("links", 5)
        return chain(links=lk, pos=(v - 1) % lk)
    if fam == "sound":
        return sound(pos=(v - 1) % 12)
    return motif(seed=v)


def main():
    os.makedirs(OUT, exist_ok=True)
    for v, fam, sec, kw in CURATED:
        im = render_fam(fam, v, kw)
        im.save(os.path.join(OUT, "fig_V%03d.png" % v))
    # Appendix 1: twelve sound-levels ascent (uses sound grammar)
    sound(pos=11).save(os.path.join(OUT, "fig_APP1.png"))
    print("wrote", len(CURATED) + 1, "curated v02 figs to", OUT)


if __name__ == "__main__":
    main()
