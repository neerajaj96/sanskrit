#!/usr/bin/env python3
"""Sarvatobhadra auto-index from final pagination (body range only).
Usage: make_index_sarv_v03.py <pdf> <out.json> [first_body_page]
"""
import json
import re
import sys

import pymupdf

BASE = "/root/sarvatobhadra_ml"
sys.path.insert(0, BASE + "/vtools")
from build_sarv_v03 import GLOSS_TERMS  # noqa


def main():
    pdf, out = sys.argv[1], sys.argv[2]
    first_body = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    d = pymupdf.open(pdf)
    last_body = len(d)
    for i in range(len(d)):
        if "പദാവലി—Glossary" in re.sub(r"\s+", "", d[i].get_text()):
            last_body = i
            break
    raws = [re.sub(r"\s+", "", d[i].get_text()) for i in range(len(d))]
    seen = set()
    entries = []
    for ml, ia in GLOSS_TERMS:
        if ml in seen:
            continue
        seen.add(ml)
        pages = [i + 1 for i in range(first_body - 1, last_body)
                 if ml in raws[i]]
        if pages:
            entries.append(["%s [%s]" % (ml, ia), pages])
    with open(out, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=1)
    print("index entries:", len(entries),
          "body range %d–%d" % (first_body, last_body))


if __name__ == "__main__":
    main()
