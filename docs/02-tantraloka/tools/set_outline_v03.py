#!/usr/bin/env python3
"""v03 custom PDF outline (§17): English L1–L3 scheme + Malayalam L4.

Reads <base>.anchors.json (Malayalam H2 titles) + <base>.pages.json
(anchor->page) + live LO auto-bookmarks (colophon/abbrev pages), then
REPLACES the outline via set_toc (page destinations — always resolving).
Usage: set_outline_v03.py <pdf> <anchors.json> <pages.json>
"""
import json
import re
import sys

import pymupdf

L3 = [
    ("ch_V001", "01 Mangalācaraṇa — Verses 1–21"),
    ("ch_V022", "02 Introduction — Verses 22–105"),
    ("ch_V106", "03 Explanation — Verses 106–139"),
    ("ch_V140", "04 Means — Verses 140–245"),
    ("ch_V247", "05 Subject Overview — Verses 247–335"),
    ("ch_APP1", "Appendix 1 — Levels of Sound"),
    ("ch_APP2", "Appendix 2 — Dvādaśānta Table"),
    ("ch_APPG", "Abbreviations"),
    ("ch_GLOSS", "Glossary"),
    ("ch_INDEX", "Index"),
    ("ch_COL", "Colophon"),
]

SKIP_ANCHORS = {"fm_edition", "fm_reading", "fm_basis", "fm_policy",
                "fm_toc", "fm_sigla"}


def norm(s):
    return re.sub(r"\s+", "", s)


_ML2EN = str.maketrans("൦൧൨൩൪൫൬൭൮൯", "0123456789")


def main():
    pdf, apath, ppath = sys.argv[1], sys.argv[2], sys.argv[3]
    anchors = json.load(open(apath, encoding="utf-8"))
    pages = json.load(open(ppath, encoding="utf-8"))
    d = pymupdf.open(pdf)
    auto = {norm(t): pg for _, t, pg in d.get_toc()}
    # resolve special pages from live headings
    extra = {}
    for key, needle in (("ch_APPG", "സംക്ഷിപ്തസൂചിക"),
                        ("ch_COL", "സമാപനം"),
                        ("ch_GLOSS", "പദാവലി"),
                        ("ch_INDEX", "സൂചിക")):
        for title, pg in auto.items():
            if needle in title:
                extra[key] = pg
                break
    by_anchor = {a["anchor"]: (a["level"], a["title"]) for a in anchors}
    toc = [[1, "Tantrāloka — Volume One (Malayalam Edition)", 1],
           [2, "Chapter One — Types of Liberating Knowledge "
               "(vijñānabheda)", pages.get("ch_V001", 7)]]
    l4 = {code: [] for code, _ in L3}
    # chapter code per anchor: ch_V001_X -> V001 etc.
    code_of = {}
    for a in anchors:
        m = re.match(r"ch_(V\d+|APP\d|APPG|GLOSS|INDEX|COL)", a["anchor"])
        if m:
            code_of[a["anchor"]] = "ch_" + m.group(1)
    order = ["ch_V001", "ch_V022", "ch_V106", "ch_V140", "ch_V247"]
    for a in anchors:
        if a["level"] != 2 or a["anchor"] in SKIP_ANCHORS:
            continue
        if a["anchor"] not in pages:
            continue
        if "_R" in a["anchor"]:
            continue  # recaps stay out of the outline (noise reduction)
        c = code_of.get(a["anchor"])
        if c in order:
            l4[c].append(a)
    for code, title in L3:
        if code in ("ch_APPG", "ch_COL", "ch_GLOSS", "ch_INDEX"):
            pg = extra.get(code)
        else:
            pg = pages.get(code)
        if pg is None:
            print("WARN no page for", code)
            continue
        toc.append([3, title, pg])
        if code in l4:
            for a in l4[code]:
                toc.append([4, a["title"].translate(_ML2EN),
                            pages[a["anchor"]]])
    d.set_toc(toc)
    d.save(pdf + ".new", garbage=3, deflate=True)
    import os
    os.replace(pdf + ".new", pdf)
    d2 = pymupdf.open(pdf)
    print("outline entries:", len(d2.get_toc()))


if __name__ == "__main__":
    main()
