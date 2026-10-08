# CONTENT_CORRECTIONS_V1.md — Tantrāloka Malayalam Vol.1, v02 copy-edit log

Scope: professional copy-editing QA pass over `translated/*.md` (approved Malayalam
translation preserved; doctrinal meaning never altered for prose). Each entry:
location, before → after, reason. Only substantive corrections are listed;
pure layout decisions live in `BUILD_LOG_V1_v02.md`.

## 1. Script-contamination fixes

### ORI-001 — Oriya digits masquerading as Malayalam numerals (ta_front.md:16)
- Before: `സമാപനം (൨൨୨–൨൩୨); ഗുരുപരമ്പര (൨൩୨–൨൩୮); … (൨൩୯–…)` containing
  U+0B68 ×2, U+0B6E ×1, U+0B6F ×1 (Oriya ୨ ୮ ୯).
- After: same four positions set in Malayalam digits (U+0D68, U+0D6E, U+0D6F):
  `സമാപനം (൨൨൫–൨൩൨); ഗുരുപരമ്പര (൨൩൨–൨൩൮); … (൨൩൯–൨൪൫)`.
- Reason: wrong-script glyphs break the text layer, trigger fallback fonts
  (NotoSansOriya embedded in v01 PDF), and corrupt search/copy. Verified:
  zero `[\u0b66-\u0b6f]` remain in all sources.

## 2. Editorial-policy wording (Mula policy, spec §D)

### MULA-WORD-001 — "fully translated" ambiguity (ta_front.md §എങ്ങനെ വായിക്കാം)
- Before: `…സ്വർണ്ണപ്പെട്ടിയിൽ നൽകിയിരിക്കുന്നു; അവ പൂർണ്ണമായി
  പരിഭാഷപ്പെടുത്തിയിരിക്കുന്നു.` — reads as if the Mula block itself is translated.
- After: `മൂലശ്ലോകങ്ങൾ സംസ്കൃതത്തിൽത്തന്നെ — മലയാളലിപിയിൽ — സ്വർണ്ണപ്പെട്ടിയിൽ
  നൽകിയിരിക്കുന്നു; മൂലപാഠം പരിഭാഷപ്പെടുത്തിയിട്ടില്ല. ഓരോ മൂലശ്ലോകത്തിനും
  തുടർന്ന് മലയാളത്തിൽ നേരർത്ഥവും വിശദീകരണവും പൂർണ്ണമായി നൽകിയിരിക്കുന്നു.`
- Reason: enforces the locked three-tier policy —
  Sanskrit Mula → Malayalam-script Sanskrit → Malayalam commentary.
  The old builder string with identical wording (tools/build_ta.py:309) is
  superseded by the v02 frontmatter and is not carried forward.

### MARKER-001 — note-marker example uses Latin (ta_front.md §എങ്ങനെ വായിക്കാം)
- Before: `` `[കു.N]` `` (Latin N inside brackets in running text).
- After: `` `[കു.൧]` `` (Malayalam numeral, matching the actual
  `**കുറിപ്പ് ൧ —**` apparatus).
- Reason: keep running text free of stray Latin; example now mirrors real usage.

## 3. Malformed IAST (spec §C) — abbreviation table (ta_app.md:170–183)

| # | Before | After | Note |
|---|--------|-------|------|
| IAST-001 | [Vijnanabhairava] | [Vijñānabhairava] | ñ, ā restored |
| IAST-002 | [Pararthasara] | [Paramārthasāra] | ā ×3 restored |
| IAST-003 | [Isvarapratyabhijnakarika] | [Īśvarapratyabhijñākārikā] | Ī, ś, jñ, ā restored |
| IAST-004 | [Malinivijayottaratantra] | [Mālinīvijayottaratantra] | ā, ī restored |
| IAST-005 | [Yogavasistha] | [Yogavāsiṣṭha] | ā, ṣ, ṭh restored |
| IAST-006 | [Mahabharata] | [Mahābhārata] | ā ×2 restored |
| IAST-007 | [Rgveda] | [Ṛgveda] | Ṛ restored |
| IAST-008 | [Chandogyopanisad] | [Chāndogyopaniṣad] | ā, ṣ restored |
| IAST-009 | [Brhadaranyakopanisad] | [Bṛhadāraṇyakopaniṣad] | ṛ, ā, ṇ, ṣ restored |
| IAST-010 | [Spandakarika] | [Spandakārikā] | ā ×2 restored |

