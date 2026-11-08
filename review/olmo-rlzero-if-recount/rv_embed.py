"""Embedded-answer diagnostic (mine, not pre-registered) on the hand-reach prompts whose checker defines the whole answer
(IFBench format:options -- the answer must be exactly one option; custom:csv_city -- exactly a header + 7 rows):
for each base response within its first 256 draws (and each base_btok diagnostic response), does some segment of the
response pass the official checker on its own? Segments: every line; every blank-line-separated block; every fenced
code block; the text after the last 'answer' marker ('Answer:', 'answer is', 'Final answer'). A response with such a
segment carries the answer but fails the checker because of the surrounding text (planning, explanation, debris).
Output: out/embed.txt, out/embed.json"""
import json
import os
import re

import rv_core as C
from rv_graders import if_check

PIDS = ["ifbench_100", "ifbench_102", "ifbench_103", "ifbench_104", "ifbench_274"]


def segments(text):
    segs = set()
    for ln in text.split("\n"):
        if ln.strip():
            segs.add(ln.strip())
    for blk in re.split(r"\n\s*\n", text):
        if blk.strip():
            segs.add(blk.strip())
    for m in re.finditer(r"```[a-zA-Z]*\n(.*?)```", text, re.S):
        segs.add(m.group(1).strip())
    m = list(re.finditer(r"(?i)(final answer|answer is|answer:)", text))
    if m:
        segs.add(text[m[-1].end():].strip().strip(":").strip())
    return [s for s in segs if s]


def main():
    P = C.load_problems()
    cells = json.load(open(os.path.join(C.OUT, "cells.json")))
    want = {}
    for p in PIDS:
        for model in ("base", "base_btok"):
            for x in cells[model].get(p, [])[:256]:
                want[(x[0], x[1], x[2], p)] = (model, x[3])
    from rv_hand_items import fetch_texts
    T = fetch_texts(set(want))
    res, lines = {}, []
    for p in PIDS:
        for model in ("base", "base_btok"):
            rows = [(k, v) for k, v in want.items() if k[3] == p and v[0] == model]
            if not rows:
                continue
            n = len(rows)
            succ = sum(v[1] for _, v in rows)
            emb = 0
            ex = None
            for k, v in rows:
                if v[1]:
                    continue
                t = T[k]
                ans = C.remove_thinking_section(t)
                for s in segments(ans):
                    if if_check(P[p]["task"], P[p], s)[0]:
                        emb += 1
                        ex = ex or s[:80]
                        break
            res[f"{p}|{model}"] = {"n": n, "strict": succ, "fail": n - succ, "embedded": emb}
            lines.append(f"{p:12s} {model:9s} draws {n:3d} strict {succ:3d} failures {n - succ:3d} with an embedded "
                         f"checker-passing segment {emb:3d} ({emb / max(1, n - succ):.0%}); e.g. {ex!r}")
    json.dump(res, open(os.path.join(C.OUT, "embed.json"), "w"), indent=1)
    open(os.path.join(C.OUT, "embed.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
