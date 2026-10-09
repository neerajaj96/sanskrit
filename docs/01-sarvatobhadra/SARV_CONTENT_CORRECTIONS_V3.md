# SARV_CONTENT_CORRECTIONS_V3.md — Sarvatobhadra v03 correction record
Hierarchy honored: Drive original (inaccessible; never fabricated) →
source.txt (read-only) → translated_peak/ (byte-identical; md5 below) →
render layer → PDF. Every item: location / old / new / reason / source
evidence / confidence / status. No silent corrections.

Source integrity: `translated_peak/*.md` untouched by the build (all
fixes applied in `build_sarv_v03.py` at render; verified by re-scan —
zero Bengali/Telugu/math-digit codepoints reachable in output).

## CC-S1 — Wrong-script clusters → Malayalam (AUTHORITY_LOCK R1)
Render-layer `FIXMAP` (exact cross-script equivalents; each instance
verified against source.txt):
| # | Location | Old (codepoints) | New | Evidence |
|---|----------|------------------|-----|----------|
| 1 | ch06:398,461 `നേങ্গതേ` | U+09CD,U+0997 | U+0D4D,U+0D17 `നേങ്ഗതേ` | source.txt:3357 `नेङ्गते` |
| 2 | ch09:195 `സൃജാമি` | U+09BF | U+0D3F `സൃജാമി` | source.txt:2263 `सृजामि` |
| 3 | ch11:333 `കకుഭു` | U+0C15,U+0C41 | U+0D15,U+0D41 `കകുഭു` | source.txt:5643 `ककुभः` |
| 4 | ch18c:181 `സകലവಿಪക്ഷ` | U+0C3F,U+0C2A | U+0D3F,U+0D2A | source.txt:8791 `सकल विपक्ष` |
Confidence: certain (phonetically exact, evidence-pinned). Status: applied,
verified in PDF layer (e.g. `നേങ്ഗതേ` renders in Malayalam cluster).

## CC-S2 — Math-digit verse marks → ASCII (AUTHORITY_LOCK R2)
All `॥ ൧𝟨 ॥`-class marks (15 instances: ch07,09,11,12) normalized via
Unicode decimal values at render. Numbers verified correct per print
EXCEPT CC-S3. Status: applied.

## CC-S3 — ch09 v15 mark 19→15 (sole genuine digit error)
- Location: ch09 mula + commentary ref (सततं-verse).
- Old: `॥ ൧𝟫 ॥` (19). New: `॥ 15 ॥`.
- Reason/evidence: source.txt:4713 numbers the verse `॥ १५ ॥`; ch09's
  legitimate 19 (प्रभवः, line 395, clean digits) is untouched — fix is
  line-targeted with count assertions, never global.
- Confidence: certain. Status: applied, verified (`॥15॥` in layer).

## CC-S4 — Print-faithful numberings retained (NOT errors)
ch02c colophon `॥ 2 ॥`; ch18c quoted stanzas 1–6 + colophon 18;
beyond-end marks ch02:73–74, ch03:44–48, ch06:48–49, ch09:35, ch11:56–60
(Kashmir recension, print maxima 74/48/49/35/60); ch05-final 28 and
ch13-final 34 (print, ll.3104/ch13 segment); ch18 single-78 group for
print's split 78/79 (content-complete; editorial footnote added at the
group noting the print split). Status: kept, logged.

## CC-S5 — Colophon Arabic example retained (AUTHORITY_LOCK R5)
`('من' …)` kept as intentional content; rendered in explicitly approved
DejaVu Sans fallback (2 chars, verified as the only non-locked spans).
Layout fix (post-QA): the example moved from inline sentence position to
its own centered colophon line (`ഉദാഹരണം: ('من' മുതലായവ)`) after A4 /
Research exports were found splitting من across lines with U+0002 STX
artifacts in the text layer. Wording unchanged, layout-only; all three
editions re-driven and re-verified (0 control chars).
Status: applied.

## CC-S6 — Apparatus additions (logged, not corrections)
First-use `[IAST]` insertion from locked GLOSSARY.md (58 terms, per-file
first use, whole-word guarded); numbered chapter openers (01–18 + yoga
names + print spans); chapter-architecture plate; 7 labeled plates with
`Figure N … / Based on verses …`; true footnotes only for logged
editorial notes (ch18 split note); auto glossary (first-use spans) +
auto index (converged); print concordance (Research); custom outline.
