# Doc 2 — Tantrāloka Chapter 1 Malayalam (abridged, illustrated)

Abridged Malayalam rendering of Tantrāloka Chapter 1 (Abhinavagupta,
with Jayaratha's Viveka), via Dyczkowski 2023 English.

- `Tantraloka_Malayalam_v01.pdf` (.docx alongside) — 280 pages A4:
  front + vv1–21 + vv22–105 + vv106–139 + vv140–245 + vv247–335
  + appendices (sound levels, dvādaśānta table, abbreviations).
- Every śloka carries one code-drawn figure directly beneath it
  (334 figures: ത്രിതയം, ചക്രം, സോപാനം, പ്രവാഹം, ദർപ്പണം,
  പരമ്പര, നാദതലം, അലങ്കാരം) with a Malayalam caption
  (ഉദാ. ചിത്രം ൧൦൬ — ദ്വാദശീസംഘം · ചക്രം). Named mandalas
  (12-Kālī wheel, triśūla, 36-tattva ascent, sound stages) lead;
  each verse highlights its own spoke/step/stage.
- `translated/` — 7 QA-clean Markdown sources
  (`ta_front.md`, `ta_v02.md`…`ta_v06.md`, `ta_app.md`).
  Each verse group: നേരർത്ഥം + ആചാര്യവ്യാഖ്യാനം + വിശകലനം.
- `assets/` — 334 PIL PNGs + `captions.json` (all Malayalam).
- `tools/fig_ta.py` — figure generator (deterministic, offline).
- `GLOSSARY.md` — locked term list.

Rules: mūla in Malayalam script, middle Malayalam, abridged Viveka,
verse numbering per Kashmir pāṭha (print-246 = Kashmir-245, noted
at v245). QA: zero banned scripts, Latin only in [brackets].

## v02 — publisher-grade production upgrade (same translation)
- `Tantraloka_Malayalam_Volume1_v02_A4.pdf` (+ `.docx`) — 124 pages, A4.
- `Tantraloka_Malayalam_Volume1_v02_Trade.pdf` (+ `.docx`) — 195 pages,
  true 6×9″ reflow (not scaled).
- Original series cover + house style (`SERIES_STYLE.md`, binding for Vol.2);
  36 curated diagram plates (`assets/figs_v02/`, `tools/fig_v02.py`);
  true footnotes (13); per-section running heads; continuous folios;
  linked contents with real page numbers; 61 exact PDF bookmarks; clean
  searchable text layer (3 locked font families, zero fallback/PUA).
- Copy-edits only (logged in `CONTENT_CORRECTIONS_V1.md`, terms in
  `TERM_AUDIT_V1.md`): 4 wrong-script digits, mūla-policy wording,
  10 IAST spellings, 8 heading normalisations. Verse inventory unchanged
  (334 mūla, Kashmir 1–335 minus 246).
- Build: `tools/build_v02.py` + `tools/toc_pass2.py` (two-pass TOC/folios);
  QA gate report `QA_REPORT_V1_v02.md`, log `BUILD_LOG_V1_v02.md`.

Note: pushed here by explicit override of the project's local-only
rule for this release.
