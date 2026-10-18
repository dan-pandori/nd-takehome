"""Compare reviewer RL recount (out/rl_<arm>.json) with the executor's artifacts/ps/rl_found.json, round by round."""
import json
import os

E = json.load(open("../artifacts/ps/rl_found.json"))
KEYS = ["new_by_round", "reductio_by_round", "working_by_round", "template_only_by_round", "free_working_by_round",
        "neg_goal_working_by_round"]
tot = {}
for arm in E:
    fn = f"out/rl_{arm}.json"
    if not os.path.exists(fn):
        print(f"{arm:9s} (not yet recounted)")
        continue
    M = json.load(open(fn))
    diffs = []
    for k in KEYS:
        for r in range(1, 17):
            a, b = M[k][str(r)] if str(r) in M[k] else M[k][r], E[arm][k].get(str(r), E[arm][k].get(r))
            if a != b:
                diffs.append((k, r, a, b))
    sc_m, sc_e = M["sigma_cov_first_working_round"], E[arm]["sigma_cov_first_working_round"]
    sc_diff = sum(1 for n in set(sc_m) | set(sc_e) if sc_m.get(n) != sc_e.get(n))
    print(f"{arm:9s} round-cells differing: {len(diffs)}  σ-cov targets differing: {sc_diff}  | executor unparsable {E[arm]['unparsable_dn_lines']} mine {M['unparsable']} | dup lines {M['dup_lines']}"
          + (f"  e.g. {diffs[:3]}" if diffs else ""))
    for k in KEYS:
        tot.setdefault(k, [0, 0])
        tot[k][0] += sum(M[k].values()) if isinstance(next(iter(M[k].values())), int) else 0
        tot[k][1] += sum(E[arm][k].values())
print("totals (mine, executor):", tot)
