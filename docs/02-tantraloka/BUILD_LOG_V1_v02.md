# BUILD_LOG_V1_v02.md — production build record

## Toolchain
`tools/build_v02.py` (new, ~1350 lines; v01 `build_ta.py` untouched) +
`tools/fig_v02.py` (36 curated plates) + `tools/cover_v02.py` (emblem) +
`tools/toc_pass2.py` (two-pass TOC + folio starts + gates).
Convert: `libreoffice --headless --convert-to pdf`. Post: `/Lang=ml`
via pymupdf catalog write (LibreOffice drops document language).

## Pass history (both editions: pass1 → convert → pass2 --toc --starts)
- P1: base build (124pp A4). Found: shared header/footer accumulation →
  unlink+clear per section; CTL fallback (Lohit/DejaVu in headings) →
  explicit per-run fonts (`styled_heading`); `•/·` missing from Noto
  Malayalam → routed to Noto Serif (fontTools-verified).
- P2: footnotes wired (lost-paragraph bug: `fn.append(par)` missing →
  fixed); empty TOC (rendered before collection) → `scan_headings`
  pre-pass + `AnchorGen` dedupe + mismatch gate; duplicate V-anchors
  resolved (`_2` suffix, deterministic).
- P3: folio restart-per-section (measured) → explicit absolute starts
  via `--starts`; even/odd heads ignored by converter (spike-proven) →
  single centered combined head; footnote eachSect renders "0" past first
  (visually proven 1,0,0,0) → global numbering, titles kept per-part.
- P4: visual QA → VQ-001 drop page frames (propagate to all pages);
  VQ-002 drop `w:background` (ignored → DOCX/PDF desync); VQ-003 drop
  internal-H1 render; VQ-004 lead paras flush-left; VQ-005 cover imprint;
  Trade heads to 7pt + trim-adapted series string (wrap measured);
  figures 3.1→2.9" / 2.7→2.5"; ornaments keepNext; appendix ornament
  dropped (orphaned unit measured A4 p122/Trade p192); intro restored;
  `(footnotes)`/`2023` prose leaks fixed; colophon series note added.
- P5 (final): A4 124pp / Trade 195pp… (final rerun) A4 124pp, Trade 195pp;
  all gates green twice (pre/post intro-restore).

## Converter constraints discovered (binding for Vol.2)
1. Even/odd Word headers ignored (all pages get default head).
2. Page numbering restarts at each section without explicit `pgNumType/start`.
3. `footnotePr numRestart=eachSect` yields markers 1,0,0,0… — never use.
4. `w:background` page color ignored in PDF export.
5. First-section `pgBorders` propagate to all pages.
6. Footnote numbering is correct only globally (1..N in document order).
7. PyMuPDF layout-mode splits Malayalam clusters with newlines — always
   verify text assertions against `-raw` output / whitespace-stripped.

## Repro (Vol.2 runs the same)
`build_v02.py --edition {a4,trade}` → LO convert → `toc_pass2.py {A4,Trade}`
(rebuilds with numbers+starts, reconverts, asserts stability+folios) →
set `/Lang` → verify per QA_REPORT. Do NOT hand-edit DOCX between passes.
