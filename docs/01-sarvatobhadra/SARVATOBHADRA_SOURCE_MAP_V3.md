# SARVATOBHADRA_SOURCE_MAP_V3.md — Phase 1 source map + forensic verdict
Status: PHASE 1 COMPLETE. No rebuild started. No GitHub changes. No PDFs
overwritten. No source/content corrections made (findings only).

## 1. Source chain (traceability)
| # | SOURCE | LOCAL PATH / URL | ROLE | AUTHORITY | R/W |
|---|--------|------------------|------|-----------|-----|
| 1 | Google Drive original | `docs.google.com/document/d/1Bp9lVOa…` (KSTS LXIV Sarvatobhadra) | Ultimate textual authority | Highest | **INACCESSIBLE** from this environment (auth wall; fetch returns Drive shell only). Reported, never fabricated |
| 2 | Local edition text | `/root/sarvatobhadra_ml/source.txt` (1,495,407 bytes, 9,454 lines) | Presumed exported copy of #1 | High — VERIFIED (see §2) | Read-only by policy |
| 3 | Chunked source | `/root/sarvatobhadra_ml/chunks/` (27 files: frontmatter, upodghata, ch01–ch18c, appendix; split map in `split_chunks.py`) | Working segments of #2 | Derived | Read |
| 4a | Scholarly translation (base) | `/root/sarvatobhadra_ml/translated/` (27 files; ch + 3 appendices A/B/C) | Book 1 content candidate | Under ruling (Phase 2) | Read |
| 4b | Scholarly translation (peak) | `/root/sarvatobhadra_ml/translated_peak/` (27 files; sole input of `build_docx.py`) | Book 1 production input | Under ruling (Phase 2) | Read |
| 4c | Layman translation | `/root/sarvatobhadra_ml/translated_layman/` (21 files) | Book 2 only — comparison/pedagogy | Supplementary; must not contaminate Book 1 | Read |
| 5 | Term locks | `/root/sarvatobhadra_ml/GLOSSARY.md` (granthika, LOCKED) + `LAYMAN_TERMS.md` (LOCKED) | Terminology authority | Binding | Read |
| 6 | Repo baseline PDF | `docs/01-sarvatobhadra/Sarvatobhadra_Malayalam.pdf` (471pp A4; inspected via sparse clone to `/tmp/sanskrit/`) — byte-identical to local `pdf/` build | Diagnostic baseline ONLY, never textual authority | Reference | Read |
| 7 | Repo layman PDF | `docs/01-sarvatobhadra/Sarvatobhadra_Layman.pdf` (125pp Letter) | Design/pedagogy comparison only | Supplementary | Read |
| 8 | Build toolchain | `build_docx.py` (Book 1, v01-architecture) + `build_layman.py` + `build_appendix.py` + `deva2mal.py` + `purge_scrub.py` + `qa_peak.py` + `split_chunks.py` | Existing pipeline (DOCX→LibreOffice, Noto Serif/Sans Malayalam) | Reuse/adapt | Read |
| 9 | Releases | `part-19` (Book 1), `layman-14` (Book 2) | Superseded snapshots | Reference | — |

Rebuild output convention (unused paths, nothing written): `build/sarvatobhadra_v03/pdf/…_v03_Trade.pdf`, `…_v03_A4.pdf`, `…_v03_Research.pdf` + DOCX.

## 2. Provenance verdict: source.txt = complete KSTS LXIV (VERIFIED)
- Title page: Kashmir Series of Texts and Studies No. LXIV, Bhagavadgītā with Sarvatobhadra by Rājānaka Rāmakāntha, ed. Madhusudan Kaul Shastri, Nirnaya Sagar Press 1943; trilingual frontmatter (English/Sanskrit/Hindi-Kashmir).
- All 18 chapter openers (`अथ …ऽध्यायः`, ll.163–7949) and 18 closers (`…ऽध्यायः ॥ N ॥`) present, in order.
- Root verses present (e.g. `धर्मक्षेत्रे`, l.398; speaker labels `अर्जुन उवाच`).
- End apparatus (ll.~8814–9453) carries Rāmakantha-vs-Śaṅkara readings = Appendix B (pāṭhāntara) matter and śuddhipatra/adhika matter = Appendices A/C. Matches the 3 local appendix files.
- Conclusion: source.txt is a SUFFICIENT authority stand-in for the inaccessible Drive doc. Residual risk (Drive may contain post-1943 corrections) is logged, not assumed away.

## 3. Baseline forensic findings (471pp repo PDF)
Metrics: 84,646 words · median 181 w/pp · 0 FFFD / 0 PUA · 525 bookmarks (L1:30/L2:456/L3:39) · /Lang en-US (wrong) · 0 embedded figures · low-word pages only structural (1, 3, 20, 470–471).
Verse marks: 1,237 Malayalam-digit `॥N॥` (max 78 = ch18), 0 ASCII, 0 Devanagari. Per-file source inventory (translated_peak): ch totals consistent with Gita (47,72,43,42,29,47,30,28,34,42,55,20,35,27,20,24,28,78) plus quoted stanzas; frontmatter 4, upodghata 14, appendix C 9.
Builder (build_docx.py): v01-architecture — per-line mula boxes, `List Bullet/Number` styles, `Light Grid Accent 1` tables, static running head + ASCII folios, bookmarks+H1/H2 links, NO true footnotes.

