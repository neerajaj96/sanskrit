# QA_REPORT_V1_v02.md — final quality gate (both editions)

Artifacts: `pdf/Tantraloka_Malayalam_Volume1_v02_A4.pdf` (124pp),
`pdf/Tantraloka_Malayalam_Volume1_v02_Trade.pdf` (6×9", 195pp),
companion DOCX + `.anchors/.pages/.starts.json`. v01 untouched.

## Gate results (identical both editions unless noted)
| Check | Spec | A4 | Trade |
|---|---|---|---|
| Source QA (`qa_ta.py`) | C | ALL CLEAN (7 files) | same sources |
| Verse inventory (Kashmir 1–335 minus 246) | D | 334/334, 0 missing/extra/dup | 334/334 |
| Mula marks in PDF text | D | 334 | 334 |
| FFFD / PUA / control chars (raw layer) | S | 0 / 0 | 0 / 0 |
| Fallback-font spans (DejaVu/Lohit/Oriya/Symbol) | B | 0 chars | 0 chars |
| Embedded families | B | exactly 3 locked (+Noto Serif Italic/Bold = 7 subsets) | same |
| IAST malformed survivors | C | 0 (10 fixed, spot-verified rendered) | 0 |
| Terminology audit | C | TERM_AUDIT_V1: consistent | — |
| Footnotes render (13 notes, rule, markers) | P | 15 കുറിപ്പ് hits; markers 1–13 global verified visually | verified p122-class |
| Footnote anchors at group close, no orphans | P/U | yes | yes |
| TOC entries → real absolute numbers | M | 51 anchors mapped, leaders+numbers | same |
| Pagination stability (pass1 vs pass2 headings) | U | 0 shifts / 51 | 0 shifts / 51 |
| Folios == absolute pages (body) | O | gate passes (roman i–vii + decimal) | passes |
| Bookmarks land exactly (whitespace-insensitive) | T | 65/65 | 65/65 |
| Metadata (Title/Author/Subject/Keywords/ml + /Lang) | S | set, verified | set, verified |
| Tables real with repeated headers + captions | R/Q | പട്ടിക ൧/൨ verified rendered | verified |
| Figures curated+captions, units intact | F/G | 36 + emblem | 36 + emblem |
| Diagrams answer distinction (caption = section·family) | F | yes | yes |
| Occupancy: <45%-median pages | U | 3 (all structural: 2 chapter-closes + colophon) | 4 (closes + app-opener + colophon) |
| Orphan headings/ornaments/diagrams | H/U | none (keepNext verified) | none |
| Chapter-opener heads suppressed | N | verified | verified |
| Cover architecture (series/title/author/edition/imprint) | K | verified rendered | verified rendered |
| Frontmatter completeness | L | half/title/edition/guide/intro/index/contents | same |

## Visual QA coverage (rendered ≥110dpi, inspected)
cover, half-title, title, edition note, TOC (both pages), chapter opener,
mula close-up (conjuncts/chillu/dandas/ numerals), figure unit, footnote
page + marker close-ups (1,2,3,4,5), recap+bullets, appendix opener,
APP1 figure region, dvādaśānta table, glossary table + digit close-up,
colophon, trade cover/head/interior/footnote, low-page triage (all flags).

## Corrections log
CONTENT_CORRECTIONS_V1.md (4 Oriya digits, mula-policy wording, marker
example, 10 IAST, 8 heading normalisations, year digits, footnotes-word,
intro restoration) + TERM_AUDIT_V1.md (consistent; scope decision T5).

## Verdict: PASS — finished scholarly publication, both trims.
