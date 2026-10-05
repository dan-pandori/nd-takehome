"""Task 5 manual verdicts for the 12 sampled REVIEW.md sentences (indices from s5_sample.txt). Sentences are read
from s5_candidates.txt, not retyped. verdict: traced / traced-imprecise / not-traced. Writes s5_verdicts.tsv and
s5_tally.txt."""
import re
from collections import Counter

from common import OUT

cands = {int(l.split("\t")[0]): l.rstrip("\n").split("\t") for l in open(f"{OUT}/s5_candidates.txt", encoding="utf-8")}
picked = [int(x) for x in re.search(r"indices \[([^\]]+)\]", open(f"{OUT}/s5_sample.txt").read()).group(1).split(",")]
V = {
    3: ("traced", "L1 #113 (2410.13211v2 Sec. 3.1: re-weighting 'gives an unbiased estimator for the true probability')",
        "unbiasedness traces; 'a stronger policy as the proposal' is the review's application (Wu & Hilton's proposal "
        "is any other distribution q over inputs; unbiasedness also needs q to cover the target's support)"),
    12: ("traced", "L2 #101 (SEP Abilities Sec. 4.3, Kenny's darts player; source line 1146); L2 #72 (2405.08989v1 abstract)",
         "both quotes verbatim in source"),
    13: ("traced", "L5 #52/#55/#56 (compound divergence, 1912.09713v2); L5 #65 (Skill-Mix counting bound, Sec. 6); "
                   "L6 #102/#103 (novelty vs historical game database, 2303.07462v2 p. 7)", ""),
    15: ("traced", "L1 #2 (2107.03374v2 Sec. 2.1, Eq. 1; Eq. (1) at source lines 312-316)", ""),
    19: ("traced", "L1 #40 (2510.05197v1 Sec. 4.1; also my sample S5)", ""),
    20: ("traced", "L1 #52 (2310.03262v3 Sec. 4.1, Eq. 2: 'We stop sampling until r ... samples have passed')", ""),
    35: ("traced-imprecise", "L2 #95 (CA, Sec. 3.1); L2 #99 (Jaster, Sec. 3.4); L2 #100 (Sec. 4.1); L2 #101 (Sec. 4.3)",
         "\"mere possibility\" is printed as a quotation but the phrase does not occur in the SEP text; the verified "
         "possibility-is-not-sufficient sentence is in Sec. 4.1 (L2 #100), while Sec. 4.3 holds Kenny's fluky-success case"),
    36: ("traced", "L2 #72 (abstract) and L2 #78 (CAMA, Sec. 4.1, Def. 10)", ""),
    38: ("traced", "L2 #116 (2309.11975v2 Sec. 6); quote verbatim at source line 205", ""),
    46: ("traced", "L3 #101 (2505.11711v2 abstract; title 'Reinforcement Learning Finetunes Small Subnetworks'); "
                   "L3 #127 (2509.04259v1 Sec. 6: bfloat16 vs float32)", ""),
    52: ("traced", "L4 #13 / L1 #196 (2405.10938v3 abstract, low-dimensional capability space); L4 #21 (Sec. 3.4, Eq. 8, "
                   "f-equivalent FLOPs)", ""),
    70: ("traced-imprecise", "L6 #129 (2504.02922v4 abstract); L6 #134 (Sec. 3.1)",
         "source finding is for L1-loss crosscoders; the same ledger row records 'most BatchTopK chat-only latents are "
         "genuinely chat-specific', which REVIEW.md omits, so 'crosscoder model-only features are mostly artefacts' "
         "over-generalises"),
}
assert sorted(V) == sorted(picked), (sorted(V), picked)
rows = []
for k in picked:
    _, ln, sent = cands[k]
    v, trace, note = V[k]
    rows.append((k, ln, sent, v, trace, note))
with open(f"{OUT}/s5_verdicts.tsv", "w", encoding="utf-8") as fh:
    fh.write("cand\treview_line\tsentence\tverdict\ttraced_to\tnote\n")
    for r in rows:
        fh.write("\t".join(str(x).replace("\t", " ") for x in r) + "\n")
c = Counter(r[3] for r in rows)
out = f"REVIEW.md sentences checked: {len(rows)}; traced {c['traced']}; traced-imprecise {c['traced-imprecise']}; " \
      f"not traced {c['not-traced']}"
open(f"{OUT}/s5_tally.txt", "w").write(out + "\n")
print(out)
