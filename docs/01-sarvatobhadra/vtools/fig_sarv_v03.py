#!/usr/bin/env python3
"""Sarvatobhadra v03 plates — labeled, source-traceable, 2800px (~480 dpi).

Every plate is anchored to a verse group whose commentary gives the exact
enumeration shown; labels are IAST/ASCII (Noto Serif — no complex shaping).
No rotating highlight; stable reference plates. See manifest.
"""
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

BASE = "/root/sarvatobhadra_ml"
OUT = os.path.join(BASE, "assets_sarv_v03")
FONT = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"

IVORY = (255, 251, 240)
GOLD = (166, 124, 46)
MAROON = (90, 26, 16)
SLATE = (46, 64, 87)
LABEL = (74, 20, 12)
WHITE = (255, 255, 255)

S = 2
W, H = 1400 * S, 900 * S


def font(px):
    return ImageFont.truetype(FONT, px)


def canvas():
    im = Image.new("RGB", (W, H), IVORY)
    d = ImageDraw.Draw(im)
    d.rectangle([6 * S, 6 * S, W - 6 * S, H - 6 * S], outline=GOLD,
                width=3 * S)
    d.rectangle([16 * S, 16 * S, W - 16 * S, H - 16 * S], outline=GOLD,
                width=1 * S)
    return im, d


def _label(d, xy, text, size=110, anchor="mm", fill=None):
    d.text(xy, text, font=font(size), fill=fill or LABEL, anchor=anchor)


