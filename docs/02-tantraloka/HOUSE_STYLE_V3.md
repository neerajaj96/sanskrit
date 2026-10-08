# HOUSE_STYLE_V3.md — Tantrāloka Malayalam Series, House Style v03
Supersedes the v02 record where they differ (numerals, captions, outline,
tables, reference apparatus). Binding for Volume Two. Toolchain:
`tools/build_v03.py` → LibreOffice headless → `toc_pass2.py` passes →
`set_outline_v03.py` → `/Lang` → gates.

## 1. Numeral law (§0)
Every ordinary book number in ASCII 0–9 — verses (॥ 1 ॥), ranges
(Verses 1–21), chapters (01–05), footnotes, figures (Figure 15), tables
(Table 2), appendices (Appendix 1), TOC, bookmarks, heads, folios,
years, colophon, index. Render-layer `NORM()`; sources byte-identical.
Gate: NUMERAL_AUDIT_V3.md (zero non-ASCII decimals or BUILD FAILURE).

## 2. Palette / fonts
Unchanged from v02 (ivory plates, antique gold, deep maroon, slate, ink;
Noto Serif Malayalam / Noto Sans Malayalam / Noto Serif). Additions:
`·`/`•`/`…` routed to Noto Serif; NO arrow/dingbat glyphs exist in the
stack (flow guides use `·` separators). 7 subsets embedded, zero fallback.

## 3. Trade format (§7)
6×9" (152×229mm), reflowed (never scaled): inner 0.75" (binding),
outer 0.70", top 0.75", bottom 0.80"; measure 4.55". A4 twin kept
(measure 6.47") from the same sources.

## 4. Type rhythm (§6)
Body 10.2pt/1.40 (Trade; 10.8/1.42 A4), justified, 0.22" first-line
indent; label-led and list paragraphs flush left. H1 16.5 maroon-dark,
H2 12.5 maroon, H3 11 slate. Commentary labels (§12): quiet 10pt bold
slate run-ins (no boxes, no loud colour). Footnotes 8.4pt true notes,
global 1–13. Captions 8/7.5pt (title bold maroon + grey source line).
Tables 9pt (8.5pt floor never breached; current: 9pt both trims).

## 5. Openers (§9) / recaps (§35) / ornaments (§34)
Major sections: gold `01`–`05` (26pt Latin), Malayalam H1, IAST/English
subtitle, `Verses N–M` slate line, gold rule. Minor sections compact.
Recaps: `ഈ ഭാഗത്തിൽ നിന്ന്` H3 + bullets. Ornament family: `• • •` +
gold rules only; emblem plates on cover/colophon.

## 6. Mula (§10–11)
Ivory box, 0.5pt antique-gold frame, maroon bold, optical centering,
ASCII verse numbers; one compact box per verse group, adaptive for long
groups, never dominating. Hierarchy: VERSE → നേരർത്ഥം →
ആചാര്യവ്യാഖ്യാനം → വിശകലനം → notes, differentiated by spacing and
quiet labels, not colour shouting.

## 7. Figures (§19–25)
37 plates (36 + architecture), 2800px (~480 dpi), unified hairlines;
labels in IAST/ASCII only where the commentary gives exact enumerations;
no rotating highlight (stable reference plates). Captions: `Figure N —
<section> · <family>` + `Based on verses R`. Units kept intact adjacent
to discussion; sizes: standard 2.5" (Trade). Manifest:
VISUAL_MANIFEST_V3.json (every visual source-traced).

## 8. Tables (§26–27, §36–37)
Real tables, repeated headers, measure-relative `tblGrid` (explicit
gridCol — LO ignores tcW-only widths), per-trim column plans; IAST never
shattered (verified cell-by-cell); source notes where due. Portrait
throughout (landscape reserved; never needed after retune).

## 9. Heads / folios (§14–15)
Centered 7pt gold combined head (`series · section · range`; Trade uses
trim-adapted series string) — parity-split impossible in the converter
(spike-proven), documented. Suppressed on cover/openers/major openers.
Folios centered grey: frontmatter lower-roman (explicit convention),
body absolute arabic via explicit per-section starts (converter restarts
otherwise). TOC numbers are absolute; folio gate enforces equality.

## 10. TOC / bookmarks / links (§16–18)
Linked TOC with dot leaders + real absolute numbers (two-pass, 0-shift
gate). Custom outline via post-export set_toc: L1 Volume, L2 Chapter,
L3 English sections/appendices/reference, L4 Malayalam subsections
(recaps excluded). Verse citations `(106)` hyperlinked to containing
sections (verified: zero dead links).

## 11. Frontmatter (§31) / cover (§32) / colophon (§38)
half-title → series page → title page (bilingual hierarchy §33) →
edition note → source/translation basis → reading guide (flow plate) →
textual policy → overview (+ architecture plate) → contents → key sigla
→ text. Cover: series line, framed emblem, bilingual title/volume/author
lines, imprint. Colophon: balanced explicit page (ornament, iti,
production plate with ASCII stats, emblem, śubhamastu).

## 12. Glossary / index (§28–29)
39-entry reader glossary (Malayalam + IAST + gloss + context + first
occurrence; IAST-alphabetised) + fully automatic page index (body range
only; converges by fixpoint; absent terms omitted).

## 13. Page balance (§8)
Occupancy gate (<45% median triaged; ornaments keepNext-bound; tables
unbroken or header-repeated). Intentional whitespace only for openers,
major breaks, explicit pages. Never global shrink-to-fit.

## 14. Build passes (replicate for Vol.2)
`drive_v03.py {trade|a4}`: build → convert → toc_pass2 (maps+starts,
rebuild, stability+folio gates, starts-refresh fixpoint) → make_index →
index rounds (≤3, convergence asserted) → set_outline → /Lang →
numeral_audit (exit 1 on any non-ASCII decimal). Converter limits (§P
in forensic audit) are binding constraints, not bugs to re-litigate.
