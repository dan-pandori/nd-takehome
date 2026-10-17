"""How our textbook72 attempts fail, in the terms of Leon's mechanism claim ("Lean rejections of environment-accepted
textbook72 attempts fall from 55.4 % (T0) to 17.8 % (search-proof Stage-1)", L/OVERNIGHT_20261008.md:L179-181).

Inputs: best-state textbook72 reads (state_eval.py, k 256, T 0.8, max_steps 96, max_action 512, Lean alone), one row
per theorem with n_ok, n_tried and one failure reason per failed attempt:
  hf://buckets/dan-pandori/nd-rl/best-state/artifacts/bs/eval/{Fz,T1}_best12_s{0,1,2}__tb72.jsonl
  Fz = stage1_best12_s{s}_b1200 (frozen, no RL); T1 = la_T1_best12_s{s}_r8 (best-state seeds).
"lean rejected" = the environment accepted every step and Lean rejected the finished proof; reasons starting with
"lean_seq parse" are attempts that ended on a step the environment (strict grammar) rejected.

Usage: python3 peer_rl_review/lean_reject_share.py [scratch_dir] > peer_rl_review/out/lean_reject_share.txt
"""
import collections
import json
import os
import sys

SCR = sys.argv[1] if len(sys.argv) > 1 else "scratch"


def main():
    print(__doc__.split("\n")[0])
    print(f"{'read':<14} {'attempts':>8} {'accepted':>8} {'Lean-rej':>8} {'env-rej':>8} {'other':>6}"
          f"  {'Lean-rej / attempts':>19} {'env-rej / attempts':>18} {'Lean-rej / finished':>19}")
    for tag in ["Fz_best12_s0", "Fz_best12_s1", "Fz_best12_s2", "T1_best12_s0", "T1_best12_s1", "T1_best12_s2"]:
        tot = collections.Counter()
        ok = tried = 0
        for line in open(os.path.join(SCR, "bs_eval", f"{tag}__tb72.jsonl")):
            r = json.loads(line)
            ok += r["n_ok"]
            tried += r["n_tried"]
            assert len(r["reasons"]) == r["n_tried"] - r["n_ok"], (tag, r["name"])
            tot.update(r["reasons"])
        lean = tot["lean rejected"]
        env = sum(v for k, v in tot.items() if k.startswith("lean_seq parse"))
        other = tried - ok - lean - env
        print(f"{tag:<14} {tried:>8} {ok:>8} {lean:>8} {env:>8} {other:>6}  {lean / tried:>19.3f} {env / tried:>18.3f}"
              f" {lean / (lean + ok):>19.3f}")


if __name__ == "__main__":
    main()
