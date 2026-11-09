#!/usr/bin/env python3
"""Prompt set of the next rung under cut 2 (pre-registration § Budget: rungs 3 and 4 only on reach prompts no earlier rung
elicited; calibration always runs). VPS-side.

  python3 olmo_ifladder/next_rung.py 3   -> olmo_ifladder/order_r3.txt (needs R2_dpo's gate decided on every candidate)
  python3 olmo_ifladder/next_rung.py 4   -> olmo_ifladder/order_r4.txt (needs R3_dpo's gate)
Order: longest expected first (rung 3: S0r3's per-prompt mean tokens; rung 4: R3_dpo's), for --order given.
"""
import csv
import gzip
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

A = Path("artifacts/olmo_ifladder")
O = Path("olmo_ifladder")
spec = importlib.util.spec_from_file_location("gate", O / "gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def means(job):
    t = defaultdict(list)
    with gzip.open(A / "samples" / f"{job}.jsonl.gz", "rt") as f:
        for ln in f:
            r = json.loads(ln)
            t[r["pid"]].append(r["n_tok"])
    return {p: sum(v) / len(v) for p, v in t.items()}


def main():
    r = int(sys.argv[1])
    prompts = list(csv.DictReader(open(O / "prompts.csv")))
    earlier = [f"R{k}_dpo" for k in range(2, r)]
    cells, _, _ = gate.walk(earlier)
    st = {(c["job"], c["pid"]): c["status"] for c in cells}
    keep, undecided = [], []
    for p in prompts:
        pid = p["pid"]
        if p["set"] == "calib":
            keep.append(pid)
            continue
        if p["r1_elicited"] == "True":
            continue
        s = [st.get((j, pid), "no strict success") for j in earlier]
        if "open" in s:
            undecided.append(pid)
        elif "elicited" not in s:
            keep.append(pid)
    if undecided:
        sys.exit(f"undecided cells (finish the gate first): {undecided}")
    m = means("S0r3" if r == 3 else f"R{r - 1}_dpo")
    keep.sort(key=lambda x: -m.get(x, 0))
    (O / f"order_r{r}.txt").write_text("\n".join(keep) + "\n")
    n_reach = sum(1 for x in keep if x.startswith("if") and x not in {p["pid"] for p in prompts if p["set"] == "calib"})
    print(f"rung {r}: {len(keep)} prompts ({n_reach} reach + calibration) -> olmo_ifladder/order_r{r}.txt")


if __name__ == "__main__":
    main()
