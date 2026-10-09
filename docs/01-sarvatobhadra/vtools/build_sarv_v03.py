#!/usr/bin/env python3
"""Tantraloka Malayalam Series — v02 production builder (A4 + Trade).

Implements SERIES_STYLE.md: original house style, true footnotes, curated
figures, per-chapter running heads, roman/arabic folios, two-pass TOC with
real page numbers, locked 3-family font architecture, PDF bookmarks via
heading styles + explicit anchors.

Usage:
  python3 build_v02.py --edition a4            # pass 1 (TOC without numbers)
  python3 build_v02.py --edition a4 --toc TOC.json   # pass 2 (final)
  python3 build_v02.py --edition trade [--toc ...]
Outputs (never touches v01):
  pdf/Tantraloka_Malayalam_Volume1_v02_A4.docx / _A4.pdf
  pdf/Tantraloka_Malayalam_Volume1_v02_Trade.docx / _Trade.pdf
"""
import argparse
import copy
import json
import os
import re

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = "/root/sarvatobhadra_ml"
TR = os.path.join(BASE, "translated_peak")
FIGDIR = os.path.join(BASE, "assets_sarv_v03")
# (ch, anchor-verse) -> (Figure No, ml label, family-ml, range).
# Anchors are first verses of the H2 groups whose commentary gives the
# exact enumeration shown. Manifest: SARV_VISUAL_MANIFEST_V3.json.
FIG_SARV = {
    (14, 5): (2, "ഗുണത്രയം", "ത്രിതയം", "14.5–7"),
    (13, 1): (3, "ക്ഷേത്രക്ഷേത്രജ്ഞൻ", "ദർപ്പണം", "13.1–2"),
    (16, 1): (4, "ദൈവാസുരസമ്പത്ത്", "ദർപ്പണം", "16.1–6"),
    (17, 2): (5, "ശ്രദ്ധാത്രയം", "ത്രിതയം", "17.2–4"),
    (15, 16): (6, "പുരുഷത്രയം", "ത്രിതയം", "15.16–18"),
    (7, 1): (7, "ജ്ഞാനവിജ്ഞാനം", "ദർപ്പണം", "7.1–3"),
    (1, 1): (8, "സംവാദകർ", "ചക്രം", "1.1"),
}
FIG_TRIGGER = set(FIG_SARV)
EMBLEM = os.path.join(BASE, "assets_sarv_v03", "cover_emblem.png")
CAPJSON = None
FIGCAPS = {}

# ---------------- Series design tokens (see SERIES_STYLE.md) ----------------
IVORY = RGBColor(0xFF, 0xFB, 0xF0)
GOLD = RGBColor(0xA6, 0x7C, 0x2E)
GOLD_LT = RGBColor(0xC4, 0x9E, 0x50)
MAROON = RGBColor(0x5A, 0x1A, 0x10)
MAROON_DK = RGBColor(0x4A, 0x14, 0x0C)
SLATE = RGBColor(0x2E, 0x40, 0x57)
INK = RGBColor(0x21, 0x21, 0x21)
GREY = RGBColor(0x6E, 0x6E, 0x6E)

BODY_FONT = "Noto Serif Malayalam"
HEAD_FONT = "Noto Sans Malayalam"
LATIN_FONT = "Noto Serif"          # IAST / Latin: full diacritic coverage
ARABIC_FONT = "DejaVu Sans"  # approved single-instance fallback: the
# colophon intentionally cites an Arabic-script OCR example ('من');
# DejaVu Sans carries Arabic coverage (verified). No other Arabic use.

_MLD = "൦൧൨൩൪൫൬൭൮൯"
_ML2EN = str.maketrans("൦൧൨൩൪൫൬൭൮൯", "0123456789")

# P0 render-layer script corrections (AUTHORITY_LOCK R1; each instance
# verified against source.txt; sources stay byte-identical).
# Bengali/Telugu single-char contaminations → exact Malayalam equivalents.
FIXMAP = str.maketrans({
    "\u09cd": "\u0d4d",  # Bengali hasanta → chandrakkala (നേങ്ഗതേ etc.)
    "\u0997": "\u0d17",  # Bengali ga → ga
    "\u09bf": "\u0d3f",  # Bengali i-vowel → i-vowel (സൃജാമി)
    "\u0c15": "\u0d15",  # Telugu ka → ka (കകുഭ്)
    "\u0c41": "\u0d41",  # Telugu u-vowel → u-vowel
    "\u0c3f": "\u0d3f",  # Telugu i-vowel → i-vowel (വிபക്ഷ)
    "\u0c2a": "\u0d2a",  # Telugu pa → pa
})


def NORM(s):
    """v03 numeral law + P0 script hygiene, render-layer only.
    Every Unicode decimal digit → ASCII (Malayalam, math-bold/sans,
    Devanagari alike); wrong-script clusters fixed per FIXMAP."""
    import unicodedata
    s = s.translate(FIXMAP)
    return re.sub(r"\d",
                  lambda m: str(unicodedata.digit(m.group(0))), s,
                  flags=re.UNICODE)

LATIN_RUN = re.compile(r"[A-Za-z\u0100-\u024F\u1E00-\u1EFF\u2C60-\u2C7F\u00B7\u2022\u2026]+")
# NB: U+00B7 MIDDLE DOT and U+2022 BULLET are absent from the Noto Malayalam
# fonts (verified via fontTools); routing them to Noto Serif kills fallback.


def m2i(s):
    v = 0
    for ch in s:
        if ch in _MLD:
            v = v * 10 + _MLD.index(ch)
    return v


EDITIONS = {
    "a4": dict(
        page_w=Inches(8.27), page_h=Inches(11.69),
        m_top=Inches(0.75), m_bot=Inches(0.80),
        m_left=Inches(0.90), m_right=Inches(0.90),
        body_pt=10.8, mula_pt=11.5, note_pt=8.8, cap_pt=8.5,
        fig_w=Inches(2.9), emblem_w=Inches(3.0),
        line_mult=1.42, head_pt=7.5, series_head="സർവ്വതോഭദ്രം — മലയാളവിവർത്തനം",
        measure=6.47, suffix="A4",
    ),
    "trade": dict(
        page_w=Inches(6.0), page_h=Inches(9.0),
        m_top=Inches(0.75), m_bot=Inches(0.80),
        m_left=Inches(0.75), m_right=Inches(0.70),
        body_pt=10.2, mula_pt=10.8, note_pt=8.4, cap_pt=8.0,
        fig_w=Inches(2.5), emblem_w=Inches(2.4),
        line_mult=1.40, head_pt=7.0, series_head="സർവ്വതോഭദ്രം",
        measure=4.55, suffix="Trade",
    ),
    "research": dict(
        page_w=Inches(8.27), page_h=Inches(11.69),
        m_top=Inches(0.85), m_bot=Inches(0.90),
        m_left=Inches(1.0), m_right=Inches(1.0),
        body_pt=10.5, mula_pt=11.2, note_pt=8.6, cap_pt=8.2,
        fig_w=Inches(2.9), emblem_w=Inches(3.0),
        line_mult=1.45, head_pt=7.5, series_head="സർവ്വതോഭദ്രം — ഗവേഷണപതിപ്പ്",
        measure=6.27, suffix="Research",
    ),
}

# Sarvatobhadra chapter metadata: (file, code, gita-ch, ml short, en yoga,
# print maxima). Verse spans live in file H1s; print maxima from source audit.
CHAPTERS = [
    ("frontmatter_ml.md", "FRONT", 0, "മുഖപത്രം", "Frontmatter", 0),
    ("upodghata_ml.md", "UPO", 0, "ഉപോദ്ഘാതം", "Introduction", 0),
    ("ch01_ml.md", "CH01", 1, "അർജ്ജുനവിഷാദയോഗം", "Arjunaviṣādayoga", 47),
    ("ch02a_ml.md", "CH02A", 2, "സാംഖ്യയോഗം", "Sāṅkhyayoga", 74),
    ("ch02b_ml.md", "CH02B", 2, "സാംഖ്യയോഗം", "Sāṅkhyayoga", 74),
    ("ch02c_ml.md", "CH02C", 2, "സാംഖ്യയോഗം", "Sāṅkhyayoga", 74),
    ("ch03_ml.md", "CH03", 3, "കർമ്മയോഗം", "Karmayoga", 48),
    ("ch04_ml.md", "CH04", 4, "ജ്ഞാനകർമ്മസന്ന്യാസയോഗം",
     "Jñānakarmasannyāsayoga", 42),
    ("ch05_ml.md", "CH05", 5, "കർമ്മസന്ന്യാസയോഗം", "Karmasannyāsayoga", 28),
    ("ch06_ml.md", "CH06", 6, "ധ്യാനയോഗം", "Dhyānayoga", 49),
    ("ch07_ml.md", "CH07", 7, "ജ്ഞാനവിജ്ഞാനയോഗം", "Jñānavijñānayoga", 30),
    ("ch08_ml.md", "CH08", 8, "അക്ഷരബ്രഹ്മയോഗം", "Akṣarabrahmayoga", 28),
    ("ch09_ml.md", "CH09", 9, "രാജവിദ്യാരാജഗുഹ്യയോഗം",
     "Rājavidyārājaguhyayoga", 35),
    ("ch10_ml.md", "CH10", 10, "വിഭൂതിയോഗം", "Vibhūtiyoga", 42),
    ("ch11_ml.md", "CH11", 11, "വിശ്വരൂപദർശനയോഗം", "Viśvarūpadarśanayoga",
     60),
    ("ch12_ml.md", "CH12", 12, "ഭക്തിയോഗം", "Bhaktiyoga", 20),
    ("ch13_ml.md", "CH13", 13, "ക്ഷേത്രക്ഷേത്രജ്ഞവിഭാഗയോഗം",
     "Kṣetrakṣetrajñavibhāgayoga", 34),
    ("ch14_ml.md", "CH14", 14, "ഗുണത്രയവിഭാഗയോഗം",
     "Guṇatrayavibhāgayoga", 27),
    ("ch15_ml.md", "CH15", 15, "പുരുഷോത്തമയോഗം", "Puruṣottamayoga", 20),
    ("ch16_ml.md", "CH16", 16, "ദൈവാസുരസമ്പദ്വിഭാഗയോഗം",
     "Daivāsurasampadvibhāgayoga", 24),
    ("ch17_ml.md", "CH17", 17, "ശ്രദ്ധാത്രയവിഭാഗയോഗം",
     "Śraddhātrayavibhāgayoga", 28),
    ("ch18a_ml.md", "CH18A", 18, "മോക്ഷസന്ന്യാസയോഗം", "Mokṣasannyāsayoga",
     79),
    ("ch18b_ml.md", "CH18B", 18, "മോക്ഷസന്ന്യാസയോഗം", "Mokṣasannyāsayoga",
     79),
    ("ch18c_ml.md", "CH18C", 18, "മോക്ഷസന്ന്യാസയോഗം", "Mokṣasannyāsayoga",
     79),
    ("appendix_A_shuddhipatra_ml.md", "APPA", 0, "ശുദ്ധിപത്രം",
     "Corrigenda", 0),
    ("appendix_B_pathantara_ml.md", "APPB", 0, "പാഠാന്തരങ്ങൾ",
     "Variant readings", 0),
    ("appendix_C_adhika_ml.md", "APPC", 0, "അധികശ്ലോകങ്ങൾ",
     "Additional verses", 0),
]
ORDER = CHAPTERS

# (FIGCAP + CURATED_VERSES defined near FIGDIR above)


# ---------------- low-level helpers ----------------
def set_run_font(run, family, size=None, bold=None, italic=None, color=None):
    run.font.name = family
    if size is not None:
        run.font.size = size
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    for attr in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'):
        rFonts.set(qn(attr), family)


SEGRX = re.compile(r"[A-Za-zĀ-ɏḀ-ỿⱠ-Ɀ·•…]+|[\u0600-\u06FF]+")


def segfam(seg, ml_font):
    """Font family for a segment: Latin/IAST, approved Arabic, else Malayalam."""
    c = seg[0]
    if '\u0600' <= c <= '\u06FF':
        return ARABIC_FONT
    if re.fullmatch(r"[A-Za-zĀ-ɏḀ-ỿⱠ-Ɀ·•…]+", seg):
        return LATIN_FONT
    return ml_font


def add_mixed_text(paragraph, text, ml_font, base_size=None, base_bold=False,
                   base_italic=False, color=None, latin_bold=None,
                   latin_italic=None):
    """Segment-wise font locking: Latin/IAST runs -> LATIN_FONT, Arabic
    runs -> approved ARABIC_FONT (colophon OCR example only), all else
    Malayalam family. Kills arbitrary fallback for diacritics."""
    text = NORM(text)
    pos = 0
    for m in re.compile(r"[A-Za-z\u0100-\u024F\u1E00-\u1EFF\u2C60-\u2C7F\u00B7\u2022\u2026]+|[\u0600-\u06FF]+").finditer(text):
        if m.start() > pos:
            r = paragraph.add_run(text[pos:m.start()])
            set_run_font(r, ml_font, base_size, base_bold, base_italic, color)
        fam = ARABIC_FONT if '\u0600' <= m.group(0)[0] <= '\u06FF' else LATIN_FONT
        r = paragraph.add_run(m.group(0))
        set_run_font(r, fam, base_size,
                     base_bold if latin_bold is None else latin_bold,
                     base_italic if latin_italic is None else latin_italic,
                     color)
        pos = m.end()
    if pos < len(text):
        r = paragraph.add_run(text[pos:])
        set_run_font(r, ml_font, base_size, base_bold, base_italic, color)


