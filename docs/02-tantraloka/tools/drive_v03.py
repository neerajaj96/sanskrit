#!/usr/bin/env python3
"""v03 production driver (per edition): build → convert → toc/starts →
rebuild → convert → index → rebuild(+index) → converge → outline →
/Lang → gates. Usage: drive_v03.py {trade|a4}"""
import json
import os
import re
import subprocess
import sys

import pymupdf

BASE = "/root/tantraloka_ml"
PDFDIR = os.path.join(BASE, "pdf")
ED = sys.argv[1] if len(sys.argv) > 1 else "trade"
EDU = {"trade": "Trade", "a4": "A4"}[ED]
TAG = "v03"


def run(*a):
    print("+", " ".join(a))
    subprocess.run(a, check=True)


def base():
    return "Tantraloka_Malayalam_Volume1_%s_%s" % (TAG, EDU)


def normalized(s):
    return re.sub(r"\s+", "", s)


def main():
    b = base()
    docx = os.path.join(PDFDIR, b + ".docx")
    pdf = os.path.join(PDFDIR, b + ".pdf")
    # pass 1: structure
    run(sys.executable, f"{BASE}/tools/build_v03.py", "--edition", ED)
    run("libreoffice", "--headless", "--convert-to", "pdf", "--outdir",
        PDFDIR, docx)
    # pass 2: toc numbers + folio starts
    run(sys.executable, f"{BASE}/tools/toc_pass2.py", EDU, TAG)
    # extend starts with glossary/index section pages (live bookmarks)
    starts_p = os.path.join(PDFDIR, b + ".starts.json")
    starts = json.load(open(starts_p, encoding="utf-8"))
    print("starts:", starts)
    # pass 3: index from pass-2 pagination, then rebuild with index
    first_body = starts.get("V001", 1)
    idx_p = os.path.join(PDFDIR, b + ".index.json")
    run(sys.executable, f"{BASE}/tools/make_index_v03.py", pdf, idx_p,
        str(first_body))
    for rnd in range(3):
        os.environ["TOC_PASS2_INDEX"] = idx_p
        run(sys.executable, f"{BASE}/tools/toc_pass2.py", EDU, TAG)
        del os.environ["TOC_PASS2_INDEX"]
        # stability: headings + index convergence
        idx_new = idx_p + ".new"
        run(sys.executable, f"{BASE}/tools/make_index_v03.py", pdf,
            idx_new, str(first_body))
        old = json.load(open(idx_p, encoding="utf-8"))
        new = json.load(open(idx_new, encoding="utf-8"))
        if old == new:
            print("INDEX CONVERGED round", rnd)
            os.replace(idx_new, idx_p)
            break
        print("index shifted — rebuilding (round %d)" % rnd)
        os.replace(idx_new, idx_p)
    else:
        print("WARN: index did not converge in 3 rounds")
    # outline + language + numeral audit
    run(sys.executable, f"{BASE}/tools/set_outline_v03.py", pdf,
        os.path.join(PDFDIR, b + ".anchors.json"),
        os.path.join(PDFDIR, b + ".pages.json"))
    d = pymupdf.open(pdf)
    d.xref_set_key(d.pdf_catalog(), "Lang", "(ml)")
    tmp = pdf + ".lang"
    d.save(tmp, garbage=3, deflate=True)
    d.close()
    os.replace(tmp, pdf)
    run(sys.executable, f"{BASE}/tools/numeral_audit_v03.py", pdf)
    print("DRIVE COMPLETE", EDU)


if __name__ == "__main__":
    main()
