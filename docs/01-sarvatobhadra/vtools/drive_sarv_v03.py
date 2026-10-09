#!/usr/bin/env python3
"""Sarvatobhadra v03 production driver (per edition).
Usage: drive_sarv_v03.py {trade|a4|research}
Flow: build → convert → toc/starts → rebuild → convert → index →
index rounds (≤3) → outline → /Lang → numeral audit.
"""
import json
import os
import subprocess
import sys

import pymupdf

BASE = "/root/sarvatobhadra_ml"
PDFDIR = os.path.join(BASE, "build", "sarvatobhadra_v03", "pdf")
ED = sys.argv[1] if len(sys.argv) > 1 else "trade"
EDU = {"trade": "Trade", "a4": "A4", "research": "Research"}[ED]


def run(*a):
    print("+", " ".join(a))
    subprocess.run(a, check=True)


def base():
    return "Sarvatobhadra_Malayalam_v03_%s" % EDU


def main():
    b = base()
    docx = os.path.join(PDFDIR, b + ".docx")
    pdf = os.path.join(PDFDIR, b + ".pdf")
    run(sys.executable, f"{BASE}/vtools/build_sarv_v03.py", "--edition", ED)
    run("libreoffice", "--headless", "--convert-to", "pdf", "--outdir",
        PDFDIR, docx)
    run(sys.executable, f"{BASE}/vtools/toc_sarv_v03.py", EDU)
    starts = json.load(open(os.path.join(PDFDIR, b + ".starts.json"),
                            encoding="utf-8"))
    print("starts:", starts)
    first_body = starts.get("CH01", 1)
    idx_p = os.path.join(PDFDIR, b + ".index.json")
    run(sys.executable, f"{BASE}/vtools/make_index_sarv_v03.py", pdf,
        idx_p, str(first_body))
    for rnd in range(3):
        os.environ["SARV_INDEX_JSON"] = idx_p
        run(sys.executable, f"{BASE}/vtools/toc_sarv_v03.py", EDU)
        del os.environ["SARV_INDEX_JSON"]
        idx_new = idx_p + ".new"
        run(sys.executable, f"{BASE}/vtools/make_index_sarv_v03.py", pdf,
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
    run(sys.executable, f"{BASE}/vtools/set_outline_sarv_v03.py", pdf,
        os.path.join(PDFDIR, b + ".anchors.json"),
        os.path.join(PDFDIR, b + ".pages.json"))
    d = pymupdf.open(pdf)
    d.xref_set_key(d.pdf_catalog(), "Lang", "(ml)")
    tmp = pdf + ".lang"
    d.save(tmp, garbage=3, deflate=True)
    d.close()
    os.replace(tmp, pdf)
    run(sys.executable, f"{BASE}/vtools/numeral_audit_sarv_v03.py", pdf)
    print("DRIVE COMPLETE", EDU)


if __name__ == "__main__":
    main()
