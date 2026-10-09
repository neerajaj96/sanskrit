# SARVATOBHADRA_AUTHORITY_LOCK_V3.md — Phase 2 ruling + reconciliation
Status: AUTHORITY LOCKED. Rebuild (Phase 3) is green-lit on these terms.
No sources modified; no content corrected yet — all corrections are
render-layer + logged (see §4).

## 1. Ruling: production input = `translated_peak/`
Evidence: (a) sole input of the shipping `build_docx.py`; (b) repo PDF is
byte-identical to a peak build; (c) substantively newer — ch01–13 expanded
2–3× (half-verses restored, fuller commentary, structural `## അവതരണം`
heads, `# Title (range)` H1s), ch14–18 + appendices polished, quotes
normalised; (d) carries the footnote6869-class markers the base set lacks
(there are no standalone note markers anywhere — apparatus is inline
`॥ N ॥` refs, so v03 needs no note-conversion program); (e) both sets
share the same P0 contaminations, so base offers no purity advantage.
`translated/` is superseded (kept for diff reference only).

## 2. Verse reconciliation vs print (source.txt line-segment evidence)
Print (Kashmir recension) chapter maxima: 47, 74, 48, 42, 28, 47, 30, 28,
35, 42, 60, 20, 34, 27, 20, 24, 28, 79. Translation maxima match EXCEPT:
- ch18: translation 78 vs print 79 — print splits vulgate 18.78 into
  78 (`യത്ര യോഗേശ്വരഃ`, l.8787) + 79 (`തത്ര ശ്രീഃ`, l.8788); translation
  keeps both pādas under one `## ശ്ലോകം 78` group (ch18c:177–178) with full
  commentary. CONTENT-COMPLETE, structure differs. Ruling: keep structure;
  v03 adds one editorial footnote at the group (print numbers 78–79).
- ch05 final = 28, ch13 final = 34: faithful to print (ll.3104, ch13 seg);
  vulgate-bias assumptions (29/35) REFUTED by source evidence.
- ch02c `॥ ൨ ॥` = chapter colophon number; ch18c `൧–൬` = quoted praśasti
  stanzas + `൧൮` colophon; beyond-end marks (ch02:73–74, ch03:44–48,
  ch06:48–49, ch09:35, ch11:56–60) all match print maxima — Kashmir
  recension extras, FAITHFUL. Keep with source tags intact.

## 3. P0 rulings (each with line-level evidence; applied at render, logged)
- R1 — Wrong-script clusters (~20 instances: peak ch06×2, ch09×1, ch11×2,
  ch18c×2): correct to Malayalam-script equivalents (e.g. U+09CD→U+0D4D,
  U+0997→U+0D17 in `നേങ്ഗതേ`, evidence source.txt:3357 `नेङ्गते`).
- R2 — Math-digit verse marks (൧𝟨-type, 15 instances): normalize second
  digit to ASCII at render; numbers verified correct EXCEPT:
- R3 — ch09 v15 mark reads 19, print (l.4713 `॥ १५ ॥`) reads 15:
  CORRECT 19→15 (sole genuine digit error found).
- R4 — ch12 group mark `൧𝟫` for range 15–19: correct number (range-end
  convention), script-fix only.
- R5 — Colophon Arabic `('من' …)` OCR example: RETAIN as intentional
  content; render via explicitly approved single-instance fallback, logged.
- R6 — No standalone footnote markers exist anywhere (all math digits are
  mark-embedded; apparent standalones are line-split artifacts across page
  breaks). v03 footnotes = only logged editorial textual notes (R-ch18
  split note et al.). No note-conversion program needed.

## 4. Apparatus audit results
- Notes/linkage: N/A (inline `॥ N ॥` refs only; v03 hyperlinks resolvable
  ones to containing sections, same scheme as Tantraloka v03 §18).
- Tables: appendix tables exist (pp450–451); cell-level audit deferred to
  build QA (measure-relative gridCol rule already proven).
- Openers: chapter H1 + kicker structure present (e.g. Appendix A p450);
  v03 applies numbered-opener treatment per House Style.
- Glossary compliance: NEITHER set implements GLOSSARY.md first-use
  `[IAST]` (peak: 6 proper-noun brackets total; terms plain/single-quoted).
  Ruling: v03 ADDS first-use `[IAST]` at render from the locked term list
  (apparatus addition, fully logged — not a source correction).

## 5. Builder verse map (locked)
frontmatter→FRONT; upodghata→UPO; ch01→CH1 (1–47); ch02a/b/c→CH2 (1–27,
28–50, 51–72); ch03→CH3 … ch17→CH17 (single files); ch18a/b/c→CH18
(1–30, 31–53, 54–78); appendix_A/B/C→APPA/B/C. Headings: `#` chapter H1,
`## ശ്ലോകം N[-M]` groups (+`അവതരണം` intros), `**speaker**` labels,
`>` mula, `**വിവരണം:**` commentary. Verse ranges ASCII in v03.

## 6. Phase 3 green light
Build `build_sarv_v03.py` (new pipeline `drive_sarv_v03.py` + gates mirroring
Tantraloka v03): A4 + Trade 6×9 + Research PDFs + DOCX under
`build/sarvatobhadra_v03/`; ASCII numeral law; true footnotes only for
logged editorial notes; curated text-supported figures (baseline has
ZERO images — every plate must be source-traceable); glossary + index;
custom outline; /Lang ml. Then QA gates, docs, and — only on explicit
instruction — push/release.
