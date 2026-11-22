"""Same-shape audit of my labels (the pre-registered confirmation step: 'audit ... same-shape inconsistencies per
prompt across all checkpoints, which I adjudicate'), done mechanically with the checkers' own units:
- per-sentence constraints (sentence:increment, sentence:alliteration_increment, words:last_first, format:emoji):
  the number of sentences the upstream checker's own splitter (instructions_util.split_into_sentences) sees; <= 1
  means the per-sentence rule held vacuously (rule 1);
- format:sub-bullets: answers whose '*' bullets have no line starting with '-' (inline '- ' fragments only, rule 7)
  or no '*' line at all (rule 1).
Lists every item currently labelled genuine (by readers or by me) that has such a shape, and every gamed one that
does not (for the other direction). Writes out/audit.txt / .json.
"""
import json
import re
import sys

import rvc_hand as H
from rvc_core import SCR, Tee, dump, upstream_record

sys.path.insert(0, str(SCR / "upstream" / "ifbench"))
from rvc_graders import IFB  # noqa: E402,F401  (loads the upstream package)
from ifbench import instructions_util as IU  # noqa: E402

PER_SENT = {"sentence:increment", "sentence:alliteration_increment", "words:last_first", "format:emoji"}


def shape(pid, ans):
    ids = set(upstream_record(pid)[1]["instruction_id_list"])
    out = {}
    if ids & PER_SENT:
        out["n_sent_checker"] = len(IU.split_into_sentences(ans))
    if "format:sub-bullets" in ids:
        lines = ans.splitlines()
        out["star_lines"] = sum(l.lstrip().startswith("*") for l in lines)
        out["dash_lines"] = sum(bool(re.match(r"\s*-", l)) for l in lines)
    return out


def main():
    T = Tee("audit.txt")
    L = H.labels()
    lab = H.lab_fn(L)
    allk = set()
    for c in H.CK:
        for p in H.REACH:
            allk |= set(H.B[c][p])
    for p, d in H.X.items():
        for c, ks in d.items():
            allk |= set(ks)
    for c in H.CKA:
        allk |= set(H.ARMC[c])
    flags = []
    seen = set()
    for k in sorted(allk):
        v = lab(k)
        if v is None:
            continue
        g = H.gkey(k)
        if g in seen:
            continue
        seen.add(g)
        s = shape(k[1], H.answers()[k])
        if not s:
            continue
        vac = s.get("n_sent_checker", 9) <= 1 or (("star_lines" in s) and (s["star_lines"] == 0 or s["dash_lines"] == 0))
        if (v == "genuine" and vac) or (v == "gamed" and not vac and H.source(L, k) == "screen"):
            flags.append({"key": list(k), "group": list(g), "label": v, "how": H.source(L, k), "shape": s})
    T(f"labelled groups with a per-sentence or sub-bullet constraint whose label disagrees with the vacuous-shape test: {len(flags)}")
    for f in flags:
        T(f"   {f['key']} {f['label']} ({f['how'][:40]}) {f['shape']}")
    dump(flags, "audit.json")


if __name__ == "__main__":
    main()