CITE_RE = re.compile(r'\((\d{1,3})\)')
DOTTED_RE = re.compile(r'\((\d{1,2})\.(\d{1,3})(?:[–—-](\d{1,3}))?\)')

# P0-R3: ch09 v15 mark reads 19 (print l.4713: v15). Only the सततं-verse
# marks (mula line 338 + its commentary ref 364) are corrected; ch09's
# legitimate clean 19 (प्रभवः, line 395) is untouched.
P0CH09_OLD = "നമസ്യന്തശ്ച മാം ഭക്ത്യാ നിത്യയുക്താ ഉപാസതേ ॥ ൧\U0001d7eb ॥"
P0CH09_NEW = "നമസ്യന്തശ്ച മാം ഭക്ത്യാ നിത്യയുക്താ ഉപാസതേ ॥ ൧൫ ॥"
P0CH09R_OLD = "പരിചരിക്കുന്നു എന്നർത്ഥം ॥ ൧\U0001d7eb ॥"
P0CH09R_NEW = "പരിചരിക്കുന്നു എന്നർത്ഥം ॥ ൧൫ ॥"


def apply_p0_file_fixes(fname, text):
    """Line-targeted P0 corrections with source evidence (logged, never
    silent). All other wrong-script/math digits handled generically."""
    if fname == "ch09_ml.md":
        assert text.count(P0CH09_OLD) == 1, "P0CH09 mula anchor moved"
        text = text.replace(P0CH09_OLD, P0CH09_NEW)
        assert text.count(P0CH09R_OLD) == 1, "P0CH09 ref anchor moved"
        text = text.replace(P0CH09R_OLD, P0CH09R_NEW)
    return text


def parse_glossary_terms():
    """[(ml_term, iast)] from locked GLOSSARY.md, longest-first."""
    terms = []
    for line in open(os.path.join(BASE, "GLOSSARY.md"), encoding="utf-8"):
        for m in re.finditer(r'([\u0d00-\u0d7f][\u0d00-\u0d7f\u200c\u200d\-–]*)\s*\[([^\]]+)\]', line):
            ml, ia = m.group(1).strip(), m.group(2).strip()
            if ml and ia and (ml, ia) not in terms:
                terms.append((ml, ia))
    terms.sort(key=lambda x: -len(x[0]))
    return terms


GLOSS_TERMS = parse_glossary_terms()


def iast_first_use(text, seen):
    """Append [IAST] after first whole-word use per file (locked rule).
    Skips existing [...] spans. Returns (new_text, hit_logged)."""
    out = []
    pos = 0
    # protect existing bracket spans
    spans = [(m.start(), m.end()) for m in re.finditer(r'\[[^\]\n]*\]', text)]
    def inside(p):
        return any(a <= p < b for a, b in spans)
    changed = False
    for ml, ia in GLOSS_TERMS:
        if ml in seen or ml not in text:
            continue
        m = re.search(r'(?<![\u0d00-\u0d7f\u200c\u200d])' + re.escape(ml) + r'(?![\u0d00-\u0d7f\u200c\u200d])', text)
        if m and not inside(m.start()):
            text = text[:m.end()] + " [%s]" % ia + text[m.end():]
            seen.add(ml)
            changed = True
    return text, changed


def add_cite_link(paragraph, num_text, target, size=None):
    hl = OxmlElement('w:hyperlink')
    hl.set(qn('w:anchor'), target)
    hl.set(qn('w:history'), '1')
    run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    rF = OxmlElement('w:rFonts')
    for attr in ('w:ascii', 'w:hAnsi', 'w:cs'):
        rF.set(qn(attr), LATIN_FONT)
    color = OxmlElement('w:color')
    color.set(qn('w:val'), '2E4057')
    if size is not None:
        sz = OxmlElement('w:sz')
        sz.set(qn('w:val'), str(int(size.pt * 2)))
        rPr.append(sz)
    rPr.append(rF)
    rPr.append(color)
    run.append(rPr)
    tt = OxmlElement('w:t')
    tt.set(qn('xml:space'), 'preserve')
    tt.text = num_text
    run.append(tt)
    hl.append(run)
    paragraph._p.append(hl)


def add_rich_mixed(paragraph, text, ml_font, base_size=None, color=None,
                   cite=None):
    """**bold** / *italic* markup + script-aware fonts + optional
    verse-citation hyperlinks. cite = None (no linkification) or dict:
    {'bare': (vmap, anchor)} for bare (N) and/or
    {'dotted': {(ch, v): anchor}, 'chap': {ch: anchor}} for (ch.v[-w]).
    Only in-range references linkify; years and ranges never match."""
    text = NORM(text)
    if cite is not None:
        # dotted refs first (they contain bare-like digits)
        def _split_dotted(t):
            out = []
            pos = 0
            for m in DOTTED_RE.finditer(t):
                out.append(t[pos:m.start()])
                out.append(m)
                pos = m.end()
            out.append(t[pos:])
            return out
        chunks = _split_dotted(text)
        for ck, chunk in enumerate(chunks):
            if ck % 2 == 1:
                ch, v = int(chunk.group(1)), int(chunk.group(2))
                tgt = None
                dm = cite.get('dotted', {})
                if (ch, v) in dm:
                    tgt = dm[(ch, v)]
                elif ch in cite.get('chap', {}):
                    tgt = cite['chap'][ch]
                if tgt is not None:
                    inner = chunk.group(0)[1:-1]
                    r = paragraph.add_run("(")
                    set_run_font(r, ml_font, base_size, False, False, color)
                    add_cite_link(paragraph, inner, tgt, base_size)
                    r = paragraph.add_run(")")
                    set_run_font(r, ml_font, base_size, False, False, color)
                    continue
                chunk = chunk.group(0)
            _add_rich_bare(paragraph, chunk, ml_font, base_size, color,
                           cite.get('bare'))
        return
    _add_rich_tokens(paragraph, text, ml_font, base_size, color)


def _add_rich_bare(paragraph, text, ml_font, base_size, color, bare):
    if bare is None:
        _add_rich_tokens(paragraph, text, ml_font, base_size, color)
        return
    vmap, ch_anchor = bare
    parts = CITE_RE.split(text)
    for k, part in enumerate(parts):
        if k % 2 == 1:
            v = int(part)
            if 1 <= v <= 335 and v != 246:
                tgt = resolve_verse(vmap, ch_anchor, v)
                r = paragraph.add_run("(")
                set_run_font(r, ml_font, base_size, False, False, color)
                add_cite_link(paragraph, part, tgt, base_size)
                r = paragraph.add_run(")")
                set_run_font(r, ml_font, base_size, False, False, color)
                continue
            part = "(%s)" % part
        _add_rich_tokens(paragraph, part, ml_font, base_size, color)


def _add_rich_tokens(paragraph, text, ml_font, base_size, color):
    tokens = re.split(r'(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)', text)
    for tok in tokens:
        if not tok:
            continue
        if tok.startswith('**') and tok.endswith('**') and len(tok) > 4:
            add_mixed_text(paragraph, tok[2:-2], ml_font, base_size,
                           True, False, color)
        elif tok.startswith('*') and tok.endswith('*') and len(tok) > 2:
            add_mixed_text(paragraph, tok[1:-1], ml_font, base_size,
                           False, True, color)
        elif tok.startswith('`') and tok.endswith('`') and len(tok) > 2:
            add_mixed_text(paragraph, tok[1:-1], ml_font, base_size,
                           False, False, color)
        else:
            add_mixed_text(paragraph, tok, ml_font, base_size,
                           False, False, color)


def shade(paragraph, hex_fill):
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_fill)
    pPr.append(shd)


def box(paragraph, color_hex="A67C2E", size="4"):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    for edge in ('top', 'left', 'bottom', 'right'):
        el = OxmlElement(f'w:{edge}')
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), size)
        el.set(qn('w:color'), color_hex)
        pBdr.append(el)
    pPr.append(pBdr)


def hline(paragraph, color="A67C2E", size="6"):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), size)
    bottom.set(qn('w:color'), color)
    pBdr.append(bottom)
    pPr.append(pBdr)


