# CONTENT_CORRECTIONS_V3.md — v03 rebuild correction record

Hierarchy honored: authoritative source → translated content → editorial
structure → render data → PDF. **No translated-content file was modified
for v03** (md5-verified byte-identical against `/tmp/sources_v03_baseline.md5`:
all 7 files OK). Every item below is therefore render-layer or editorial
apparatus, never a meaning change. Confidence/status per correction.

## CC3-01 — Numeral policy (§0): render-layer ASCII conversion
- Location: every rendered number (verses, ranges, heads, folios, tables,
  TOC, bookmarks, captions, colophon, metadata-adjacent prose).
- Old → New: `൧൨൩…` → `123…` (central `NORM()` in text entry points).
- Reason: v03 policy mandates ASCII 0–9 throughout.
- Source evidence: N/A (presentation only); NUMERAL_AUDIT_V3.md gate.
- Confidence: certain (mechanical, reversible). Status: applied, gated.

## CC3-02 — Recap heading normalisation (§35)
- Location: 13 `##` headings (ta_v02…ta_v06): `ഇതിൽനിന്ന് — …` →
  `ഈ ഭാഗത്തിൽ നിന്ന് — …` (render-time replace; sources untouched).
- Reason: spec §35 prescribes the fuller heading; same sense, no meaning
  delta. Anchors (`_R<num>`) unaffected.
- Confidence: certain. Status: applied.

## CC3-03 — Appendix kickers → "Appendix 1/2" (render-time)
- Location: appendix openers (render_appendices).
- Reason: matches English outline scheme (§17); the Malayalam titles stay.
- Confidence: certain (apparatus). Status: applied.

## CC3-04 — Chapter-opener apparatus (§9)
- Added: section numbers 01–05, IAST subtitles (01 Mangalācaraṇa per the
  spec example; 02–05 descriptive English matching the §17 outline),
  "Verses N–M" range lines. No translated sentence altered.
- Confidence: certain. Status: applied.

## CC3-05 — New reference apparatus (additions, not corrections)
- Glossary (§28): 39 entries from GLOSSARY.md + build-time first-use spans;
  two glossary-only related terms marked as such. English glosses are
  standard dictionary equivalents, logged per entry in build_v03.py.
- Index (§29): purely mechanical concordance from final pagination
  (make_index_v03.py); absent terms omitted, never fabricated.
- Abbreviation key-sigla (§31), source-basis + textual-policy frontmatter:
  factual restatements of PROJECT_SPEC/GLOSSARY, no new claims.
- Chapter-architecture plate: structural boxes + verse spans only.
- Confidence: high (all traceable). Status: applied.

## CC3-06 — Caption scheme (§23)
- `ചിത്രം ൧ — …` → `Figure 15 — … · …` + `Based on verses …`.
  Verse ranges per figure cross-checked against H2 ranges; no interpretive
  claims added (purposes logged in VISUAL_MANIFEST_V3.json).
- Confidence: certain. Status: applied.

## CC3-07 — Textual-integrity findings (audit, §3)
- Verse count/order: 334 unique, ascending, Kashmir 1–335 minus 246 — PASS.
- Spot-verification vs source Devanagari/IAST: v1 and v14 PASS (translators
  correctly follow IAST over a Devanagari typo at 14p2:
  `षडधीर्थ` → `ṣaḍardhārtha` → `ഷഡര്ധാര്ഥ`).
- Danda attachments, pāda groupings (mostly 2–4 lines), IAST brackets,
  invisible-character scan, script-leakage scan: all PASS (see forensic
  audit). The table-cell `ഷ്ഠം` sighting was investigated at 280 pt and
  disproven (correct conjunct; small-size misread).
- `ÜKau` retained as source siglum convention (source.txt l.477).
- Result: **zero meaning corrections required**; nothing normalised on
  Malayalam-spelling assumptions. Status: closed.

## CC3-08 — Tandem v02 corrections carried forward
All CONTENT_CORRECTIONS_V1 items (Oriya digits, mula-policy wording, 10
IAST, heading order, year numerals) remain in force; v03 sources inherit
them byte-identically.
