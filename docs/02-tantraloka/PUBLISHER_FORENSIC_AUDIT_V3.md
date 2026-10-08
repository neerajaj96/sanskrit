# PUBLISHER_FORENSIC_AUDIT_V3.md — v02 Trade prototype audit for v03 rebuild
Prototype: `Tantraloka_Malayalam_Volume1_v02_Trade.pdf` (195pp, 6×9").
Method: full-text programmatic scan (fonts, layer, marks, bookmarks,
occupancy) + rendered inspection (110–220 dpi, ~25 pages) + shaping probes
(280-pt isolation render) + source cross-checks (6 verses vs Devanagari/IAST).

## Baseline metrics
- 195pp · 29,236 words · median 161 w/pp · 7 embedded subsets (3 locked
  families) on every page · 0 FFFD / 0 PUA / 0 fallback spans.
- 334/334 mula marks, ascending, Kashmir 1–335 minus 246 (2 spot-verified
  against source Devanagari/IAST: v1, v14 — translators correctly follow
  IAST over a Devanagari typo at v14p2).
- 65 bookmarks (L1:13/L2:39/L3:13), all landing exactly.
- Images-per-page reads 26 everywhere = shared LO resources (file 2.8 MB —
  no duplication).

## Defect register
### P0 — scholarly/content errors: NONE.
Translation meaning intact; no silent normalisation found; danda
attachments (`text ॥ N ॥`) verified normal Sanskrit; IAST brackets all
valid (ASCII-only forms confirmed diacritic-free-correct; `ÜKau` retained
as source siglum convention).

### P1 — rendering/Unicode errors (must fix in v03)
- P1-1: Appendix tables overflow the Trade measure (built 6.4" wide on a
  4.7" measure) and shatter long IAST (`[Chāndogyopaniṣad` + dangling `]`,
  `[Mālinīvijayottarata-ntra]`, `[Bṛhadāraṇyakopa-niṣad]`) plus Malayalam
  fragments. v03: measure-relative widths + tuned columns.
- P1-2 (suspect DISPROVEN): `ഷ്ഠം` rendering as "Oo" — isolated 280-pt
  probe shows the shaping engine forms the conjunct correctly; the table
  sighting was a small-size misread of loop+anusvāra. No action, recorded
  to prevent repeat investigation.

### P2 — serious typography/layout vs v03 policy (must fix)
- P2-1: NUMERAL POLICY (§0): v02 numbers everything in Malayalam digits
  (verses, ranges, heads, folios, captions, tables, TOC, bookmarks,
  years). v03 renders ALL ordinary numbering in ASCII 0–9 (render layer;
  sources untouched). NUMERAL_AUDIT gate before release.
- P2-2: Running heads cannot be parity-split (converter ignores even
  headers — spike-proven); combined centered head retained as documented
  toolchain limit (series + section identity preserved, suppressions kept).
- P2-3: Folio restart-per-section (converter behaviour) — already
  countered in v02 via explicit absolute starts; v03 keeps the mechanism.
- P2-4: Footnote per-section restart renders markers 1,0,0,0… (visually
  proven) — global 1–13 numbering kept; titles keep per-part indexing.
- P2-5: Figures visually too simple for a premium edition (§19): geometry
  correct but unlabeled; v03 enriches with IAST/ASCII node labels +
  chapter-architecture plate. No scholarly figure removed.
- P2-6: Captionsologue form (`ചിത്രം ൧ — …`) → v03 scholarly form
  (`Figure 15 — … / Based on verses …`), sequential ASCII numbering.

### P3 — aesthetic/consistency (fix in v03)
- P3-1: Chapter openers weak (stacked duplicate titles in v02 achetype…
  already deduped; v03 adds numbered opener treatment 01–05 + verse range).
- P3-2: Commentary labels visually loud (navy bold blocks); v03 restyles
  to quiet label-like run-ins.
- P3-3: Recap headings raw H3; v03 designed summary treatment.
- P3-4: Colophon half-empty; v03 balanced explicit page.
- P3-5: Bookmarks Malayalam + noisy (65, incl. recaps); v03 English
  L1–L3 scheme (~40) via post-export outline, Malayalam L4 retained.
- P3-6: No glossary depth / no index / no cross-ref links; v03 adds all
  three (auto-generated, source-traceable).
- P3-7: Frontmatter missing series-title page, source-basis, textual
  policy, key sigla; v03 completes the §31 order.
- P3-8: Short structural pages (chapter closes, TOC tail vii, appendix
  opener, colophon): conventional rhythm — accepted, monitored by
  occupancy gate (<45% flags triaged, orphans eliminated).
- P3-9: Cover/title refinements per §32–33 (full bilingual hierarchy).

### P4 — optional refinements (deferred, logged)
- True SVG figure sources (v03 ships 2× raster plates, print-sharp at
  ~480 dpi; manifest notes migration path).
- Landscape appendix tables (portrait verified adequate after retune).
- Even/odd parity heads (needs ODT pipeline; combined head retained).

## Release rule
No unresolved P0/P1/P2 at v03 release. This audit's P1/P2 items map to
v03 builder requirements one-to-one (see HOUSE_STYLE_V3.md).