def keep_lines(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    pPr.append(OxmlElement('w:keepLines'))


def keep_with_next(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    pPr.append(OxmlElement('w:keepNext'))

def styled_heading(doc, text, level, anchor=None, toc=None, toc_level=None,
                   size=None, color=None, align=None, latin_italic_heading=False):
    """Heading with explicit per-run fonts (LibreOffice-safe CTL)."""
    text = NORM(text)
    h = doc.add_heading(level=level)
    h.alignment = align if align is not None else WD_ALIGN_PARAGRAPH.LEFT
    pos = 0
    for m in LATIN_RUN.finditer(text):
        if m.start() > pos:
            r = h.add_run(text[pos:m.start()])
            set_run_font(r, HEAD_FONT, size, True, False, color)
        r = h.add_run(m.group(0))
        set_run_font(r, LATIN_FONT, size, True, latin_italic_heading, color)
        pos = m.end()
    if pos < len(text):
        r = h.add_run(text[pos:])
        set_run_font(r, HEAD_FONT, size, True, False, color)
    if anchor:
        add_bookmark(h, anchor)
    if toc is not None and anchor:
        toc.append((toc_level or level, text, anchor))
    return h



_bookmark_id = [2000]


class AnchorGen:
    """Deterministic unique anchor factory (shared by scanner + renderer)."""

    def __init__(self):
        self.used = set()

    def slug(self, t):
        return re.sub(r'\s+', '_', re.sub(
            r'[^\w൦-൯]+', ' ', t, flags=re.UNICODE)).strip('_')[:20]

    def get(self, base):
        if base not in self.used:
            self.used.add(base)
            return base
        k = 2
        while f"{base}_{k}" in self.used:
            k += 1
        self.used.add(f"{base}_{k}")
        return f"{base}_{k}"

    def h2(self, code, t):
        m = re.search(r'[൦-൯]+', t)
        base = (f"ch_{code}_V{m.group(0)}" if m
                else f"ch_{code}_{self.slug(t)}")
        return self.get(base)

    def recap(self, code, t):
        m = re.search(r'[൦-൯]+', t)
        base = (f"ch_{code}_R{m.group(0)}" if m
                else f"ch_{code}_R{self.slug(t)}")
        return self.get(base)


def verse_map_from_file(fname, code, chapter_anchor):
    """Ordered [(start_verse, anchor)] for citation links (§18). A cited
    verse resolves to its containing section's anchor (or chapter)."""
    path = os.path.join(TR, fname)
    with open(path, encoding="utf-8") as f:
        md = f.read().splitlines()
    starts = []
    seen = set()
    # replicate AnchorGen.h2 exactly (dedup-free: uniqueness asserted)
    agen = AnchorGen()
    for line in md:
        s = line.strip()
        if s.startswith('## ') and not s.startswith('### '):
            tt = s[3:].strip()
            if tt.startswith('ഇതിൽനിന്ന്'):
                continue
            m = re.search(r'[൦-൯]+', tt)
            if not m:
                continue
            bm = agen.h2(code, tt)
            assert bm not in seen, "anchor collision " + bm
            seen.add(bm)
            starts.append((int(NORM(m.group(0))), bm))
    starts.sort()
    return starts, chapter_anchor


def resolve_verse(starts, chapter_anchor, v):
    tgt = chapter_anchor
    for sv, bm in starts:
        if sv <= v:
            tgt = bm
        else:
            break
    return tgt


# File spans (root-verse ranges) from forensic inventory; print maxima in
# CHAPTERS. Quoted/colophon marks excluded from spans by construction.
SPANS = {
    "frontmatter_ml.md": None, "upodghata_ml.md": None,
    "ch01_ml.md": (1, 47), "ch02a_ml.md": (1, 27), "ch02b_ml.md": (28, 50),
    "ch02c_ml.md": (51, 74), "ch03_ml.md": (1, 48), "ch04_ml.md": (1, 42),
    "ch05_ml.md": (1, 28), "ch06_ml.md": (1, 49), "ch07_ml.md": (1, 30),
    "ch08_ml.md": (1, 28), "ch09_ml.md": (1, 35), "ch10_ml.md": (1, 42),
    "ch11_ml.md": (1, 60), "ch12_ml.md": (1, 20), "ch13_ml.md": (1, 34),
    "ch14_ml.md": (1, 27), "ch15_ml.md": (1, 20), "ch16_ml.md": (1, 24),
    "ch17_ml.md": (1, 28), "ch18a_ml.md": (1, 30), "ch18b_ml.md": (31, 53),
    "ch18c_ml.md": (1, 78),
}


def h2_range(title):
    """(start, end) from 'ശ്ലോകം N' / 'ശ്ലോകം N–M' (any digit kind)."""
    t = NORM(title)
    m = re.search(r'(\d+)\s*[–—-]\s*(\d+)', t)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r'(\d+)\s*$', t)
    if m:
        v = int(m.group(1))
        return v, v
    return None


def opener_map():
    """{opener anchor: raw H1 title} for every file section + UPO.
    Deterministic (no AG state) — used for starts + outline."""
    m = {}
    for fname, code, chno, ml, en, _ in CHAPTERS:
        if fname in ("frontmatter_ml.md",):
            continue
        if fname.startswith("appendix"):
            m[f"ch_{code}"] = ml
            continue
        if fname == "upodghata_ml.md":
            m["ch_UPO"] = "ഉപോദ്ഘാതം"
            continue
        h1 = ""
        for _l in open(os.path.join(TR, fname), encoding="utf-8"):
            if _l.strip().startswith('# '):
                h1 = _l.strip()[2:].strip()
                break
        m[f"ch_{code}"] = h1 or ml
    return m


def scan_sarv(AG=None, research=False):
    """Pre-scan: TOC display list + all anchors + verse maps.
    Returns (display, allanchors, h2map, dotted, chap_anchor, h2ent).
    h2map: {(fname): [(start, end, anchor)]}; dotted: {(ch, v): anchor};
    h2ent: [(2, title-ascii, anchor)] for outline use (not printed TOC)."""
    AG = AG or AnchorGen()
    display, allanchors, h2ent = [], [], []
    h2map, dotted, chap_anchor = {}, {}, {}
    # map file -> chapter no + code
    fmeta = {f: (c, ch) for f, c, ch, _, _, _ in CHAPTERS}
    for fname, code, chno, ml, en, _ in CHAPTERS:
        if fname in ("frontmatter_ml.md", "upodghata_ml.md"):
            continue
        if fname.startswith("appendix"):
            continue
        path = os.path.join(TR, fname)
        md = open(path, encoding="utf-8").read().splitlines()
        cha = AG.get(f"ch_{code}")
        allanchors.append(cha)
        chap_anchor[code] = cha
        h2map[fname] = []
        for line in md:
            s = line.strip()
            if s.startswith('## ') and not s.startswith('### '):
                t = s[3:].strip()
                if t.startswith('അവതരണം'):
                    bm = AG.get(f"ch_{code}_intro")
                    allanchors.append(bm)
                    # intro bookmark only, not in TOC
                    h2map[fname].append(('intro', bm))
                    continue
                r = h2_range(t)
                bm = AG.h2(code, t)
                allanchors.append(bm)
                h2ent.append((2, NORM(t), bm))
                if r:
                    h2map[fname].append((r[0], r[1], bm))
    # chapter display entries (18) + dotted global map
    by_ch = {}
    for fname, code, chno, ml, en, _ in CHAPTERS:
        if not chno:
            continue
        by_ch.setdefault(chno, []).append((fname, code, ml, en))
    for chno in sorted(by_ch):
        files = by_ch[chno]
        code0 = files[0][1]
        cha = chap_anchor[code0]
        ml, en = files[0][2], files[0][3]
        lo = SPANS[files[0][0]][0]
        hi = max(SPANS[f][1] for f, _, _, _ in files)
        display.append((1, "%02d · %s — Verses %d–%d" % (chno, ml, lo, hi),
                        cha))
        # dotted map: every verse in span -> its H2 anchor
        for fname, code, _, _ in files:
            for entry in h2map.get(fname, []):
                if entry[0] == 'intro':
                    continue
                s0, s1, bm = entry
                for v in range(s0, s1 + 1):
                    dotted.setdefault((chno, v), bm)
    # upodghata: chapter anchor + H2 counters (mirrors render_upodghata)
    _up = os.path.join(TR, "upodghata_ml.md")
    _umd = open(_up, encoding="utf-8").read().splitlines()
    _a = AG.get("ch_UPO")
    allanchors.append(_a)
    display.append((1, "ഉപോദ്ഘാതം", _a))
    _k = 0
    for _line in _umd:
        if _line.strip().startswith('## '):
            _k += 1
            _bm = AG.get(f"ch_UPO_h{_k}")
            allanchors.append(_bm)
            h2ent.append((2, NORM(_line.strip()[3:].strip()), _bm))
    # appendices: chapter anchor + H2 counters (mirrors render_sarv_appendix)
    for fname, code, _, ml, en, _ in CHAPTERS:
        if not fname.startswith("appendix"):
            continue
        _a = AG.get(f"ch_{code}")
        allanchors.append(_a)
        out = "അനുബന്ധം %s — %s" % ({"APPA": "1", "APPB": "2",
                                     "APPC": "3"}[code], ml)
        display.append((1, out, _a))
        md = open(os.path.join(TR, fname), encoding="utf-8").read().splitlines()
        k = 0
        for line in md:
            if line.strip().startswith('## '):
                k += 1
                bm = AG.get(f"ch_{code}_h{k}")
                allanchors.append(bm)
                h2ent.append((2, NORM(line.strip()[3:].strip()), bm))
    # glossary / colophon literal anchors (+ concordance iff research).
    # NOTE: ch_INDEX stays out of the gate registry (index section is
    # conditional); its DOCX bookmark is still written for navigation.
    lits = ["ch_GLOSS", "ch_COL"]
    if research:
        lits.append("ch_CONC")
    for lit in lits:
        allanchors.append(AG.get(lit))
    return display, allanchors, h2map, dotted, chap_anchor, h2ent


def scan_headings(AG=None, research=False):
    """Compat wrapper (frontmatter/appendix anchors handled by callers)."""
    display, allanchors, _, _, _, _ = scan_sarv(AnchorGen(), research)
    return display, allanchors


def add_bookmark(paragraph, name):
    _bookmark_id[0] += 1
    bid = str(_bookmark_id[0])
    start = OxmlElement('w:bookmarkStart')
    start.set(qn('w:id'), bid)
    start.set(qn('w:name'), name)
    end = OxmlElement('w:bookmarkEnd')
    end.set(qn('w:id'), bid)
    p = paragraph._p
    p.insert(0, start)
    p.append(end)


def add_internal_link(paragraph, bookmark, text, size=None):
    text = NORM(text)
    hl = OxmlElement('w:hyperlink')
    hl.set(qn('w:anchor'), bookmark)
    hl.set(qn('w:history'), '1')
    run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    rF = OxmlElement('w:rFonts')
    for attr in ('w:ascii', 'w:hAnsi', 'w:cs'):
        rF.set(qn(attr), HEAD_FONT)
    color = OxmlElement('w:color')
    color.set(qn('w:val'), '2E4057')
    if size is not None:
        sz = OxmlElement('w:sz')
        sz.set(qn('w:val'), str(int(size.pt * 2)))
        rPr.append(sz)
    rPr.append(rF)
    rPr.append(color)
    run.append(rPr)
    t = OxmlElement('w:t')
    t.set(qn('xml:space'), 'preserve')
    t.text = text
    run.append(t)
    hl.append(run)
    paragraph._p.append(hl)


def add_toc_dot_leader(paragraph):
    """Right tab with dot leader for TOC page numbers."""
    pPr = paragraph._p.get_or_add_pPr()
    tabs = pPr.find(qn('w:tabs'))
    if tabs is None:
        tabs = OxmlElement('w:tabs')
        pPr.append(tabs)
    tab = OxmlElement('w:tab')
    tab.set(qn('w:val'), 'right')
    tab.set(qn('w:leader'), 'dot')
    tab.set(qn('w:pos'), '9350')
    tabs.append(tab)


# ---------------- footnotes ----------------
class Footnotes:
    FN_RT = ('http://schemas.openxmlformats.org/officeDocument/'
             '2006/relationships/footnotes')

    def __init__(self, doc, note_size):
        self.doc = doc
        self.note_size = note_size
        self.counter = [1]
        self.footnotes_el = OxmlElement('w:footnotes')
        for fid, typ in (('0', 'separator'), ('1', 'continuationSeparator')):
            fn = OxmlElement('w:footnote')
            fn.set(qn('w:id'), fid)
            fn.set(qn('w:type'), typ)
            par = OxmlElement('w:p')
            run = OxmlElement('w:r')
            sep = OxmlElement('w:separator') if typ == 'separator' else \
                OxmlElement('w:continuationSeparator')
            run.append(sep)
            par.append(run)
            fn.append(par)
            self.footnotes_el.append(fn)
        self._installed = False

    def _install(self):
        if self._installed:
            return
        from lxml import etree
        from docx.opc.part import Part
        from docx.opc.packuri import PackURI
        xml_bytes = etree.tostring(self.footnotes_el, xml_declaration=True,
                                   encoding='UTF-8', standalone=True)
        uri = PackURI('/word/footnotes.xml')
        fpart = Part(uri, 'application/vnd.openxmlformats-officedocument.'
                          'wordprocessingml.footnotes+xml',
                     xml_bytes, self.doc.part.package)
        self.doc.part.relate_to(fpart, self.FN_RT)
        self._part = fpart
        self._installed = True

    def add(self, anchor_paragraph, text, cite=None):
        """Attach footnote; anchor appended to anchor_paragraph."""
        from lxml import etree
        text = NORM(text)
        fid = str(self.counter[0] + 1)
        self.counter[0] += 1
        fn = OxmlElement('w:footnote')
        fn.set(qn('w:id'), fid)
        par = OxmlElement('w:p')
        pPr = OxmlElement('w:pPr')
        jc = OxmlElement('w:jc')
        jc.set(qn('w:val'), 'both')
        pPr.append(jc)
        # widow control inside footnotes: never strand a 1-line fragment
        pPr.append(OxmlElement('w:widowControl'))
        par.append(pPr)
        # build runs manually with mixed fonts
        # tokenize bold lead
        m = re.match(r'(\*\*.+?\*\*)\s*(.*)', text, re.S)
        segs = []
        if m:
            segs.append((m.group(1)[2:-2], True, False))
            text = m.group(2)
        # split remaining **..** occurrences
        for tok in re.split(r'(\*\*.+?\*\*)', text):
            if not tok:
                continue
            if tok.startswith('**') and tok.endswith('**'):
                segs.append((tok[2:-2], True, False))
            else:
                segs.append((tok, False, False))
        for seg_text, b, it in segs:
            pos = 0
            for mm in LATIN_RUN.finditer(seg_text):
                if mm.start() > pos:
                    self._note_run(par, seg_text[pos:mm.start()],
                                   BODY_FONT, b, it)
                self._note_run(par, mm.group(0), LATIN_FONT, b, it)
                pos = mm.end()
            if pos < len(seg_text):
                self._note_run(par, seg_text[pos:], BODY_FONT, b, it)
        fn.append(par)
        self.footnotes_el.append(fn)
        # reference run on anchor
        r = anchor_paragraph.add_run()
        rPr = r._r.get_or_add_rPr()
        st = OxmlElement('w:rStyle')
        st.set(qn('w:val'), 'FootnoteReference')
        rPr.append(st)
        ref = OxmlElement('w:footnoteReference')
        ref.set(qn('w:id'), fid)
        r._r.append(ref)

    def _note_run(self, par, text, family, bold, italic):
        if not text:
            return
        run = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')
        rF = OxmlElement('w:rFonts')
        for attr in ('w:ascii', 'w:hAnsi', 'w:cs'):
            rF.set(qn(attr), family)
        rPr.append(rF)
        sz = OxmlElement('w:sz')
        sz.set(qn('w:val'), str(int(self.note_size.pt * 2)))
        rPr.append(sz)
        if bold:
            rPr.append(OxmlElement('w:b'))
        if italic:
            rPr.append(OxmlElement('w:i'))
        run.append(rPr)
        t = OxmlElement('w:t')
        t.set(qn('xml:space'), 'preserve')
        t.text = text
        run.append(t)
        # footnote text lives in w:p of the footnote
        par.append(run)

    def finalize(self):
        from lxml import etree
        self._install()
        self._part._blob = etree.tostring(
            self.footnotes_el, xml_declaration=True, encoding='UTF-8',
            standalone=True)


# ---------------- tables ----------------
def add_word_table(doc, E, header_cells, body_rows, body_pt, caption=None,
                   widths=None, source_note=None):
    if caption:
        cp = doc.add_paragraph()
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.space_before = Pt(6)
        cp.paragraph_format.space_after = Pt(2)
        add_mixed_text(cp, caption, HEAD_FONT, Pt(9), True, False, MAROON)
        keep_with_next(cp)
    table = doc.add_table(rows=1 + len(body_rows), cols=len(header_cells))
    table.style = 'Table Grid'
    table.autofit = False
    # §26: never exceed the text measure (Trade 4.7" ≠ A4 6.47").
    measure = E.get("measure", 6.4)
    n = len(header_cells)
    if widths is None:
        if n == 4:
            widths = [1.9, 1.5, 1.7, 1.3]
        elif n == 3:
            if measure < 5.5:
                widths = [0.85, 2.25, 1.45]  # Trade: room for long IAST
            else:
                widths = [1.1, 2.6, 2.7]
        else:
            widths = [measure / n] * n
    s = sum(widths)
    widths = [w / s * measure for w in widths]
    for j, w in enumerate(widths):
        for row in table.rows:
            row.cells[j].width = Inches(w)
    # LO lays out from tblGrid, not tcW: set gridCol explicitly or all
    # tuned widths are silently equal-split (measured P1-1).
    grid = table._tbl.tblGrid
    for j, gc in enumerate(grid.xpath('./w:gridCol')):
        if j < len(widths):
            gc.set(qn('w:w'), str(int(widths[j] * 1440)))
    for j, h in enumerate(header_cells):
        cell = table.cell(0, j)
        cell.text = ""
        p = cell.paragraphs[0]
        add_mixed_text(p, h, HEAD_FONT, Pt(9), True, False,
                       RGBColor(0xFF, 0xFF, 0xFF))
        tcPr = cell._tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), '5A1A10')
        tcPr.append(shd)
    # repeat header row on page breaks
    tr = table.rows[0]._tr
    trPr = tr.get_or_add_trPr()
    trPr.append(OxmlElement('w:tblHeader'))
    for _row in table.rows[1:]:
        # data rows never split across pages (no orphan cell fragments)
        _row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
    for i, row in enumerate(body_rows):
        for j in range(len(header_cells)):
            txt = row[j] if j < len(row) else "—"
            cell = table.cell(i + 1, j)
            cell.text = ""
            p = cell.paragraphs[0]
            add_mixed_text(p, txt, BODY_FONT, body_pt, False, False, INK)
            if i % 2 == 1:
                tcPr = cell._tc.get_or_add_tcPr()
                shd = OxmlElement('w:shd')
                shd.set(qn('w:val'), 'clear')
                shd.set(qn('w:color'), 'auto')
                shd.set(qn('w:fill'), 'FFFBF0')
                tcPr.append(shd)
    if source_note:
        sn = doc.add_paragraph()
        sn.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sn.paragraph_format.first_line_indent = Inches(0)
        sn.paragraph_format.space_before = Pt(1)
        add_mixed_text(sn, source_note, HEAD_FONT, Pt(8), False, True, GREY)
    else:
        doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return table


