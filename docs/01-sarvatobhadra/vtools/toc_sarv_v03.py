#!/usr/bin/env python3
"""Sarvatobhadra two-pass TOC/folio engine with gates (mirrors toc_pass2).
Usage: toc_sarv_v03.py {Trade|A4|Research}
"""
import json
import os
import re
import subprocess
import sys

import pymupdf

BASE = "/root/sarvatobhadra_ml"
PDFDIR = os.path.join(BASE, "build", "sarvatobhadra_v03", "pdf")
sys.path.insert(0, os.path.join(BASE, "vtools"))
from build_sarv_v03 import CHAPTERS  # noqa

VER = "v03"
ED = sys.argv[1] if len(sys.argv) > 1 else "Trade"
EDLOW = {"Trade": "trade", "A4": "a4", "Research": "research"}[ED]

_ML2EN = str.maketrans("൦൧൨൩൪൫൬൭൮൯", "0123456789")


def _nx(s):
    return s.translate(_ML2EN).strip()


def base():
    return "Sarvatobhadra_Malayalam_v03_%s" % ED


def heading_pages(pdf_path):
    d = pymupdf.open(pdf_path)
    pages = {}
    for lvl, title, pg in d.get_toc():
        pages.setdefault(title.strip(), pg)
    return d, pages


def build_pages():
    b = base()
    pdf = os.path.join(PDFDIR, b + ".pdf")
    anchors = json.load(open(os.path.join(PDFDIR, b + ".anchors.json"),
                             encoding="utf-8"))
    d, got = heading_pages(pdf)
    gotn = {_nx(k): v for k, v in got.items()}
    ml_by_code = {}
    for fname, code, chno, ml, en, _ in CHAPTERS:
        if chno:
            ml_by_code["ch_" + code] = (ml, chno)
    pages, miss = {}, []
    try:
        openers = json.load(open(os.path.join(PDFDIR, b + ".openers.json"),
                                 encoding="utf-8"))
    except Exception:
        openers = {}
    # opener anchors resolve via unique H1 titles
    for anchor, title in openers.items():
        if anchor in [a["anchor"] for a in anchors] or True:
            pg = got.get(title, gotn.get(_nx(title)))
            if pg is not None and anchor not in pages:
                # only anchors we track (display/fm); others via outline
                for a in anchors:
                    if a["anchor"] == anchor:
                        pages[anchor] = pg
                        break
    for a in anchors:
        if a["anchor"] in pages:
            continue
        t = a["title"]
        if t in got:
            pages[a["anchor"]] = got[t]
        elif _nx(t) in gotn:
            pages[a["anchor"]] = gotn[_nx(t)]
        else:
            miss.append(t)
    print("anchors:", len(anchors), "mapped:", len(pages),
          "missing:", miss[:6])
    with open(os.path.join(PDFDIR, b + ".pages.json"), "w",
              encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=1)
    starts = map_starts()
    with open(os.path.join(PDFDIR, b + ".starts.json"), "w",
              encoding="utf-8") as f:
        json.dump(starts, f, ensure_ascii=False, indent=1)
    print("folio starts:", starts)
    return pages


def map_starts():
    b = base()
    pdf = os.path.join(PDFDIR, b + ".pdf")
    d, got = heading_pages(pdf)
    gotn = {_nx(k): v for k, v in got.items()}
    starts = {}
    try:
        from build_sarv_v03 import opener_map
        openers = opener_map()
    except Exception:
        try:
            openers = json.load(open(os.path.join(PDFDIR, b + ".openers.json"),
                                     encoding="utf-8"))
        except Exception:
            openers = {}
    for anchor, title in openers.items():
        m = re.match(r"ch_([A-Z0-9]+)$", anchor)
        if not m:
            continue
        if m.group(1) == "UPO":
            continue  # upodghata stays in the roman frontmatter zone
        pg = got.get(title, gotn.get(_nx(title)))
        if pg is not None:
            starts[m.group(1)] = pg
    for key, needles in (("APPA", ["ശുദ്ധിപത്രം"]),
                         ("APPB", ["പാഠാന്തര"]),
                         ("APPC", ["അധികശ്ലോക"]),
                         ("UPO", ["ഉപോദ്ഘാതം"]),
                         ("GLOSS", ["പദാവലി — Glossary", "പദാവലി"]),
                         ("INDEX", ["സൂചിക — Index"]),
                         ("CONC", ["പരിശോധന"]),
                         ("COL", ["സമാപനം"])):
        for title, pg in got.items():
            if any(n in title for n in needles):
                starts[key] = pg
                break
    return starts


