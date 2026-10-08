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

BASE = "/root/tantraloka_ml"
TR = os.path.join(BASE, "translated")
FIGDIR = os.path.join(BASE, "assets", "figs_v03")
# verse -> (Figure No, Malayalam section label, family-ml, verse range)
FIGCAP = {
    1: (1, "മംഗളം", "അലങ്കാരം", "1"),
    2: (2, "ദേവീസ്തുതി", "ത്രിതയം", "2–6"),
    7: (3, "ഗുരുസ്തുതി", "പരമ്പര", "7–13"),
    14: (4, "ഗ്രന്ഥോദ്ദേശ്യം", "പ്രവാഹം", "14–21"),
    22: (5, "സ്വാതന്ത്ര്യം", "ദർപ്പണം", "22–35"),
    36: (6, "അറിയുന്നവൻ", "ത്രിതയം", "36–38"),
    39: (7, "നിർവചനം", "പ്രവാഹം", "39–51"),
    52: (8, "സ്വതഃസിദ്ധി", "ദർപ്പണം", "52–59"),
    60: (9, "സർവവ്യാപി", "ചക്രം", "59–66"),
    67: (10, "സ്വാതന്ത്ര്യശക്തി", "ചക്രം", "66–80"),
    81: (11, "സമൂഹധർമ്മം", "ചക്രം", "81–85"),
    90: (12, "ഭേദം", "സോപാനം", "90–93"),
    94: (13, "നാമനിർവചനം", "ത്രിതയം", "94–105"),
    106: (14, "ദ്വാദശീസംഘം", "ചക്രം", "106–115"),
    116: (15, "കല്പനാശക്തി", "പ്രവാഹം", "116–122"),
    125: (16, "വിധിനിഷേധം", "ദർപ്പണം", "125–133"),
    134: (17, "മറവുതെളിവ്", "പ്രവാഹം", "134–139"),
    140: (18, "ഇച്ഛാജ്ഞാനക്രിയ", "സോപാനം", "140–149"),
    150: (19, "അറിവുക്രിയ", "പ്രവാഹം", "150–155"),
    156: (20, "സർവശക്തിമയം", "പ്രവാഹം", "156–160"),
    161: (21, "മോക്ഷോപായം", "സോപാനം", "161–166"),
    167: (22, "സമാവേശത്രയം", "സോപാനം", "167–170"),
    171: (23, "ശാംഭവം", "പ്രവാഹം", "171–196"),
    202: (24, "ദേവീശക്തി", "ചക്രം", "202–210"),
    211: (25, "ശാക്തം", "സോപാനം", "211–213"),
    214: (26, "ശാക്താണവം", "സോപാനം", "214–218"),
    219: (27, "ആണവം", "സോപാനം", "219–225"),
    226: (28, "ഫലം", "പരമ്പര", "225–232"),
    232: (29, "ഗുരുപരമ്പര", "പരമ്പര", "232–238"),
    239: (30, "മലനീക്കം", "പരമ്പര", "239–245"),
    247: (31, "സംശയനിശ്ചയം", "പ്രവാഹം", "247–274"),
    274: (32, "സംബന്ധം", "പരമ്പര", "274–279"),
    279: (33, "മുൻപറച്ചിൽ", "പ്രവാഹം", "279–287"),
    288: (34, "വിസ്തൃതനിർദ്ദേശം", "സോപാനം", "288–330"),
    331: (35, "സമാപനം", "അലങ്കാരം", "331–335"),
}
CURATED_VERSES = set(FIGCAP)
EMBLEM = os.path.join(BASE, "assets", "cover_emblem.png")
CAPJSON = os.path.join(BASE, "assets", "captions.json")
try:
    with open(CAPJSON, encoding="utf-8") as _cf:
        FIGCAPS = json.load(_cf)
except Exception:
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

_MLD = "൦൧൨൩൪൫൬൭൮൯"
_ML2EN = str.maketrans("൦൧൨൩൪൫൬൭൮൯", "0123456789")


def NORM(s):
    """Spec §0: every ordinary book number in ASCII 0-9. Render-layer
    conversion — authoritative sources stay byte-identical."""
    return s.translate(_ML2EN)

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
        line_mult=1.42, head_pt=7.5, series_head="തന്ത്രാലോകം — മലയാളപതിപ്പ്",
        measure=6.47, suffix="A4",
    ),
    "trade": dict(
        page_w=Inches(6.0), page_h=Inches(9.0),
        m_top=Inches(0.75), m_bot=Inches(0.80),
        m_left=Inches(0.75), m_right=Inches(0.70),
        body_pt=10.2, mula_pt=10.8, note_pt=8.4, cap_pt=8.0,
        fig_w=Inches(2.5), emblem_w=Inches(2.4),
        line_mult=1.40, head_pt=7.0, series_head="തന്ത്രാലോകം",
        measure=4.55, suffix="Trade",
    ),
}

ORDER = [
    ("ta_v02.md", "ആമുഖവന്ദനം", "01", "Mangalācaraṇa", "1–21", "V001"),
    ("ta_v03.md", "ആമുഖം", "02", "Introduction", "22–105", "V022"),
    ("ta_v04.md", "വിവരണം", "03", "Explanation", "106–139", "V106"),
    ("ta_v05.md", "സാധനമാർഗങ്ങൾ", "04", "Means", "140–245", "V140"),
    ("ta_v06.md", "വിഷയനിർദ്ദേശം", "05", "Subject Overview", "247–335",
     "V247"),
 ]

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


def add_mixed_text(paragraph, text, ml_font, base_size=None, base_bold=False,
                   base_italic=False, color=None, latin_bold=None,
                   latin_italic=None):
    """Segment-wise font locking: Latin/IAST runs -> LATIN_FONT, all else
    Malayalam family. Kills arbitrary fallback for diacritics."""
    text = NORM(text)
    pos = 0
    for m in LATIN_RUN.finditer(text):
        if m.start() > pos:
            r = paragraph.add_run(text[pos:m.start()])
            set_run_font(r, ml_font, base_size, base_bold, base_italic, color)
        r = paragraph.add_run(m.group(0))
        set_run_font(r, LATIN_FONT, base_size,
                     base_bold if latin_bold is None else latin_bold,
                     base_italic if latin_italic is None else latin_italic,
                     color)
        pos = m.end()
    if pos < len(text):
        r = paragraph.add_run(text[pos:])
        set_run_font(r, ml_font, base_size, base_bold, base_italic, color)