def parse_md_row(s):
    return [c.strip() for c in s.strip().strip('|').split('|')]


# ---------------- document-wide styles ----------------
def style_document(doc, E):
    style = doc.styles['Normal']
    style.font.name = BODY_FONT
    style.font.size = Pt(E["body_pt"])
    style.font.color.rgb = INK
    pf = style.paragraph_format
    pf.space_after = Pt(4)
    pf.space_before = Pt(0)
    pf.line_spacing = E["line_mult"]
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.widow_control = True
    pf.first_line_indent = Inches(0.22)
    rPr = style.element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    for attr in ('w:ascii', 'w:hAnsi', 'w:cs'):
        rFonts.set(qn(attr), BODY_FONT)
    specs = {1: (16.5, MAROON_DK, 10, 4), 2: (12.5, MAROON, 8, 3),
             3: (11.0, SLATE, 6, 3)}
    for i, (size, color, before, after) in specs.items():
        hs = doc.styles[f'Heading {i}']
        hs.font.name = HEAD_FONT
        hs.font.size = Pt(size)
        hs.font.bold = True
        hs.font.color.rgb = color
        hs.paragraph_format.keep_with_next = True
        hs.paragraph_format.widow_control = True
        hs.paragraph_format.space_before = Pt(before)
        hs.paragraph_format.space_after = Pt(after)
        hs.paragraph_format.first_line_indent = Inches(0)
        if i > 1:
            hs.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        rPr2 = hs.element.get_or_add_rPr()
        rf = rPr2.find(qn('w:rFonts'))
        if rf is None:
            rf = OxmlElement('w:rFonts')
            rPr2.append(rf)
        for attr in ('w:ascii', 'w:hAnsi', 'w:cs'):
            rf.set(qn(attr), HEAD_FONT)


def setup_section(sec, E, header_odd=None, header_even=None,
                  footer_fmt="decimal", footer_start=None,
                  first_empty=True, page_border=False, folio=True,
                  restart_footnotes=False):
    sec.page_height = E["page_h"]
    sec.page_width = E["page_w"]
    sec.top_margin = E["m_top"]
    sec.bottom_margin = E["m_bot"]
    sec.left_margin = E["m_left"]
    sec.right_margin = E["m_right"]
    sec.odd_and_even_pages_header_footer = True
    sec.different_first_page_header_footer = first_empty
    # Each section needs INDEPENDENT header/footer parts; otherwise Word
    # links to previous and our runs accumulate across chapters (spec N/O).
    for _part in (sec.header, sec.footer):
        try:
            _part.is_linked_to_previous = False
        except Exception:
            pass
    if header_even is not None:
        try:
            sec.even_page_header.is_linked_to_previous = False
        except Exception:
            pass
    try:
        sec.first_page_header.is_linked_to_previous = False
    except Exception:
        pass
    try:
        sec.first_page_footer.is_linked_to_previous = False
    except Exception:
        pass
    # NOTE: no w:pgBorders page frames anywhere (spec O — restrained folios).
    # LibreOffice propagates the first section's page border to all pages,
    # which overdecorates the book; the cover is framed by its emblem plate.
    if footer_start is not None:
        sectPr = sec._sectPr
        pgNum = OxmlElement('w:pgNumType')
        pgNum.set(qn('w:start'), str(footer_start))
        pgNum.set(qn('w:fmt'), footer_fmt)
        sectPr.append(pgNum)
    # NOTE: w:footnotePr numRestart=eachSect makes LibreOffice render
    # every marker after the first as "0" (verified visually); global
    # numbering renders correctly, so restart is intentionally NOT set.
    # Footnote TITLE labels (കുറിപ്പ് ൧..) preserve the source per-part
    # indexing; markers are document-unique anchors. See BUILD_LOG.
    if False and restart_footnotes:
        pass
    # Single centered running head carrying BOTH series + section identity.
    # (Word even/odd heads are ignored by the LibreOffice converter — verified
    # by spike — so parity-split Left/Right heads are not achievable in this
    # toolchain; combined head preserves the spec-N information. See BUILD_LOG.)
    if header_odd:
        hp = sec.header.paragraphs[0]
        hp.clear()
        hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        hp.paragraph_format.first_line_indent = Inches(0)
        add_mixed_text(hp, header_odd, HEAD_FONT, Pt(E.get("head_pt", 7.5)),
                       False, False, GOLD)
    if header_even:
        hp = sec.even_page_header.paragraphs[0]
        hp.clear()
        hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        hp.paragraph_format.first_line_indent = Inches(0)
        add_mixed_text(hp, header_even, HEAD_FONT, Pt(7.5), False, False,
                       GOLD)
    # footer folio
    if not folio:
        try:
            sec.footer.paragraphs[0].clear()
            sec.header.paragraphs[0].clear()
        except Exception:
            pass
        return
    fp = sec.footer.paragraphs[0]
    fp.clear()
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.paragraph_format.first_line_indent = Inches(0)
    run = fp.add_run()
    fld1 = OxmlElement('w:fldChar')
    fld1.set(qn('w:fldCharType'), 'begin')
    instr = OxmlElement('w:instrText')
    instr.set(qn('xml:space'), 'preserve')
    instr.text = 'PAGE'
    fld2 = OxmlElement('w:fldChar')
    fld2.set(qn('w:fldCharType'), 'end')
    run._r.append(fld1)
    run2 = fp.add_run()
    run2._r.append(instr)
    run3 = fp.add_run()
    run3._r.append(fld2)
    for r in fp.runs:
        set_run_font(r, HEAD_FONT, Pt(8), False, False, GREY)
    if first_empty:
        # thin folio on first pages too (reduced): leave default (empty
        # first header, but first footer keeps folio via primary footer?
        # Word uses separate first-page footer; copy folio there.)
        try:
            ffp = sec.first_page_footer.paragraphs[0]
            ffp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            rr = ffp.add_run()
            ff1 = OxmlElement('w:fldChar')
            ff1.set(qn('w:fldCharType'), 'begin')
            ii = OxmlElement('w:instrText')
            ii.set(qn('xml:space'), 'preserve')
            ii.text = 'PAGE'
            ff2 = OxmlElement('w:fldChar')
            ff2.set(qn('w:fldCharType'), 'end')
            rr._r.append(ff1)
            rr2 = ffp.add_run()
            rr2._r.append(ii)
            rr3 = ffp.add_run()
            rr3._r.append(ff2)
            for r in ffp.runs:
                set_run_font(r, HEAD_FONT, Pt(8), False, False, GREY)
        except Exception:
            pass


# ---------------- content rendering ----------------
def render_mula_group(doc, E, lines):
    """One compact box per verse group (multi-line verses stay together)."""
    text = "\n".join(l.lstrip('> ').strip() for l in lines if l.strip('> '))
    text = NORM(re.sub(r'\n{2,}', '\n', text).strip())
    if not text:
        return None
    pp = doc.add_paragraph()
    pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pp.paragraph_format.space_before = Pt(4)
    pp.paragraph_format.space_after = Pt(6)
    pp.paragraph_format.first_line_indent = Inches(0)
    shade(pp, "FFFBF0")
    box(pp, "A67C2E", "4")
    parts = text.split('\n')
    # short groups stay intact; very long groups (praśasti runs) break in
    # a controlled way rather than stranding their heading on a void page
    if len(parts) <= 10:
        keep_lines(pp)
    for k, part in enumerate(parts):
        r = pp.add_run(part)
        set_run_font(r, BODY_FONT, Pt(E["mula_pt"]), True, False, MAROON)
        if k < len(parts) - 1:
            r.add_break()
    return pp


def render_figure_unit(doc, E, fno, sec, famml, rng):
    """Figure + two-line scholarly caption as one unit (§23–24)."""
    png = os.path.join(FIGDIR, "fig_F%02d.png" % fno)
    if not os.path.exists(png):
        return
    pp = doc.add_paragraph()
    pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pp.paragraph_format.space_before = Pt(4)
    pp.paragraph_format.space_after = Pt(1)
    pp.paragraph_format.first_line_indent = Inches(0)
    keep_lines(pp)
    try:
        pp.add_run().add_picture(png, width=E["fig_w"])
    except Exception:
        return
    keep_with_next(pp)
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.space_before = Pt(1)
    cp.paragraph_format.space_after = Pt(0)
    cp.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(cp, "Figure %d — %s · %s" % (fno, sec, famml),
                   HEAD_FONT, Pt(E["cap_pt"]), True, False, MAROON)
    keep_lines(cp)
    keep_with_next(cp)
    cs = doc.add_paragraph()
    cs.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cs.paragraph_format.space_before = Pt(0)
    cs.paragraph_format.space_after = Pt(6)
    cs.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(cs, "Based on verses %s" % rng, HEAD_FONT,
                   Pt(E["cap_pt"] - 0.5), False, True, GREY)
    keep_lines(cs)


def body_para(doc, E, text, footnote_text=None, F=None, no_indent=False,
              size=None, italic=False, cite=None, first_use=None):
    pp = doc.add_paragraph()
    if no_indent:
        pp.paragraph_format.first_line_indent = Inches(0)
    if first_use is not None:
        text, _ = iast_first_use(text, first_use)
    add_rich_mixed(pp, text, BODY_FONT, size, INK, cite)
    if italic:
        for r in pp.runs:
            r.italic = True
    if footnote_text and F is not None:
        F.add(pp, footnote_text, cite)
    return pp


LEAD_LABELS = ("**നേരർത്ഥം:**", "**ആചാര്യവ്യാഖ്യാനം:**", "**വിശകലനം:**",
               "**കുറിപ്പ്")


# chapter number -> first section code (for cross-chapter citation fallback)
_CH2CODE = {}
for _f, _c, _n, _m, _e, _x in CHAPTERS:
    if _n and _n not in _CH2CODE:
        _CH2CODE[_n] = _c


def iter_blocks(md_lines):
    """Join hard-wrapped source lines into logical blocks (sources wrap at
    ~70 chars; every physical line must NOT become a paragraph).
    Returns [(kind, payload)]: h1/h2/h3 (text), mula ([lines]),
    table ([lines]), bullet (text), boldline (text), body (joined text).
    Blank lines and all block markers close the open body. A **-line opens
    fresh; following plain lines join it (covers വിവരണം continuations)."""
    pending = []
    mula_buf, tbl_buf = [], []
    cur = None  # [kind, [parts]] joinable body-ish block

    def close_cur():
        nonlocal cur
        if cur and any(p.strip() for p in cur[1]):
            pending.append((cur[0], " ".join(p.strip() for p in cur[1])))
        cur = None

    for line in md_lines:
        s = line.strip()
        if not s or s.startswith('```'):
            if mula_buf:
                pending.append(('mula', mula_buf)); mula_buf = []
            if tbl_buf:
                pending.append(('table', tbl_buf)); tbl_buf = []
            close_cur()
            continue
        if s.startswith('>'):
            if tbl_buf:
                pending.append(('table', tbl_buf)); tbl_buf = []
            close_cur()
            mula_buf.append(s)
            continue
        if mula_buf:
            pending.append(('mula', mula_buf)); mula_buf = []
        if s.startswith('# '):
            if tbl_buf:
                pending.append(('table', tbl_buf)); tbl_buf = []
            close_cur()
            pending.append(('h1', s[2:].strip()))
            continue
        if s.startswith('### '):
            if tbl_buf:
                pending.append(('table', tbl_buf)); tbl_buf = []
            close_cur()
            pending.append(('h3', s[4:].strip()))
            continue
        if s.startswith('## '):
            if tbl_buf:
                pending.append(('table', tbl_buf)); tbl_buf = []
            close_cur()
            pending.append(('h2', s[3:].strip()))
            continue
        if s.startswith('|'):
            close_cur()
            tbl_buf.append(s)
            continue
        if tbl_buf:
            pending.append(('table', tbl_buf)); tbl_buf = []
        if s.startswith('- ') or s.startswith('* '):
            close_cur()
            pending.append(('bullet', s[2:].strip()))
            continue
        if s.startswith('**'):
            close_cur()
            cur = ['boldline', [s]]
            continue
        if cur is None:
            cur = ['body', [s]]
        else:
            cur[1].append(s)
    if mula_buf:
        pending.append(('mula', mula_buf))
    if tbl_buf:
        pending.append(('table', tbl_buf))
    close_cur()
    return pending


