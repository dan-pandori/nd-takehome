"""Our state-env checkpoints scored on Leon's GRPO-v2 read-out protocol, from existing per-attempt files (no new sampling).

Leon's protocol (RECIPE.md L35-39, L224-227 / v2_results_ynez.md on nd-rl `leon/main`): unbiased pass@1 and pass@5 from
k samples per problem, in % of the set; plain sampling at T 0.8, max_steps 96, max_action 512; "guided" = the logical
arm with <= 10 redraws per attempt; 95 % hierarchical bootstrap over seeds and problems. Sets: textbook72 (58 dev + 14
train, his k 64), charles173 = Charles's 2026-10-02 release (candidate_v0 + candidate_v1 + batch3), Charles149 =
charles173 minus the 24 names in his `charles_eval/charles_clean.report.json` (overlap with his own training sets).
tb72_clean62 = textbook72 minus the 10 theorems with substitution instances among our ladder's RL targets
(`peer_rl_review/schema_overlap.py`, out/tb72_with_target_instances.json).

Our files (all: 9,560,832-param ALiBiGPT, proof state `lean_staten`, Stage-1 on K12 (155,000 proofs, 2-12 lines, cap 12),
T 0.8, max_steps 96, max_action 512, k 256 per problem, Lean alone):
  frozen  stage1_best12_s{0,1,2}_b1200 (no RL)            hf://buckets/dan-pandori/nd-rl/best-state/artifacts/bs/eval/Fz_best12_s{s}__tb72.jsonl
  r8-bs   la_T1_best12_s{0,1,2}_r8 (best-state seeds)       .../best-state/artifacts/bs/eval/T1_best12_s{s}__tb72.jsonl
  r8-tj   la_T1_best12_s{0,1,2}_r8 (trajectory seeds)       .../guided-tts/artifacts/gt/eval/best12_s{s}_{plain,logical}.rows.jsonl.gz
  r16     la_T1_best12_s{0,1,2}_r16 (rl-continue)           .../rl-continue/artifacts/rc/eval/s{s}_r16__tb72_x1.jsonl (plain)
                                                            .../capability-defs/artifacts/cd/j3/s{s}_r16_logical.rows.jsonl.gz (guided)
  gb-*    gb_{default,unlikely,passk}_s{0,1,2}_r8: GRPO arms of run grpo-best from the trajectory seeds' Stage-1, at EI r8's
          sampled attempts; .../grpo-best/artifacts/gb/eval/gb_<arm>_s{s}_r8__tb72_x1.jsonl (sample seed 1, as r8-tj)
T1 ladder = expert iteration, 8 (r8) or 16 (r16) rounds x k 32 on 4,495 rl_targets with K12 replay.
The unbiased estimator has the same expectation at n = 256 as at Leon's n = 64 (smaller variance).

Usage: python3 peer_rl_review/ours_on_leon_passk.py [scratch_dir] > peer_rl_review/out/ours_on_leon_passk.txt
"""
import gzip
import json
import math
import os
import random
import sys

SCR = sys.argv[1] if len(sys.argv) > 1 else "scratch"
HERE = os.path.dirname(os.path.abspath(__file__))
REMOVED = set(json.load(open(os.path.join(HERE, "data", "charles149_removed.json")))["names"])
assert len(REMOVED) == 24


def names_of(path):
    return [json.loads(l)["name"] for l in open(path)]


TB_DEV = set(names_of("data/gt/tb72_textbook_dev.jsonl"))
TB_TRAIN = set(names_of("data/gt/tb72_textbook_train.jsonl"))
CH173 = set()
for f in ["candidate_v0", "candidate_v1", "batch3"]:
    CH173 |= set(names_of(f"data/gt/{f}.jsonl"))
assert len(TB_DEV) == 58 and len(TB_TRAIN) == 14 and len(CH173) == 173 and REMOVED <= CH173
EXPOSED = set(json.load(open(os.path.join(HERE, "out", "tb72_with_target_instances.json"))))  # schema_overlap.py
assert len(EXPOSED) == 10 and EXPOSED <= (TB_DEV | TB_TRAIN)
SETS = {"textbook72": TB_DEV | TB_TRAIN, "tb72_dev58": TB_DEV, "tb72_clean62": (TB_DEV | TB_TRAIN) - EXPOSED,
        "charles173": CH173, "charles149": CH173 - REMOVED}

MODELS = [  # label, arm, path template, kind
    ("frozen  stage1_best12_s{0,1,2}_b1200", "plain", "bs_eval/Fz_best12_s{s}__tb72.jsonl", "se"),
    ("r8-bs   la_T1_best12_s{0,1,2}_r8 (best-state seeds)", "plain", "bs_eval/T1_best12_s{s}__tb72.jsonl", "se"),
    ("r8-tj   la_T1_best12_s{0,1,2}_r8 (trajectory seeds)", "plain", "gt_eval/best12_s{s}_plain.rows.jsonl.gz", "gt"),
    ("r8-tj   la_T1_best12_s{0,1,2}_r8 (trajectory seeds)", "guided", "gt_eval/best12_s{s}_logical.rows.jsonl.gz", "gt"),
    ("r16     la_T1_best12_s{0,1,2}_r16", "plain", "rc_eval/s{s}_r16__tb72_x1.jsonl", "se"),
    ("r16     la_T1_best12_s{0,1,2}_r16", "guided", "cd_j3/s{s}_r16_logical.rows.jsonl.gz", "gt"),
    ("gb-def  gb_default_s{0,1,2}_r8 (GRPO, grpo-best)", "plain", "gb_eval/gb_default_s{s}_r8__tb72_x1.jsonl", "se"),
    ("gb-unl  gb_unlikely_s{0,1,2}_r8 (GRPO, grpo-best)", "plain", "gb_eval/gb_unlikely_s{s}_r8__tb72_x1.jsonl", "se"),
    ("gb-p@4  gb_passk_s{0,1,2}_r8 (GRPO, grpo-best)", "plain", "gb_eval/gb_passk_s{s}_r8__tb72_x1.jsonl", "se"),
]


