#!/usr/bin/env python3
"""Headline results-registry rows of run olmo-transplant from olmo_transplant/summary.json (analyze.py): per cell on
reach-41, brief20 and calibration, the strict and (hand-gated) genuine rate, mean over prompts, with the 95 % prompt
bootstrap; plus the pre-registered contrasts. Models: writer dpo = allenai/Olmo-3-32B-Think-DPO main (97604023),
writer s2300 = allenai/Olmo-3.1-32B-Think main (97ade57a = step_2300); 32 B, bf16, pretrained, natural-language chat.
Usage: ND_RUN_ID=olmo-transplant headline_rows.py"""
import json
import sys

sys.path.insert(0, ".")
import record  # noqa: E402

S = json.load(open("olmo_transplant/summary.json"))
MODEL = {"dpo": "allenai/Olmo-3-32B-Think-DPO@97604023", "s2300": "allenai/Olmo-3.1-32B-Think@97ade57a (step_2300)"}
n = 0
for st in ("reach-41", "brief20", "calibration"):
    for cell, v in S[st].items():
        if cell == "contrasts":
            continue
        writer = "dpo" if cell in ("T1", "T4") or cell.endswith("-dpo") else "s2300"
        for kind in ("strict", "genuine"):
            t = v.get(kind)
            if not t or t[0] is None:
                continue
            record.record(f"{kind}_rate", round(t[0], 4), n=v["prompts"], split=st, arm=cell, role="eval",
                          source="olmo_transplant/summary.json (analyze.py; per-prompt rows in olmo_transplant/results.csv)",
                          ci95=[None if x is None else round(x, 4) for x in t[1:]], samples=v["samples"],
                          writer=writer, ckpt=MODEL[writer], checker="IFBench official strict"
                          + (" + blinded hand gate" if kind == "genuine" else ""))
            n += 1
    for k, t in S[st]["contrasts"].items():
        if t[0] is None:
            continue
        record.record("contrast", round(t[0], 4), n=t[3], split=st, arm=k, role="eval", source="olmo_transplant/summary.json",
                      ci95=[None if x is None else round(x, 4) for x in t[1:3]])
        n += 1
print(f"{n} headline rows")
