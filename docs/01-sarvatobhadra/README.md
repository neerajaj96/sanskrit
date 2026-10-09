# Doc 1 — Sarvatobhadra Malayalam

Complete Malayalam translation of the Bhagavadgītā with Rājānaka
Rāmakāṇṭha's Sarvatobhadra commentary (KSTS No. LXIV).

- `Sarvatobhadra_Malayalam.pdf` — Book 1, scholarly verbatim rendering
  (mūla in Malayalam script). Also released as `part-19`.
- `Sarvatobhadra_Layman.pdf` — Book 2, beginner-friendly rendering with
  one-line essence per verse. Also released as `layman-14`.

Sources live in the build workspace (`sarvatobhadra_ml/`); this folder
ships the readable PDFs. Latest release assets supersede earlier ones.

## v03 — maximum production-grade rebuild (locked `translated_peak/` sources, byte-identical)
- `Sarvatobhadra_Malayalam_v03_Trade.pdf` (+ `.docx`) — 672 pages, true
  6×9″ reflow. `Sarvatobhadra_Malayalam_v03_A4.pdf` (+ `.docx`) — 378
  pages. `Sarvatobhadra_Malayalam_v03_Research.pdf` (+ `.docx`) — 404
  pages (A4 + print concordance appendix).
- Numeral law: every ordinary number in ASCII 0–9 (render layer;
  `SARV_NUMERAL_AUDIT_V3.md` gate, PASS on all trims).
- Numbered chapter openers (01–18 + yoga names + print spans); 8 labeled
  plates (`assets_sarv_v03/`, `vtools/fig_sarv_v03.py`) with scholarly
  captions (`Figure N … / Based on verses …`; manifest
  `SARV_VISUAL_MANIFEST_V3.json`).
- True footnotes for logged editorial notes only; dotted verse citations
  hyperlinked (zero dead links); rebuilt appendix tables (IAST intact);
  granthika glossary (`GLOSSARY.md`) with first-use `[IAST]` +
  auto-generated page index (converged); English navigational outline;
  bilingual cover/title; balanced colophon (Arabic OCR example retained
  on its own centered line); continuous absolute folios.
- Paper trail: authority lock `SARVATOBHADRA_AUTHORITY_LOCK_V3.md`
  (production input ruling + verse reconciliation vs print), corrections
  `SARV_CONTENT_CORRECTIONS_V3.md` (render-layer only, evidence-pinned),
  QA `SARV_QA_REPORT_V3.md` (PASS), log `SARV_BUILD_LOG_V3.md`, notes
  `SARV_RELEASE_NOTES_V3.md`.
- Repro: `vtools/drive_sarv_v03.py {trade|a4|research}` (all gates inside).
- `translated_peak/` — 27 production source files (sole input of the
  build; untouched, fixes applied at render).

Note: pushed here by explicit override of the project's local-only
rule for this release.
