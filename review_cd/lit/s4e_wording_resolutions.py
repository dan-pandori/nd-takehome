"""Manual resolution of (a) the 13 V rows that the population scan matched below fuzzy 0.85 / not at all and (b) the
26 fuzzy fragment matches the diff pass flagged as possible wording changes. Each was inspected in the raw source
(ctx.py / near.py). Categories: markup (LaTeX/unicode math rendering), short-fragment (too few tokens for the fuzzy
matcher; found by direct search), nested-quotes (fragment extractor split at inner quotes; real quotes found),
pdf-artefact (watermark / two-column interleaving / footnote marker), window-edge (diff includes a word just outside
the quote), editorial-bracket ([s] edits), inflection (quoted word inflected differently: a real, minor wording change).
Checks coverage against s4b_population.txt and s4c_fuzzy_diffs.txt; writes s4e_resolutions.tsv and s4e_tally.txt."""
import re
from collections import Counter

from common import OUT

R = {
    ("L1", 2): ("short-fragment, markup", "'$n=200$ and $k\\leq 100$' at line 308; Eq. (1) confirmed"),
    ("L1", 30): ("markup", "'$\\sim$2-4 orders of magnitude'"),
    ("L1", 128): ("markup", "'\\approx 1\\times 10'"),
    ("L1", 129): ("markup", "'$1.21\\text{\\times}{10}^{-1}$ to $3.75...$' line 181"),
    ("L1", 131): ("markup", "'\\mathord{\\sim}5'"),
    ("L1", 132): ("markup", "'\\mathord{\\sim}'"),
    ("L1", 149): ("inflection", "source: SGD \"stumbles in the dark\"; ledger quotes \"stumble in the dark\" (meaning kept)"),
    ("L1", 161): ("markup", "'p\\sim Beta(\\alpha,\\beta)'"),
    ("L2", 74): ("window-edge, markup", "'(ceteris paribus) the more reliably the model $\\phi$ s'"),
    ("L4", 8): ("markup", "'\\tilde{Y}', '\\mathds{1}', '\\geq'"),
    ("L4", 20): ("window-edge, markup", "'h\\in[0.8,1.0]'"),
    ("L4", 21): ("markup", "'\\bar{C}_{m,f}'"),
    ("L4", 27): ("markup", "'X^{\\top}X(X_{\\mathcal{M}}^{\\top}X_{\\mathcal{M}})^{-1}' line 487"),
    ("L4", 52): ("markup", "'1/\\sqrt{n}'"),
    ("L4", 88): ("window-edge, markup", "'$\\theta_{i}(s,t)$'"),
    ("L4", 94): ("markup", "'the $\\theta$ scales linearly with $\\log\\mathrm{FLOP}$' line 200"),
    ("L4", 103): ("markup", "'$\\theta_{i}=b_{j}$ (where $I=a_{j}^{2}/4$)' line 198"),
    ("L4", 158): ("nested-quotes", "quotes 'We cannot determine ...' and 'as to how much the person probably knows' found (lines 73, 103)"),
    ("L4", 159): ("pdf-artefact", "footnote marker: 'Specific Objectivity1 is the requirement ...'"),
    ("L5", 143): ("nested-quotes", "quotes found in Defs. 3.5-3.6 (lines 299-313); paraphrase matches Def. 3.6"),
    ("L6", 29): ("markup", "'\\mathtt{reFT}'"),
    ("L6", 31): ("window-edge, markup", "'\\mathtt{Scr.+FT}', '$4.5$ K'"),
    ("L6", 33): ("short-fragment, markup", "'Not in $\\mathtt{PT}$' row 12/31/44/81% and caption found (line 321)"),
    ("L6", 35): ("markup", "'\\mathtt{...}'"),
    ("L6", 68): ("short-fragment, markup", "'$\\sim-13$ to $-8$' line 95"),
    ("L6", 78): ("short-fragment, markup", "'$\\sim 83\\%$' line 323"),
    ("L6", 90): ("short-fragment, markup", "'$\\sim\\!77\\%$' line 672"),
    ("L6", 95): ("short-fragment, markup", "'recovers $\\sim\\!20\\%$' line 654"),
    ("L6", 96): ("editorial-bracket", "'assume[s]'; full sentence 'they assume the diff can be explained ...' found"),
    ("L6", 99): ("pdf-artefact", "'ACCEPTED ARTICLE' watermark between '58' and 'billion'"),
    ("L6", 106): ("pdf-artefact", "'ACCEPTED ARTICLE' watermark"),
    ("L6", 172): ("pdf-artefact", "two-column interleaving: '... whereas RL opti- / mizes for the single best move'"),
}
low = open(f"{OUT}/s4b_population.txt").read().split("rows below fuzzy 0.85")[1].split("V rows whose location")[0]
low_rows = set((a, int(b)) for a, b in re.findall(r"^  (L\d) #(\d+) ", low, re.M))
flagged = set((a, int(b)) for a, b in re.findall(r"^(L\d) #(\d+) .*\[WORDING\?\]", open(f"{OUT}/s4c_fuzzy_diffs.txt").read(),
                                                  re.M))
need = low_rows | flagged
have = set(R)
lines = [f"rows needing manual review: {len(need)} (low-score {len(low_rows)}, wording-flagged {len(flagged)}, "
         f"overlap {len(low_rows & flagged)}); resolved {len(have & need)}; missing {sorted(need - have)}; "
         f"extra {sorted(have - need)}"]
cats = Counter()
for k in sorted(need & have):
    for c in R[k][0].split(", "):
        cats[c] += 1
lines.append("categories (a row can have two): " + ", ".join(f"{k} {v}" for k, v in cats.most_common()))
lines.append(f"genuine wording differences: {sum(1 for k in need & have if 'inflection' in R[k][0])} "
             f"({[f'{a} #{b}' for (a, b) in sorted(need & have) if 'inflection' in R[(a, b)][0]]})")
with open(f"{OUT}/s4e_resolutions.tsv", "w", encoding="utf-8") as fh:
    fh.write("reader\tn\tcategory\tnote\n")
    for (a, b) in sorted(need & have):
        fh.write(f"{a}\t{b}\t{R[(a, b)][0]}\t{R[(a, b)][1]}\n")
open(f"{OUT}/s4e_tally.txt", "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
