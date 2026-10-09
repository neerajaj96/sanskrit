# SARV_BUILD_LOG_V3.md — Sarvatobhadra v03 production record

## Pipeline (all new, in `vtools/`)
`build_sarv_v03.py` (DOCX→LibreOffice) + `fig_sarv_v03.py` (8 plates) +
`toc_sarv_v03.py` (maps/starts/gates) + `drive_sarv_v03.py` (orchestration)
+ `make_index_sarv_v03.py` + `set_outline_sarv_v03.py` +
`numeral_audit_sarv_v03.py`. Tantraloka v03 patterns reused (proven
mechanisms: explicit run fonts, unlink+clear sections, absolute folio
starts, two-pass TOC, index fixpoint, custom outline, /Lang post-write).

## Flow incidents and fixes
1. **Hard-wrapped sources**: translated_peak wraps at ~70 chars/line; first
   build treated every line as a paragraph (851pp, rivers). Fixed with a
   shared `iter_blocks()` paragraph joiner used by all renderers.
2. **tblGrid equal-split**: LO lays out from the grid, not tcW — set both
   (measured P1-class defect class, same as Tantraloka).
3. **AnchorGen sharing**: scan and render briefly shared one instance
   (every anchor `_2`-suffixed); gate caught it; scan takes a fresh one.
4. **Stale starts poisoning**: removed blind preservation; live discovery
   + starts-refresh fixpoint (index insertion shifts only the colophon).
5. **Mid-drive code edit**: stability gate correctly failed the run;
   clean re-drive converged.
6. **Weak stability (12/33)**: display titles ≠ on-page H1s by design;
   opener-title resolution now compares ~60 headings.
7. **Upodghata**: missing from first builds (loop skipped chno=0 files);
   restored as its own roman-zone section.
8. **Colophon Arabic split (post-QA catch)**: A4/Research exports broke
   the 2-letter RTL example من across lines and emitted U+0002 STX into
   the text layer (Trade unaffected); QA's 0-control claim was
   re-scanned and falsified. Fixed layout-only in `build_colophon` —
   the example now sits on its own centered line
   (`ഉദാഹരണം: ('من' മുതലായവ)`), mid-line in every trim — and all
   three editions re-driven clean (0 controls, numeral PASS).

## Outputs (build/sarvatobhadra_v03/pdf/)
Trade 672pp + A4 378pp + Research 404pp (concordance appendix); DOCX per trim;
anchors/pages/starts/index/openers/h2 JSONs. Gates inside every drive:
mapping ≥30, 0-shift stability, folios==absolute, index convergence ≤3,
custom outline, /Lang=ml, numeral audit exit 0.

## Repro
`vtools/drive_sarv_v03.py {trade|a4|research}` alone reproduces everything.
Freeze code during a drive. Never push without explicit instruction.
