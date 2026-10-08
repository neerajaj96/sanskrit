# NUMERAL_AUDIT_V3.md — spec §0 gate

Policy: every ordinary book number in ASCII 0–9; no Malayalam (or any non-ASCII decimal) numerals anywhere in production.

## PDF scan (Tantraloka_Malayalam_Volume1_v03_A4.pdf, 134 pages)
- Non-ASCII decimal hits: **0** (none)
- ASCII verse marks (॥ N ॥): 334 unique 334
- Verdict: **PASS**

## Source inventory (must be fully converted at render)
- Malayalam digits in `translated/*.md`: 1556
- Render-layer conversion: central NORM() in text entry points; sources byte-identical (md5 baseline /tmp/sources_v03_baseline.md5).

Status: PASS — release allowed