def flush_mula_buf(doc, E, lines):
    """Render one mula group block; return (para, first_verse or None)."""
    pp = render_mula_group(doc, E, list(lines))
    nums = re.findall('\u0965\\s*([\\d]+)\\s*\u0965', "\n".join(lines))
    first_v = int(NORM(nums[0])) if nums else None
    return pp, first_v


def render_sarv_file(doc, E, fname, code, chno, ml, en, span, F,
                   AG, h2map, dotted, chap_anchor, first_use, fig_here):
    """Render one translated_peak file: H1 skipped (opener built by caller),
    ## അവതരണം intro, ## ശ്ലോകം groups, speaker labels, mula boxes,
    **വിവരണം:** commentary, dotted citation links, P0 fixes, IAST."""
    path = os.path.join(TR, fname)
    md = open(path, encoding="utf-8").read().splitlines()
    if fname == "ch09_ml.md":
        md = apply_p0_file_fixes(fname, "\n".join(md)).splitlines()
    cite = {'dotted': dotted,
            'chap': {c: chap_anchor.get(_CH2CODE.get(c, code))
                     for c in range(1, 19)}}
    last_body = [None]
    pending_fn78 = [False]
    mula_buf = []

    def flush_mula():
        if not mula_buf:
            return None
        pp = render_mula_group(doc, E, list(mula_buf))
        nums = re.findall(r'\u0965\s*([\d]+)\s*\u0965', "\n".join(mula_buf))
        first_v = int(NORM(nums[0])) if nums else None
        mula_buf.clear()
        return pp, first_v

    for kind, pay in iter_blocks(md):
        if kind == 'h1':
            continue  # opener built by caller
        if kind == 'h2':
            t = pay
            if t.startswith('അവതരണം'):
                styled_heading(doc, t, 2,
                               anchor=AG.get(f"ch_{code}_intro"),
                               size=Pt(12.5), color=MAROON)
            else:
                bm = AG.h2(code, t)
                styled_heading(doc, t, 2, anchor=bm,
                               size=Pt(12.5), color=MAROON)
            continue
        if kind == 'h3':
            flush_mula()
            styled_heading(doc, pay, 3, size=Pt(11.0), color=SLATE)
            continue
        if kind == 'mula':
            res = flush_mula_buf(doc, E, pay)
            if res:
                pp, first_v = res
                last_body[0] = pp
                if first_v is not None and (chno, first_v) in FIG_TRIGGER:
                    fno, sec, famml, rng = FIG_SARV[(chno, first_v)]
                    render_figure_unit(doc, E, fno, sec, famml, rng)
                if fname == "ch18c_ml.md" and first_v == 78:
                    pending_fn78[0] = True
            continue
        if kind == 'table':
            rows = [parse_md_row(t) for t in pay]
            rows = [r for r in rows if not all(
                re.fullmatch(r':?---+:?', c or '---') for c in r)]
            if rows:
                add_word_table(doc, E, rows[0], rows[1:],
                               Pt(E["body_pt"] - 1))
            continue
        if kind == 'bullet':
            pp = doc.add_paragraph()
            pp.paragraph_format.first_line_indent = Inches(0)
            pp.paragraph_format.left_indent = Inches(0.3)
            add_mixed_text(pp, "\u2022  ", HEAD_FONT, None, True, False,
                           GOLD)
            t2, _ = iast_first_use(pay, first_use)
            add_rich_mixed(pp, t2, BODY_FONT, None, INK, cite)
            last_body[0] = pp
            continue
        if kind == 'boldline':
            s = pay
            if re.fullmatch(r'\*\*.+ഉവാച\*\*', s):
                pp = doc.add_paragraph()
                pp.paragraph_format.first_line_indent = Inches(0)
                pp.paragraph_format.space_before = Pt(5)
                pp.paragraph_format.space_after = Pt(2)
                add_mixed_text(pp, s.strip('*'), HEAD_FONT, Pt(11), True,
                               False, MAROON)
                keep_with_next(pp)
                last_body[0] = pp
                continue
            m = re.match(r'(\*\*.+?:\*\*)\s*(.*)', s, re.S)
            pp = doc.add_paragraph()
            pp.paragraph_format.first_line_indent = Inches(0)
            if m:
                add_mixed_text(pp, m.group(1)[2:-3] + " \u2014 ", HEAD_FONT,
                               Pt(E["body_pt"] - 0.8), True, False, SLATE)
                t2, _ = iast_first_use(m.group(2), first_use)
                add_rich_mixed(pp, t2, BODY_FONT, None, INK, cite)
            else:
                t2, _ = iast_first_use(s, first_use)
                add_rich_mixed(pp, t2, BODY_FONT, None, INK, cite)
            last_body[0] = pp
            if pending_fn78[0]:
                F.add(pp, "**കുറിപ്പ് \u2014** അച്ചടി 78–79 ആയി എണ്ണുന്നു "
                      "(യത്ര/തത്ര); ഇവിടെ ഒറ്റ ശ്ലോകം.")
                pending_fn78[0] = False
            continue
        # kind == 'body'
        t2, _ = iast_first_use(pay, first_use)
        pp = body_para(doc, E, t2, no_indent=False, cite=cite)
        last_body[0] = pp
    if last_body[0] is not None:
        keep_with_next(last_body[0])
    ep = doc.add_paragraph()
    ep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ep.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(ep, "\u2022 \u2022 \u2022", HEAD_FONT, Pt(10), False,
                   False, GOLD)


def build_cover(doc, E):
    for _ in range(2):
        sp = doc.add_paragraph()
        sp.paragraph_format.first_line_indent = Inches(0)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(p, "കാശ്മീർ സംസ്കൃതഗ്രന്ഥാവലി · ഗ്രന്ഥാങ്കം 64",
                   HEAD_FONT, Pt(11), False, False, GOLD)
    ep = doc.add_paragraph()
    ep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ep.paragraph_format.first_line_indent = Inches(0)
    ep.paragraph_format.space_before = Pt(2)
    shade(ep, "FAF4E6")
    box(ep, "A67C2E", "4")
    try:
        ep.add_run().add_picture(EMBLEM, width=E["emblem_w"])
    except Exception:
        pass
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t.paragraph_format.first_line_indent = Inches(0)
    t.paragraph_format.space_before = Pt(6)
    add_mixed_text(t, "ശ്രീമദ്ഭഗവദ്ഗീതാ", HEAD_FONT, Pt(30), True, False,
                   MAROON_DK)
    t2 = doc.add_paragraph()
    t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t2.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(t2, "Bhagavadgītā · Malayalam Edition", HEAD_FONT,
                   Pt(11), False, True, SLATE)
    rl = doc.add_paragraph()
    rl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rl.paragraph_format.first_line_indent = Inches(0)
    hline(rl)
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.paragraph_format.first_line_indent = Inches(0)
    sub.paragraph_format.space_before = Pt(4)
    sub.paragraph_format.space_after = Pt(0)
    add_mixed_text(sub, "രാജാനക രാമകണ്ഠവിരചിതമായ സർവ്വതോഭദ്രവിവരണത്തോടെ",
                   BODY_FONT, Pt(12), True, False, SLATE)
    sub2 = doc.add_paragraph()
    sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub2.paragraph_format.first_line_indent = Inches(0)
    sub2.paragraph_format.space_before = Pt(0)
    add_mixed_text(sub2, "with Rājānaka Rāmakaṇṭha's Sarvatobhadra",
                   HEAD_FONT, Pt(11), False, False, SLATE)
    au = doc.add_paragraph()
    au.alignment = WD_ALIGN_PARAGRAPH.CENTER
    au.paragraph_format.first_line_indent = Inches(0)
    au.paragraph_format.space_before = Pt(6)
    add_mixed_text(au, "സമ്പൂർണ്ണ മലയാളവിവർത്തനം · Complete Malayalam "
                   "Translation", BODY_FONT, Pt(10.5), False, False, INK)
    ed = doc.add_paragraph()
    ed.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ed.paragraph_format.first_line_indent = Inches(0)
    ed.paragraph_format.space_before = Pt(10)
    add_mixed_text(ed, "മൂലം മലയാളലിപിയിൽ · 18 അദ്ധ്യായങ്ങൾ · 3 അനുബന്ധങ്ങൾ",
                   HEAD_FONT, Pt(9), False, False, GREY)
    fin = doc.add_paragraph()
    fin.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fin.paragraph_format.first_line_indent = Inches(0)
    fin.paragraph_format.space_before = Pt(14)
    add_mixed_text(fin, "• • •", HEAD_FONT, Pt(10), False, False, GOLD)
    imp = doc.add_paragraph()
    imp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    imp.paragraph_format.first_line_indent = Inches(0)
    imp.paragraph_format.space_before = Pt(48)
    add_mixed_text(imp, "സർവ്വതോഭദ്രം മലയാളപരമ്പര · ഒന്നാം പുസ്തകം",
                   HEAD_FONT, Pt(8.5), False, False, GREY)


def fm_heading(doc, text, fm, level=1, anchor=None):
    size = Pt(16.5) if level == 1 else Pt(12.5)
    color = MAROON_DK if level == 1 else MAROON
    h = styled_heading(doc, text, level, anchor=anchor, size=size,
                       color=color)
    if anchor:
        fm.append((level, text, anchor))
    return h


def fm_heading(doc, text, fm, level=1, anchor=None):
    size = Pt(16.5) if level == 1 else Pt(12.5)
    color = MAROON_DK if level == 1 else MAROON
    h = styled_heading(doc, text, level, anchor=anchor, size=size,
                       color=color)
    if anchor:
        fm.append((level, text, anchor))
    return h


def render_sarv_intro(doc, E, fm, cite=None):
    """frontmatter_ml.md: grantha title + mangala + mukham/avatharika."""
    path = os.path.join(TR, "frontmatter_ml.md")
    md = open(path, encoding="utf-8").read().splitlines()
    seen_h1 = [False]
    for kind, pay in iter_blocks(md):
        if kind == 'h1':
            continue
        if kind == 'h2':
            t = pay
            if not seen_h1[0]:
                styled_heading(doc, "ഗ്രന്ഥപരിചയം", 1, anchor="fm_intro",
                               size=Pt(16.5), color=MAROON_DK)
                fm.append((1, "ഗ്രന്ഥപരിചയം", "fm_intro"))
                seen_h1[0] = True
                if t in ("ഗ്രന്ഥപരിചയം", "ഗ്രന്ഥശീർഷകം"):
                    continue
            styled_heading(doc, t, 2, anchor="fm_intro_%d" % len(fm),
                           size=Pt(12.5), color=MAROON)
            fm.append((2, t, "fm_intro_%d" % (len(fm))))
            continue
        if kind == 'mula':
            render_mula_group(doc, E, list(pay))
            continue
        if kind in ('h3',):
            styled_heading(doc, pay, 3, size=Pt(11.0), color=SLATE)
            continue
        if kind == 'bullet':
            pp = doc.add_paragraph()
            pp.paragraph_format.first_line_indent = Inches(0)
            pp.paragraph_format.left_indent = Inches(0.3)
            add_mixed_text(pp, "\u2022  ", HEAD_FONT, None, True, False,
                           GOLD)
            add_rich_mixed(pp, pay, BODY_FONT, None, INK, cite)
            continue
        if kind == 'table':
            rows = [parse_md_row(t) for t in pay]
            rows = [r for r in rows if not all(
                re.fullmatch(r':?---+:?', c or '---') for c in r)]
            if rows:
                add_word_table(doc, E, rows[0], rows[1:],
                               Pt(E["body_pt"] - 1))
            continue
        m = re.match(r'(\*\*.+?:\*\*)\s*(.*)', pay, re.S)
        pp = doc.add_paragraph()
        if m:
            add_mixed_text(pp, m.group(1)[2:-3] + " \u2014 ", HEAD_FONT,
                           Pt(E["body_pt"] - 0.8), True, False, SLATE)
            add_rich_mixed(pp, m.group(2), BODY_FONT, None, INK)
        else:
            pp.paragraph_format.first_line_indent = Inches(0)
            add_rich_mixed(pp, pay, BODY_FONT, None, INK)


