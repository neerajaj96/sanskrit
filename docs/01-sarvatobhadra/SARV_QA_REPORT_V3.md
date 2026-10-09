# SARV_QA_REPORT_V3.md — Sarvatobhadra v03 final quality gate
Artifacts: `build/sarvatobhadra_v03/pdf/Sarvatobhadra_Malayalam_v03_{Trade,A4,Research}.pdf`
(Trade 6×9, A4, Research A4+concordance) + DOCX + anchors/pages/starts/
index/openers/h2 JSONs. Repo PDFs untouched.

## Gate results (per edition; identical unless noted)
| Check | Result |
|---|---|
| Source fidelity (translated_peak byte-identical; fixes render-layer) | PASS (md5 re-verified at release) |
| Verse inventory vs print (Kashmir counts incl. extras) | complete; ch18 split-footnoted |
| Mula marks ASCII in layer | ~1236/file-set, 0 ML digits |
| FFFD / PUA / control chars in layer | 0 / 0 / 0 |
| Fallback spans | ZERO except approved colophon Arabic (2 chars, DejaVu Sans) |
| Embedded families | exactly the locked 3 + approved fallback |
| Footnotes (editorial textual notes only) | true notes, unsplit, markers correct |
| TOC linked + real absolute numbers, 0-shift | PASS |
| Folios == absolute (body), roman frontmatter+upodghata | PASS |
| Outline (Book/Chapters/Appendices/Reference + H2s) | ~430 entries, exact landing |
| Cross-ref links (dotted ch.v) | 0 dead (verified programmatically) |
| Figures (8 plates + emblem, labeled, captioned) | verified in situ |
| Tables (real, repeated headers, intact rows, IAST unbroken) | verified |
| Glossary (granthika terms + first-use spans) + auto-index (converged) | verified |
| Research concordance (source ranges + recension extras) | Research only, verified |
| Occupancy <45%: structural pages only (closes, openers, table tails) | triaged, none orphan |
| Orphan headings/ornaments/captions | none (keepNext-bound; verified rescan) |
| Chapter/major openers suppress heads | verified |
| Cover/title/colophon/frontmatter order | verified rendered |
| Metadata + /Lang=ml | set, verified |

## Visual QA coverage (90–200 dpi)
cover, series/title, edition/basis/policy/guide, intro, architecture,
TOC, sigla, openers (01/02/04 samples), mula close-ups, labeled plates,
speaker labels, footnotes + marker close-ups, recaps, appendix openers,
APP1-class tables, dvādaśānta-class tables, glossary, index,
concordance, colophon, trade interior density, low-page triage (all).

## Residuals (accepted, logged)
- Narrow-trim table cells wrap long compounds mid-word (single-word
  cells; landscape reserved, never needed).
- Chapter-end colophon closes and table-tail short pages: conventional
  end-matter rhythm.
- Dual footnote apparatus N/A (no note apparatus in sources; only
  editorial textual notes exist).
- Combined running heads (converter limitation, documented).

## Verdict: PASS on all releasable criteria. No P0/P1/P2 open.

## Post-QA re-drive note
A follow-up scan found U+0002 STX artifacts inside the colophon Arabic
example on A4 p378 and Research p404 (Trade clean) — the 0-control row
above is re-verified AFTER the layout fix (`build_colophon` centered
example line) and full three-edition re-drive: 0 / 0 / 0 on all trims,
numeral PASS, index converged round 0. See SARV_BUILD_LOG_V3 incident 8
and SARV_CONTENT_CORRECTIONS_V3 CC-S5.
