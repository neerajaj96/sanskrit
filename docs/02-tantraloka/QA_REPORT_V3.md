# QA_REPORT_V3.md — final quality gate (both trims)

Artifacts: `pdf/Tantraloka_Malayalam_Volume1_v03_Trade.pdf` (218pp, 6×9"),
`pdf/Tantraloka_Malayalam_Volume1_v03_A4.pdf` (134pp), companion DOCX +
`.anchors/.pages/.starts/.index.json`. v01/v02 outputs untouched.

## Gate results (§0–§38)
| Check | Trade | A4 |
|---|---|---|
| NUMERAL_AUDIT: non-ASCII decimals in layer | 0 — PASS | 0 — PASS |
| Verse inventory (Kashmir 1–335 minus 246) | 334/334 exact | 334/334 exact |
| Verse marks ASCII (॥ N ॥) | 334 | 334 |
| FFFD / PUA / control chars | 0 / 0 | 0 / 0 |
| Fallback-font spans | ZERO (7 locked subsets) | ZERO (same) |
| Mula order / dandas / IAST brackets | ascending, clean, valid | same sources |
| Footnotes (13, rule, global markers, no orphans) | verified rendered | verified |
| TOC: linked, dot leaders, real absolute numbers | 53 anchors, 0-shift | 53 anchors, 0-shift |
| Folios == absolute (body), roman frontmatter | gate passes | gate passes |
| Outline (§17 custom scheme) | 48 entries, exact landing | 48 entries |
| Cross-ref links (§18) | 126 links, 0 dead | 124 links, 0 dead |
| Figures (36 + architecture, labeled, captioned) | verified in situ | verified |
| Tables (real, repeated headers, IAST unbroken) | verified cell-by-cell | verified |
| Glossary (39) + auto-index (37 entries, converged) | verified | verified |
| Occupancy <45%: only structural pages | 10 flags, all structural | 6 flags, all structural |
| Orphan headings/ornaments/captions/diagrams | none | none |
| Chapter/major openers suppressed heads | verified | verified |
| Cover/title/colophon/frontmatter order (§31–33,38) | verified rendered | verified |
| Metadata + /Lang=ml | set, verified | set, verified |

## Visual QA coverage (110–220 dpi)
cover, series/title pages, edition/basis/policy, guide flow-plate,
intro, architecture plate, TOC, sigla, 01/02/04 openers, mula close-up,
labeled triad/ladder/sound plates, footnote markers 1/2/3/4/5 close-ups,
recap, appendix openers, APP1, dvādaśānta + abbreviation tables (incl.
gridCol fix verification), glossary, index, colophon, trade interior.

## Residuals (accepted, logged)
- Malayalam compound mid-word breaks in narrow table cells (single-word
  cells; landscape reserved, never needed).
- One footnote-adjacent short page per volume (structural cost of
  keep-intact figure units; alternative — splitting units — is worse).
- Dual footnote apparatus (global markers + per-part titles; converter
  limitation, BUILD_LOG).
- Combined (non-parity) running heads (converter limitation).

## Verdict: PASS on all releasable criteria. No P0/P1/P2 open.
