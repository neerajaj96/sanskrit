# SERIES_STYLE.md — Tantrāloka Malayalam Series, House Style v02
Master style record for Volume One; binding for Volume Two and all reprints.
Toolchain: `tools/build_v02.py` (python-docx) → LibreOffice headless PDF.
Shaping-safe: every run carries explicit `w:rFonts` (ascii/hAnsi/cs);
headings never rely on style inheritance (LibreOffice CTL fallback).

## 1. Palette (exact)
- Page ground: white `#FFFFFF`; ivory plates `#FFFBF0` (mula), `#FFFBF0`
  alternating table rows; emblem ground `#FAF4E6`.
- Antique gold `#A67C2E` (rules, mula borders, figure frames, bullets,
  running heads); light gold `#C49E50` (emblem accents).
- Deep maroon `#5A1A10` (mula text, table headers, captions, H2),
  dark maroon `#4A140C` (H1, cover title).
- Slate `#2E4057` (H3, lead labels, TOC links); ink `#212121` (body);
  grey `#6E6E6E` (folios, TOC numbers, imprint); muted red `#8E2F21`
  (diagram highlight node only).

## 2. Fonts (locked, 3 families — no others embedded)
- Body: Noto Serif Malayalam Regular/Bold.
- Headings: Noto Sans Malayalam Regular/Bold.
- IAST/Latin: Noto Serif Regular/Italic/Bold (full diacritic coverage,
  verified ā ī ū ṛ ḷ ṃ ḥ ṅ ñ ṭ ḍ ṇ ś ṣ).
- Script-segmented runs: Latin/IAST/digit-letter runs → Noto Serif; all
  else → Malayalam family. `·` (U+00B7), `•` (U+2022), `…` routed to
  Noto Serif (absent from Noto Malayalam fonts — verified via fontTools).

## 3. Page geometry
- A4: 210×297mm; margins T 0.75" / B 0.80" / L-R 0.90" (≈6.47" measure).
- Trade: 6×9" (152×229mm); margins T 0.65" / B 0.70" / L-R 0.65".
- Body A4 10.8pt / Trade 10.2pt; line spacing 1.42 / 1.40; justified;
  first-line indent 0.22" (label-led and list paragraphs flush left);
  space-after 4pt; widow control on.

## 4. Hierarchy
- H1 16.5pt maroon-dark (chapter / appendix / frontmatter titles),
  keep-with-next, gold rule below chapter titles.
- H2 12.5pt maroon (doctrinal sections; verse-range in title).
- H3 11pt slate (`ഇതിൽനിന്ന്` recaps — bookmarked, NOT in TOC).
- Kicker (appendices): 9pt gold bold (`അനുബന്ധം ൧`) above H1 opener.
- Bullets: literal `•` + 0.3" hanging indent (never Word list styles —
  those emit PUA bullets). Tables use `Table Grid` + explicit fonts.

## 5. Verse (mula) boxes
- Consecutive `>` lines = ONE box per verse group (never one box per line).
- Warm ivory `#FFFBF0`, 0.5pt antique-gold frame, centered, 11.5pt bold
  maroon (A4; 10.8pt Trade), keepLines; space 4pt before / 6pt after.
- Mula stays Sanskrit in Malayalam script; dandas + Malayalam numerals kept.

## 6. Figures
- Curated only: one per doctrinal section (35) + appendix ascent (1);
  1400×900 plates, double gold hairline frame, unified line weights
  (4px primary maroon / 2px secondary gold), muted-red highlight.
- Width A4 2.9" / Trade 2.5"; figure + caption = one keepLines unit placed
  after its verse group's opening commentary; caption 8.5/8pt maroon
  italic centered (`ചിത്രം N — section · family`).

## 7. Running heads / folios (spec N+O as built)
- Centered 7.5pt gold (A4; 7pt Trade): `series · section-short`.
  A4 series string `തന്ത്രാലോകം — മലയാളപതിപ്പ്`; Trade trim-adapted
  `തന്ത്രാലോകം` (one-line rule). No head on cover/chapter openers.
  (Word even/odd heads are ignored by the converter — verified by spike —
  so parity-split Left/Right heads are not used.)
- Folios centered 8pt grey; frontmatter lowerRoman (i,ii…), body decimal
  restarted explicitly per section to ABSOLUTE numbers (the converter
  restarts otherwise). TOC numbers are absolute.

## 8. Footnotes
- True Word footnotes (footnotes.xml), 8.8/8.4pt, separator rule,
  superscript markers; global document numbering 1–13 (converter renders
  per-section restart as "0" — verified — so no numRestart is set).
  Each `**കുറിപ്പ് N —**` note anchors at its verse-group close; titles
  preserve source per-part indexing, markers are document-unique anchors.

## 9. Tables / glossary / appendices
- Maroon header (white bold 9pt), alternating ivory rows, repeated header
  row across page breaks, explicit column widths, caption above
  (`പട്ടിക ൧/൨ — …`). Abbreviations: `ചുരുക്കം | വിപുലരൂപം | മലയാളം`.

## 10. Cover / frontmatter / metadata / nav
- Cover: series line, framed emblem plate (original yantra-geometry line
  art, no text in art), 30pt title, parallel Latin title (italic slate),
  gold rule, volume/author/edition lines, bottom series imprint. No folio.
- Frontmatter: half-title, title page, edition note (three-tier mula
  policy), reading guide, ഗ്രന്ഥപരിചയം + overview + text-name index,
  linked contents with dot leaders + real absolute page numbers (two-pass).
- Metadata: Title/Author/Subject/Keywords/Language(ml) + PDF `/Lang=ml`.
- Bookmarks: H1+H2+H3(+appendix/colophon); every bookmark lands exactly
  (verified whitespace-insensitively, 61+61).

## 11. Build passes (replicate exactly for Vol.2)
1. `build_v02.py --edition {a4,trade}` → DOCX (+ `.anchors.json`).
2. Convert via LibreOffice headless → PDF.
3. `toc_pass2.py {A4,Trade}` → `.pages.json` + `.starts.json`,
   rebuild with `--toc/--starts`, reconvert.
4. Gates: heading stability (0 shifts), folio==absolute, 334 mula marks,
   zero fallback/FFFD/PUA, occupancy review.
