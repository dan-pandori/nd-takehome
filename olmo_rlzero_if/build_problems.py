#!/usr/bin/env python3
"""Build the evaluation and Stage-0 prompt sets of run olmo-rlzero-if (seeded; inputs pinned).

  build <dolci_parquet>   write olmo_rlzero_if/problems.jsonl, stage0_problems.jsonl, pids_ifbench.txt, pids_ifeval.txt

Evaluation (450): the IFBench (300, allenai/IFBench_test @ ed7c1245, all) and IFEval (150, the seeded subset of
google/IFEval @ 966cd895) rows of olmo_ifomega/problems.jsonl, unchanged (same pids, prompts, instruction lists and
kwargs), plus `ifomega_excl`: True for the 82 IFBench prompts olmo-ifomega excluded for Think-SFT/DPO/RL overlap
(olmo_ifomega/exclusions.csv), so "the 218" is ifbench & not ifomega_excl.
Stage 0 (lengths and throughput only; never an evaluation number): the 40 IFEval prompts of
olmo_ifomega/stage0_problems.jsonl (outside the 150 subset) and 24 prompts of allenai/Dolci-RL-Zero-IF-7B
@ c96e4e42 (RL-Zero-IF's own training prompts; random.Random(20261108) draw; the "user: " prefix of the released
`prompt` field dropped), task `rlzif`.
"""
import csv
import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OIF = HERE.parent / "olmo_ifomega"
SEED = 20261108


def main():
    if len(sys.argv) != 3 or sys.argv[1] != "build":
        sys.exit(__doc__)
    import pandas as pd
    pq = sys.argv[2]
    excl = {r["pid"] for r in csv.DictReader(open(OIF / "exclusions.csv"))}
    rows = [json.loads(l) for l in open(OIF / "problems.jsonl")]
    ev = [dict(r, ifomega_excl=r["pid"] in excl) for r in rows if r["task"] in ("ifbench", "ifeval")]
    assert len(ev) == 450 and sum(r["ifomega_excl"] for r in ev) == 82
    with open(HERE / "problems.jsonl", "w") as f:
        for r in ev:
            f.write(json.dumps(r) + "\n")
    for t in ("ifbench", "ifeval"):
        (HERE / f"pids_{t}.txt").write_text("\n".join(r["pid"] for r in ev if r["task"] == t) + "\n")
    s0 = [json.loads(l) for l in open(OIF / "stage0_problems.jsonl")]
    s0 = [r for r in s0 if r["task"] == "ifeval"]
    assert len(s0) == 40 and not {r["pid"] for r in s0} & {r["pid"] for r in ev}
    df = pd.read_parquet(pq)
    assert len(df) == 13179
    idx = random.Random(SEED).sample(range(len(df)), 24)
    for i in idx:
        p = df.iloc[i]["prompt"]
        assert p.startswith("user: ")
        s0.append({"pid": f"rlzif_{i}", "task": "rlzif", "prompt": p[len("user: "):], "rl_key": df.iloc[i]["key"],
                   "ground_truth": list(df.iloc[i]["ground_truth"])})
    with open(HERE / "stage0_problems.jsonl", "w") as f:
        for r in s0:
            f.write(json.dumps(r) + "\n")
    print(f"problems.jsonl {len(ev)} (ifbench 300, ifeval 150; ifomega_excl {sum(r['ifomega_excl'] for r in ev)}); "
          f"stage0 {len(s0)}; parquet sha256 {hashlib.sha256(open(pq, 'rb').read()).hexdigest()[:16]}")


if __name__ == "__main__":
    main()
