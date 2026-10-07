#!/usr/bin/env python3
"""Render one PIL figure per Tantraloka Ch.1 root verse (334 figs, code-drawn).

Families: motif/triad/wheel/ladder/flow/mirror/chain/sound.
Output: assets/figs/fig_V{nnn}.png (1600x1000, 300dpi-ish line art) + assets/captions.json
Palette matches mula boxes: cream #FFF8E1, gold #B8860B, maroon #4A140C.
Inside figures: Malayalam numerals only (no conjunct text; shaping-safe).
"""
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

BASE = "/root/tantraloka_ml"
OUT = os.path.join(BASE, "assets", "figs")
CAP = os.path.join(BASE, "assets", "captions.json")

CREAM = (255, 248, 225)
GOLD = (184, 134, 11)
MAROON = (74, 20, 12)
INK = (33, 33, 33)
LITE = (255, 255, 255)
HL = (178, 34, 34)

W, H = 1600, 1000

FONT_CANDS = [
    "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Bold.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Regular.ttf",
]


def _font(sz):
    for p in FONT_CANDS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                continue
    return ImageFont.load_default()


MLD = "൦൧൨൫൬൭൮൯" if False else "൦൧൨൩൪൫൬൭൮൯"


def ml(n):
    return "".join(MLD[int(d)] for d in str(n))


def canvas():
    im = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(im)
    d.rectangle([8, 8, W - 8, H - 8], outline=GOLD, width=6)
    return im, d


def _num(d, xy, n, size=64, fill=MAROON):
    f = _font(size)
    t = ml(n)
    bb = d.textbbox((0, 0), t, font=f)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    d.text((xy[0] - w / 2, xy[1] - h / 2), t, font=f, fill=fill)


def motif(seed=0):
    im, d = canvas()
    cx, cy = W // 2, H // 2
    for i, r in enumerate(range(120, 420, 60)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=GOLD if i % 2 else MAROON, width=5)
    for k in range(12):
        a = math.radians(k * 30 + seed * 7)
        x1, y1 = cx + 120 * math.cos(a), cy + 120 * math.sin(a)
        x2, y2 = cx + 400 * math.cos(a), cy + 400 * math.sin(a)
        d.line([x1, y1, x2, y2], fill=GOLD, width=3)
    d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=MAROON)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=GOLD)
    return im


def triad(h=0):
    im, d = canvas()
    pts = [(W // 2 - 320, H // 2 + 180), (W // 2 + 320, H // 2 + 180),
           (W // 2, H // 2 - 240)]
    d.polygon(pts, outline=MAROON, width=6)
    for i, (x, y) in enumerate(pts):
        fill = HL if i == h % 3 else LITE
        d.ellipse([x - 130, y - 130, x + 130, y + 130],
                  fill=fill, outline=MAROON, width=6)
        _num(d, (x, y), i + 1, 72, LITE if i == h % 3 else MAROON)
    _num(d, (W // 2, H // 2 + 60), 0, 1)  # noop keep font warm
    cx, cy = W // 2, H // 2 - 20
    d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], fill=GOLD, outline=MAROON, width=5)
    return im


def wheel(n=12, h=0):
    im, d = canvas()
    cx, cy = W // 2, H // 2
    R = 360
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=MAROON, width=8)
    d.ellipse([cx - R + 40, cy - R + 40, cx + R - 40, cy + R - 40],
              outline=GOLD, width=3)
    for k in range(n):
        a = math.radians(k * 360.0 / n - 90)
        x, y = cx + (R - 8) * math.cos(a), cy + (R - 8) * math.sin(a)
        wdt = 10 if k == h % n else 4
        col = HL if k == h % n else MAROON
        d.line([cx, cy, x, y], fill=col, width=wdt)
        lx, ly = cx + (R + 62) * math.cos(a), cy + (R + 62) * math.sin(a)
        _num(d, (lx, ly), k + 1, 52, HL if k == h % n else MAROON)
    d.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], fill=MAROON)
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=GOLD)
    return im


