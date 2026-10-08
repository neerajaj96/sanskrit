# BUILD_LOG_V3.md — maximum rebuild production record

## Forensic phase (prototype: v02 Trade 195pp)
Full-program scan + 110–220 dpi renders + 280-pt shaping probes + 6-verse
source checks → PUBLISHER_FORENSIC_AUDIT_V3.md (P0: none; P1: table
overflow/shatter; P2: numeral policy, heads/folio/footnote converter
limits, figure simplicity, captions; P3/P4 logged). `ഷ്ഠം` shaping scare
investigated and disproven (correct conjunct; small-size misread).

## Textual integrity (§3) + typography forensics (§4)
334 unique ascending marks; zero invisible/control chars; only U+0965
beyond Malayalam+Latin-brackets; danda attachments normal; IAST brackets
valid (`ÜKau` kept as source siglum); v1/v14 verified vs Devanagari/IAST
(translators rightly follow IAST over a Devanagari typo at 14p2).
Result: zero meaning corrections (CONTENT_CORRECTIONS_V3.md CC3-07).

## Rebuild (tools: fig_v03.py, build_v03.py, make_index_v03.py,
set_outline_v03.py, numeral_audit_v03.py, drive_v03.py, toc_pass2.py)
- Numerals: central NORM() render conversion; sources md5-identical.
- Figures: 37 plates at 2800px, IAST/ASCII labels only for exact
  commentary enumerations; rotating highlight retired; manifest emitted.
- Print-legibility catch: labels resized 46→~110px after architecture
  plate rendered microscopic (verified in plate renders).
- tblGrid gridCol fix: LO lays out from the grid, not tcW (measured equal
  split) — set both; Trade 3-col plan [0.85, 2.25, 1.45].
- Flow incidents, all gated: shared-headers (v02 carry), folio restarts →
  explicit absolute starts; eachSect markers 1,0,0,0 → global numbering;
  stale starts.json poisoning → removed preservation, live discovery +
  starts-refresh fixpoint; mid-drive code edit → stability gate caught it.
- Converter limits re-confirmed (binding): even/odd heads ignored,
  section folio restart, per-section footnote restart broken, page
  background ignored, first-section page-frame propagation.

## Pass record (final code)
Trade: 53/53 mapped, 0-shift ×3 rounds, index converged round 0,
folios match, 219pp. A4: same gates, 134pp. Numeral audit exit 0 both.
Outline replaced post-export (48 entries). /Lang=ml set post-export.

## Repro
`drive_v03.py {trade|a4}` alone reproduces everything (gates inside).
Freeze code during a drive — the stability gate treats mid-run edits as
pagination faults (observed once, correctly).
