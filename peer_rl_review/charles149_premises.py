"""Charles149 and textbook72 by premise count for our r8 (trajectory seeds), plus sampled tokens per attempt.

Why: Charles's premise-count wall (no solves at >= 4 premises) also caps our models on Charles149, so part of the
Leon-vs-ours gap on that set sits in its >= 4-premise problems. Same inputs as ours_on_leon_passk.py (guided-tts rows of
la_T1_best12_s{0,1,2}_r8, k 256, T 0.8, plain and logical arms, Lean alone).

Usage: python3 peer_rl_review/charles149_premises.py [scratch_dir] > peer_rl_review/out/charles149_premises.txt
"""
import collections
import gzip
import json
import os
import sys

SCR = sys.argv[1] if len(sys.argv) > 1 else "scratch"
HERE = os.path.dirname(os.path.abspath(__file__))
REMOVED = set(json.load(open(os.path.join(HERE, "data", "charles149_removed.json")))["names"])


def n_prem(prompt):
    toks = prompt.split()
    prem = toks[1:toks.index("SEQ")]
    return 0 if not prem else prem.count(",") + 1  # formulas are fully parenthesised: commas only separate premises


def main():
    print(__doc__.split("\n")[0])
    for arm in ["plain", "logical"]:
        rows = [[json.loads(l) for l in gzip.open(os.path.join(SCR, "gt_eval", f"best12_s{s}_{arm}.rows.jsonl.gz"), "rt")]
                for s in range(3)]
        for setname, keep in [("charles149", lambda r: r["file"] in ("candidate_v0", "candidate_v1", "batch3")
                               and r["name"] not in REMOVED),
                              ("textbook72", lambda r: r["file"].startswith("tb72"))]:
            by = collections.defaultdict(list)
            for r in rows[0]:
                if keep(r):
                    by[n_prem(r["prompt"])].append(r["name"])
            idx = [{r["name"]: r for r in rs} for rs in rows]
            print(f"\n== {arm}, {setname} ({sum(len(v) for v in by.values())} problems), by premise count")
            print(f"{'premises':>8} {'n':>4}  {'solved@256 s0/s1/s2':>20}  {'pass@1 % s0/s1/s2':>20}  {'accepted attempts':>18}")
            for p in sorted(by):
                names = by[p]
                solved = [sum(1 for n in names if ix[n]["n_ok"] > 0) for ix in idx]
                p1 = [100.0 * sum(ix[n]["n_ok"] / len(ix[n]["ok"]) for n in names) / len(names) for ix in idx]
                acc = sum(ix[n]["n_ok"] for ix in idx for n in names)
                print(f"{p:>8} {len(names):>4}  {' / '.join(map(str, solved)):>20}  "
                      f"{' / '.join(f'{x:.1f}' for x in p1):>20}  {acc:>18}")
        tok = []
        for rs in rows:
            t = n = 0
            for r in rs:
                if r["file"].startswith("tb72"):
                    t += sum(r["tokens"])
                    n += len(r["tokens"])
            tok.append(t / n)
        print(f"\n{arm}: textbook72 sampled tokens per attempt s0/s1/s2: {' / '.join(f'{x:.1f}' for x in tok)}")


if __name__ == "__main__":
    main()
