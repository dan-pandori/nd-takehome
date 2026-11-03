#!/usr/bin/env python3
"""Relative L2 distance between checkpoints over the tensors of one safetensors shard.

Usage: weight_dist.py <label>=<file.safetensors> ... -- <labelA>:<labelB> ...
Prints, for each pair, ||A - B|| / ||B|| over all tensors present in both files (float32 arithmetic).
Used to check which base revision RL-Zero started from: the distance from step_0100 to its start should be of the
order of one 100-step RL increment (step_0200 vs step_0100), and far below the distance between base revisions.
"""
import json
import sys

import torch
from safetensors import safe_open


def main():
    argv = sys.argv[1:]
    k = argv.index("--")
    files = dict(a.split("=", 1) for a in argv[:k])
    pairs = [p.split(":") for p in argv[k + 1:]]
    handles = {lab: safe_open(path, framework="pt") for lab, path in files.items()}
    out = []
    for a, b in pairs:
        names = sorted(set(handles[a].keys()) & set(handles[b].keys()))
        num = den = 0.0
        for n in names:
            ta = handles[a].get_tensor(n).float()
            tb = handles[b].get_tensor(n).float()
            num += float(((ta - tb) ** 2).sum())
            den += float((tb ** 2).sum())
        out.append({"a": a, "b": b, "tensors": len(names), "rel_l2": (num / den) ** 0.5 if den else None})
        print(json.dumps(out[-1]), flush=True)


if __name__ == "__main__":
    main()