def load(path, kind):
    out = {}
    op = gzip.open if path.endswith(".gz") else open
    for l in op(path, "rt"):
        r = json.loads(l)
        if kind == "gt":
            n, c = len(r["ok"]), sum(1 for x in r["ok"] if x)
            assert n == r["k"] == 256 and c == r["n_ok"], (path, r["name"])
        else:
            n, c = r["n_tried"], r["n_ok"]
            assert n == 256, (path, r["name"])
        assert r["name"] not in out
        out[r["name"]] = (n, c)
    return out


def passk(n, c, k):
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def hier_boot(per_seed, B=2000, seed=0):
    """per_seed: list (seeds) of lists (problems) of values. Resample seeds, then problems within each seed."""
    rng = random.Random(seed)
    S = len(per_seed)
    means = []
    for _ in range(B):
        tot = 0.0
        for _s in range(S):
            vals = per_seed[rng.randrange(S)]
            P = len(vals)
            tot += sum(vals[rng.randrange(P)] for _ in range(P)) / P
        means.append(tot / S)
    means.sort()
    return means[int(0.025 * B)], means[int(0.975 * B) - 1]


def paired_grpo_vs_ei(B=2000, seed=0):
    """GRPO arm minus EI r8 (trajectory seeds, same Stage-1 seed, both sample seed 1), paired by seed and problem."""
    ei = [load(os.path.join(SCR, f"gt_eval/best12_s{s}_plain.rows.jsonl.gz"), "gt") for s in range(3)]
    print("Paired GRPO - EI r8 (grpo-best arms vs trajectory-seed EI r8; same Stage-1 seed; sample seed 1), pp")
    print(f"{'arm':<10} {'set':<12} {'k':>2}  {'per seed s0/s1/s2':>22}  {'mean [95% CI]':>20}")
    for arm in ["default", "unlikely", "passk"]:
        gb = [load(os.path.join(SCR, f"gb_eval/gb_{arm}_s{s}_r8__tb72_x1.jsonl"), "se") for s in range(3)]
        for setname in ["textbook72", "tb72_clean62"]:
            keys = sorted(SETS[setname])
            for k in (1, 5):
                diffs = [[100.0 * (passk(*g[key], k) - passk(*e[key], k)) for key in keys] for g, e in zip(gb, ei)]
                vals = [sum(v) / len(v) for v in diffs]
                lo, hi = hier_boot(diffs, B=B, seed=seed)
                print(f"{arm:<10} {setname:<12} {k:>2}  {' / '.join(f'{v:+.1f}' for v in vals):>22}  "
                      f"{sum(vals) / 3:+6.1f} [{lo:+5.1f}, {hi:+5.1f}]")
    print()


def main():
    print(__doc__.split("\n")[0])
    print(f"Charles149 = charles173 minus {len(REMOVED)} names; bootstrap B 2000, seed 0\n")
    hdr = (f"{'model':<52} {'arm':<6} {'set':<11} {'n':>3}  {'pass@1 s0/s1/s2':>18} {'mean [95% CI]':>19}"
           f"  {'pass@5 s0/s1/s2':>18} {'mean [95% CI]':>19}  {'solved@64 (exp.)':>18}  {'solved@256':>12}")
    print(hdr)
    print("-" * len(hdr))
    for label, arm, tmpl, kind in MODELS:
        paths = [os.path.join(SCR, tmpl.format(s=s)) for s in range(3)]
        if not all(os.path.exists(p) for p in paths):
            print(f"{label:<52} {arm:<6} files missing: {[p for p in paths if not os.path.exists(p)]}")
            continue
        datas = [load(p, kind) for p in paths]
        for setname, members in SETS.items():
            keys = sorted(members & set(datas[0]))
            if not keys:
                continue
            assert keys == sorted(members), (label, setname, len(keys))  # complete coverage or skip
            for d in datas[1:]:
                assert members <= set(d)
            cells = []
            for k in (1, 5):
                per_seed = [[100.0 * passk(*d[key], k) for key in keys] for d in datas]
                vals = [sum(v) / len(v) for v in per_seed]
                lo, hi = hier_boot(per_seed)
                cells.append(f"{' / '.join(f'{v:.1f}' for v in vals):>18} {sum(vals) / 3:6.1f} [{lo:4.1f}, {hi:4.1f}]")
            s64 = " / ".join(f"{sum(passk(*d[key], 64) for key in keys):.1f}" for d in datas)
            s256 = " / ".join(f"{sum(1 for key in keys if d[key][1] > 0)}" for d in datas)
            print(f"{label:<52} {arm:<6} {setname:<11} {len(keys):>3}  {cells[0]}  {cells[1]}  {s64:>18}  {s256:>12}")
        print()
    paired_grpo_vs_ei()
    print("pass@k in % of the set (unbiased, from 256 draws per problem; mean over problems, then over seeds).")
    print("solved@64 (exp.) = expected number solved at k 64; solved@256 = observed number with >= 1 accepted proof.")


if __name__ == "__main__":
    main()