def build_frontmatter(doc, E, display, toc_pages=None, cite0=None):
    fm = []
    # half-title
    for _ in range(4):
        sp = doc.add_paragraph()
        sp.paragraph_format.first_line_indent = Inches(0)
    ht = doc.add_paragraph()
    ht.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ht.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(ht, "ശ്രീമദ്ഭഗവദ്ഗീതാ", HEAD_FONT, Pt(22), True, False,
                   MAROON_DK)
    ht2 = doc.add_paragraph()
    ht2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ht2.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(ht2, "സർവ്വതോഭദ്രം · മലയാളപരമ്പര · ഒന്നാം പുസ്തകം",
                   BODY_FONT, Pt(12), False, False, SLATE)
    doc.add_page_break()
    # series title page
    for _ in range(5):
        sp = doc.add_paragraph()
        sp.paragraph_format.first_line_indent = Inches(0)
    st = doc.add_paragraph()
    st.alignment = WD_ALIGN_PARAGRAPH.CENTER
    st.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(st, "Sarvatobhadra · Malayalam Series", HEAD_FONT,
                   Pt(13), False, True, SLATE)
    st2 = doc.add_paragraph()
    st2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    st2.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(st2, "സർവ്വതോഭദ്രം മലയാളപരമ്പര", HEAD_FONT, Pt(16),
                   True, False, MAROON_DK)
    sto = doc.add_paragraph()
    sto.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sto.paragraph_format.first_line_indent = Inches(0)
    sto.paragraph_format.space_before = Pt(12)
    add_mixed_text(sto, "• • •", HEAD_FONT, Pt(10), False, False, GOLD)
    doc.add_page_break()
    # title page
    for _ in range(2):
        sp = doc.add_paragraph()
        sp.paragraph_format.first_line_indent = Inches(0)
    tp = doc.add_paragraph()
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(tp, "ശ്രീമദ്ഭഗവദ്ഗീതാ", HEAD_FONT, Pt(26), True, False,
                   MAROON_DK)
    tp2 = doc.add_paragraph()
    tp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp2.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(tp2, "Bhagavadgītā", HEAD_FONT, Pt(14), False, True,
                   SLATE)
    tp3 = doc.add_paragraph()
    tp3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp3.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(tp3, "Malayalam Edition · Scholarly Book One",
                   HEAD_FONT, Pt(10.5), False, False, SLATE)
    rl = doc.add_paragraph()
    rl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rl.paragraph_format.first_line_indent = Inches(0)
    hline(rl)
    au = doc.add_paragraph()
    au.alignment = WD_ALIGN_PARAGRAPH.CENTER
    au.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(au, "രാജാനക രാമകണ്ഠൻ · Rājānaka Rāmakaṇṭha", BODY_FONT,
                   Pt(13), True, False, INK)
    au2 = doc.add_paragraph()
    au2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    au2.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(au2, "സർവ്വതോഭദ്രവിവരണത്തോടെ — with the Sarvatobhadra "
                   "commentary", BODY_FONT, Pt(10.5), False, False, INK)
    ml = doc.add_paragraph()
    ml.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ml.paragraph_format.first_line_indent = Inches(0)
    ml.paragraph_format.space_before = Pt(8)
    ml.paragraph_format.space_after = Pt(0)
    add_mixed_text(ml, "സമ്പൂർണ്ണ മലയാളവിവർത്തനം", HEAD_FONT,
                   Pt(10), False, False, SLATE)
    ml2 = doc.add_paragraph()
    ml2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ml2.paragraph_format.first_line_indent = Inches(0)
    ml2.paragraph_format.space_before = Pt(0)
    add_mixed_text(ml2, "Complete Malayalam Translation", HEAD_FONT,
                   Pt(10), False, False, SLATE)
    doc.add_page_break()
    # edition note
    fm_heading(doc, "പതിപ്പുകുറിപ്പ്", fm, 1, "fm_edition")
    body_para(doc, E, "കാശ്മീർ സംസ്കൃതഗ്രന്ഥാവലി 64-ാം ഗ്രന്ഥമായി 1943-ൽ "
              "നിർണ്ണയസാഗർ പ്രസ്സിൽ അച്ചടിച്ച ശ്രീമദ്ഭഗവദ്ഗീതാ "
              "സർവ്വതോഭദ്രവിവരണത്തിന്റെ സമ്പൂർണ്ണ മലയാളവിവർത്തനമാണ് ഈ "
              "പതിപ്പ് — പതിനെട്ട് അദ്ധ്യായങ്ങളും മൂന്ന് അനുബന്ധങ്ങളും.",
              no_indent=True)
    body_para(doc, E, "സ്വകാര്യപഠനത്തിനുള്ള പരിഭാഷണം മാത്രം.",
              no_indent=True)
    # source / translation basis
    fm_heading(doc, "ആധാരവും പരിഭാഷയും", fm, 1, "fm_basis")
    for _para in [
        "മൂലാധാരം: KSTS No. 64 — Rājānaka Rāmakaṇṭha's Sarvatobhadra "
        "commentary as edited by Madhusudan Kaul Shastri (1943). "
        "ഗീതാമൂലം 700-ൽപ്പരം ശ്ലോകങ്ങൾ (കാശ്മീരപാഠപ്രകാരം അധികശ്ലോകങ്ങൾ "
        "സഹിതം), ഉപോദ്ഘാതം, ശുദ്ധിപത്രം, പാഠാന്തരപ്പട്ടിക, അധികശ്ലോകങ്ങൾ.",
        "ഈ മലയാളപതിപ്പ് വിവരണസഹിതമായ സമ്പൂർണ്ണ വിവർത്തനമാണ് — "
        "മൂലശ്ലോകങ്ങൾ സംസ്കൃതത്തിൽ മലയാളലിപിയിൽ, തുടർന്ന് അക്ഷരാർത്ഥവും "
        "താത്പര്യവിവരണവും.",
    ]:
        body_para(doc, E, _para, no_indent=True)
    # reading guide
    fm_heading(doc, "എങ്ങനെ വായിക്കാം", fm, 1, "fm_reading")
    body_para(doc, E, "ഓരോ ഭാഗവും ഈ ക്രമത്തിൽ വായിക്കുക —", no_indent=True)
    flow = doc.add_paragraph()
    flow.alignment = WD_ALIGN_PARAGRAPH.CENTER
    flow.paragraph_format.first_line_indent = Inches(0)
    flow.paragraph_format.space_before = Pt(2)
    flow.paragraph_format.space_after = Pt(2)
    shade(flow, "FFFBF0")
    box(flow, "A67C2E", "4")
    add_mixed_text(flow, "മൂലം · അക്ഷരാർത്ഥം · താത്പര്യം · വിവരണം · "
                   "അടിക്കുറിപ്പുകൾ / ചിത്രങ്ങൾ", BODY_FONT, Pt(10),
                   True, False, MAROON)
    rg = [
        "മൂലം: സ്വർണ്ണപ്പെട്ടിയിലെ സംസ്കൃതം (മലയാളലിപിയിൽ) ചൊല്ലി, "
        "തുടർന്ന് അക്ഷരാർത്ഥം വായിക്കുക. മൂലപാഠം പരിഭാഷപ്പെടുത്തിയിട്ടില്ല.",
        "വിവരണം രാമകണ്ഠവിവരണത്തിന്റെ സമ്പൂർണ്ണ വിവർത്തനമാണ് — "
        "പദഛേദവും താത്പര്യവും സഹിതം.",
        "Figure N എന്ന ചിത്രം അതാത് ഭാഗത്തിന്റെ ആശയഭേദം കാട്ടുന്നു; "
        "\"Based on verses\" എന്ന വരി ഏത് ശ്ലോകങ്ങളെ ആധാരമാക്കിയെന്ന് "
        "പറയുന്നു.",
        "പ്രധാനപദങ്ങൾ ആദ്യപ്രയോഗത്തിൽ [ബ്രാക്കറ്റിൽ] വരുന്നു — "
        "ഉദാ. ആത്മാവ് [Ātman].",
        "ശ്ലോകസംഖ്യകൾ കാശ്മീരപാഠപ്രകാരം അന്താരാഷ്ട്ര അക്കങ്ങളിൽ "
        "(1, 2, 3 …). വാചകത്തിലെ (13.34) പോലുള്ള സംഖ്യകൾ "
        "ശ്ലോകപരാമർശങ്ങളാണ് — ഞെക്കിയാൽ ആ ഭാഗത്തേക്ക് പോകാം.",
    ]
    for item in rg:
        pp = doc.add_paragraph()
        pp.paragraph_format.first_line_indent = Inches(0)
        pp.paragraph_format.left_indent = Inches(0.3)
        add_mixed_text(pp, "•  ", HEAD_FONT, None, True, False, GOLD)
        add_rich_mixed(pp, item, BODY_FONT, None, INK)
    # textual policy
    fm_heading(doc, "പാഠനയം", fm, 1, "fm_policy")
    for _para in [
        "മൂലം സംസ്കൃതത്തിൽത്തന്നെ മലയാളലിപിയിൽ നിലനിർത്തി; മൂലപേടകത്തിനുള്ളിൽ "
        "പരിഭാഷയില്ല. ഓരോ മൂലത്തിനും തുടർന്ന് അക്ഷരാർത്ഥവും വിവരണവും.",
        "IAST പദങ്ങൾ ആദ്യപ്രയോഗത്തിൽ [ബ്രാക്കറ്റിൽ]; പിന്നീട് വെറും "
        "മലയാളം. അദ്ധ്യായം.ശ്ലോകം എന്ന പരാമർശരീതി കാശ്മീരപാഠത്തിലെ "
        "ശ്ലോകസംഖ്യ പിന്തുടരുന്നു.",
        "ചിത്രങ്ങൾ ആശയവ്യക്തതയ്ക്ക് മാത്രം; അലങ്കാരചിത്രങ്ങളില്ല. "
        "പട്ടികകൾ യഥാർത്ഥ പട്ടികകളായി, തലക്കെട്ട് ആവർത്തിച്ച്.",
    ]:
        body_para(doc, E, _para, no_indent=True)
    # book introduction from frontmatter_ml.md (mangala + mukham/avatharika)
    render_sarv_intro(doc, E, fm, cite0)
    # chapter architecture plate
    arch = os.path.join(FIGDIR, "fig_ARCH.png")
    if os.path.exists(arch):
        ap = doc.add_paragraph()
        ap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        ap.paragraph_format.first_line_indent = Inches(0)
        ap.paragraph_format.space_before = Pt(4)
        ap.paragraph_format.space_after = Pt(1)
        keep_lines(ap)
        try:
            ap.add_run().add_picture(arch, width=E["fig_w"])
        except Exception:
            pass
        keep_with_next(ap)
        ac = doc.add_paragraph()
        ac.alignment = WD_ALIGN_PARAGRAPH.CENTER
        ac.paragraph_format.first_line_indent = Inches(0)
        ac.paragraph_format.space_after = Pt(6)
        add_mixed_text(ac, "Eighteen chapters — architecture · structural "
                       "overview", HEAD_FONT, Pt(E["cap_pt"]), False, True,
                       MAROON)
        keep_lines(ac)
    # contents (dynamic, linked, real numbers in pass 2)
    doc.add_page_break()
    fm_heading(doc, "ഉള്ളടക്കം", fm, 1, "fm_toc")
    for lvl, title, anchor in display:
        pp = doc.add_paragraph()
        pp.paragraph_format.first_line_indent = Inches(0)
        pp.paragraph_format.space_before = Pt(1) if lvl == 1 else Pt(0)
        pp.paragraph_format.space_after = Pt(1) if lvl == 1 else Pt(0)
        if lvl == 2:
            pp.paragraph_format.left_indent = Inches(0.3)
        add_toc_dot_leader(pp)
        size = Pt(10.5) if lvl == 1 else Pt(9.5)
        add_internal_link(pp, anchor, title, size)
        pg = (toc_pages or {}).get(anchor)
        if pg is not None:
            r = pp.add_run("\t%d" % pg)
            set_run_font(r, HEAD_FONT, size, False, False, GREY)
    # key sigla (compact; full abbreviations live with the appendices)
    doc.add_page_break()
    fm_heading(doc, "പ്രധാന ചുരുക്കപ്പേരുകൾ", fm, 1, "fm_sigla")
    for _sig in ["RmK — Rāmakaṇṭha · രാമകണ്ഠൻ",
                 "Śaṅ — Śaṅkara · ശങ്കരൻ",
                 "KSTS — Kashmir Series · കാശ്മീർ ഗ്രന്ഥമാല",
                 "Bg — Bhagavadgītā · ഭഗവദ്ഗീത",
                 "Sarv — Sarvatobhadra · സർവ്വതോഭദ്രം"]:
        pp = doc.add_paragraph()
        pp.paragraph_format.first_line_indent = Inches(0)
        pp.paragraph_format.left_indent = Inches(0.3)
        add_mixed_text(pp, "•  ", HEAD_FONT, None, True, False, GOLD)
        add_rich_mixed(pp, _sig, BODY_FONT, None, INK)
    body_para(doc, E, "പാഠാന്തരങ്ങളിൽ RmK = രാമകണ്ഠപാഠം, Śaṅ = ശങ്കരപാഠം.",
              no_indent=True)
    return fm
