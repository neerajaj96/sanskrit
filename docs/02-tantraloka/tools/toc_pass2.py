#!/usr/bin/env python3
"""Two-pass TOC page numbers + pagination stability check.

Pass 1 PDF bookmarks (exported from Word headings by LibreOffice) give
heading->page. Map onto builder anchors (anchors.json), rebuild DOCX with
--toc pages.json, reconvert, and verify every heading lands on the same page
(pagination stability gate for spec M/U).
"""
import json
import os
import re
import subprocess
import sys

import pymupdf

import sys as _sys
sys_path_base = os.path.dirname(os.path.abspath(__file__))
if sys_path_base not in _sys.path:
    _sys.path.insert(0, sys_path_base)
from build_v02 import ORDER as ORDER_SRC

BASE = "/root/tantraloka_ml"
PDFDIR = os.path.join(BASE, "pdf")


def heading_pages(pdf_path):
    d = pymupdf.open(pdf_path)
    pages = {}
    for lvl, title, pg in d.get_toc():
        pages.setdefault(title.strip(), pg)
    # full-text fallback for anchors whose TOC title != heading text
    full = "\n".join(p.get_text() for p in d)
    return d, pages


SECTION_ANCHORS = {"ch_V001": "V001", "ch_V022": "V022",
                   "ch_V106": "V106", "ch_V140": "V140",
                   "ch_V247": "V247", "ch_APP": "APP", "ch_COL": "COL"}


def build_pages(ed_suffix, anchors_name, out_name):
    pdf = os.path.join(PDFDIR, "Tantraloka_Malayalam_Volume1_v02_%s.pdf" % ed_suffix)
    anchors = json.load(open(os.path.join(PDFDIR, anchors_name), encoding="utf-8"))
    d, got = heading_pages(pdf)
    pages = {}
    miss = []
    for a in anchors:
        t = a["title"]
        if t in got:
            pages[a["anchor"]] = got[t]
        else:
            miss.append(t)
    # known title divergences (TOC display title vs on-page heading)
    alias = {
        "അനുബന്ധം ൧ — നേത്രതന്ത്രപ്രകാരം ശബ്ദതലങ്ങൾ":
            "നേത്രതന്ത്രപ്രകാരം ശബ്ദതലങ്ങൾ",
        "അനുബന്ധം ൨ — ദ്വാദശാന്തം താരതമ്യപ്പട്ടിക":
            "ദ്വാദശാന്തം താരതമ്യപ്പട്ടിക",
        "അനുബന്ധങ്ങൾ — ശബ്ദതലങ്ങൾ · ദ്വാദശാന്തം": "അനുബന്ധങ്ങൾ",
    }
    for t in list(miss):
        if t in alias and alias[t] in got:
            for a in anchors:
                if a["title"] == t:
                    pages[a["anchor"]] = got[alias[t]]
            miss.remove(t)
    print("anchors:", len(anchors), "mapped:", len(pages), "missing:", miss)
    with open(os.path.join(PDFDIR, out_name), "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=1)
    # explicit absolute folio starts per section (spec O): LibreOffice
    # restarts numbering at each DOCX section unless given an explicit
    # start, which would desync printed folios from TOC numbers.
    # Look up ON-PAGE section-opening headings in the PDF bookmarks.
    d, got = heading_pages(pdf)
    starts = {}
    want = {}
    for fname, title, short, code in ORDER_SRC:
        if code != "APP":
            want[code] = title
    want["APP"] = "അനുബന്ധങ്ങൾ"
    want["COL"] = "സമാപനം · കൊളോഫൺ"
    for code, ht in want.items():
        if ht in got:
            starts[code] = got[ht]
    starts_name = out_name.replace(".pages.json", ".starts.json")
    with open(os.path.join(PDFDIR, starts_name), "w", encoding="utf-8") as f:
        json.dump(starts, f, ensure_ascii=False, indent=1)
    print("folio starts:", starts)
    return pages


def convert(docx):
    subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf",
                    "--outdir", PDFDIR, docx], check=True,
                   capture_output=True)


def verify(pdf_path, pages, label):
    d = pymupdf.open(pdf_path)
    _, got = heading_pages(pdf_path)
    bad = []
    for anchor, pg in pages.items():
        pass
    # re-derive mapping and compare page-per-title
    import json as j
    return len(d)


if __name__ == "__main__":
    ed = sys.argv[1] if len(sys.argv) > 1 else "A4"  # A4 | Trade
    edlow = ed.lower()
    anchors_name = "Tantraloka_Malayalam_Volume1_v02_%s.anchors.json" % ed
    out_name = "Tantraloka_Malayalam_Volume1_v02_%s.pages.json" % ed
    pages = build_pages(ed, anchors_name, out_name)
    if len(pages) < 45:
        print("FATAL: too few mappings")
        sys.exit(1)
    docx = os.path.join(PDFDIR, "Tantraloka_Malayalam_Volume1_v02_%s.docx" % ed)
    print("rebuilding %s with page numbers..." % docx)
    subprocess.run([sys.executable, os.path.join(BASE, "tools", "build_v02.py"),
                    "--edition", edlow, "--toc",
                    os.path.join(PDFDIR, out_name), "--starts",
                    os.path.join(PDFDIR, out_name.replace(
                        ".pages.json", ".starts.json"))], check=True)
    convert(docx)
    # stability: heading pages must be unchanged after TOC numbers added
    d2 = pymupdf.open(os.path.join(
        PDFDIR, "Tantraloka_Malayalam_Volume1_v02_%s.pdf" % ed))
    anchors = json.load(open(os.path.join(PDFDIR, anchors_name),
                             encoding="utf-8"))
    _, got2 = heading_pages(os.path.join(
        PDFDIR, "Tantraloka_Malayalam_Volume1_v02_%s.pdf" % ed))
    alias = {
        "അനുബന്ധം ൧ — നേത്രതന്ത്രപ്രകാരം ശബ്ദതലങ്ങൾ":
            "നേത്രതന്ത്രപ്രകാരം ശബ്ദതലങ്ങൾ",
        "അനുബന്ധം ൨ — ദ്വാദശാന്തം താരതമ്യപ്പട്ടിക":
            "ദ്വാദശാന്തം താരതമ്യപ്പട്ടിക",
        "അനുബന്ധങ്ങൾ — ശബ്ദതലങ്ങൾ · ദ്വാദശാന്തം": "അനുബന്ധങ്ങൾ",
    }
    shifts = []
    for a in anchors:
        t = a["title"]
        key = alias.get(t, t)
        p1 = pages.get(a["anchor"])
        p2 = got2.get(key)
        if p1 is not None and p2 is not None and p1 != p2:
            shifts.append((t, p1, p2))
    print("pass2 pages:", len(d2))
    if shifts:
        print("PAGINATION SHIFTED:")
        for s in shifts:
            print("  ", s)
        sys.exit(2)
    print("STABLE: all %d headings on identical pages" % len(pages))
    # folio gate: printed body folios must equal absolute page numbers
    bad_folio = []
    for i in range(len(d2)):
        pg = d2[i]
        band = pg.get_text(clip=pymupdf.Rect(
            0, pg.rect.height - 60, pg.rect.width,
            pg.rect.height)).strip().replace("\n", " ")
        m = re.match(r"^([ivxl]+|\d+)\b", band)
        if i >= 6 and m and m.group(1).isdigit():
            if int(m.group(1)) != i + 1:
                bad_folio.append((i + 1, m.group(1)))
    if bad_folio:
        print("FOLIO MISMATCH (absolute:printed):", bad_folio[:12])
        sys.exit(3)
    print("FOLIOS: body folios match absolute pages")