def ladder(steps=3, pos=0):
    im, d = canvas()
    bw, bh, gap = 560, 110, 40
    total = steps * (bh + gap)
    y0 = (H - total) // 2 + 40
    for k in range(steps):
        y = y0 + k * (bh + gap)
        fill = HL if k == pos % steps else LITE
        d.rounded_rectangle([W // 2 - bw // 2, y, W // 2 + bw // 2, y + bh],
                            radius=24, fill=fill, outline=MAROON, width=6)
        _num(d, (W // 2, y + bh // 2), k + 1, 64,
             LITE if k == pos % steps else MAROON)
        if k < steps - 1:
            d.line([W // 2, y + bh, W // 2, y + bh + gap],
                   fill=GOLD, width=8)
            d.polygon([(W // 2 - 16, y + bh + gap - 18),
                       (W // 2 + 16, y + bh + gap - 18),
                       (W // 2, y + bh + gap)], fill=GOLD)
    return im


def flow(stages=4, pos=0):
    im, d = canvas()
    stages = max(2, min(stages, 6))
    bw, bh, gap = 220, 200, 40
    total = stages * bw + (stages - 1) * gap
    x0 = (W - total) // 2
    y = H // 2 - bh // 2
    for k in range(stages):
        x = x0 + k * (bw + gap)
        fill = HL if k == pos % stages else LITE
        d.rounded_rectangle([x, y, x + bw, y + bh], radius=28,
                            fill=fill, outline=MAROON, width=6)
        _num(d, (x + bw // 2, y + bh // 2), k + 1, 72,
             LITE if k == pos % stages else MAROON)
        if k < stages - 1:
            ax = x + bw
            d.line([ax, H // 2, ax + gap, H // 2], fill=GOLD, width=8)
            d.polygon([(ax + gap - 22, H // 2 - 16),
                       (ax + gap - 22, H // 2 + 16),
                       (ax + gap, H // 2)], fill=GOLD)
    return im


def mirror(mode=0):
    im, d = canvas()
    lw, lh = 420, 560
    y = H // 2 - lh // 2
    x1 = W // 2 - lw - 60
    x2 = W // 2 + 60
    d.rounded_rectangle([x1, y, x1 + lw, y + lh], radius=30,
                        fill=MAROON, outline=MAROON, width=6)
    d.ellipse([x1 + lw // 2 - 90, y + lh // 2 - 90,
               x1 + lw // 2 + 90, y + lh // 2 + 90],
              fill=GOLD)
    style = mode % 3
    if style == 0:
        d.rounded_rectangle([x2, y, x2 + lw, y + lh], radius=30,
                            outline=MAROON, width=6)
    elif style == 1:
        d.rounded_rectangle([x2 + 60, y + 60, x2 + lw - 60, y + lh - 60],
                            radius=30, outline=HL, width=8)
    else:
        for off in (0, 26, 52):
            d.rounded_rectangle([x2 + off, y + off, x2 + lw - off, y + lh - off],
                                radius=30, outline=MAROON if off < 52 else HL,
                                width=5)
    d.line([W // 2 - 20, y - 60, W // 2 - 20, y + lh + 60], fill=GOLD, width=6)
    for i in range(3):
        for xx in (x1 + lw + 18, x2 - 18):
            yy = y + 120 + i * 140
            d.line([xx - 34, yy, xx + 34, yy],
                   fill=GOLD, width=5)
    return im


def chain(links=5, pos=0):
    im, d = canvas()
    bw, bh, gap = 520, 96, 34
    total = links * (bh + gap)
    y0 = (H - total) // 2 + 40
    for k in range(links):
        y = y0 + k * (bh + gap)
        fill = HL if k == pos % links else LITE
        d.rounded_rectangle([W // 2 - bw // 2, y, W // 2 + bw // 2, y + bh],
                            radius=48, fill=fill, outline=MAROON, width=6)
        _num(d, (W // 2, y + bh // 2), k + 1, 56,
             LITE if k == pos % links else MAROON)
        if k < links - 1:
            d.line([W // 2 - 60, y + bh, W // 2 - 60, y + bh + gap],
                   fill=GOLD, width=6)
            d.line([W // 2 + 60, y + bh, W // 2 + 60, y + bh + gap],
                   fill=GOLD, width=6)
    return im


def sound(pos=0):
    im, d = canvas()
    n = 12
    bw, bh, gap = 900, 40, 26
    total = n * (bh + gap)
    y0 = (H - total) // 2 + 20
    for k in range(n):
        y = y0 + k * (bh + gap)
        wdt = bw - k * 38
        x0 = (W - wdt) // 2
        fill = HL if k == pos % n else GOLD
        d.rounded_rectangle([x0, y, x0 + wdt, y + bh], radius=20,
                            fill=fill if k == pos % n else None,
                            outline=MAROON, width=4)
        _num(d, (x0 - 60, y + bh // 2), k + 1, 40, MAROON)
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

# verse -> (family, section-short-Malayalam, kwargs)
VMAP = {}


def _rng(a, b, fam, sec, **kw):
    for v in range(a, b + 1):
        if v == 246:
            continue
        VMAP[v] = (fam, sec, dict(kw))


def build_map():
    _rng(1, 1, "motif", "മംഗളം", seed=1)
    _rng(2, 6, "triad", "ദേവീസ്തുതി")
    _rng(7, 13, "chain", "ഗുരുസ്തുതി", links=5)
    _rng(14, 21, "flow", "ഗ്രന്ഥോദ്ദേശ്യം", stages=4)
    _rng(22, 35, "mirror", "സ്വാതന്ത്ര്യം", mode=0)
    _rng(36, 38, "triad", "അറിയുന്നവൻ")
    _rng(39, 51, "flow", "നിർവചനം", stages=4)
    _rng(52, 59, "mirror", "സ്വതഃസിദ്ധി", mode=1)
    _rng(60, 66, "wheel", "സർവവ്യാപി", n=6)
    _rng(67, 80, "wheel", "സ്വാതന്ത്ര്യശക്തി", n=8)
    _rng(81, 85, "wheel", "സമൂഹധർമ്മം", n=5)
    _rng(86, 89, "flow", "രാമസ്ഥത്വം", stages=3)
    _rng(90, 93, "ladder", "ഭേദം", steps=3)
    _rng(94, 105, "triad", "നാമനിർവചനം")
    _rng(106, 115, "wheel", "ദ്വാദശീസംഘം", n=12)
    _rng(116, 124, "flow", "കല്പനാശക്തി", stages=4)
    _rng(125, 133, "mirror", "വിധിനിഷേധം", mode=2)
    _rng(134, 139, "flow", "മറവുതെളിവ്", stages=3)
    _rng(140, 149, "ladder", "ഇച്ഛാജ്ഞാനക്രിയ", steps=3)
    _rng(150, 160, "flow", "അറിവുക്രിയ", stages=4)
    _rng(161, 170, "ladder", "മോക്ഷോപായം", steps=4)
    _rng(171, 197, "flow", "ശാംഭവം", stages=5)
    _rng(198, 210, "wheel", "ദേവീശക്തി", n=12)
    _rng(211, 225, "ladder", "ശാക്താണവം", steps=3)
    _rng(226, 245, "chain", "ഫലഗുരുമലം", links=5)
    _rng(247, 273, "flow", "സംശയനിശ്ചയം", stages=4)
    _rng(274, 278, "chain", "സംബന്ധം", links=5)
    _rng(279, 287, "flow", "മുൻപറച്ചിൽ", stages=4)
    _rng(288, 330, "ladder", "വിസ്തൃതനിർദ്ദേശം", steps=6)
    _rng(331, 335, "motif", "സമാപനം", seed=2)


def render_one(v):
    fam, sec, kw = VMAP[v]
    idx = {"motif": 0, "triad": 1, "wheel": 2, "ladder": 3, "flow": 4,
           "mirror": 5, "chain": 6, "sound": 7}[fam]
    if fam == "motif":
        im = motif(seed=kw.get("seed", 0) + v)
    elif fam == "triad":
        im = triad(h=(v - 1) % 3)
    elif fam == "wheel":
        n = kw.get("n", 12)
        im = wheel(n=n, h=(v - 1) % n)
    elif fam == "ladder":
        st = kw.get("steps", 3)
        im = ladder(steps=st, pos=(v - 1) % st)
    elif fam == "flow":
        st = kw.get("stages", 4)
        im = flow(stages=st, pos=(v - 1) % st)
    elif fam == "mirror":
        im = mirror(mode=kw.get("mode", 0) + (v % 2))
    elif fam == "chain":
        lk = kw.get("links", 5)
        im = chain(links=lk, pos=(v - 1) % lk)
    elif fam == "sound":
        im = sound(pos=(v - 1) % 12)
    else:
        im = motif(seed=v)
    cap = "ചിത്രം %s — %s · %s" % (ml(v), sec, FAM_ML[fam])
    return im, cap, idx


def main():
    build_map()
    os.makedirs(OUT, exist_ok=True)
    caps = {}
    verses = [v for v in range(1, 336) if v != 246]
    print("verses:", len(verses))
    for v in verses:
        im, cap, _ = render_one(v)
        im.save(os.path.join(OUT, "fig_V%03d.png" % v))
        caps[str(v)] = cap
    with open(CAP, "w", encoding="utf-8") as f:
        json.dump(caps, f, ensure_ascii=False, indent=1)
    print("wrote", len(verses), "figs to", OUT)


if __name__ == "__main__":
    main()
