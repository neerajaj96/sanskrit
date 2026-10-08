# RELEASE_NOTES_V1_v03.md — Tantrāloka Malayalam, Volume One (v03 rebuild)

## What this is
Forensic, maximum production-grade rebuild of Volume One Chapter One +
appendices: same approved translation (byte-identical sources), completely
re-engineered edition under the v03 numeral law (all ordinary numbers in
ASCII 0–9) and house style (HOUSE_STYLE_V3.md).

## Files (in `pdf/`, v01/v02 untouched)
- `Tantraloka_Malayalam_Volume1_v03_Trade.pdf` — 219 pages, true 6×9".
- `Tantraloka_Malayalam_Volume1_v03_A4.pdf` — 134 pages.
- Companion `.docx` + `.anchors/.pages/.starts/.index.json` per trim.
- Sources: `VISUAL_MANIFEST_V3.json`, `NUMERAL_AUDIT_V3.md`,
  `PUBLISHER_FORENSIC_AUDIT_V3.md`, `CONTENT_CORRECTIONS_V3.md`,
  `HOUSE_STYLE_V3.md`, `QA_REPORT_V3.md`, `BUILD_LOG_V3.md`.
- Tools: `fig_v03.py`, `build_v03.py`, `make_index_v03.py`,
  `set_outline_v03.py`, `numeral_audit_v03.py`, `drive_v03.py`.

## New in v03
Numbered section openers (01–05 + verse spans); 37 labeled plates with
scholarly captions (`Figure N … / Based on verses …`); true footnotes
with working markers; linked verse citations (126/124, zero dead);
39-entry glossary + auto-generated page index; rebuilt appendix tables
(IAST intact); English navigational outline; bilingual cover/title;
balanced colophon explicit; continuous absolute folios; clean searchable
layer (zero fallback, zero non-ASCII digits).

## Reproduce
`tools/drive_v03.py {trade|a4}` — all quality gates run inside.
Volume Two inherits HOUSE_STYLE_V3.md.
