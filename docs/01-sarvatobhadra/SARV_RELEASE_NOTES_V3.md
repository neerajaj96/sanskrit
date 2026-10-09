# SARV_RELEASE_NOTES_V3.md — Sarvatobhadra Malayalam, complete Gita + appendices (v03 production)

## What this is
Production-grade v03 edition of the complete Sarvatobhadra (Rajanaka
Ramakantha's Bhagavadgita commentary, KSTS LXIV) Malayalam translation:
18 chapters + Upodghata + 3 appendices, built from the locked
`translated_peak/` sources (byte-identical, render-layer fixes only)
under the v03 numeral law (all ordinary numbers in ASCII 0-9) and
series house style.

## Files (in `build/sarvatobhadra_v03/pdf/`, repo PDFs untouched)
- `Sarvatobhadra_Malayalam_v03_Trade.pdf` — 672 pages, true 6x9".
- `Sarvatobhadra_Malayalam_v03_A4.pdf` — 378 pages.
- `Sarvatobhadra_Malayalam_v03_Research.pdf` — 404 pages (A4 + print
  concordance appendix).
- Companion `.docx` + `.anchors/.pages/.starts/.index/.openers/.h2.json`
  per edition.
- Sources: `SARV_VISUAL_MANIFEST_V3.json`, `SARV_NUMERAL_AUDIT_V3.md`,
  `SARV_CONTENT_CORRECTIONS_V3.md`, `SARV_QA_REPORT_V3.md`,
  `SARV_BUILD_LOG_V3.md`.
- Tools: `vtools/build_sarv_v03.py`, `fig_sarv_v03.py`,
  `toc_sarv_v03.py`, `drive_sarv_v03.py`, `make_index_sarv_v03.py`,
  `set_outline_sarv_v03.py`, `numeral_audit_sarv_v03.py`.

## New in v03
Numbered chapter openers (01-18 + yoga names + print spans); 8 labeled
plates with scholarly captions (`Figure N … / Based on verses …`);
true footnotes for logged editorial notes only; linked dotted verse
citations (zero dead); granthika glossary with first-use `[IAST]` +
auto-generated page index (converged); print concordance (Research);
rebuilt appendix tables (IAST intact); English navigational outline
(~430 entries); bilingual cover/title; balanced colophon with retained
Arabic OCR example on its own centered line; continuous absolute
folios (roman frontmatter + Upodghata); clean searchable layer (zero
fallback except the approved colophon Arabic, zero non-ASCII digits,
zero control chars).

## Reproduce
`vtools/drive_sarv_v03.py {trade|a4|research}` — all quality gates run
inside. Freeze code during a drive. Never push without explicit
instruction.
