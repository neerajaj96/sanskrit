# PUBLISHER_AUDIT_V1.md — v01 baseline → v02 production audit

## v01 baseline (Tantraloka_Malayalam_v01.pdf, 280pp A4)
Strengths kept: gold/ivory mula concept; H1+H2 bookmarks; hyperlinked
contents; abbreviation tables; genuine translated content (334 verses).

## Defects found in v01 (all fixed in v02 unless noted)
1. **Figure-per-verse pagination collapse**: 334 full-width (5") figures →
   ~100–200 words/page, 280 pages. v02: 36 curated figures at 2.9"/2.5".
2. **PUA text-layer pollution**: Word list styles → 84× U+F0B7 + U+FFFD-class
   artefacts. v02: literal `•`, zero PUA/FFFD.
3. **Fallback-font clutter**: DejaVu/OpenSymbol/Lohit/Oriya subsets embedded
   (bullets, Oriya digits, unsegmented IAST). v02: exactly the 3 locked
   families; script-segmented runs; Oriya digits expunged (ORI-001).
4. **Malformed IAST**: 10 abbreviation-table entries in plain ASCII
   (IAST-001…010 fixed; zero survivors in v02 layer).
5. **Mula-policy wording**: "fully translated" ambiguity (MULA-WORD-001 fixed
   in frontmatter, edition note, colophon).
6. **Shared header/footer parts**: N/A to v01 (static heads) — caught and
   fixed during v02 build (unlink+clear per section).
7. **Running heads**: v01 static strings; v02 per-section heads (centered
   combined head — parity-split impossible in toolchain, logged).
8. **Folios**: v01 single-section continuous; v02 multi-section required
   explicit absolute restarts (converter restarts otherwise — measured).
9. **Footnotes**: v01 end-of-group shaded lists; v02 true footnotes, global
   numbering (per-section restart renders "0" in converter — measured).
10. **TOC**: v01 links without numbers; v02 two-pass real numbers + stability
    gate (0 shifts across passes, both editions).
11. **Internal-H1 duplication**: chapter H1 + file H1 stacked on openers;
    v02 drops the redundant on-page H1 (VQ-003).
12. **Orphan ornaments**: closing `• • •` stranded alone (Trade); v02 keeps
    ornament with content (keepNext) + drops appendix ornament.
13. **Missing frontmatter**: v02 first omitted ഗ്രന്ഥപരിചയം; restored with
    text-name index (ta_front.md now fully represented).
14. **Latin/prose leaks in builder strings**: `(footnotes)`, ASCII year
    `2023` — corrected (`൨൦൨൩`, English word dropped).

## v02 residual / accepted items (intentional, logged)
- Chapter-end short pages (A4 p56/p86 etc.) and colophon/appendix-opener
  short pages: conventional end-matter rhythm, not defects.
- TOC tail page (vii): 38-word overflow — standard contents behaviour.
- Footnote markers (global 1–13) vs per-part titles (കുറിപ്പ് ൧..):
  dual apparatus, unambiguous, preserves locked per-part numbering.
- Trade heads trim-adapted (`തന്ത്രാലോകം · short`); A4 full series string.
- No raw TOC *field* (would render "no entries" until Word updates it);
  the linked+numbered TOC is the real navigation surface plus 61 bookmarks.
- Roman frontmatter numbering kept (implemented safely: restarts verified
  i–vii, body restarts at absolute).
