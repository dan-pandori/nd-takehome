"""Follow-up to s6: fragments of notes/*.md not found exactly anywhere are fuzzy-matched (s4 matcher) against the
note's own sources (arXiv ids in the note header + a map for non-arXiv notes). Writes s6b_note_misses.txt listing
the best score per fragment; fragments below 0.85 are for manual classification."""
import glob
import os
import re

import s4_reverify as M
import s6_quotes_notes_review as Q
from common import LIT, OUT, arxiv_ids

NONARX = {"firestone2020performance.md": ["firestone2020-performance.txt"],
          "maier2025abilities.md": ["sep-abilities.txt", "sep-dispositions.txt"],
          "martinezplumed2019irt.md": ["martinezplumed2016irt-ecai.txt"],
          "lindsey2024crosscoders.md": ["lindsey2024crosscoders.txt"],
          "hernandezorallo2017evaluation.md": ["hernandezorallo2021generality.txt"],
          "shin2023superhuman.md": [], "korbak2022rlkl.md": []}
srcs = {}
lines = []
low = []
n_all = n_fz = 0
for f in sorted(glob.glob(f"{LIT}/notes/*.md")):
    name = os.path.basename(f)
    t = open(f, encoding="utf-8").read()
    head = t.split("## Learnings")[0]
    files = []
    for a in dict.fromkeys(arxiv_ids(head)):
        files += M.find_source(a)
    files += NONARX.get(name, [])
    for q in Q.frags(t):
        if Q.find(q)[0] != "notfound":
            continue
        n_all += 1
        best = (0.0, None, None)
        for fn in files:
            if fn not in srcs:
                srcs[fn] = M.Source(fn)
            got = srcs[fn].search(q)
            sc = 1.0 if got[0] in ("exact", "exact(dehyph)", "alnum") else (
                float(got[0][5:]) if got[0].startswith("fuzzy") else 0.0)
            if sc > best[0]:
                best = (sc, fn, got[2] if len(got) > 2 else None)
        if best[0] >= 0.85:
            n_fz += 1
        else:
            low.append((name, round(best[0], 2), q[:170]))
lines.append(f"note fragments not found exactly anywhere: {n_all}; fuzzy >= 0.85 in the note's own source: {n_fz}; "
             f"below 0.85 (manual): {len(low)}")
for x in low:
    lines.append(f"  [{x[0]}] best={x[1]} | {x[2]}")
open(f"{OUT}/s6b_note_misses.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
