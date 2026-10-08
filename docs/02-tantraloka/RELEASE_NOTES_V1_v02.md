# RELEASE_NOTES_V1_v02.md — Tantrāloka Malayalam, Volume One (v02)

## What this is
Publisher-grade production upgrade of the Malayalam Volume One (Chapter One
+ appendices): same approved translation and scholarly content, completely
re-typeset in the new series house style (SERIES_STYLE.md).

## Files (in `pdf/`, v01 untouched)
- `Tantraloka_Malayalam_Volume1_v02_A4.pdf` — 124 pages, A4 book-like.
- `Tantraloka_Malayalam_Volume1_v02_Trade.pdf` — 195 pages, true 6×9" reflow
  (not a scaled print).
- Companion `.docx` build artifacts + `.anchors/.pages/.starts.json`.
- Build tools: `tools/build_v02.py`, `fig_v02.py`, `cover_v02.py`, `toc_pass2.py`.

## Editorial (meaning-preserving; full log in CONTENT_CORRECTIONS_V1.md)
4 wrong-script digits, mula-policy wording (three-tier formula), 10 IAST
spellings in the abbreviation table, 8 heading normalisations (labels kept),
year numerals, frontmatter prose. Verse inventory unchanged: 334 mula
(Kashmir 1–335 minus 246). Terminology audit: consistent (TERM_AUDIT_V1.md).

## Production highlights
Original series cover (yantra-geometry line art, no stock); curated
36-plate diagram system (was 334 repetitive full-page figures); true
footnotes (13); per-section running heads; continuous folios (roman
frontmatter, absolute body); linked contents with real page numbers;
61 exact PDF bookmarks; locked 3-family typography with clean searchable
text layer; language metadata.

## Known dual-numbering note
Footnote markers run 1–13 document-wide while note titles keep the source
per-part labels (കുറിപ്പ് ൧..) — markers locate, titles index the group.
A converter limitation (per-section restart misrenders) makes any other
arrangement worse; see BUILD_LOG.

## Next: Volume Two inherits SERIES_STYLE.md unchanged.