### P0 — content/scholarly (verify before any fix; Phase 2 evidence each)
- P0-1: Wrong-script glyphs INSIDE sources: Bengali (peak ch06 ×2 clusters, ch09 ×1; base ch04 ×4, ch06 ×4, ch12 ×4, upodghata ×1; layman ch06 ×1) and Telugu (peak ch11 ×2, ch18c ×2; base ch04 ×1, ch12 ×3, upodghata ×1). Mechanism proven: e.g. peak ch06:398 `നേങ্গതേ` uses Bengali ്+ഗ (U+09CD+U+0997) for correct Malayalam ്+ഗ (U+0D4D+U+0D17); source.txt:3357 reads `नेङ्गते`, fixing the correction target. Each instance needs logged render-layer correction with this evidence.
- P0-2: Verse-number anomalies: ch02c contains mark "2" (file spans 51–72); ch18c contains mark "1" (file spans 54–78) — quoted verse vs misnumbering, to rule against source.txt.
- P0-3: Arabic `('من' …)` example embedded in colophon p471 (OCR-defect discussion). Content ruling needed: retain-documented vs replace-with-description.
- P0-4: ch13 shows 34 marks (34- vs 35-verse tradition) — completeness check vs source.

### P1 — rendering/Unicode (must fix in v03)
- P1-1: Footnote markers as literal math-bold digits 𝟭𝟮𝟱𝟲𝟴𝟵 (14× on 12pp: 201,202,204,249,250,258,296,297,299,309,310,329) — live in translated_peak sources (ch07/ch09/ch11/ch12); translated/ has none. v03: true footnotes, ASCII markers.
- P1-2: Control chars \x01×14 + \x03×1 in text layer (build-emitted bullets/symbols; sources clean) — v03 literal-• pipeline eliminates.
- P1-3: Fallback fonts on every page: Lohit-Malayalam (heading CTL inheritance), DejaVuSans (• ×478, ❖ ×81), DejaVuSans-Bold (dashes/spaces), NotoSansBengali (গ ×15 from P0 sources), NotoSansTelugu (fragments from P0 sources) — v03 locked 3-family + script segmentation.
- P1-4: /Lang `en-US` on Malayalam content — must be `ml`.
- P1-5: ❖ ornament (81×) unrenderable in locked fonts — v03 ornament family restricted to covered glyphs.

### P2 — serious layout vs v03 bar (must fix)
- P2-1: Malayalam-digit numbering throughout → v03 ASCII law (render layer).
- P2-2: Static single running head, present even on colophon → per-section heads, suppressed on openers/colophon (parity-split impossible in toolchain — documented limit).
- P2-3: End-of-group note lists, no true footnotes, marker↔note linkage to verify in Phase 2.
- P2-4: 525 noisy bookmarks → v03 English-scheme outline + Malayalam subsections.
- P2-5: TOC is a manually typed title list WITHOUT page numbers (p2) → dynamic linked TOC with real numbers.
- P2-6: Plain typographic cover; half-empty colophon (p471, ~70% void, running head present).
- P2-7: Justification rivers in dense mixed-script passages (pp6–8 and throughout IAST-dense commentary).
- P2-8: Mula boxes hold 6+ verse lines singly (comfortable but undivided); v03 adaptive grouping.

### P3 — aesthetic/consistency
- P3-1: No figures at all (0 images) — v03 adds text-supported scholarly plates only (never decorative).
- P3-2: No glossary/index volume apparatus found (confirm in Phase 2: search found no പദാവലി section) — v03 adds both (auto-generated).
- P3-3: Appendix tables present (pp450–451) but unverified for breaks/headers — Phase 2 cell audit.
- P3-4: Chapter-opener hierarchy weak (verify across chapters in Phase 2).
- P3-5: Frontmatter order (cover, guide+TOC p2, mukham p4…) → v03 §31 order.

### P4 — deferred/optional
- Layman Book 2 rebuild (out of scope unless instructed; comparison only).
- SVG figure sources; landscape tables (only if portrait proves inadequate).

## 4. Authority input for the Phase 2 ruling
Evidence favours `translated_peak`: sole input of the shipping builder, byte-identical output to the released PDF, and substantively newer (ch01–13 expanded 2–3× with half-verses, fuller commentary, structural headings; ch14–18 + appendices polished; straight-quote normalisation). `translated/` is the superseded base. Recommendation: lock `translated_peak` (after P0 ruling on its contaminations, which the base set shares anyway). Ruling itself is Phase 2's first act.

## 5. Exact next action for Phase 2
1. Rule production input (peak vs base) on the forensic record above.
2. Reconcile verse inventory per chapter against source.txt (700 root + quoted/appendix stanzas; rule P0-2/P0-4 with line-level evidence).
3. Rule P0-3 (Arabic example) and audit P2-3/P3-3/P3-4 specifics (note linkage, table cells, openers).
4. Emit authority lock + full verse map, then — only then — begin the v03 build.