# ---------------- appendices + colophon ----------------
def render_upodghata(doc, E, F, AG, dotted, chap_anchor, first_use):
    """upodghata_ml.md as its own section (H1 skipped; H2s anchored)."""
    kick = doc.add_paragraph()
    kick.alignment = WD_ALIGN_PARAGRAPH.LEFT
    kick.paragraph_format.first_line_indent = Inches(0)
    kick.paragraph_format.space_after = Pt(0)
    add_mixed_text(kick, "ഉപോദ്ഘാതം · Introduction", HEAD_FONT, Pt(9),
                   True, False, GOLD)
    styled_heading(doc, "ഉപോദ്ഘാതം", 1, anchor=AG.get("ch_UPO"),
                   size=Pt(16.5), color=MAROON_DK)
    rl = doc.add_paragraph()
    rl.paragraph_format.first_line_indent = Inches(0)
    hline(rl)
    cite = {'dotted': dotted,
            'chap': {c: chap_anchor.get(_CH2CODE.get(c, "CH01"))
                     for c in range(1, 19)}}
    md = open(os.path.join(TR, "upodghata_ml.md"), encoding="utf-8").read().splitlines()
    h2n = [0]
    for kind, pay in iter_blocks(md):
        if kind == 'h1':
            continue
        if kind == 'h2':
            h2n[0] += 1
            styled_heading(doc, pay, 2,
                           anchor=AG.get(f"ch_UPO_h{h2n[0]}"),
                           size=Pt(12.5), color=MAROON)
            continue
        if kind == 'h3':
            styled_heading(doc, pay, 3, size=Pt(11.0), color=SLATE)
            continue
        if kind == 'mula':
            render_mula_group(doc, E, list(pay))
            continue
        if kind == 'table':
            rows = [parse_md_row(t) for t in pay]
            rows = [r for r in rows if not all(
                re.fullmatch(r':?---+:?', c or '---') for c in r)]
            if rows:
                add_word_table(doc, E, rows[0], rows[1:],
                               Pt(E["body_pt"] - 1))
            continue
        if kind == 'bullet':
            pp = doc.add_paragraph()
            pp.paragraph_format.first_line_indent = Inches(0)
            pp.paragraph_format.left_indent = Inches(0.3)
            add_mixed_text(pp, "\u2022  ", HEAD_FONT, None, True, False,
                           GOLD)
            t2, _ = iast_first_use(pay, first_use)
            add_rich_mixed(pp, t2, BODY_FONT, None, INK, cite)
            continue
        if kind == 'boldline':
            s = pay
            m = re.match(r'(\*\*.+?:\*\*)\s*(.*)', s, re.S)
            pp = doc.add_paragraph()
            pp.paragraph_format.first_line_indent = Inches(0)
            if m:
                add_mixed_text(pp, m.group(1)[2:-3] + " \u2014 ", HEAD_FONT,
                               Pt(E["body_pt"] - 0.8), True, False, SLATE)
                t2, _ = iast_first_use(m.group(2), first_use)
                add_rich_mixed(pp, t2, BODY_FONT, None, INK, cite)
            else:
                t2, _ = iast_first_use(s, first_use)
                add_rich_mixed(pp, t2, BODY_FONT, None, INK, cite)
            continue
        t2, _ = iast_first_use(pay, first_use)
        body_para(doc, E, t2, no_indent=False, cite=cite)


def render_sarv_appendix(doc, E, fname, code, title_ml, title_en, F,
                       AG, first_use):
    """One appendix file: opener, tables (Table N), mula groups, prose."""
    kick = doc.add_paragraph()
    kick.alignment = WD_ALIGN_PARAGRAPH.LEFT
    kick.paragraph_format.first_line_indent = Inches(0)
    kick.paragraph_format.space_after = Pt(0)
    add_mixed_text(kick, "Appendix " + code[-1], HEAD_FONT, Pt(9), True,
                   False, GOLD)
    styled_heading(doc, title_ml, 1, anchor=AG.get(f"ch_{code}"),
                   size=Pt(16.5), color=MAROON_DK)
    rl = doc.add_paragraph()
    rl.paragraph_format.first_line_indent = Inches(0)
    hline(rl)
    path = os.path.join(TR, fname)
    md = open(path, encoding="utf-8").read().splitlines()
    h2n = [0]
    cite = {'dotted': {}, 'chap': {}}
    for kind, pay in iter_blocks(md):
        if kind == 'h1':
            continue
        if kind == 'h2':
            h2n[0] += 1
            styled_heading(doc, pay, 2,
                           anchor=AG.get(f"ch_{code}_h{h2n[0]}"),
                           size=Pt(12.5), color=MAROON)
            continue
        if kind == 'h3':
            styled_heading(doc, pay, 3, size=Pt(11.0), color=SLATE)
            continue
        if kind == 'mula':
            render_mula_group(doc, E, list(pay))
            continue
        if kind == 'table':
            rows = [parse_md_row(t) for t in pay]
            rows = [r for r in rows if not all(
                re.fullmatch(r':?---+:?', c or '---') for c in r)]
            if rows:
                cap = "Table %s — %s" % (code[-1], title_ml)
                add_word_table(doc, E, rows[0], rows[1:],
                               Pt(8.5), caption=cap,
                               source_note="Source: KSTS print apparatus "
                               "(render-layer transcription only).")
            continue
        if kind == 'bullet':
            pp = doc.add_paragraph()
            pp.paragraph_format.first_line_indent = Inches(0)
            pp.paragraph_format.left_indent = Inches(0.3)
            add_mixed_text(pp, "\u2022  ", HEAD_FONT, None, True, False,
                           GOLD)
            t2, _ = iast_first_use(pay, first_use)
            add_rich_mixed(pp, t2, BODY_FONT, None, INK, cite)
            continue
        if kind == 'boldline':
            s = pay
            m = re.match(r'(\*\*.+?:\*\*)\s*(.*)', s, re.S)
            pp = doc.add_paragraph()
            pp.paragraph_format.first_line_indent = Inches(0)
            if m:
                add_mixed_text(pp, m.group(1)[2:-3] + " \u2014 ", HEAD_FONT,
                               Pt(E["body_pt"] - 0.8), True, False, SLATE)
                t2, _ = iast_first_use(m.group(2), first_use)
                add_rich_mixed(pp, t2, BODY_FONT, None, INK, cite)
            else:
                t2, _ = iast_first_use(s, first_use)
                add_rich_mixed(pp, t2, BODY_FONT, None, INK, cite)
            continue
        t2, _ = iast_first_use(pay, first_use)
        body_para(doc, E, t2, no_indent=False, cite=cite)
    # appendix closes on its last block (no orphan ornament)


def sarv_glossary_terms():
    """[(ml, iast, gloss_en, context)] from locked GLOSSARY.md.
    English glosses are the lock file's own short glosses where present,
    else standard dictionary equivalents (logged as apparatus)."""
    terms = []
    seen = set()
    for line in open(os.path.join(BASE, "GLOSSARY.md"), encoding="utf-8"):
        s = line.strip()
        if not s.startswith('-'):
            continue
        parts = [c.strip() for c in s[1:].split('|')]
        for part in parts:
            m = re.match(r'([\u0d00-\u0d7f][\u0d00-\u0d7f\u200c\u200d\-\u2013]*)\s*\[([^\]]+)\]', part)
            if m:
                ml, ia = m.group(1).strip(), m.group(2).strip()
                if (ml, ia) not in seen:
                    seen.add((ml, ia))
                    terms.append((ml, ia))
    return terms


SARV_GLOSS_EXTRA = {
    # term: (english gloss, context) for lock entries lacking glosses
    "രാജാനക": ("Rājānaka", "Kashmirian preceptor-title"),
    "രാമകണ്ഠൻ": ("Rāmakaṇṭha", "author of the Sarvatobhadra"),
    "ശങ്കരൻ": ("Śaṅkara", "author of the rival Gītā commentary"),
    "മധുസൂദൻ": ("Madhusūdana Kaul", "editor of the KSTS print"),
    "സോമാനന്ദൻ": ("Somānanda", "fountainhead of the lineage"),
    "കാശ്മീർ": ("Kashmir", "land of the lineage"),
    "നിർണ്ണയസാഗർ": ("Nirnaya Sagar", "Bombay press of the print"),
    "സർവ്വതോഭദ്രം": ("Sarvatobhadra", "all-auspicious commentary"),
    "ഭഗവദ്ഗീത": ("Bhagavadgītā", "the Song of the Lord"),
}


def render_glossary(doc, E, AG):
    h = styled_heading(doc, "പദാവലി — Glossary", 1, anchor=AG.get("ch_GLOSS"),
                       size=Pt(16.5), color=MAROON_DK)
    lp = doc.add_paragraph()
    lp.paragraph_format.first_line_indent = Inches(0)
    hline(lp)
    order = [(f, "ch %d" % ch) for f, _, ch, _, _, _ in CHAPTERS
             if ch and not f.startswith("appendix")]
    texts = {}
    for fn, _ in order:
        with open(os.path.join(TR, fn), encoding="utf-8") as f:
            texts[fn] = f.read()
    items = []
    for ml, ia in sarv_glossary_terms():
        sp = "—"
        for fn, s in order:
            if ml in texts[fn]:
                sp = s
                break
        items.append((ia.lower(), ml, ia, sp))
    items.sort(key=lambda x: x[0])
    for _, ml, ia, sp in items:
        pp = doc.add_paragraph()
        pp.paragraph_format.first_line_indent = Inches(0)
        pp.paragraph_format.space_before = Pt(2)
        pp.paragraph_format.space_after = Pt(2)
        add_mixed_text(pp, ml + " ", BODY_FONT, None, True, False, MAROON)
        add_mixed_text(pp, "[%s]" % ia, LATIN_FONT, None, False, False,
                       SLATE)
        extra = SARV_GLOSS_EXTRA.get(ml)
        tail = (" — %s; %s." % extra) if extra else "."
        add_rich_mixed(pp, tail + " First occurs: %s." % sp, BODY_FONT,
                       None, INK)
    ep = doc.add_paragraph()
    ep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ep.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(ep, "\u2022 \u2022 \u2022", HEAD_FONT, Pt(10), False,
                   False, GOLD)


def render_index(doc, E, AG, index_pages):
    h = styled_heading(doc, "സൂചിക — Index", 1, anchor="ch_INDEX",
                       size=Pt(16.5), color=MAROON_DK)
    lp = doc.add_paragraph()
    lp.paragraph_format.first_line_indent = Inches(0)
    hline(lp)
    intro = doc.add_paragraph()
    intro.paragraph_format.first_line_indent = Inches(0)
    add_rich_mixed(intro, "Terms and names with the pages where they occur "
                   "(auto-generated from final pagination).", BODY_FONT,
                   None, INK)
    for term, pages in index_pages:
        if not pages:
            continue
        pp = doc.add_paragraph()
        pp.paragraph_format.first_line_indent = Inches(0)
        pp.paragraph_format.space_before = Pt(1)
        pp.paragraph_format.space_after = Pt(1)
        add_mixed_text(pp, term + " — ", BODY_FONT, None, True, False,
                       MAROON)
        add_mixed_text(pp, ", ".join(str(p) for p in pages), LATIN_FONT,
                       None, False, False, INK)


def build_colophon(doc, E, AG):
    # §38 explicit page: balanced composition with approved Arabic example.
    for _ in range(2):
        sp = doc.add_paragraph()
        sp.paragraph_format.first_line_indent = Inches(0)
    top = doc.add_paragraph()
    top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    top.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(top, "\u2022 \u2022 \u2022", HEAD_FONT, Pt(10), False,
                   False, GOLD)
    styled_heading(doc, "സമാപനം · Colophon", 1,
                   anchor=AG.get("ch_COL"), size=Pt(16.5), color=MAROON_DK)
    lp = doc.add_paragraph()
    lp.paragraph_format.first_line_indent = Inches(0)
    hline(lp)
    body_para(doc, E, "ഇതി ശ്രീമദ്രാജാനകരാമകണ്ഠവിരചിതമായ "
              "വാക്യാർത്ഥാന്വയമാത്രമായ സർവ്വതോഭദ്രനാമക ഭഗവദ്ഗീതാവിവരണത്തിന്റെ "
              "മലയാളവിവർത്തനം സമ്പൂർണ്ണം — പതിനെട്ട് അദ്ധ്യായങ്ങളും മൂന്ന് "
              "അനുബന്ധങ്ങളും സഹിതം. മൂലശ്ലോകങ്ങൾ സംസ്കൃതത്തിൽ "
              "മലയാളലിപിയിൽ നിലനിർത്തി; തുടർന്ന് അക്ഷരാർത്ഥവും വിവരണവും "
              "നൽകി.", no_indent=True)
    body_para(doc, E, "മൂലപാഠത്തിലെ അച്ചടിദോഷങ്ങൾ തിരുത്തി "
              "നൽകിയിരിക്കുന്നു; വിശദാംശങ്ങൾ അനുബന്ധം 1 "
              "(ശുദ്ധിപത്രം)-ൽ കാണുക.", no_indent=True)
    # The Arabic OCR example lives on its own centered line: a 2-letter
    # RTL word mid-line can never straddle a wrap edge. (A4/Research
    # exports otherwise split من across lines and emit U+0002 STX into
    # the text layer — P1-2 class. Content-identical, layout-only.)
    ex = doc.add_paragraph()
    ex.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ex.paragraph_format.first_line_indent = Inches(0)
    ex.paragraph_format.space_before = Pt(4)
    add_mixed_text(ex, "ഉദാഹരണം: ('من' മുതലായവ)", BODY_FONT, Pt(10),
                   False, False, INK)
    prod = doc.add_paragraph()
    prod.alignment = WD_ALIGN_PARAGRAPH.CENTER
    prod.paragraph_format.first_line_indent = Inches(0)
    prod.paragraph_format.space_before = Pt(6)
    shade(prod, "FFFBF0")
    box(prod, "A67C2E", "4")
    add_mixed_text(prod, "700+ root verses (Kashmir reckoning) · 8 figures "
                   "· Series style v03", HEAD_FONT, Pt(9), False, False,
                   MAROON)
    em = doc.add_paragraph()
    em.alignment = WD_ALIGN_PARAGRAPH.CENTER
    em.paragraph_format.first_line_indent = Inches(0)
    em.paragraph_format.space_before = Pt(10)
    try:
        em.add_run().add_picture(EMBLEM, width=Inches(1.5))
    except Exception:
        pass
    fin = doc.add_paragraph()
    fin.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fin.paragraph_format.first_line_indent = Inches(0)
    fin.paragraph_format.space_before = Pt(10)
    add_mixed_text(fin, "ശുഭമസ്തു · ॥ ഓം തത്സത് ॥", BODY_FONT, Pt(11),
                   True, False, MAROON)


