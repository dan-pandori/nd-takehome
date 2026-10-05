"""Classify the note fragments that s6b left below fuzzy 0.85 (manual inspection recorded as rules + explicit lists).
Categories: misparse (text between two different quotations, caused by unbalanced quote marks: contains '**'/'##' or
starts with a parenthesis/full stop or a section reference), markup (verified in the raw source: LaTeX rendering),
pdf-artefact, near-quote (paper wording altered inside quotation marks), own-phrase (readers' scare-quoted phrases in
interpretive text; not attributed to the paper). Writes s6c_classes.txt."""
import re
from collections import Counter

from common import OUT

MARKUP = ["We found the fail-to-success ratio", "Typically at least the first 1/64", "maximized when θ_i=b_j",
          "the expected prediction error from using the subset", "from 1.21×10^-1", "well fit by a 3-parameter Kumaraswamy",
          "Empirically, we observe that the θ scales", "not already covered by π_ref", "log(c) ≈ a k^b"]
PDF = ["58 billion counterfactual game patterns"]
NEAR = {"Best currently available elicitation": "2406.07358 Sec. 2 has 'the best currently available capability "
                                                  "elicitation techniques'",
        "how much a representation encodes property Y": "2003.12298 abstract has 'how well pretrained representations "
                                                          "encode some linguistic property'"}
MISPARSE_EXTRA = ["V-information (App. F). The authors suggest", "(chain rule) but the same"]
rows = re.findall(r"^  \[([^\]]+)\] best=([\d.]+) \| (.*)$", open(f"{OUT}/s6b_note_misses.txt").read(), re.M)
cls = []
for note, sc, frag in rows:
    if any(frag.startswith(m) for m in MARKUP):
        c = "markup"
    elif any(frag.startswith(m) for m in PDF):
        c = "pdf-artefact"
    elif any(frag.startswith(m) for m in NEAR):
        c = "near-quote"
    elif ("**" in frag or "##" in frag or re.match(r"^[().]", frag) or re.search(r"\((Sec|App|Abstract|same section)",
                                                                                   frag)
          or any(frag.startswith(m) for m in MISPARSE_EXTRA)):
        c = "misparse"
    else:
        c = "own-phrase"
    cls.append((c, note, sc, frag))
cnt = Counter(c for c, *_ in cls)
out = [f"note fragments below fuzzy 0.85: {len(cls)}; " + ", ".join(f"{k} {v}" for k, v in cnt.most_common())]
for c, note, sc, frag in sorted(cls):
    extra = next((v for k, v in NEAR.items() if frag.startswith(k)), "")
    out.append(f"  {c:12s} [{note}] {frag[:110]} {('-- ' + extra) if extra else ''}")
# REVIEW.md fragments not found exactly (s6_quotes.txt), classified by inspection
REV = {"sum over known proofs": "own-phrase", "it was already there": "own-phrase", "more of the same": "own-phrase",
       "RL moves the model along the pretraining axis vs off it": "own-phrase", "is RL more pretraining?": "own-phrase",
       "for each additional 10× of train-time compute, about 15× of test-time compute can be eliminated":
           "markup (2104.03113 line 371: '$10\\times$ ... $15\\times$')",
       "the original probability π0(x) up to Z": "markup (2205.11275 Sec. 5: '\\pi_0(x) up to Z'; ledger L5 #4)",
       "examples needed to reach a stated loss": "near-quote (2009.07368 line 97: 'the number of samples required to "
                                                 "reach that loss tolerance')"}
rev = re.findall(r"^    NOT FOUND \[REVIEW.md\] (.*)$", open(f"{OUT}/s6_quotes.txt").read(), re.M)
rc = Counter(REV[x].split(" ")[0] for x in rev)
out.append("")
out.append(f"REVIEW.md fragments not found exactly: {len(rev)}; " + ", ".join(f"{k} {v}" for k, v in rc.most_common()))
for x in rev:
    out.append(f"  {REV[x]} | {x}")
open(f"{OUT}/s6c_classes.txt", "w").write("\n".join(out) + "\n")
print("\n".join(out))
