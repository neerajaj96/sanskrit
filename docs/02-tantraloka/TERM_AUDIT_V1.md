# TERM_AUDIT_V1.md — terminology consistency audit (v02)

Authority: `GLOSSARY.md` (locked). Rule: Malayalam term + [IAST] on first use
per chapter, plain Malayalam after; abbreviations expanded in the glossary
table, never re-translated.

## Method
Automated inventory of every `[...]` token across `translated/*.md`
(≈120 unique tokens), plus targeted scans for known variant spellings
(വരമശിവൻ, ഷഡർദ്ധ-misuse, Latin leaks, provenance terms).

## Findings

### T1. Core doctrinal terms — PASS
All 30+ locked terms appear in canonical Malayalam form with correct IAST on
first use, e.g. പരമശിവൻ [Paramaśiva], ബൈരവൻ [Bhairava], ശക്തി [śakti],
ത്രികം [Trika], ഉപായം [upāya], ശാംഭവോപായം [śāmbhavopāya],
ശാക്തോപായം [śāktopāya], ആണവോപായം [āṇavopāya], അനുപായം [anupāya],
വിജ്ഞാനം [vijñāna], പ്രത്യഭിജ്ഞ [pratyabhijñā], സ്പന്ദം [spanda],
വിമർശം [vimarśa], പ്രകാശം [prakāśa], അനുത്തരം [anuttara], ഹൃദയം [hṛdaya],
വിസർഗം [visarga], സമാവേശം [samāveśa], മോക്ഷം [mokṣa], ദീക്ഷ [dīkṣā].
No invented variants found (zero hits for വരമശിവൻ and similar corruptions).

### T2. ṣāḍardha usage — PASS (checked, retained)
`ഷഡർദ്ധം [ṣāḍardha]` at ta_v02:134,209 is used exactly where the source
invokes the Trika code-name (cf. source discussion of ṣaḍardha-śāstra).
Other `ഷഡ്…` strings are inside Mula Sanskrit lines — correctly untouched.

### T3. Persons/texts — PASS
അഭിനവഗുപ്തൻ [Abhinavagupta], ജയരഥൻ [Jayaratha], വിവേകം [Viveka],
തന്ത്രാലോകം [Tantrāloka] used transliterated-only, never translated.

### T4. Abbreviation table — 10 IAST spellings CORRECTED (see CONTENT_CORRECTIONS
IAST-001…010)
The appendix table (ta_app.md) carried ten plain-ASCII approximations
([Vijnanabhairava], [Pararthasara], [Isvarapratyabhijnakarika],
[Malinivijayottaratantra], [Yogavasistha], [Mahabharata], [Rgveda],
[Chandogyopanisad], [Brhadaranyakopanisad], [Spandakarika]). All restored to
full IAST. Remaining table tokens ([TA], [TAv], [SvT], [VBh], [NT], [SpK],
[PT], [IPK], [MV], [YV], [MBh], [ChUp], [BrUp], [MPA], [MrT], [KM], [JY],
[KJN], [VāSū], [YG], [SvāSūSam], [NSA], [SJña], [PMNK], [TTP], [SYM], [VM],
[ÜKau], [TBh], [ŚM], [ŚSt], [Śvet], [Mund]) verified against the source
abbreviation list (source.txt ll.314–486).

### T5. Abbreviation scope — DECISION (not an error)
The v02 table keeps 40 compact rows (the load-bearing sigla of the abridged
commentary) rather than the source's ~80-entry apparatus-catalogue. This
follows the locked abridgment rule (drop MS-variant/parallel-passage
catalogues; compact glossary table). GLOSSARY.md:50 already flags the
uncertain source rows; no unverified row was carried in.

### T6. Verse-number convention — PASS
Malayalam numerals throughout (൧ ൨ ൳…), Kashmir numbering, dandas ॥
retained per GLOSSARY conventions. Post-fix scan: zero non-Malayalam digits
in numeral positions (Oriya contamination removed, ORI-001).

### T7. First-use-per-chapter bracketing — PASS with one noted exception
Spot-check across all six chapter files: each doctrinal term's first
occurrence carries [IAST]; later occurrences are bare Malayalam. Exception:
the frontmatter overview (§സംക്ഷിപ്തസൂചിക) re-brackets major text names —
intentional, as the frontmatter is a standalone reference aid, not the
chapter flow.

## Verdict
Terminology: CONSISTENT. 10 IAST spelling corrections applied (meaning-neutral).
No doctrinal term altered, added, or removed.
