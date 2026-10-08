#!/usr/bin/env python3
"""v03 figure system — enriched, label-bearing plates at 2x resolution.

Design decisions (see PUBLISHER_FORENSIC_AUDIT_V3 P2-5/P2-6):
- Same 8 geometric families/positions as v02 (visual continuity), rendered
  at 2800x1800 (~480 dpi at print size) with refined hairlines.
- RETIRED the per-verse rotating highlight (decorative, non-semantic).
  Plates are stable reference diagrams; emphasis is structural only.
- IAST/ASCII node labels ONLY where the commentary gives exact
  enumerations (icchā-jñāna-kriyā; upāya triad; pramātṛ triad;
  Bhairava/deva/pati; parā triad; pañca-kṛtya; 12 sound levels).
  All other plates stay unlabeled (captions + commentary carry meaning;
  cf. spec §21 against false flowcharts).
- Latin-script labels use Noto Serif (no complex shaping involved).
Outputs: assets/figs_v03/fig_F{NN}.png (sequential Figure numbers) +
  fig_ARCH.png (chapter architecture) + fig_APP1.png; also emits the
  data block consumed by VISUAL_MANIFEST_V3.json.
"""
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

BASE = "/root/tantraloka_ml"
OUT = os.path.join(BASE, "assets", "figs_v03")
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


def _label(d, xy, text, size=110, anchor="mm"):
    f = font(size)
    d.text(xy, text, font=f, fill=LABEL, anchor=anchor)


def motif(seed=0):
    im, d = canvas()
    cx, cy = W // 2, H // 2
    for i, r in enumerate(range(100 * S, 340 * S, 60 * S)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=GOLD if i % 2 else MAROON,
                  width=4 * S if i % 2 == 0 else 2 * S)
    for k in range(12):
        a = math.radians(k * 30 + seed * 7)
        x1, y1 = cx + 100 * S * math.cos(a), cy + 100 * S * math.sin(a)
        x2, y2 = cx + 320 * S * math.cos(a), cy + 320 * S * math.sin(a)
        d.line([x1, y1, x2, y2], fill=GOLD, width=2 * S)
    d.ellipse([cx - 34 * S, cy - 34 * S, cx + 34 * S, cy + 34 * S],
              fill=MAROON)
    d.ellipse([cx - 12 * S, cy - 12 * S, cx + 12 * S, cy + 12 * S],
              fill=(196, 158, 80))
    return im


def triad(labels=None):
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
    if labels:
        # order: bottom-left, bottom-right, top
        for (x, y), lab in zip(pts, labels):
            _label(d, (x, y), lab)
    return im


def wheel(n=12, numbered=False):
    im, d = canvas()
    cx, cy = W // 2, H // 2
    R = 300 * S
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=MAROON, width=4 * S)
    d.ellipse([cx - R + 34 * S, cy - R + 34 * S, cx + R - 34 * S,
               cy + R - 34 * S], outline=GOLD, width=2 * S)
    for k in range(n):
        a = math.radians(k * 360.0 / n - 90)
        x, y = cx + (R - 6 * S) * math.cos(a), cy + (R - 6 * S) * math.sin(a)
        d.line([cx, cy, x, y], fill=SLATE, width=2 * S)
    d.ellipse([cx - 50 * S, cy - 50 * S, cx + 50 * S, cy + 50 * S],
              fill=MAROON)
    d.ellipse([cx - 18 * S, cy - 18 * S, cx + 18 * S, cy + 18 * S],
              fill=(196, 158, 80))
    if numbered:
        for k in range(n):
            a = math.radians(k * 360.0 / n - 90)
            mx = cx + (R - 78 * S) * math.cos(a)
            my = cy + (R - 78 * S) * math.sin(a)
            _label(d, (mx, my), str(k + 1), size=96)
    return im


def wheel_labeled(n, labels):
    im, d = canvas()
    cx, cy = W // 2, H // 2
    R = 300 * S
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=MAROON, width=4 * S)
    d.ellipse([cx - R + 34 * S, cy - R + 34 * S, cx + R - 34 * S,
               cy + R - 34 * S], outline=GOLD, width=2 * S)
    for k in range(n):
        a = math.radians(k * 360.0 / n - 90)
        x, y = cx + (R - 6 * S) * math.cos(a), cy + (R - 6 * S) * math.sin(a)
        d.line([cx, cy, x, y], fill=SLATE, width=2 * S)
        la = a + math.pi / n  # labels sit between spokes, not on them
        mx = cx + (R - 96 * S) * math.cos(la)
        my = cy + (R - 96 * S) * math.sin(la)
        _label(d, (mx, my), labels[k % len(labels)], size=92)
    d.ellipse([cx - 50 * S, cy - 50 * S, cx + 50 * S, cy + 50 * S],
              fill=MAROON)
    d.ellipse([cx - 18 * S, cy - 18 * S, cx + 18 * S, cy + 18 * S],
              fill=(196, 158, 80))
    return im


