#!/usr/bin/env python3
"""Sarvatobhadra custom outline: L1 Book, L2 chapters/appendices/reference,
L3 Malayalam H2s. L3 pages via document-order alignment of expected headings
against LO auto-bookmarks (handles duplicate titles like "ശ്ലോകം 1").
Usage: set_outline_sarv_v03.py <pdf> <anchors.json> <pages.json>
"""
import json
import os
import re
import sys

import pymupdf

_ML2EN = str.maketrans("൦൧൨൩൪൫൬൭൮൯", "0123456789")


def nx(s):
    return re.sub(r"\s+", "", s.translate(_ML2EN))


CH_EN = {1: "Arjunaviṣādayoga", 2: "Sāṅkhyayoga", 3: "Karmayoga",
         4: "Jñānakarmasannyāsayoga", 5: "Karmasannyāsayoga",
         6: "Dhyānayoga", 7: "Jñānavijñānayoga", 8: "Akṣarabrahmayoga",
         9: "Rājavidyārājaguhyayoga", 10: "Vibhūtiyoga",
         11: "Viśvarūpadarśanayoga", 12: "Bhaktiyoga",
         13: "Kṣetrakṣetrajñavibhāgayoga", 14: "Guṇatrayavibhāgayoga",
         15: "Puruṣottamayoga", 16: "Daivāsurasampadvibhāgayoga",
         17: "Śraddhātrayavibhāgayoga", 18: "Mokṣasannyāsayoga"}
CH_SPAN = {1: "1–47", 2: "1–74", 3: "1–48", 4: "1–42", 5: "1–28",
           6: "1–49", 7: "1–30", 8: "1–28", 9: "1–35", 10: "1–42",
           11: "1–60", 12: "1–20", 13: "1–34", 14: "1–27", 15: "1–20",
           16: "1–24", 17: "1–28", 18: "1–79"}


def main():
    import os
    pdf, apath, ppath = sys.argv[1], sys.argv[2], sys.argv[3]
    pdfdir = os.path.dirname(pdf)
    base = os.path.splitext(os.path.basename(pdf))[0]
    anchors = json.load(open(apath, encoding="utf-8"))
    pages = json.load(open(ppath, encoding="utf-8"))
    try:
        h2 = json.load(open(os.path.join(pdfdir, base + ".h2.json"),
                            encoding="utf-8"))
    except Exception:
        h2 = []
    try:
        openers = json.load(open(os.path.join(pdfdir, base + ".openers.json"),
                                 encoding="utf-8"))
    except Exception:
        openers = {}
    d = pymupdf.open(pdf)
    lo = [(lvl, t.strip(), pg) for lvl, t, pg in d.get_toc()]

    # Step 1: locate opener pages via unique H1 titles.
    opages = {}
    for anchor, title in openers.items():
        nt = nx(title)
        for lvl, t, pg in lo:
            if nx(t) == nt:
                opages[anchor] = pg
                break

    # Step 2: per opener, H2s lie between its page and the next opener.
    resolved = {}
    bounds = sorted(opages.values())
    code_page = dict(opages)
    # map anchor prefix -> code
    for h in h2:
        m = re.match(r"ch_([A-Z0-9]+?)(?:_V|_h|_intro)", h["anchor"])
        code = m.group(1) if m else None
        opg = code_page.get("ch_" + code) if code else None
        if opg is None:
            # appendix/upo H2s: bound by their opener too
            m2 = re.match(r"ch_((?:APP|UPO)[A-Z]*)", h["anchor"])
            if m2 and ("ch_" + m2.group(1)) in code_page:
                opg = code_page["ch_" + m2.group(1)]
        if opg is None:
            continue
        # next opener page after opg
        nxt = min([p for p in bounds if p > opg] + [10 ** 9])
        nt = nx(h["title"])
        for lvl, t, pg in lo:
            if opg <= pg < nxt and nx(t) == nt:
                # take first unclaimed match in range (doc order)
                if h["anchor"] not in resolved:
                    resolved[h["anchor"]] = pg
                    break
    # assemble outline
    toc = [[1, "Sarvatobhadra — Book One (Malayalam)", 1]]
    # chapters L2 in order with L3 children
    for ch in range(1, 19):
        pg = None
        for a in anchors:
            if a["anchor"] in (f"ch_CH{ch:02d}", f"ch_CH{ch:02d}A",
                               f"ch_CH{ch:02d}B", f"ch_CH{ch:02d}C"):
                if a["anchor"] in pages:
                    pg = pages[a["anchor"]]
                    break
        if pg is None:
            # from openers
            for anchor, p in opages.items():
                if re.match(r"ch_CH%02d[A-C]?$" % ch, anchor):
                    pg = p
                    break
        if pg is None:
            print("WARN no page ch", ch)
            continue
        toc.append([2, "%02d %s — Verses %s" % (ch, CH_EN[ch],
                                                CH_SPAN[ch]), pg])
        for h in h2:
            if h["anchor"] in resolved and re.match(
                    r"ch_CH%02d[A-C]?_" % ch, h["anchor"]):
                toc.append([3, h["title"].translate(_ML2EN),
                            resolved[h["anchor"]]])
    for anchor, title in (("ch_UPO", "Upodghāta"),
                          ("ch_APPA", "Appendix 1 — Corrigenda"),
                          ("ch_APPB", "Appendix 2 — Variant readings"),
                          ("ch_APPC", "Appendix 3 — Additional verses"),
                          ("ch_GLOSS", "Glossary"),
                          ("ch_INDEX", "Index"),
                          ("ch_CONC", "Print concordance"),
                          ("ch_COL", "Colophon")):
        pg = pages.get(anchor)
        if pg is None:
            for a2, p in opages.items():
                if a2 == anchor:
                    pg = p
                    break
        if pg is None:
            for t, p in auto_title_page(d, title):
                pg = p
                break
        if pg is None:
            print("WARN no page", anchor)
            continue
        toc.append([2, title, pg])
    d.set_toc(toc)
    d.save(pdf + ".new", garbage=3, deflate=True)
    import os
    os.replace(pdf + ".new", pdf)
    print("outline entries:", len(pymupdf.open(pdf).get_toc()))


def auto_title_page(d, title):
    for _, t, pg in d.get_toc():
        if title.lower() in t.lower():
            yield t, pg


if __name__ == "__main__":
    main()