CITE_RE = re.compile(r'\((\d{1,3})\)')


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
    verse-citation hyperlinks (§18). cite = (verse_map, chapter_anchor)
    or None (no linkification: headings, TOC, captions, tables)."""
    text = NORM(text)
    if cite is not None:
        vmap, ch_anchor = cite
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
        return
    _add_rich_tokens(paragraph, text, ml_font, base_size, color)


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


def scan_headings(AG=None):
    """Pure pre-scan of content order/titles/anchors for the TOC (spec M:
    TOC built from final structure before frontmatter is rendered)."""
    AG = AG or AnchorGen()
    out = []
    allanchors = []
    for fname, ml, num, en, rng, code in ORDER:
        path = os.path.join(TR, fname)
        with open(path, encoding="utf-8") as f:
            md = f.read().splitlines()
        _a = AG.get(f"ch_{code}")
        allanchors.append(_a)
        out.append((1, "%s · %s — Verses %s" % (num, ml, NORM(rng)), _a))
        for line in md:
            s = line.strip()
            if s.startswith('# ') and not s.startswith('## '):
                # file-internal H1: skipped on-page (VQ-003); no anchor.
                continue
            elif s.startswith('## '):
                t = s[3:].strip()
                if t.startswith('ഇതിൽനിന്ന്'):
                    allanchors.append(AG.recap(code, t))  # not in TOC
                else:
                    _a = AG.h2(code, t)
                    allanchors.append(_a)
                    out.append((2, t, _a))
    # appendices (mirror render_appendices)
    path = os.path.join(TR, "ta_app.md")
    with open(path, encoding="utf-8") as f:
        md = f.read().splitlines()
    _a = AG.get("ch_APP")
    allanchors.append(_a)
    out.append((1, "അനുബന്ധങ്ങൾ — ശബ്ദതലങ്ങൾ · ദ്വാദശാന്തം", _a))
    for line in md:
        s = line.strip()
        if s.startswith('## '):
            t = s[3:].strip()
            if t.startswith('അനുബന്ധം'):
                parts = t.split('—', 1)
                code2 = ('APP1' if '൧' in parts[0]
                         else ('APP2' if '൨' in parts[0] else 'APPG'))
                _a = AG.get(f"ch_{code2}")
                allanchors.append(_a)
                out.append((1, t, _a))
            else:
                _a = AG.get("ch_APPG")
                allanchors.append(_a)
                out.append((2, t, _a))
    return out, allanchors


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
    keep_lines(pp)
    parts = text.split('\n')
    for k, part in enumerate(parts):
        r = pp.add_run(part)
        set_run_font(r, BODY_FONT, Pt(E["mula_pt"]), True, False, MAROON)
        if k < len(parts) - 1:
            r.add_break()
    return pp


def render_figure_unit(doc, E, verse, caption_text=None):
    """Figure + two-line scholarly caption as one unit (§23–24)."""
    if verse not in FIGCAP:
        return
    fno, sec, famml, rng = FIGCAP[verse]
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
              size=None, italic=False, cite=None):
    pp = doc.add_paragraph()
    if no_indent:
        pp.paragraph_format.first_line_indent = Inches(0)
    add_rich_mixed(pp, text, BODY_FONT, size, INK, cite)
    if italic:
        for r in pp.runs:
            r.italic = True
    if footnote_text and F is not None:
        F.add(pp, footnote_text, cite)
    return pp


LEAD_LABELS = ("**നേരർത്ഥം:**", "**ആചാര്യവ്യാഖ്യാനം:**", "**വിശകലനം:**",
               "**കുറിപ്പ്")


def render_chapter_file(doc, E, fname, ml, num, en, rng, code, F,
                         AG, verse_map):
    path = os.path.join(TR, fname)
    with open(path, encoding="utf-8") as f:
        md = f.read().splitlines()
    # §9 major-section opener: number / Malayalam title / IAST subtitle /
    # verse range — restrained, no overdesign.
    kn = doc.add_paragraph()
    kn.alignment = WD_ALIGN_PARAGRAPH.LEFT
    kn.paragraph_format.first_line_indent = Inches(0)
    kn.paragraph_format.space_after = Pt(0)
    add_mixed_text(kn, num, LATIN_FONT, Pt(26), True, False, GOLD)
    ch = styled_heading(doc, ml, 1, anchor=AG.get(f"ch_{code}"),
                        size=Pt(16.5), color=MAROON_DK)
    sub = doc.add_paragraph()
    sub.paragraph_format.first_line_indent = Inches(0)
    sub.paragraph_format.space_before = Pt(0)
    sub.paragraph_format.space_after = Pt(1)
    add_mixed_text(sub, en, LATIN_FONT, Pt(11), False, True, SLATE)
    vr = doc.add_paragraph()
    vr.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(vr, "Verses %s" % NORM(rng), LATIN_FONT, Pt(10.5),
                   True, False, SLATE)
    lp = doc.add_paragraph()
    lp.paragraph_format.first_line_indent = Inches(0)
    hline(lp)
    mula_buf = []
    last_body = [None]
    cite = verse_map  # (starts_list, chapter_anchor) pair

    def flush_mula():
        if not mula_buf:
            return None
        pp = render_mula_group(doc, E, list(mula_buf))
        nums = re.findall(r'॥\s*([൦-൯]+)\s*॥', "\n".join(mula_buf))
        first_v = m2i(nums[0]) if nums else None
        mula_buf.clear()
        return pp, first_v

    pending_fig = [None]
    i = 0
    while i < len(md):
        line = md[i]
        i += 1
        s = line.strip()
        if not s:
            continue
        if s.startswith('```'):
            continue
        if s.startswith('# '):
            flush_mula()
            # file-internal H1 duplicates the chapter H1 on-page: skip
            # rendering entirely (no heading, no anchor). Scan mirrors this.
            continue
        if s.startswith('## '):
            flush_mula()
            t = s[3:].strip()
            if t.startswith('ഇതിൽനിന്ന്'):
                t = t.replace('ഇതിൽനിന്ന്', 'ഈ ഭാഗത്തിൽ നിന്ന്', 1)
                m = re.search(r'[൦-൯]+', t)
                bm = AG.recap(code, t)
                styled_heading(doc, t, 3, anchor=bm, size=Pt(11.0),
                               color=SLATE)
            else:
                m = re.search(r'[൦-൯]+', t)
                slug = re.sub(r'\s+', '_', re.sub(
                    r'[^\w൦-൯]+', ' ', t, flags=re.UNICODE)).strip('_')[:20]
                bm = AG.h2(code, t)
                styled_heading(doc, t, 2, anchor=bm,
                               size=Pt(12.5), color=MAROON)
            continue
        if s.startswith('### '):
            flush_mula()
            styled_heading(doc, s[4:].strip(), 3, size=Pt(11.0), color=SLATE)
            continue
        if s.startswith('>'):
            mula_buf.append(s)
            continue
        if mula_buf:
            res = flush_mula()
            if res:
                pp, first_v = res
                if pending_fig[0] is not None:
                    render_figure_unit(doc, E, pending_fig[0])
                    pending_fig[0] = None
                if first_v in CURATED_VERSES:
                    pending_fig[0] = first_v
        if s.startswith('|'):
            block = [s]
            while i < len(md) and md[i].strip().startswith('|'):
                block.append(md[i].strip())
                i += 1
            rows = [parse_md_row(t) for t in block]
            rows = [r for r in rows if not all(
                re.fullmatch(r':?---+:?', c or '---') for c in r)]
            if rows:
                add_word_table(doc, E, rows[0], rows[1:],
                               Pt(E["body_pt"] - 1))
            continue
        if s.startswith('- ') or s.startswith('* '):
            pp = doc.add_paragraph()
            pp.paragraph_format.first_line_indent = Inches(0)
            pp.paragraph_format.left_indent = Inches(0.3)
            add_mixed_text(pp, "•  ", HEAD_FONT, None, True, False, GOLD)
            add_rich_mixed(pp, s[2:], BODY_FONT, None, INK, cite)
            last_body[0] = pp
            continue
        if s.startswith('**കുറിപ്പ്'):
            # true footnote anchored at previous body paragraph (spec P)
            m = re.match(r'\*\*കുറിപ്പ്\s*([൦-൯]+)\s*—\*\*\s*(.*)', s)
            note_text = s
            if m:
                note_text = "**കുറിപ്പ് %s —** %s" % (m.group(1), m.group(2))
            if last_body[0] is not None:
                F.add(last_body[0], note_text, cite)
            else:
                pp = body_para(doc, E, note_text, None, None,
                               no_indent=True, size=Pt(E["note_pt"]),
                               cite=cite)
            continue
        is_lead = s.startswith(LEAD_LABELS[:3])
        pp = doc.add_paragraph()
        if is_lead:
            pp.paragraph_format.first_line_indent = Inches(0)
        if is_lead:
            m = re.match(r'(\*\*.+?:\*\*)\s*(.*)', s, re.S)
            if m:
                # quiet label-like run-in (§12): smaller, slate, no shout
                add_mixed_text(pp, m.group(1)[2:-3] + " — ", HEAD_FONT,
                               Pt(E["body_pt"] - 0.8), True, False, SLATE)
                add_rich_mixed(pp, m.group(2), BODY_FONT, None, INK, cite)
            else:
                add_rich_mixed(pp, s, BODY_FONT, None, INK, cite)
        else:
            add_rich_mixed(pp, s, BODY_FONT, None, INK, cite)
        last_body[0] = pp
        if pending_fig[0] is not None:
            # figure unit directly after its verse-group commentary opens:
            # place after the FIRST body paragraph following the mula
            render_figure_unit(doc, E, pending_fig[0])
            pending_fig[0] = None
    if mula_buf:
        flush_mula()
    if pending_fig[0] is not None:
        render_figure_unit(doc, E, pending_fig[0])
        pending_fig[0] = None
    # keep closing ornament with its content (never strand "• • •" alone)
    if last_body[0] is not None:
        keep_with_next(last_body[0])
    ep = doc.add_paragraph()
    ep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ep.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(ep, "• • •", HEAD_FONT, Pt(10), False, False, GOLD)


# ---------------- cover + frontmatter ----------------
def build_cover(doc, E):
    for _ in range(2):
        sp = doc.add_paragraph()
        sp.paragraph_format.first_line_indent = Inches(0)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(p, "തന്ത്രാലോകം · മലയാളപരമ്പര", HEAD_FONT, Pt(11),
                   False, False, GOLD)
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
    add_mixed_text(t, "തന്ത്രാലോകം", HEAD_FONT, Pt(30), True, False,
                   MAROON_DK)
    t2 = doc.add_paragraph()
    t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    t2.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(t2, "Tantrāloka · Malayalam Edition", HEAD_FONT, Pt(11),
                   False, True, SLATE)
    rl = doc.add_paragraph()
    rl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rl.paragraph_format.first_line_indent = Inches(0)
    hline(rl)
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.paragraph_format.first_line_indent = Inches(0)
    sub.paragraph_format.space_before = Pt(4)
    sub.paragraph_format.space_after = Pt(0)
    add_mixed_text(sub, "ഒന്നാം ഭാഗം · ഒന്നാം അദ്ധ്യായം", BODY_FONT,
                   Pt(13), True, False, SLATE)
    sub2 = doc.add_paragraph()
    sub2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub2.paragraph_format.first_line_indent = Inches(0)
    sub2.paragraph_format.space_before = Pt(0)
    add_mixed_text(sub2, "Volume One · Chapter One", HEAD_FONT, Pt(11),
                   False, False, SLATE)
    au = doc.add_paragraph()
    au.alignment = WD_ALIGN_PARAGRAPH.CENTER
    au.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(au, "അഭിനവഗുപ്തൻ · Abhinavagupta", BODY_FONT, Pt(12),
                   True, False, INK)
    au2 = doc.add_paragraph()
    au2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    au2.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(au2, "ജയരഥന്റെ വിവേകവ്യാഖ്യാനത്തോടെ — with Jayaratha's "
                   "Viveka", BODY_FONT, Pt(10.5), False, False, INK)
    ed = doc.add_paragraph()
    ed.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ed.paragraph_format.first_line_indent = Inches(0)
    ed.paragraph_format.space_before = Pt(10)
    add_mixed_text(ed, "മൂലം മലയാളലിപിയിൽ · മലയാളവ്യാഖ്യാനം", HEAD_FONT,
                   Pt(9), False, False, GREY)
    fin = doc.add_paragraph()
    fin.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fin.paragraph_format.first_line_indent = Inches(0)
    fin.paragraph_format.space_before = Pt(14)
    add_mixed_text(fin, "• • •", HEAD_FONT, Pt(10), False, False, GOLD)
    imp = doc.add_paragraph()
    imp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    imp.paragraph_format.first_line_indent = Inches(0)
    imp.paragraph_format.space_before = Pt(56)
    add_mixed_text(imp, "തന്ത്രാലോകം മലയാളപരമ്പര · ഒന്നാം ഭാഗം",
                   HEAD_FONT, Pt(8.5), False, False, GREY)


def render_intro_file(doc, E, fm):
    """ഗ്രന്ഥപരിചയം + chapter-overview + text-name index (ta_front.md)."""
    path = os.path.join(TR, "ta_front.md")
    with open(path, encoding="utf-8") as f:
        md = f.read().splitlines()
    seen_h1 = [False]
    for line in md:
        s = line.strip()
        if not s or s.startswith('# ') or s.startswith('```'):
            continue
        if s.startswith('## '):
            t = s[3:].strip()
            if t.startswith('എങ്ങനെ വായിക്കാം'):
                continue  # superseded by expanded guide
            if not seen_h1[0]:
                h = styled_heading(doc, "ഗ്രന്ഥപരിചയം", 1,
                                   anchor="fm_intro", size=Pt(16.5),
                                   color=MAROON_DK)
                fm.append((1, "ഗ്രന്ഥപരിചയം", "fm_intro"))
                seen_h1[0] = True
                if t == "ഗ്രന്ഥപരിചയം":
                    continue  # file's own H2 duplicates the H1
            styled_heading(doc, t, 2, anchor="fm_intro_%d" % len(fm),
                           size=Pt(12.5), color=MAROON)
            fm.append((2, t, "fm_intro_%d" % (len(fm))))
            continue
        if s.startswith('- ') or s.startswith('* '):
            pp = doc.add_paragraph()
            pp.paragraph_format.first_line_indent = Inches(0)
            pp.paragraph_format.left_indent = Inches(0.3)
            add_mixed_text(pp, "•  ", HEAD_FONT, None, True, False, GOLD)
            add_rich_mixed(pp, s[2:], BODY_FONT, None, INK)
            continue
        # dense mixed-script reference prose: ragged-right reads cleaner
        # than gappy justification here (frontmatter reference matter)
        pp = body_para(doc, E, s, no_indent=False)
        pp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pp.paragraph_format.first_line_indent = Inches(0)


def fm_heading(doc, text, fm, level=1, anchor=None):
    size = Pt(16.5) if level == 1 else Pt(12.5)
    color = MAROON_DK if level == 1 else MAROON
    h = styled_heading(doc, text, level, anchor=anchor, size=size,
                       color=color)
    if anchor:
        fm.append((level, text, anchor))
    return h


def build_frontmatter(doc, E, display, toc_pages=None):
    fm = []
    # half-title
    for _ in range(4):
        sp = doc.add_paragraph()
        sp.paragraph_format.first_line_indent = Inches(0)
    ht = doc.add_paragraph()
    ht.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ht.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(ht, "തന്ത്രാലോകം", HEAD_FONT, Pt(22), True, False,
                   MAROON_DK)
    ht2 = doc.add_paragraph()
    ht2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ht2.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(ht2, "ഒന്നാം ഭാഗം · ഒന്നാം അദ്ധ്യായം", BODY_FONT,
                   Pt(12), False, False, SLATE)
    doc.add_page_break()
    # series title page (§31)
    for _ in range(5):
        sp = doc.add_paragraph()
        sp.paragraph_format.first_line_indent = Inches(0)
    st = doc.add_paragraph()
    st.alignment = WD_ALIGN_PARAGRAPH.CENTER
    st.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(st, "Tantrāloka · Malayalam Series", HEAD_FONT, Pt(13),
                   False, True, SLATE)
    st2 = doc.add_paragraph()
    st2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    st2.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(st2, "തന്ത്രാലോകം മലയാളപരമ്പര", HEAD_FONT, Pt(16),
                   True, False, MAROON_DK)
    sto = doc.add_paragraph()
    sto.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sto.paragraph_format.first_line_indent = Inches(0)
    sto.paragraph_format.space_before = Pt(12)
    add_mixed_text(sto, "• • •", HEAD_FONT, Pt(10), False, False, GOLD)
    doc.add_page_break()
    # title page (§33)
    for _ in range(2):
        sp = doc.add_paragraph()
        sp.paragraph_format.first_line_indent = Inches(0)
    tp = doc.add_paragraph()
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(tp, "തന്ത്രാലോകം", HEAD_FONT, Pt(26), True, False,
                   MAROON_DK)
    tp2 = doc.add_paragraph()
    tp2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp2.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(tp2, "Tantrāloka", HEAD_FONT, Pt(14), False, True,
                   SLATE)
    tp3 = doc.add_paragraph()
    tp3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tp3.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(tp3, "Malayalam Edition · Volume One · Chapter One",
                   HEAD_FONT, Pt(10.5), False, False, SLATE)
    rl = doc.add_paragraph()
    rl.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rl.paragraph_format.first_line_indent = Inches(0)
    hline(rl)
    au = doc.add_paragraph()
    au.alignment = WD_ALIGN_PARAGRAPH.CENTER
    au.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(au, "അഭിനവഗുപ്തൻ · Abhinavagupta", BODY_FONT, Pt(14),
                   True, False, INK)
    au2 = doc.add_paragraph()
    au2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    au2.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(au2, "ജയരഥന്റെ വിവേകം എന്ന വ്യാഖ്യാനത്തോടെ — with "
                   "Jayaratha's Viveka commentary", BODY_FONT, Pt(10.5),
                   False, False, INK)
    ml = doc.add_paragraph()
    ml.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ml.paragraph_format.first_line_indent = Inches(0)
    ml.paragraph_format.space_before = Pt(8)
    add_mixed_text(ml, "മലയാളപരിഭാഷ · Malayalam translation", HEAD_FONT,
                   Pt(10), False, False, SLATE)
    doc.add_page_break()
    # edition note
    fm_heading(doc, "പതിപ്പുകുറിപ്പ്", fm, 1, "fm_edition")
    body_para(doc, E, "ഈ പതിപ്പ് മാർക്ക് ഡിക്സ്കോവ്സ്കിയുടെ ഇംഗ്ലീഷ് "
              "പരിഭാഷയെ (2023, ഒന്നാം ഭാഗം) ആധാരമാക്കിയുള്ള ചുരുക്കിയ "
              "മലയാളപതിപ്പാണ് — ഒന്നാം അദ്ധ്യായവും അനുബന്ധങ്ങളും. "
              "കാശ്മീരഗ്രന്ഥമാലയുടെ അച്ചടിമൂലം പിന്തുടരുന്നു.",
              no_indent=True)
    body_para(doc, E, "സ്വകാര്യപഠനത്തിനുള്ള പരിഭാഷണം മാത്രം.",
              no_indent=True)
    # source / translation basis (§31)
    fm_heading(doc, "ആധാരവും പരിഭാഷയും", fm, 1, "fm_basis")
    for _para in [
        "മൂലാധാരം: മാർക്ക് ഡിക്സ്കോവ്സ്കിയുടെ Tantrāloka വിവർത്തനവും "
        "വിശദകുറിപ്പുകളും (2023, Volume One, Chapter One with Jayaratha's "
        "Viveka); അച്ചടിമൂലം കാശ്മീരഗ്രന്ഥമാല.",
        "ഈ മലയാളപതിപ്പിൽ 334 മൂലശ്ലോകങ്ങൾ (കാശ്മീരസംഖ്യ 1–335, 246 "
        "ഒഴികെ), അനുബന്ധം 1 (ശബ്ദതലങ്ങൾ), അനുബന്ധം 2 (ദ്വാദശാന്തം) എന്നിവ "
        "അടങ്ങുന്നു. വിവേകവ്യാഖ്യാനം സിദ്ധാന്തച്ചുരുക്കമായി നൽകിയിരിക്കുന്നു.",
    ]:
        body_para(doc, E, _para, no_indent=True)
    # reading guide (§30)
    fm_heading(doc, "എങ്ങനെ വായിക്കാം", fm, 1, "fm_reading")
    body_para(doc, E, "ഓരോ ഭാഗവും ഈ ക്രമത്തിൽ വായിക്കുക —", no_indent=True)
    flow = doc.add_paragraph()
    flow.alignment = WD_ALIGN_PARAGRAPH.CENTER
    flow.paragraph_format.first_line_indent = Inches(0)
    flow.paragraph_format.space_before = Pt(2)
    flow.paragraph_format.space_after = Pt(2)
    shade(flow, "FFFBF0")
    box(flow, "A67C2E", "4")
    add_mixed_text(flow, "മൂലം · നേരർത്ഥം · ആചാര്യവ്യാഖ്യാനം · വിശകലനം "
                   "· അടിക്കുറിപ്പുകൾ / ചിത്രങ്ങൾ", BODY_FONT, Pt(10),
                   True, False, MAROON)
    rg = [
        "മൂലം: സ്വർണ്ണപ്പെട്ടിയിലെ സംസ്കൃതം (മലയാളലിപിയിൽ) ചൊല്ലി, "
        "തുടർന്ന് നേരർത്ഥം വായിക്കുക. മൂലപാഠം പരിഭാഷപ്പെടുത്തിയിട്ടില്ല.",
        "ആചാര്യവ്യാഖ്യാനം ജയരഥവിവേകത്തിന്റെ സിദ്ധാന്തച്ചുരുക്കമാണ്; "
        "വിശകലനം ആശയം തെളിയിക്കുന്നു.",
        "Figure N എന്ന ചിത്രം അതാത് ഭാഗത്തിന്റെ ആശയഭേദം കാട്ടുന്നു; "
        "\"Based on verses\" എന്ന വരി ഏത് ശ്ലോകങ്ങളെ ആധാരമാക്കിയെന്ന് "
        "പറയുന്നു.",
        "പ്രധാനപദങ്ങൾ ആദ്യപ്രയോഗത്തിൽ [ബ്രാക്കറ്റിൽ] വരുന്നു — "
        "ഉദാ. പരമശിവൻ [Paramaśiva].",
        "ശ്ലോകസംഖ്യകൾ കാശ്മീരപാഠപ്രകാരം അന്താരാഷ്ട്ര അക്കങ്ങളിൽ "
        "(1, 2, 3 …).",
        "അടിക്കുറിപ്പുകൾ അതാത് ഭാഗത്തിന്റെ തുടർച്ചയായ കുറിപ്പുകളാണ്; "
        "വാചകത്തിലെ (106) പോലുള്ള സംഖ്യകൾ ശ്ലോകപരാമർശങ്ങളാണ് — "
        "ഞെക്കിയാൽ ആ ഭാഗത്തേക്ക് പോകാം.",
    ]
    for item in rg:
        pp = doc.add_paragraph()
        pp.paragraph_format.first_line_indent = Inches(0)
        pp.paragraph_format.left_indent = Inches(0.3)
        add_mixed_text(pp, "•  ", HEAD_FONT, None, True, False, GOLD)
        add_rich_mixed(pp, item, BODY_FONT, None, INK)
    # textual policy (§31)
    fm_heading(doc, "പാഠനയം", fm, 1, "fm_policy")
    for _para in [
        "മൂലം സംസ്കൃതത്തിൽത്തന്നെ മലയാളലിപിയിൽ നിലനിർത്തി; മൂലപേടകത്തിനുള്ളിൽ "
        "പരിഭാഷയില്ല. ഓരോ മൂലത്തിനും തുടർന്ന് നേരർത്ഥവും വിശദീകരണവും.",
        "IAST പദങ്ങൾ ആദ്യപ്രയോഗത്തിൽ [ബ്രാക്കറ്റിൽ]; പിന്നീട് വെറും "
        "മലയാളം. ചുരുക്കപ്പേരുകൾ പട്ടിക 2-ൽ; പ്രധാന ആറെണ്ണം താഴെ.",
        "ചിത്രങ്ങൾ ആശയവ്യക്തതയ്ക്ക് മാത്രം; അലങ്കാരചിത്രങ്ങളില്ല. "
        "പട്ടികകൾ യഥാർത്ഥ പട്ടികകളായി, തലക്കെട്ട് ആവർത്തിച്ച്.",
    ]:
        body_para(doc, E, _para, no_indent=True)
    # book introduction from ta_front.md (its എങ്ങനെ-വായിക്കാം is
    # superseded by the expanded guide above — see CONTENT_CORRECTIONS)
    render_intro_file(doc, E, fm)
    # chapter architecture plate (§21)
    arch = os.path.join(BASE, "assets", "figs_v03", "fig_ARCH.png")
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
        add_mixed_text(ac, "Chapter One — section architecture · structural "
                       "overview", HEAD_FONT, Pt(E["cap_pt"]), False, True,
                       MAROON)
        keep_lines(ac)
    # contents (§16: dynamic, linked, real numbers in pass 2)
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
    # key sigla (§31: compact; full table = Table 2 in the appendix)
    doc.add_page_break()
    fm_heading(doc, "പ്രധാന ചുരുക്കപ്പേരുകൾ", fm, 1, "fm_sigla")
    for _sig in ["TA — Tantrāloka · തന്ത്രാലോകം",
                 "TAv — Viveka · വിവേകവ്യാഖ്യാനം",
                 "SvT — Svacchandatantra · സ്വച്ഛന്ദതന്ത്രം",
                 "VBh — Vijñānabhairava · വിജ്ഞാനഭൈരവം",
                 "NT — Netratantra · നേത്രതന്ത്രം",
                 "SpK — Spandakārikā · സ്പന്ദകാരിക"]:
        pp = doc.add_paragraph()
        pp.paragraph_format.first_line_indent = Inches(0)
        pp.paragraph_format.left_indent = Inches(0.3)
        add_mixed_text(pp, "•  ", HEAD_FONT, None, True, False, GOLD)
        add_rich_mixed(pp, _sig, BODY_FONT, None, INK)
    body_para(doc, E, "മുഴുവൻ പട്ടികയ്ക്ക് അനുബന്ധത്തിലെ പട്ടിക 2 കാണുക.",
              no_indent=True)
    return fm


# ---------------- appendices + colophon ----------------
def render_appendices(doc, E, F, AG):
    path = os.path.join(TR, "ta_app.md")
    with open(path, encoding="utf-8") as f:
        md = f.read().splitlines()
    styled_heading(doc, "അനുബന്ധങ്ങൾ", 1, anchor=AG.get("ch_APP"),
                   size=Pt(16.5), color=MAROON_DK)
    lp = doc.add_paragraph()
    lp.paragraph_format.first_line_indent = Inches(0)
    hline(lp)
    app1_paras = [0]
    in_app1 = [False]
    i = 0
    while i < len(md):
        line = md[i]
        i += 1
        s = line.strip()
        if not s or s.startswith('# ') or s.startswith('```'):
            continue
        if s.startswith('## '):
            t = s[3:].strip()
            if t.startswith('അനുബന്ധം'):
                parts = t.split('—', 1)
                code = 'APP1' if '൧' in parts[0] else (
                    'APP2' if '൨' in parts[0] else 'APPG')
                kick = doc.add_paragraph()
                kick.alignment = WD_ALIGN_PARAGRAPH.LEFT
                kick.paragraph_format.first_line_indent = Inches(0)
                kick.paragraph_format.space_after = Pt(0)
                add_mixed_text(kick, "Appendix " + ("1" if code == "APP1"
                               else ("2" if code == "APP2" else "")),
                               HEAD_FONT, Pt(9), True, False, GOLD)
                styled_heading(doc, parts[1].strip() if len(parts) > 1 else t,
                               1, anchor=AG.get(f"ch_{code}"),
                               size=Pt(16.5), color=MAROON_DK)
                in_app1[0] = (code == 'APP1')
                app1_paras[0] = 0
                rl = doc.add_paragraph()
                rl.paragraph_format.first_line_indent = Inches(0)
                hline(rl)
            else:
                styled_heading(doc, t, 2, anchor=AG.get("ch_APPG"),
                               size=Pt(12.5), color=MAROON)
            continue
        if s.startswith('|'):
            block = [s]
            while i < len(md) and md[i].strip().startswith('|'):
                block.append(md[i].strip())
                i += 1
            rows = [parse_md_row(t) for t in block]
            rows = [r for r in rows if not all(
                re.fullmatch(r':?---+:?', c or '---') for c in r)]
            if rows:
                if any('അളവ്' in c for c in rows[0]):
                    cap = "പട്ടിക 1 — ദ്വാദശാന്തം: തലം · അധിപൻ · സ്ഥാനം · അളവ്"
                    note = ("Source: the appendix commentary — oṅkāra ascent "
                            "in three and a half mātrās, hṛdaya to dvādaśānta.")
                else:
                    cap = ("പട്ടിക 2 — ചുരുക്കപ്പേരുകൾ: ചുരുക്കം · വിപുലരൂപം "
                           "· മലയാളം")
                    note = None
                add_word_table(doc, E, rows[0], rows[1:],
                               Pt(E["body_pt"] - 1), caption=cap,
                               source_note=note)
            continue
        if re.match(r'^[൦-൯]+\.', s):
            pp = doc.add_paragraph()
            pp.paragraph_format.first_line_indent = Inches(0)
            add_rich_mixed(pp, s, BODY_FONT, None, INK)
            for r in pp.runs:
                r.bold = True
            app1_paras[0] += 0
            continue
        pp = body_para(doc, E, s, no_indent=False)
        if in_app1[0]:
            app1_paras[0] += 1
            if app1_paras[0] == 3:
                # appendix figure: twelve sound-levels ascent
                fp = os.path.join(FIGDIR, "fig_APP1.png")
                if os.path.exists(fp):
                    up = doc.add_paragraph()
                    up.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    up.paragraph_format.first_line_indent = Inches(0)
                    up.paragraph_format.space_before = Pt(4)
                    up.paragraph_format.space_after = Pt(1)
                    keep_lines(up)
                    try:
                        up.add_run().add_picture(fp, width=E["fig_w"])
                    except Exception:
                        pass
                    keep_with_next(up)
                    cp = doc.add_paragraph()
                    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    cp.paragraph_format.first_line_indent = Inches(0)
                    cp.paragraph_format.space_after = Pt(0)
                    add_mixed_text(cp, "Figure 36 — പന്ത്രണ്ട് "
                                   "ശബ്ദതലങ്ങളുടെ കയറ്റം · നാദതലം",
                                   HEAD_FONT, Pt(E["cap_pt"]), True, False,
                                   MAROON)
                    keep_lines(cp)
                    keep_with_next(cp)
                    cs = doc.add_paragraph()
                    cs.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    cs.paragraph_format.first_line_indent = Inches(0)
                    cs.paragraph_format.space_after = Pt(6)
                    add_mixed_text(cs, "Based on Appendix 1", HEAD_FONT,
                                   Pt(E["cap_pt"] - 0.5), False, True, GREY)
                    keep_lines(cs)
    # Appendix closes on its table (the table's bottom rule is the visual
    # close). A separate closing line + ornament orphaned onto a near-empty
    # page (verified A4 p122 / Trade p192); chapters keep their ornaments.


# §28 reader glossary: (Malayalam, IAST, short English gloss, context).
# First occurrence + verse span resolved at build time from the sources.
GLOSS_V03 = [
    ("അഭിനവഗുപ്തൻ", "Abhinavagupta", "author of the Tantrāloka",
     "Kashmirian master, 10th–11th c."),
    ("അഭ്യാസം", "abhyāsa", "practice", "repeated spiritual exercise",
     "related term"),
    ("അജ്ഞാനം", "ajñāna", "ignorance", "contraction of awareness"),
    ("അനുഗ്രഹം", "anugraha", "grace", "the Lord's favour"),
    ("അനുപായം", "anupāya", "no-means", "realisation without means"),
    ("അനുത്തരം", "anuttara", "the Absolute", "the unsurpassed"),
    ("ആഗമം", "āgama", "revealed text", "scriptural revelation"),
    ("ആണവോപായം", "āṇavopāya", "individual means", "means of the bound soul"),
    ("ഉപായം", "upāya", "means", "means to realisation"),
    ("ഓങ്കാരം", "oṅkāra", "the syllable OM", "mantra ascent in Appendix 1"),
    ("കല", "kalā", "digit, phase", "energy phase; lunar digit"),
    ("കുലം", "kula", "family, body", "totality; the Heart's body"),
    ("കൗലം", "kaula", "Kaula current", "goddess-centred transmission"),
    ("ഗുരു", "guru", "teacher", "initiating master"),
    ("ചക്രം", "cakra", "wheel, cycle", "goddess-cycles; energies"),
    ("ജയരഥൻ", "Jayaratha", "commentator (Viveka)", "13th-c. exegete"),
    ("ജ്ഞാനം", "jñāna", "knowledge", "determinate awareness"),
    ("തന്ത്രം", "tantra", "tantra", "revealed ritual scripture"),
    ("തന്ത്രാലോകം", "Tantrāloka", "Light on/of the Tantras",
     "Abhinavagupta's magnum opus"),
    ("ത്രികം", "Trika", "the Triad", "threefold goddess-reality"),
    ("ദീക്ഷ", "dīkṣā", "initiation", "descent of power made ritual"),
    ("ധ്യാനം", "dhyāna", "meditation", "sustained contemplation"),
    ("ബന്ധം", "bandha", "bondage", "mala-bound contraction"),
    ("ബൈരവൻ", "Bhairava", "the Fearsome One", "plenary form of Śiva"),
    ("ഭക്തി", "bhakti", "devotion", "loving participation"),
    ("മായ", "māyā", "deluding power", "measure-taking illusion"),
    ("മണ്ഡലം", "maṇḍala", "circle, diagram", "ritual ground"),
    ("മന്ത്രം", "mantra", "sacred utterance", "articulate Śakti"),
    ("മലം", "mala", "impurity", "āṇava/māyīya/kārma stain"),
    ("മുദ്ര", "mudrā", "seal, gesture", "embodied attitude"),
    ("മോക്ഷം", "mokṣa", "liberation", "recognition of identity"),
    ("യന്ത്രം", "yantra", "device, diagram", "geometric support",
     "related term"),
    ("വിസർഗം", "visarga", "emission", "emissive pulse of the Absolute"),
    ("വിമർശം", "vimarśa", "reflective awareness", "Śakti as self-knowing"),
    ("വിജ്ഞാനം", "vijñāna", "liberating knowledge", "means-as-knowledge"),
    ("വിവേകം", "Viveka", "discernment (comm.)", "Jayaratha's commentary"),
    ("ശക്തിപാതം", "śaktipāta", "descent of power", "grace-event"),
    ("ശക്തി", "śakti", "power, energy", "parā/parāparā/aparā"),
    ("ശാക്തോപായം", "śāktopāya", "empowered means", "means of pure thought"),
    ("ശാംഭവോപായം", "śāmbhavopāya", "Śiva-means", "thought-free absorption"),
    ("ശാസ്ത്രം", "śāstra", "treatise", "authoritative exposition"),
    ("ശിഷ്യൻ", "śiṣya", "disciple", "fit recipient"),
    ("ശ്രദ്ധ", "śraddhā", "faith, confidence", "trust that opens"),
    ("സംപ്രദായം", "sampradāya", "lineage", "teacher-to-disciple flow"),
    ("സമാധി", "samādhi", "absorption", "collected stillness"),
    ("സമാവേശം", "samāveśa", "penetrative absorption", "entry into identity"),
    ("സ്പന്ദം", "spanda", "vibration", "throb of consciousness"),
    ("ഹൃദയം", "hṛdaya", "Heart", "centre of awareness"),
    ("പ്രകാശം", "prakāśa", "light", "luminous consciousness"),
    ("പ്രത്യഭിജ്ഞ", "pratyabhijñā", "recognition", "re-cognising identity"),
    ("പ്രമാതാവ്", "pramātṛ", "knower", "limited subject"),
    ("പ്രമേയം", "prameya", "knowable", "object pole"),
]


def render_glossary(doc, E):
    h = styled_heading(doc, "പദാവലി — Glossary", 1, anchor="ch_GLOSS",
                       size=Pt(16.5), color=MAROON_DK)
    lp = doc.add_paragraph()
    lp.paragraph_format.first_line_indent = Inches(0)
    hline(lp)
    order = [("ta_v02.md", "1–21"), ("ta_v03.md", "22–105"),
             ("ta_v04.md", "106–139"), ("ta_v05.md", "140–245"),
             ("ta_v06.md", "247–335"), ("ta_app.md", "App")]
    texts = {}
    for fn, _ in order:
        with open(os.path.join(TR, fn), encoding="utf-8") as f:
            texts[fn] = f.read()
    items = []
    for row in GLOSS_V03:
        ml, iast, gloss, ctx = row[:4]
        related = len(row) > 4
        span = "glossary only"
        if not related:
            for fn, sp in order:
                if ml in texts[fn]:
                    span = "verses " + sp if sp != "App" else "appendices"
                    break
        items.append((iast.lower(), ml, iast, gloss, ctx, span))
    items.sort(key=lambda x: x[0])
    for _, ml, iast, gloss, ctx, span in items:
        pp = doc.add_paragraph()
        pp.paragraph_format.first_line_indent = Inches(0)
        pp.paragraph_format.space_before = Pt(2)
        pp.paragraph_format.space_after = Pt(2)
        add_mixed_text(pp, ml + " ", BODY_FONT, None, True, False, MAROON)
        add_mixed_text(pp, "[%s] — " % iast, LATIN_FONT, None, False,
                       False, SLATE)
        add_rich_mixed(pp, "%s; %s. First occurs: %s." % (gloss, ctx,
                                                          span),
                       BODY_FONT, None, INK)
    ep = doc.add_paragraph()
    ep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ep.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(ep, "• • •", HEAD_FONT, Pt(10), False, False, GOLD)


def render_index(doc, E, index_pages):
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


def build_colophon(doc, E):
    # §38 explicit page: balanced composition, not pushed-up filler.
    for _ in range(2):
        sp = doc.add_paragraph()
        sp.paragraph_format.first_line_indent = Inches(0)
    top = doc.add_paragraph()
    top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    top.paragraph_format.first_line_indent = Inches(0)
    add_mixed_text(top, "• • •", HEAD_FONT, Pt(10), False, False, GOLD)
    styled_heading(doc, "സമാപനം · Colophon", 1, anchor="ch_COL",
                   size=Pt(16.5), color=MAROON_DK)
    lp = doc.add_paragraph()
    lp.paragraph_format.first_line_indent = Inches(0)
    hline(lp)
    body_para(doc, E, "ഇതി അഭിനവഗുപ്തവിരചിതേ തന്ത്രാലോകനാമ്നി ഒന്നാം "
              "അദ്ധ്യായം മലയാളപതിപ്പ് സമ്പൂർണ്ണം — അനുബന്ധങ്ങൾ "
              "(ശബ്ദതലങ്ങൾ, ദ്വാദശാന്തം) സഹിതം. മൂലശ്ലോകങ്ങൾ സംസ്കൃതത്തിൽ "
              "മലയാളലിപിയിൽ നിലനിർത്തി; തുടർന്ന് മലയാളത്തിൽ നേരർത്ഥവും "
              "വിശദീകരണവും നൽകി; വിവേകവ്യാഖ്യാനം ചുരുക്കി സിദ്ധാന്തഭാഗം "
              "മാത്രം നൽകി.", no_indent=True)
    prod = doc.add_paragraph()
    prod.alignment = WD_ALIGN_PARAGRAPH.CENTER
    prod.paragraph_format.first_line_indent = Inches(0)
    prod.paragraph_format.space_before = Pt(6)
    shade(prod, "FFFBF0")
    box(prod, "A67C2E", "4")
    add_mixed_text(prod, "334 root verses (1–335) · 36 figures · 13 notes "
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


# ---------------- driver ----------------
def build(edition, toc_pages=None, starts=None, index_pages=None):
    E = EDITIONS[edition]
    doc = Document()
    style_document(doc, E)
    # NOTE: pages stay white (w:background page color was tried and is
    # ignored by the LibreOffice converter, which would desync DOCX vs PDF;
    # warmth comes from the ivory plates: emblem, mula boxes, figures).
    F = Footnotes(doc, Pt(E["note_pt"]))
    AG = AnchorGen()
    display, _all = scan_headings(AnchorGen())  # TOC first (spec M)
    # cover (no folio; framed emblem plate, ivory ground)
    sec0 = doc.sections[0]
    setup_section(sec0, E, folio=False)
    build_cover(doc, E)
    # frontmatter (roman)
    doc.add_section(WD_SECTION.NEW_PAGE)
    sec_fm = doc.sections[-1]
    setup_section(sec_fm, E, footer_fmt="lowerRoman", footer_start=1)
    fm = build_frontmatter(doc, E, display, toc_pages)
    # verse→section maps for citation links (§18)
    vmaps = {}
    for fname, ml, num, en, rng, code in ORDER:
        starts_list, ch_anchor = verse_map_from_file(fname, code,
                                                     f"ch_{code}")
        vmaps[code] = (starts_list, ch_anchor)
    # chapters
    for idx, (fname, ml, num, en, rng, code) in enumerate(ORDER):
        doc.add_section(WD_SECTION.NEW_PAGE)
        sec = doc.sections[-1]
        dflt = 1 if idx == 0 else None
        start = (starts or {}).get(code, dflt)
        setup_section(sec, E,
                      header_odd=E["series_head"] + " · %s · %s"
                      % (ml, NORM(rng)),
                      header_even=None,
                      footer_fmt="decimal", footer_start=start,
                      restart_footnotes=True)
        render_chapter_file(doc, E, fname, ml, num, en, rng, code, F, AG,
                            vmaps[code])
    # appendices
    doc.add_section(WD_SECTION.NEW_PAGE)
    sec_ap = doc.sections[-1]
    setup_section(sec_ap, E,
                  header_odd=E["series_head"] + " · അനുബന്ധങ്ങൾ",
                  header_even=None,
                  footer_fmt="decimal",
                  footer_start=(starts or {}).get("APP"),
                  restart_footnotes=True)
    render_appendices(doc, E, F, AG)
    # glossary (§28)
    doc.add_section(WD_SECTION.NEW_PAGE)
    sec_gl = doc.sections[-1]
    setup_section(sec_gl, E,
                  header_odd=E["series_head"] + " · പദാവലി",
                  header_even=None,
                  footer_fmt="decimal",
                  footer_start=(starts or {}).get("GLOSS"))
    render_glossary(doc, E)
    # index (§29, auto-generated; omitted content if unavailable)
    if index_pages:
        doc.add_section(WD_SECTION.NEW_PAGE)
        sec_ix = doc.sections[-1]
        setup_section(sec_ix, E,
                      header_odd=E["series_head"] + " · സൂചിക",
                      header_even=None,
                      footer_fmt="decimal",
                      footer_start=(starts or {}).get("INDEX"))
        render_index(doc, E, index_pages)
    # colophon (§38 explicit page)
    doc.add_section(WD_SECTION.NEW_PAGE)
    sec_co = doc.sections[-1]
    setup_section(sec_co, E,
                  header_odd=E["series_head"] + " · സമാപനം",
                  header_even=None,
                  footer_fmt="decimal",
                  footer_start=(starts or {}).get("COL"))
    build_colophon(doc, E)
    F.finalize()
    # build gate: renderer anchors must equal pre-scanned TOC anchors
    scanned = set(_all)
    if set(AG.used) != scanned:
        missing = sorted(scanned - set(AG.used))
        extra = sorted(set(AG.used) - scanned)
        raise SystemExit("ANCHOR MISMATCH missing=%s extra=%s"
                         % (missing, extra))
    toc = fm + display
    doc.core_properties.title = ("Tantraloka — Volume One · Chapter One "
                                 "(Malayalam Edition v03)")
    doc.core_properties.author = ("Abhinavagupta (mula); Jayaratha (Viveka); "
                                  "Malayalam edition")
    doc.core_properties.subject = ("Tantraloka Chapter One — Malayalam trade "
                                   "edition, series style v03")
    doc.core_properties.keywords = ("Tantraloka, Abhinavagupta, Jayaratha, "
                                    "Kashmir Shaivism, Malayalam")
    doc.core_properties.language = "ml"
    doc.core_properties.comments = ("Tantraloka Malayalam Series v03; ASCII "
                                    "numbering; mula in Malayalam script")
    out = os.path.join(BASE, "pdf",
                       "Tantraloka_Malayalam_Volume1_v03_%s.docx" % E["suffix"])
    doc.save(out)
    print("saved %s (%d KB)" % (out, os.path.getsize(out) // 1024))
    return out, toc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--edition", choices=["a4", "trade"], default="a4")
    ap.add_argument("--toc", default=None,
                    help="JSON anchor->page for pass 2")
    ap.add_argument("--starts", default=None,
                    help="JSON section-code->folio-start for pass 2")
    ap.add_argument("--index", default=None,
                    help="JSON [[term,[pages]]] auto-index (pass 2+)")
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
    out, toc = build(args.edition, toc_pages, starts, index_pages)
    base = os.path.splitext(os.path.basename(out))[0]
    with open(os.path.join(BASE, "pdf", base + ".anchors.json"), "w",
              encoding="utf-8") as f:
        json.dump([{"level": l, "title": t, "anchor": a}
                   for l, t, a in toc], f, ensure_ascii=False, indent=1)
    print("anchors:", len(toc))


if __name__ == "__main__":
    main()