Reference spellings cross-checked against the source frontmatter abbreviation
list (source.txt ll.314–486) and GLOSSARY.md. No doctrinal content affected.

## 4. Heading normalisation (spec §M — hierarchy, no meaning change)

### HEAD-001…008 — bare numeral H2s (ta_v05.md:503–660)
Eight subsections were headed by verse-range first (`## ൧൯൮–൨൦൧ — …`),
breaking the Chapter → major → doctrinal → verse-range hierarchy used by all
other 40+ headings. Reordered label-first, wording otherwise byte-identical:
- `ഗുണത്താൽ ആരാധന — ശ്ലോകങ്ങൾ ൧൯൮–൨൦൧`
- `ശക്തികിരണവും ഉപമയും — ശ്ലോകങ്ങൾ ൨൦൨–൨൧൦`
- `ചിന്തകൂടാത്ത വഴി — ശ്ലോകങ്ങൾ ൨൧൧–൨൧൩`
- `ശാക്തമായ മനസ്സ് — ശ്ലോകങ്ങൾ ൨൧൪–൨൧൮` (label kept verbatim; a draft
  renaming to `ശാക്തോപായം` was considered and REJECTED to avoid loss of nuance)
- `ആണവവുമായുള്ള വ്യത്യാസം — ശ്ലോകങ്ങൾ ൨൧൯–൨൨൫` (same reason)
- `ഫലം ഒന്ന് — ശ്ലോകങ്ങൾ ൨൨൫–൨൩൨`
- `ഗുരുവും കുടുംബവും — ശ്ലോകങ്ങൾ ൨൩൨–൨൩൮`
- `മലവും അനുത്തരവും — ശ്ലോകങ്ങൾ ൨൩൯–൨൪൫`

## 5. Checks performed with NO change (recorded for audit completeness)
- Verse inventory: 334 `॥N॥` marks, unique, exactly Kashmir vv.1–335 minus
  v.246 variant — no missing, extra, or duplicated numbers.
- No Devanagari runs except intentional U+0965 ॥ terminators (972 marks).
- No Tamil/Arabic/Cyrillic; Latin only inside `[...]`; `qa_ta.py`: ALL CLEAN.
- No double spaces, no translator-voice/provenance/path leaks in sources.
- `ഷഡർദ്ധം [ṣāḍardha]` occurrences (ta_v02:134,209) verified against source
  usage — correct, retained. Mula-internal `ഷഡ്…` strings are Sanskrit, retained.
- `**കുറിപ്പ് ൧… —**` apparatus (13 notes, Malayalam numerals, renumbered per
  part per locked rule): text unchanged; v02 anchors each as a true footnote at
  the close of its verse group (editorial apparatus decision, see BUILD_LOG).

## 7. Late-pass prose fixes (builder strings + source year)
- YEAR-001: ASCII `2023` → `൨൦൨൩` in edition-note prose (build_v02.py) and
  ta_front.md:9 (source consistency; Malayalam-numeral convention).
- LATIN-001: stray English `(footnotes)` dropped from the reading guide
  (running-text Latin restricted to `[...]`; the sentence is complete
  without it).
- INTRO-001 (restoration, not correction): v02 first omitted the approved
  ഗ്രന്ഥപരിചയം frontmatter (ta_front.md); restored in full except its
  `എങ്ങനെ വായിക്കാം`, superseded by the expanded guide (logged here so
  the omission is never mistaken for lost content).
(v01 PDF artefacts, resolved in the v02 build; logged here for traceability)
- BULLET-001: Word `List Bullet` style emitted Symbol-font bullets → 84×
  U+F0B7 private-use characters in v01 text layer. v02 uses literal `•`
  (U+2022) in Noto Sans Malayalam.
- FALLBACK-001: v01 PDF embedded DejaVuSans/OpenSymbol/Lohit-Malayalam/
  NotoSansOriya fallbacks. v02 locks three families (see SERIES_STYLE.md) and
  sets ascii/hAnsi/cs on every run; IAST runs explicitly use Noto Serif.
