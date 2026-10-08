#!/usr/bin/env python3
"""Auto-generate the v03 scholarly index from FINAL pagination (§29).

For each glossary headword (+ key names/texts), find the body pages where
it occurs (raw-text substring search — the layer is clean). Output JSON
[[term, [pages...]]]. Nothing is fabricated: absent terms get no entry.
Usage: make_index_v03.py <pdf> <out.json>
"""
import json
import re
import sys

import pymupdf

INDEX_TERMS = [
    # (Malayalam headword, display label)
    ("പരമശിവൻ", "പരമശിവൻ [Paramaśiva]"),
    ("ബൈരവൻ", "ബൈരവൻ [Bhairava]"),
    ("ശക്തി", "ശക്തി [śakti]"),
    ("ത്രികം", "ത്രികം [Trika]"),
    ("ഉപായം", "ഉപായം [upāya]"),
    ("ശാംഭവോപായം", "ശാംഭവോപായം [śāmbhavopāya]"),
    ("ശാക്തോപായം", "ശാക്തോപായം [śāktopāya]"),
    ("ആണവോപായം", "ആണവോപായം [āṇavopāya]"),
    ("അനുപായം", "അനുപായം [anupāya]"),
    ("വിജ്ഞാനം", "വിജ്ഞാനം [vijñāna]"),
    ("പ്രത്യഭിജ്ഞ", "പ്രത്യഭിജ്ഞ [pratyabhijñā]"),
    ("സ്പന്ദം", "സ്പന്ദം [spanda]"),
    ("മായ", "മായ [māyā]"),
    ("മലം", "മലം [mala]"),
    ("വിമർശം", "വിമർശം [vimarśa]"),
    ("പ്രകാശം", "പ്രകാശം [prakāśa]"),
    ("അനുത്തരം", "അനുത്തരം [anuttara]"),
    ("ഹൃദയം", "ഹൃദയം [hṛdaya]"),
    ("വിസർഗം", "വിസർഗം [visarga]"),
    ("ദീക്ഷ", "ദീക്ഷ [dīkṣā]"),
    ("ഗുരു", "ഗുരു [guru]"),
    ("മോക്ഷം", "മോക്ഷം [mokṣa]"),
    ("ബന്ധം", "ബന്ധം [bandha]"),
    ("ജ്ഞാനം", "ജ്ഞാനം [jñāna]"),
    ("അജ്ഞാനം", "അജ്ഞാനം [ajñāna]"),
    ("ചക്രം", "ചക്രം [cakra]"),
    ("കുലം", "കുലം [kula]"),
    ("സമാവേശം", "സമാവേശം [samāveśa]"),
    ("മണ്ഡലം", "മണ്ഡലം [maṇḍala]"),
    ("മന്ത്രം", "മന്ത്രം [mantra]"),
    ("അഭിനവഗുപ്തൻ", "അഭിനവഗുപ്തൻ [Abhinavagupta]"),
    ("ജയരഥൻ", "ജയരഥൻ [Jayaratha]"),
    ("സ്വച്ഛന്ദതന്ത്രം", "സ്വച്ഛന്ദതന്ത്രം [Svacchandatantra]"),
    ("വിജ്ഞാനഭൈരവം", "വിജ്ഞാനഭൈരവം [Vijñānabhairava]"),
    ("നേത്രതന്ത്രം", "നേത്രതന്ത്രം [Netratantra]"),
    ("സ്പന്ദകാരിക", "സ്പന്ദകാരിക [Spandakārikā]"),
    ("മാലിനീവിജയോത്തരം", "മാലിനീവിജയോത്തരം [Mālinīvijayottaratantra]"),
    ("ശിവസൂത്രം", "ശിവസൂത്രം [Śivasūtra]"),
]


def main():
    pdf, out = sys.argv[1], sys.argv[2]
    first_body = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    d = pymupdf.open(pdf)
    # body-only range: from first chapter page up to (not incl.) glossary
    last_body = len(d)
    for i in range(len(d)):
        if "പദാവലി—Glossary" in re.sub(r"\s+", "", d[i].get_text()):
            last_body = i  # 0-based exclusive
            break
    raws = []
    for i in range(len(d)):
        t = d[i].get_text()
        raws.append(re.sub(r"\s+", "", t))
    entries = []
    for ml, label in INDEX_TERMS:
        pages = [i + 1 for i in range(first_body - 1, last_body)
                 if ml in raws[i]]
        if pages:
            entries.append([label, pages])
    with open(out, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=1)
    print("index entries:", len(entries),
          "body range %d–%d" % (first_body, last_body))


if __name__ == "__main__":
    main()