def triad(labels):
    im, d = canvas()
    pts = [(W // 2 - 320 * S, H // 2 + 150 * S),
           (W // 2 + 320 * S, H // 2 + 150 * S),
           (W // 2, H // 2 - 210 * S)]
    d.polygon(pts, outline=MAROON, width=4 * S)
    for (x, y) in pts:
        d.ellipse([x - 140 * S, y - 140 * S, x + 140 * S, y + 140 * S],
                  fill=WHITE, outline=MAROON, width=4 * S)
    cx, cy = W // 2, H // 2 - 15 * S
    d.ellipse([cx - 58 * S, cy - 58 * S, cx + 58 * S, cy + 58 * S],
              fill=GOLD, outline=MAROON, width=4 * S)
    for (x, y), lab in zip(pts, labels):
        _label(d, (x, y), lab)
    return im


def mirror(left, right):
    im, d = canvas()
    lw, lh = 340 * S, 460 * S
    y = H // 2 - lh // 2
    x1 = W // 2 - lw - 50 * S
    x2 = W // 2 + 50 * S
    d.rounded_rectangle([x1, y, x1 + lw, y + lh], radius=26 * S,
                        fill=MAROON, outline=MAROON, width=4 * S)
    _label(d, (x1 + lw // 2, y + lh // 2), left, size=110,
           fill=(255, 251, 240))
    # gold disc behind left label for contrast
    d.rounded_rectangle([x2, y, x2 + lw, y + lh], radius=26 * S,
                        outline=MAROON, width=4 * S)
    _label(d, (x2 + lw // 2, y + lh // 2), right, size=110)
    d.line([W // 2 - 16 * S, y - 50 * S, W // 2 - 16 * S, y + lh + 50 * S],
           fill=GOLD, width=3 * S)
    return im


def wheel4(labels):
    im, d = canvas()
    cx, cy = W // 2, H // 2
    R = 300 * S
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=MAROON, width=4 * S)
    d.ellipse([cx - R + 34 * S, cy - R + 34 * S, cx + R - 34 * S,
               cy + R - 34 * S], outline=GOLD, width=2 * S)
    for k in range(4):
        a = math.radians(k * 90 - 90)
        x, y = cx + (R - 6 * S) * math.cos(a), cy + (R - 6 * S) * math.sin(a)
        d.line([cx, cy, x, y], fill=SLATE, width=2 * S)
        la = a + math.pi / 4
        mx = cx + (R - 100 * S) * math.cos(la)
        my = cy + (R - 100 * S) * math.sin(la)
        _label(d, (mx, my), labels[k], size=96)
    d.ellipse([cx - 50 * S, cy - 50 * S, cx + 50 * S, cy + 50 * S],
              fill=MAROON)
    d.ellipse([cx - 18 * S, cy - 18 * S, cx + 18 * S, cy + 18 * S],
              fill=(196, 158, 80))
    return im


def emblem(size=1600):
    """Cover emblem: 18-spoke wheel for 18 chapters + bindu."""
    im = Image.new("RGB", (size, size), IVORY)
    d = ImageDraw.Draw(im)
    cx = cy = size // 2
    for i, r in enumerate((200, 340, 480, 620)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=GOLD if i % 2 else MAROON, width=6 if i % 2 == 0 else 3)
    for k in range(18):
        a = math.radians(k * 20 - 90)
        x1, y1 = cx + 340 * math.cos(a), cy + 340 * math.sin(a)
        x2, y2 = cx + 620 * math.cos(a), cy + 620 * math.sin(a)
        d.line([x1, y1, x2, y2], fill=MAROON, width=5)
        mx, my = cx + 480 * math.cos(a), cy + 480 * math.sin(a)
        d.ellipse([mx - 13, my - 13, mx + 13, my + 13], fill=GOLD)
    d.ellipse([cx - 66, cy - 66, cx + 66, cy + 66], fill=MAROON)
    d.ellipse([cx - 66, cy - 66, cx + 66, cy + 66], outline=GOLD, width=4)
    d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], fill=(196, 158, 80))
    m = 64
    for (qx, qy) in ((m, m), (size - m, m), (m, size - m), (size - m, size - m)):
        d.polygon([(qx, qy - 26), (qx + 26, qy), (qx, qy + 26), (qx - 26, qy)],
                  outline=MAROON, width=4)
        d.ellipse([qx - 7, qy - 7, qx + 7, qy + 7], fill=GOLD)
    return im


def architecture():
    im, d = canvas()
    chs = [(1, "1-47"), (2, "1-74"), (3, "1-48"), (4, "1-42"), (5, "1-28"),
           (6, "1-49")]
    chs2 = [(7, "1-30"), (8, "1-28"), (9, "1-35"), (10, "1-42"),
            (11, "1-60"), (12, "1-20")]
    chs3 = [(13, "1-34"), (14, "1-27"), (15, "1-20"), (16, "1-24"),
            (17, "1-28"), (18, "1-79")]
    f1, f2 = font(92), font(64)
    bw, bh, gap = 200 * S, 130 * S, 24 * S
    for row, y in ((chs, 150 * S), (chs2, 420 * S), (chs3, 690 * S)):
        total = 6 * bw + 5 * gap
        x0 = (W - total) // 2
        for k, (c, rng) in enumerate(row):
            x = x0 + k * (bw + gap)
            d.rounded_rectangle([x, y, x + bw, y + bh], radius=16 * S,
                                fill=WHITE, outline=MAROON, width=3 * S)
            d.text((x + bw // 2, y + bh // 2 - 40 * S), "%02d" % c,
                   font=f1, fill=LABEL, anchor="mm")
            d.text((x + bw // 2, y + bh // 2 + 52 * S), rng, font=f2,
                   fill=SLATE, anchor="mm")
    return im


# (Figure No, chapter, anchor verse, ml label, family-ml, range, kind, labels)
FIGS = [
    (2, 14, 5, "ഗുണത്രയം", "ത്രിതയം", "14.5–7",
     "triad", ["rajas", "tamas", "sattva"]),
    (3, 13, 1, "ക്ഷേത്രക്ഷേത്രജ്ഞൻ", "ദർപ്പണം", "13.1–2",
     "mirror", ["kṣetra", "kṣetrajña"]),
    (4, 16, 1, "ദൈവാസുരസമ്പത്ത്", "ദർപ്പണം", "16.1–6",
     "mirror", ["daiva", "āsura"]),
    (5, 17, 2, "ശ്രദ്ധാത്രയം", "ത്രിതയം", "17.2–4",
     "triad", ["rājasī", "tāmasī", "sāttvikī"]),
    (6, 15, 16, "പുരുഷത്രയം", "ത്രിതയം", "15.16–18",
     "triad", ["kṣara", "akṣara", "puruṣottama"]),
    (7, 7, 1, "ജ്ഞാനവിജ്ഞാനം", "ദർപ്പണം", "7.1–3",
     "mirror", ["jñāna", "vijñāna"]),
    (8, 1, 1, "സംവാദകർ", "ചക്രം", "1.1",
     "wheel4", ["kṛṣṇa", "arjuna", "sañjaya", "dhṛtarāṣṭra"]),
]

PURPOSES = {
    2: "Three guṇas (ch14 vv5–7): sattva above, rajas/tamas below.",
    3: "Field and knower-of-the-field (ch13 vv1–2) as reflexive pair.",
    4: "Divine and demoniac estates (ch16 vv1–6) as contrasting pair.",
    5: "Threefold śraddhā (ch17 vv2–4): sāttvikī supreme.",
    6: "Kṣara, akṣara, puruṣottama (ch15 vv16–18): the supreme above.",
    7: "Jñāna and vijñāna (ch7 vv1–3) as knowing pair.",
    8: "The four dialogue voices framing ch1: Kṛṣṇa, Arjuna, Sañjaya, Dhṛtarāṣṭra.",
}


def main():
    os.makedirs(OUT, exist_ok=True)
    emblem(1600).save(os.path.join(OUT, "cover_emblem.png"))
    manifest = []
    for fno, ch, v, sec, famml, rng, kind, labels in FIGS:
        if kind == "triad":
            im = triad(labels)
        elif kind == "mirror":
            im = mirror(labels[0], labels[1])
        elif kind == "wheel4":
            im = wheel4(labels)
        else:
            im = triad(labels)
        fn = "fig_F%02d.png" % fno
        im.save(os.path.join(OUT, fn))
        manifest.append({
            "visual_id": "SARV-FIG-%02d" % fno,
            "chapter": ch,
            "section": sec,
            "verse": v,
            "verse_range": rng,
            "source_basis": "Gita %d + Rāmakantha ad loc.; translated_peak" % ch,
            "purpose": PURPOSES[fno],
            "visual_type": kind,
            "caption": "Figure %d — %s · %s / Based on verses %s"
                       % (fno, sec, famml, rng),
            "interpretive_notes": "Node labels name the commentary's own enumeration.",
            "asset_path": "assets_sarv_v03/" + fn,
            "disposition": "NEW",
        })
    architecture().save(os.path.join(OUT, "fig_ARCH.png"))
    manifest.append({
        "visual_id": "SARV-ARCH",
        "chapter": "Frontmatter overview",
        "section": "18-chapter architecture",
        "verse": None,
        "verse_range": "1–18",
        "source_basis": "Chapter maxima reconciled vs source.txt (Phase 2)",
        "purpose": "Structural map: 18 chapters with Kashmir-recension verse counts.",
        "visual_type": "architecture",
        "caption": "Eighteen chapters — architecture · structural overview",
        "interpretive_notes": "Structural only; counts follow the print (74, 48, 49, 35, 60, 79).",
        "asset_path": "assets_sarv_v03/fig_ARCH.png",
        "disposition": "NEW",
    })
    with open(os.path.join(BASE, "SARV_VISUAL_MANIFEST_V3.json"), "w",
              encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print("wrote", len(manifest), "plates + manifest")


if __name__ == "__main__":
    main()
