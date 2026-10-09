#!/usr/bin/env python3
"""SARV numeral audit (§0): zero non-ASCII decimals in output or FAILURE.
Usage: numeral_audit_sarv_v03.py <pdf> ; writes SARV_NUMERAL_AUDIT_V3.md
"""
import collections
import os
import re
import sys

import pymupdf

BASE = "/root/sarvatobhadra_ml"
NONASCII_ND = re.compile(
    "[\u0660-\u0669\u06f0-\u06f9\u0966-\u096f\u09e6-\u09ef"
    "\u0a66-\u0a6f\u0ae6-\u0aef\u0b66-\u0b6f\u0be6-\u0bef"
    "\u0c66-\u0c6f\u0ce6-\u0cef\u0d66-\u0d6f\u0de6-\u0def"
    "\u0e50-\u0e59\u0ed0-\u0ed9\u0f20-\u0f29\u1040-\u1049"
    "\u17e0-\u17e9\u1810-\u1819\uff10-\uff19]")
SCRIPTS = {"\u0d66": "Malayalam", "\u0b66": "Oriya", "\u0966": "Devanagari",
           "\u0660": "Arabic-Indic", "\u06f0": "Ext-Arabic-Indic"}


def script_of(ch):
    for k, v in SCRIPTS.items():
        if k <= ch <= chr(ord(k) + 9):
            return v
    return hex(ord(ch))


def main():
    pdf = sys.argv[1]
    d = pymupdf.open(pdf)
    raw = "".join(p.get_text() for p in d)
    hits = NONASCII_ND.findall(raw)
    by = collections.Counter(script_of(c) for c in hits)
    marks = re.findall(r"॥\s*([0-9]+)\s*॥", raw)
    lines = [
        "# SARV_NUMERAL_AUDIT_V3.md — §0 gate",
        "",
        "Policy: every ordinary book number in ASCII 0–9.",
        "",
        "## PDF scan (%s, %d pages)" % (os.path.basename(pdf), len(d)),
        "- Non-ASCII decimal hits: **%d** %s" % (
            len(hits), dict(by) if hits else "(none)"),
        "- ASCII verse marks (॥ N ॥): %d unique %d" % (
            len(marks), len(set(marks))),
        "- Verdict: **%s**" % ("BUILD FAILURE" if hits else "PASS"),
        "",
        "Status: %s" % ("FAIL" if hits else "PASS — release allowed"),
    ]
    open(os.path.join(BASE, "SARV_NUMERAL_AUDIT_V3.md"), "w",
         encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