def render_concordance(doc, E, AG):
    """Research appendix: chapter → source.txt line ranges, print maxima,
    Kashmir-recension extra verses. All auto-derived, no new claims."""
    styled_heading(doc, "പരിശോധന — Print Concordance", 1,
                   anchor=AG.get("ch_CONC"), size=Pt(16.5), color=MAROON_DK)
    lp = doc.add_paragraph()
    lp.paragraph_format.first_line_indent = Inches(0)
    hline(lp)
    body_para(doc, E, "KSTS print (source.txt) line ranges per chapter; "
              "verse maxima follow the Kashmir recension as printed. "
              "Extra counts mark recension verses beyond the vulgate.",
              no_indent=True)
    bounds = [("Frontmatter", 1, 160), ("Upodghata", 161, 533),
              ("Ch 1", 163, 532), ("Ch 2", 534, 1497), ("Ch 3", 1499, 2193),
              ("Ch 4", 2195, 2720), ("Ch 5", 2722, 3123),
              ("Ch 6", 3125, 3632), ("Ch 7", 3634, 4013),
              ("Ch 8", 4016, 4503), ("Ch 9", 4506, 4968),
              ("Ch 10", 4970, 5449), ("Ch 11", 5452, 5985),
              ("Ch 12", 5988, 6200), ("Ch 13", 6203, 6775),
              ("Ch 14", 6777, 7061), ("Ch 15", 7063, 7393),
              ("Ch 16", 7396, 7661), ("Ch 17", 7664, 7945),
              ("Ch 18", 7949, 8813), ("Appendix", 8814, 9453)]
    rows = [[b, "%d–%d" % (s, e)] for b, s, e in bounds]
    add_word_table(doc, E, ["Section", "source.txt lines"], rows,
                   Pt(E["body_pt"] - 1),
                   caption="Table R — source concordance")
    kx = [("Ch 2", "74 (vv 73–74 beyond vulgate 72)"),
          ("Ch 3", "48 (vv 44–48 beyond vulgate 43)"),
          ("Ch 6", "49 (vv 48–49 beyond vulgate 47)"),
          ("Ch 9", "35 (v 35 beyond vulgate 34)"),
          ("Ch 11", "60 (vv 56–60 beyond vulgate 55)"),
          ("Ch 18", "79 (final verse split 78/79; translation keeps one 78, "
           "see note)")]
    add_word_table(doc, E, ["Chapter", "Kashmir extra"], kx,
                   Pt(E["body_pt"] - 1),
                   caption="Table R2 — recension extras")


def build(edition, toc_pages=None, starts=None, index_pages=None,
          research=False):
    E = EDITIONS[edition]
    doc = Document()
    style_document(doc, E)
    # NOTE: pages stay white (w:background page color was tried and is
    # ignored by the LibreOffice converter, which would desync DOCX vs PDF;
    # warmth comes from the ivory plates: emblem, mula boxes, figures).
    F = Footnotes(doc, Pt(E["note_pt"]))
    AG = AnchorGen()
    display, _all, h2map_all, dotted_all, chap_all, h2ent = scan_sarv(
        AnchorGen(), research)
    # cover (no folio; framed emblem plate)
    sec0 = doc.sections[0]
    setup_section(sec0, E, folio=False)
    build_cover(doc, E)
    # frontmatter (roman)
    doc.add_section(WD_SECTION.NEW_PAGE)
    sec_fm = doc.sections[-1]
    setup_section(sec_fm, E, footer_fmt="lowerRoman", footer_start=1)
    fm = build_frontmatter(doc, E, display, toc_pages,
                           {'dotted': dotted_all,
                            'chap': {c: chap_all.get(_CH2CODE.get(c, "CH01"))
                                     for c in range(1, 19)}})
    # upodghata (own section, roman frontmatter zone ends here)
    doc.add_section(WD_SECTION.NEW_PAGE)
    sec_up = doc.sections[-1]
    setup_section(sec_up, E,
                  header_odd=E["series_head"] + " · ഉപോദ്ഘാതം",
                  header_even=None,
                  footer_fmt="decimal",
                  footer_start=(starts or {}).get("UPO"))
    render_upodghata(doc, E, F, AG, dotted_all, chap_all, set())
    # chapters (one section per file; split chapters share heads)
    chap_seen = set()
    for fname, code, chno, ml, en, _ in CHAPTERS:
        if not chno:
            continue
        doc.add_section(WD_SECTION.NEW_PAGE)
        sec = doc.sections[-1]
        if code not in chap_seen:
            start = (starts or {}).get(code)
            if start is None and not chap_seen:
                start = 1
            chap_seen.add(code)
        else:
            start = (starts or {}).get(code)
        rng = "%d–%d" % SPANS[fname] if SPANS.get(fname) else ""
        setup_section(sec, E,
                      header_odd=E["series_head"] + " · അദ്ധ്യായം %d" % chno,
                      header_even=None,
                      footer_fmt="decimal", footer_start=start,
                      restart_footnotes=True)
        # opener: number / traditional H1 / yoga subtitle / verse span
        kn = doc.add_paragraph()
        kn.alignment = WD_ALIGN_PARAGRAPH.LEFT
        kn.paragraph_format.first_line_indent = Inches(0)
        kn.paragraph_format.space_after = Pt(0)
        add_mixed_text(kn, "%02d" % chno, LATIN_FONT, Pt(26), True, False,
                       GOLD)
        h1raw = ""
        for _l in open(os.path.join(TR, fname), encoding="utf-8"):
            if _l.strip().startswith('# '):
                h1raw = _l.strip()[2:].strip()
                break
        styled_heading(doc, h1raw or ml, 1, anchor=AG.get(f"ch_{code}"),
                       size=Pt(16.5), color=MAROON_DK)
        sub = doc.add_paragraph()
        sub.paragraph_format.first_line_indent = Inches(0)
        sub.paragraph_format.space_before = Pt(0)
        sub.paragraph_format.space_after = Pt(1)
        add_mixed_text(sub, en, LATIN_FONT, Pt(11), False, True, SLATE)
        vr = doc.add_paragraph()
        vr.paragraph_format.first_line_indent = Inches(0)
        if rng:
            add_mixed_text(vr, "Verses %s" % rng, LATIN_FONT, Pt(10.5),
                           True, False, SLATE)
        lp = doc.add_paragraph()
        lp.paragraph_format.first_line_indent = Inches(0)
        hline(lp)
        first_use = set()
        render_sarv_file(doc, E, fname, code, chno, ml, en, rng, F, AG,
                         h2map_all, dotted_all, chap_all,
                         first_use, FIG_TRIGGER)
    # appendices (one section each)
    appmeta = [("appendix_A_shuddhipatra_ml.md", "APPA", "ശുദ്ധിപത്രം"),
               ("appendix_B_pathantara_ml.md", "APPB", "പാഠാന്തരങ്ങൾ"),
               ("appendix_C_adhika_ml.md", "APPC", "അധികശ്ലോകങ്ങൾ")]
    for fname, code, ml in appmeta:
        doc.add_section(WD_SECTION.NEW_PAGE)
        sec = doc.sections[-1]
        setup_section(sec, E,
                      header_odd=E["series_head"] + " · അനുബന്ധം",
                      header_even=None,
                      footer_fmt="decimal",
                      footer_start=(starts or {}).get(code),
                      restart_footnotes=True)
        render_sarv_appendix(doc, E, fname, code, ml, ml, F, AG, set())
    # glossary
    doc.add_section(WD_SECTION.NEW_PAGE)
    sec_gl = doc.sections[-1]
    setup_section(sec_gl, E,
                  header_odd=E["series_head"] + " · പദാവലി",
                  header_even=None,
                  footer_fmt="decimal",
                  footer_start=(starts or {}).get("GLOSS"))
    render_glossary(doc, E, AG)
    # research concordance (Research edition only)
    if research:
        doc.add_section(WD_SECTION.NEW_PAGE)
        sec_rc = doc.sections[-1]
        setup_section(sec_rc, E,
                      header_odd=E["series_head"] + " · പരിശോധന",
                      header_even=None,
                      footer_fmt="decimal",
                      footer_start=(starts or {}).get("CONC"))
        render_concordance(doc, E, AG)
    # index (auto-generated; omitted if unavailable)
    if index_pages:
        doc.add_section(WD_SECTION.NEW_PAGE)
        sec_ix = doc.sections[-1]
        setup_section(sec_ix, E,
                      header_odd=E["series_head"] + " · സൂചിക",
                      header_even=None,
                      footer_fmt="decimal",
                      footer_start=(starts or {}).get("INDEX"))
        render_index(doc, E, AG, index_pages)
    # colophon (explicit page)
    doc.add_section(WD_SECTION.NEW_PAGE)
    sec_co = doc.sections[-1]
    setup_section(sec_co, E,
                  header_odd=E["series_head"] + " · സമാപനം",
                  header_even=None,
                  footer_fmt="decimal",
                  footer_start=(starts or {}).get("COL"))
    build_colophon(doc, E, AG)
    F.finalize()
    # build gate: renderer anchors must equal pre-scanned anchors
    scanned = set(_all)
    if set(AG.used) != scanned:
        missing = sorted(scanned - set(AG.used))
        extra = sorted(set(AG.used) - scanned)
        raise SystemExit("ANCHOR MISMATCH missing=%s extra=%s"
                         % (missing, extra))
    toc = fm + display
    doc.core_properties.title = ("Sarvatobhadra — Bhagavadgita Malayalam "
                                 "Translation v03")
    doc.core_properties.author = ("Rajanaka Ramakantha (mula); "
                                  "Malayalam translation")
    doc.core_properties.subject = ("Bhagavadgita Sarvatobhadra — complete "
                                   "Malayalam translation, series style v03")
    doc.core_properties.keywords = ("Bhagavadgita, Sarvatobhadra, Ramakantha, "
                                    "Kashmir Shaivism, Malayalam")
    doc.core_properties.language = "ml"
    doc.core_properties.comments = ("Sarvatobhadra Malayalam Series v03; "
                                    "ASCII numbering; mula in Malayalam script")
    outdir = os.path.join(BASE, "build", "sarvatobhadra_v03", "pdf")
    os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir,
                       "Sarvatobhadra_Malayalam_v03_%s.docx" % E["suffix"])
    doc.save(out)
    print("saved %s (%d KB)" % (out, os.path.getsize(out) // 1024))
    return out, toc, h2ent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", choices=["a4", "trade", "research"],
                    default="trade")
    ap.add_argument("--toc", default=None,
                    help="JSON anchor->page for pass 2")
    ap.add_argument("--starts", default=None,
                    help="JSON section-code->folio-start for pass 2")
    ap.add_argument("--index", default=None,
                    help="JSON [[term,[pages]]] auto-index (pass 2+)")
    ap.add_argument("--research", action="store_true",
                    help="include print concordance appendix")
    args = ap.parse_args()
    toc_pages = None
    if args.toc:
        with open(args.toc, encoding="utf-8") as f:
            toc_pages = json.load(f)
    starts = None
    if args.starts:
        with open(args.starts, encoding="utf-8") as f:
            starts = json.load(f)
    index_pages = None
    if args.index:
        with open(args.index, encoding="utf-8") as f:
            index_pages = json.load(f)
    out, toc, h2ent = build(args.edition, toc_pages, starts, index_pages,
                        research=args.research)
    base = os.path.splitext(os.path.basename(out))[0]
    adir = os.path.join(BASE, "build", "sarvatobhadra_v03", "pdf")
    os.makedirs(adir, exist_ok=True)
    with open(os.path.join(adir, base + ".anchors.json"), "w",
              encoding="utf-8") as f:
        json.dump([{"level": l, "title": t, "anchor": a}
                   for l, t, a in toc], f, ensure_ascii=False, indent=1)
    with open(os.path.join(adir, base + ".openers.json"), "w",
              encoding="utf-8") as f:
        json.dump(opener_map(), f, ensure_ascii=False, indent=1)
    with open(os.path.join(adir, base + ".h2.json"), "w",
              encoding="utf-8") as f:
        json.dump([{"title": t, "anchor": a} for _, t, a in h2ent],
                  f, ensure_ascii=False, indent=1)
    print("anchors:", len(toc), "h2:", len(h2ent))


if __name__ == "__main__":
    main()