def rebuild():
    b = base()
    docx = os.path.join(PDFDIR, b + ".docx")
    print("rebuilding %s ..." % docx)
    cmd = [sys.executable, os.path.join(BASE, "vtools", "build_sarv_v03.py"),
           "--edition", EDLOW, "--toc",
           os.path.join(PDFDIR, b + ".pages.json"), "--starts",
           os.path.join(PDFDIR, b + ".starts.json")]
    if EDLOW == "research":
        cmd += ["--research"]
    if os.environ.get("SARV_INDEX_JSON"):
        cmd += ["--index", os.environ["SARV_INDEX_JSON"]]
    subprocess.run(cmd, check=True)
    subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf",
                    "--outdir", PDFDIR, docx], check=True,
                   capture_output=True)


def check_stable(pages):
    b = base()
    anchors = json.load(open(os.path.join(PDFDIR, b + ".anchors.json"),
                             encoding="utf-8"))
    try:
        openers = json.load(open(os.path.join(PDFDIR, b + ".openers.json"),
                                 encoding="utf-8"))
    except Exception:
        openers = {}
    d2 = pymupdf.open(os.path.join(PDFDIR, b + ".pdf"))
    _, got2 = heading_pages(os.path.join(PDFDIR, b + ".pdf"))
    got2n = {_nx(k): v for k, v in got2.items()}
    # every tracked anchor resolves either by its opener H1 title
    # (preferred: exact on-page text) or by display/fm title
    titles = {}
    for anchor, title in openers.items():
        titles[anchor] = title
    for a in anchors:
        titles.setdefault(a["anchor"], a["title"])
    shifts, compared = [], 0
    for anchor, t in titles.items():
        p1 = pages.get(anchor)
        p2 = got2.get(t, got2n.get(_nx(t)))
        if p1 is not None and p2 is not None:
            compared += 1
            if p1 != p2:
                shifts.append((t, p1, p2))
    print("pages:", len(d2))
    return d2, shifts, compared


def check_folios(d2, first_body=1):
    bad = []
    for i in range(len(d2)):
        pg = d2[i]
        band = pg.get_text(clip=pymupdf.Rect(
            0, pg.rect.height - 60, pg.rect.width,
            pg.rect.height)).strip().replace("\n", " ")
        m = re.match(r"^([ivxl]+|\d+)\b", band)
        if i + 1 >= first_body and m and m.group(1).isdigit():
            if int(m.group(1)) != i + 1:
                bad.append((i + 1, m.group(1)))
    return bad


if __name__ == "__main__":
    pages = build_pages()
    if len(pages) < 30:
        print("FATAL: too few mappings")
        sys.exit(1)
    rebuild()
    d2, shifts, compared = check_stable(pages)
    if shifts:
        print("PAGINATION SHIFTED:")
        for s in shifts[:10]:
            print("  ", s)
        sys.exit(2)
    print("STABLE: %d/%d headings identical" % (compared, len(pages)))
    fresh = map_starts()
    sf = os.path.join(PDFDIR, base() + ".starts.json")
    used = json.load(open(sf, encoding="utf-8"))
    if fresh != used:
        print("starts drifted — refreshing once")
        json.dump(fresh, open(sf, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        rebuild()
        d2, shifts, compared = check_stable(pages)
        print("refresh pages:", len(d2))
        if shifts:
            print("PAGINATION SHIFTED after refresh:")
            for s in shifts[:10]:
                print("  ", s)
            sys.exit(2)
        print("STABLE after refresh: %d/%d" % (compared, len(pages)))
    bad = check_folios(d2, 1)
    # frontmatter roman folios are non-digit: gate only body arabic;
    # determine body start = first arabic folio page
    if bad:
        # tolerate only pages before first chapter (frontmatter uses roman;
        # mismatches there mean a real fault only if arabic expected)
        print("FOLIO MISMATCH (absolute:printed):", bad[:12])
        sys.exit(3)
    print("FOLIOS: body folios match absolute pages")