def ladder(steps=3, labels=None):
    im, d = canvas()
    bw, bh, gap = 460 * S, 92 * S, 30 * S
    total = steps * (bh + gap)
    y0 = (H - total) // 2 + 30 * S
    for k in range(steps):
        y = y0 + k * (bh + gap)
        d.rounded_rectangle([W // 2 - bw // 2, y, W // 2 + bw // 2, y + bh],
                            radius=20 * S, fill=WHITE, outline=MAROON,
                            width=4 * S)
        if labels and k < len(labels):
            _label(d, (W // 2, y + bh // 2), labels[k])
        if k < steps - 1:
            d.line([W // 2, y + bh, W // 2, y + bh + gap], fill=GOLD,
                   width=4 * S)
            d.polygon([(W // 2 - 12 * S, y + bh + gap - 14 * S),
                       (W // 2 + 12 * S, y + bh + gap - 14 * S),
                       (W // 2, y + bh + gap)], fill=GOLD)
    return im


def flow(stages=4, labels=None):
    im, d = canvas()
    stages = max(2, min(stages, 6))
    bw, bh, gap = 180 * S, 170 * S, 32 * S
    total = stages * bw + (stages - 1) * gap
    x0 = (W - total) // 2
    y = H // 2 - bh // 2
    for k in range(stages):
        x = x0 + k * (bw + gap)
        d.rounded_rectangle([x, y, x + bw, y + bh], radius=22 * S,
                            fill=WHITE, outline=MAROON, width=4 * S)
        if labels and k < len(labels):
            _label(d, (x + bw // 2, y + bh // 2), labels[k], size=104)
        if k < stages - 1:
            ax = x + bw
            d.line([ax, H // 2, ax + gap, H // 2], fill=GOLD, width=4 * S)
            d.polygon([(ax + gap - 16 * S, H // 2 - 12 * S),
                       (ax + gap - 16 * S, H // 2 + 12 * S),
                       (ax + gap, H // 2)], fill=GOLD)
    return im


def mirror():
    im, d = canvas()
    lw, lh = 340 * S, 460 * S
    y = H // 2 - lh // 2
    x1 = W // 2 - lw - 50 * S
    x2 = W // 2 + 50 * S
    d.rounded_rectangle([x1, y, x1 + lw, y + lh], radius=26 * S,
                        fill=MAROON, outline=MAROON, width=4 * S)
    d.ellipse([x1 + lw // 2 - 72 * S, y + lh // 2 - 72 * S,
               x1 + lw // 2 + 72 * S, y + lh // 2 + 72 * S], fill=GOLD)
    d.rounded_rectangle([x2, y, x2 + lw, y + lh], radius=26 * S,
                        outline=MAROON, width=4 * S)
    d.line([W // 2 - 16 * S, y - 50 * S, W // 2 - 16 * S, y + lh + 50 * S],
           fill=GOLD, width=3 * S)
    return im


def chain(links=5):
    im, d = canvas()
    bw, bh, gap = 420 * S, 80 * S, 28 * S
    total = links * (bh + gap)
    y0 = (H - total) // 2 + 30 * S
    for k in range(links):
        y = y0 + k * (bh + gap)
        d.rounded_rectangle([W // 2 - bw // 2, y, W // 2 + bw // 2, y + bh],
                            radius=40 * S, fill=WHITE, outline=MAROON,
                            width=4 * S)
        if k < links - 1:
            d.line([W // 2 - 50 * S, y + bh, W // 2 - 50 * S, y + bh + gap],
                   fill=GOLD, width=3 * S)
            d.line([W // 2 + 50 * S, y + bh, W // 2 + 50 * S, y + bh + gap],
                   fill=GOLD, width=3 * S)
    return im


SOUND_LEVELS = ["akāra", "ukāra", "makāra", "bindu", "ardhacandra",
                "nirodhinī", "nāda", "nādānta", "vyāpinī", "śakti",
                "samanā", "unmanā"]


def sound():
    im, d = canvas()
    n = 12
    bw, bh, gap = 640 * S, 34 * S, 22 * S
    total = n * (bh + gap)
    y0 = (H - total) // 2 + 16 * S
    f = font(96)
    for k in range(n):
        y = y0 + k * (bh + gap)
        wdt = bw - k * 26 * S
        x0 = (W - wdt) // 2 - 120 * S
        d.rounded_rectangle([x0, y, x0 + wdt, y + bh], radius=16 * S,
                            fill=None, outline=MAROON, width=3 * S)
        d.text((x0 + wdt + 24 * S, y + bh // 2), SOUND_LEVELS[k], font=f,
               fill=LABEL, anchor="lm")
    return im


def architecture():
    """Chapter One structural overview: 5 sections + 2 appendices."""
    im, d = canvas()
    boxes = [("01", "1-21"), ("02", "22-105"), ("03", "106-139"),
             ("04", "140-245"), ("05", "247-335"), ("A1", "sound"),
             ("A2", "dvadasanta")]
    bw, bh, gap = 230 * S, 170 * S, 30 * S
    total = 5 * bw + 4 * gap
    x0 = (W - total) // 2
    y = H // 2 - bh - 60 * S
    f1, f2 = font(120), font(88)
    for k in range(5):
        x = x0 + k * (bw + gap)
        d.rounded_rectangle([x, y, x + bw, y + bh], radius=20 * S,
                            fill=WHITE, outline=MAROON, width=4 * S)
        d.text((x + bw // 2, y + bh // 2 - 52 * S), boxes[k][0], font=f1,
               fill=LABEL, anchor="mm")
        d.text((x + bw // 2, y + bh // 2 + 62 * S), boxes[k][1], font=f2,
               fill=SLATE, anchor="mm")
        if k < 4:
            ax = x + bw
            d.line([ax, y + bh // 2, ax + gap, y + bh // 2], fill=GOLD,
                   width=4 * S)
    # appendix row
    bw2, gap2 = 380 * S, 60 * S
    x0b = (W - (2 * bw2 + gap2)) // 2
    y2 = y + bh + 110 * S
    f3 = font(80)
    for k in range(5, 7):
        x = x0b + (k - 5) * (bw2 + gap2)
        d.rounded_rectangle([x, y2, x + bw2, y2 + 130 * S], radius=20 * S,
                            fill=WHITE, outline=SLATE, width=3 * S)
        d.text((x + bw2 // 2, y2 + 65 * S),
               boxes[k][0] + " · " + boxes[k][1], font=f3, fill=LABEL,
               anchor="mm")
    return im


# verse -> (family, section-ml, family-ml, range, kwargs)
FIGS = [
    (1, "motif", "മംഗളം", "അലങ്കാരം", "1", {}),
    (2, "triad", "ദേവീസ്തുതി", "ത്രിതയം", "2–6",
     {"labels": ["parāparā", "aparā", "parā"]}),
    (7, "chain", "ഗുരുസ്തുതി", "പരമ്പര", "7–13", {"links": 5}),
    (14, "flow", "ഗ്രന്ഥോദ്ദേശ്യം", "പ്രവാഹം", "14–21", {"stages": 4}),
    (22, "mirror", "സ്വാതന്ത്ര്യം", "ദർപ്പണം", "22–35", {}),
    (36, "triad", "അറിയുന്നവൻ", "ത്രിതയം", "36–38",
     {"labels": ["pramāṇa", "prameya", "pramātṛ"]}),
    (39, "flow", "നിർവചനം", "പ്രവാഹം", "39–51", {"stages": 4}),
    (52, "mirror", "സ്വതഃസിദ്ധി", "ദർപ്പണം", "52–59", {}),
    (60, "wheel", "സർവവ്യാപി", "ചക്രം", "59–66", {"n": 6}),
    (67, "wheel", "സ്വാതന്ത്ര്യശക്തി", "ചക്രം", "66–80", {"n": 8}),
    (81, "wheel_labeled", "സമൂഹധർമ്മം", "ചക്രം", "81–85",
     {"n": 5, "labels": ["sṛṣṭi", "sthiti", "saṃhāra", "tirodhāna",
                         "anugraha"]}),
    (90, "ladder", "ഭേദം", "സോപാനം", "90–93",
     {"steps": 3, "labels": ["āṇava", "māyīya", "kārma"]}),
    (94, "triad", "നാമനിർവചനം", "ത്രിതയം", "94–105",
     {"labels": ["deva", "pati", "Bhairava"]}),
    (106, "wheel", "ദ്വാദശീസംഘം", "ചക്രം", "106–115",
     {"n": 12, "numbered": False}),
    (116, "flow", "കല്പനാശക്തി", "പ്രവാഹം", "116–122", {"stages": 4}),
    (125, "mirror", "വിധിനിഷേധം", "ദർപ്പണം", "125–133", {}),
    (134, "flow", "മറവുതെളിവ്", "പ്രവാഹം", "134–139", {"stages": 3}),
    (140, "ladder", "ഇച്ഛാജ്ഞാനക്രിയ", "സോപാനം", "140–149",
     {"steps": 3, "labels": ["icchā", "jñāna", "kriyā"]}),
    (150, "flow", "അറിവുക്രിയ", "പ്രവാഹം", "150–155", {"stages": 4}),
    (156, "flow", "സർവശക്തിമയം", "പ്രവാഹം", "156–160", {"stages": 3}),
    (161, "ladder", "മോക്ഷോപായം", "സോപാനം", "161–166", {"steps": 4}),
    (167, "ladder", "സമാവേശത്രയം", "സോപാനം", "167–170",
     {"steps": 3, "labels": ["śāmbhava", "śākta", "āṇava"]}),
    (171, "flow", "ശാംഭവം", "പ്രവാഹം", "171–196", {"stages": 5}),
    (202, "wheel", "ദേവീശക്തി", "ചക്രം", "202–210",
     {"n": 12, "numbered": False}),
    (211, "ladder", "ശാക്തം", "സോപാനം", "211–213",
     {"steps": 3, "labels": ["śāmbhava", "śākta", "āṇava"]}),
    (214, "ladder", "ശാക്താണവം", "സോപാനം", "214–218",
     {"steps": 3, "labels": ["śāmbhava", "śākta", "āṇava"]}),
    (219, "ladder", "ആണവം", "സോപാനം", "219–225",
     {"steps": 3, "labels": ["śāmbhava", "śākta", "āṇava"]}),
    (226, "chain", "ഫലം", "പരമ്പര", "225–232", {"links": 5}),
    (232, "chain", "ഗുരുപരമ്പര", "പരമ്പര", "232–238", {"links": 5}),
    (239, "chain", "മലനീക്കം", "പരമ്പര", "239–245", {"links": 5}),
    (247, "flow", "സംശയനിശ്ചയം", "പ്രവാഹം", "247–274", {"stages": 4}),
    (274, "chain", "സംബന്ധം", "പരമ്പര", "274–279", {"links": 5}),
    (279, "flow", "മുൻപറച്ചിൽ", "പ്രവാഹം", "279–287", {"stages": 4}),
    (288, "ladder", "വിസ്തൃതനിർദ്ദേശം", "സോപാനം", "288–330",
     {"steps": 6}),
    (331, "motif", "സമാപനം", "അലങ്കാരം", "331–335", {"seed": 2}),
]

PURPOSES = {
    1: "Mangala plate: the Heart (hṛdaya) as union of Śiva–Śakti; sets the invocatory frame.",
    2: "The goddess triad praised in vv2–6: parā, parāparā, aparā as one reality in three aspects.",
    7: "Guru-paramparā: lineage continuity from Macchanda through Triyambaka teachers.",
    14: "Fourfold movement of the book's purpose: need, source, fitness, fruition.",
    22: "Freedom/bondage as reflexive relation: consciousness facing its own contraction.",
    36: "Knower, means-of-knowing, known: pramātṛ–pramāṇa–prameya triad.",
    39: "Progressive definitions of knowledge/ignorance across four stages.",
    52: "Self-established Śiva-consciousness mirrored against its apparent absence.",
    60: "Ubiquity: sixfold pervasion of the one awareness.",
    67: "Eightfold deployment of the powers of freedom.",
    81: "The five acts (pañca-kṛtya) as the group's innate nature.",
    90: "Threefold obscuration: āṇava, māyīya, kārma malas as rungs.",
    94: "Etymological triad: Bhairava, deva, pati as one named reality.",
    106: "Assembly of twelve goddesses around Bhairava.",
    116: "Nourishing imagination (pratibhā) unfolding in four movements.",
    125: "Injunctions mirrored against the unbound supreme deity.",
    134: "Obscured vs unobscured consciousness in three phases.",
    140: "Will, knowledge, action as the three rungs of means-analysis.",
    150: "Knowledge extending into action and ripening into yoga.",
    156: "Śiva as all powers in three comprehensive movements.",
    161: "One liberation, four graded approaches.",
    167: "The three penetrations: śāmbhava, śākta, āṇava.",
    171: "Śāmbhava absorption across five expositions.",
    202: "The goddess's twelvefold power-wheel.",
    211: "Thought-free śāmbhava path within the three means.",
    214: "Empowered (śākta) means among the three.",
    219: "Individual (āṇava) means among the three.",
    226: "Many means converging on one fruit.",
    232: "Teacher and spiritual family as a living chain.",
    239: "Removal of impurity through the chain of four knowledges.",
    247: "Enunciation, definition, investigation in four movements.",
    274: "The supreme and secondary relations as a chain.",
    279: "Preliminary topic-list in four movements.",
    288: "Detailed topic-list as a six-rung ascent.",
    331: "Closing plate: return to the invocatory wholeness.",
}


def render_fam(fam, kw):
    if fam == "motif":
        return motif(seed=kw.get("seed", 0))
    if fam == "triad":
        return triad(labels=kw.get("labels"))
    if fam == "wheel":
        return wheel(n=kw.get("n", 12), numbered=kw.get("numbered", False))
    if fam == "wheel_labeled":
        return wheel_labeled(kw.get("n", 5), kw.get("labels", []))
    if fam == "ladder":
        return ladder(steps=kw.get("steps", 3), labels=kw.get("labels"))
    if fam == "flow":
        return flow(stages=kw.get("stages", 4), labels=kw.get("labels"))
    if fam == "mirror":
        return mirror()
    if fam == "chain":
        return chain(links=kw.get("links", 5))
    return motif()


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    for idx, (v, fam, sec, famml, rng, kw) in enumerate(FIGS, start=1):
        im = render_fam(fam, kw)
        fn = "fig_F%02d.png" % idx
        im.save(os.path.join(OUT, fn))
        labels = kw.get("labels")
        manifest.append({
            "visual_id": "FIG-%02d" % idx,
            "chapter": "Chapter One",
            "section": sec,
            "verse": v,
            "verse_range": rng,
            "source_basis": "TA 1.%s; TAv (Jayaratha)" % rng.replace("–", "-"),
            "purpose": PURPOSES[v],
            "visual_type": fam,
            "caption": "Figure %d — %s · %s / Based on verses %s"
                       % (idx, sec, famml, rng),
            "interpretive_notes":
                ("Node labels name the commentary's own enumeration; "
                 "no rotating highlight — stable reference plate."
                 if labels else
                 "Abstract plate; meaning carried by caption + adjacent "
                 "commentary. No per-verse highlight (retired v02 device)."),
            "asset_path": "assets/figs_v03/" + fn,
            "disposition": "REDESIGNED" if labels else "KEPT",
        })
    sound().save(os.path.join(OUT, "fig_APP1.png"))
    manifest.append({
        "visual_id": "FIG-36",
        "chapter": "Appendix 1",
        "section": "ശബ്ദതലങ്ങൾ",
        "verse": None,
        "verse_range": "12 levels",
        "source_basis": "Netratantra via TAv; oṅkāra ascent hṛdaya→dvādaśānta",
        "purpose": "Twelve sound-levels as a labeled ascent ladder.",
        "visual_type": "sound",
        "caption": "Figure 36 — Twelve sound-levels · ascent / "
                   "Based on Appendix 1",
        "interpretive_notes": "All twelve levels labeled in IAST in textual order.",
        "asset_path": "assets/figs_v03/fig_APP1.png",
        "disposition": "REDESIGNED",
    })
    architecture().save(os.path.join(OUT, "fig_ARCH.png"))
    manifest.append({
        "visual_id": "FIG-ARCH",
        "chapter": "Frontmatter overview",
        "section": "Chapter architecture",
        "verse": None,
        "verse_range": "1–335",
        "source_basis": "Chapter contents (Dyczkowski) + translated overview",
        "purpose": "Structural map: five sections + two appendices.",
        "visual_type": "architecture",
        "caption": "Chapter One — section architecture · structural overview",
        "interpretive_notes": "Structural only; no doctrinal linearization.",
        "asset_path": "assets/figs_v03/fig_ARCH.png",
        "disposition": "NEW",
    })
    with open(os.path.join(BASE, "VISUAL_MANIFEST_V3.json"), "w",
              encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print("wrote", len(manifest), "plates + manifest")


if __name__ == "__main__":
    main()
