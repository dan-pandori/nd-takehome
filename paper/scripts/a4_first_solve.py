"""A4 (Addendum 2, exploratory): does the base's likelihood of a member's best known sigma proof predict how early the
ladder first solves it?  r(m) = first round whose tracked k 32 sample solved m (artifacts/coe/rounds/*.json,
heldout_first_solve_round); not solved by round 16 -> 17.  Spearman rho with the member's pend log p
(paper/data/a3_member_values.json, from a3_member_prior.py).  Output paper/data/a4_first_solve.json."""
import json, os, statistics
from scipy.stats import spearmanr
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
V = json.load(open(os.path.join(ROOT, 'paper/data/a3_member_values.json')))
RF = {'full_s0': 'old_full_s0', 'full_s3': 'la_full_s3', 'full_s4': 'la_full_s4', 'full_s5': 'la_full_s5',
      'dose1_s0': 'la_dose1_s0', 'dose1_s1': 'la_dose1_s1', 'dose1_s2': 'la_dose1_s2'}
out = {}
for lad, rf in RF.items():
    fs = json.load(open(os.path.join(ROOT, f'artifacts/coe/rounds/{rf}.json')))['heldout_first_solve_round']
    mem = V[lad]
    xs = [mem[m]['logp'] for m in mem]
    rs = [min(int(fs[m]), 17) if (m in fs and fs[m] is not None and int(fs[m]) <= 16) else 17 for m in mem]
    rho, p = spearmanr(xs, rs)
    byf = {}
    for m, x, r in zip(mem, xs, rs):
        byf.setdefault(mem[m]['family'], []).append((x, r))
    wf = []
    for f, pairs in byf.items():
        if len(pairs) >= 5 and len(set(r for _, r in pairs)) > 1:
            wf.append(spearmanr([a for a, _ in pairs], [b for _, b in pairs])[0])
    out[lad] = {'rho': rho, 'p': p, 'n': len(xs), 'solved_by_r16': sum(1 for r in rs if r <= 16),
                'within_family_mean_rho': statistics.mean(wf) if wf else None, 'families_used': len(wf)}
    print(f"{lad}: rho {rho:.3f} (p {p:.2g}), solved by r16 in the tracked sample {out[lad]['solved_by_r16']}/{len(xs)}; "
          f"within-family mean rho {out[lad]['within_family_mean_rho']:.3f} over {len(wf)} families")
json.dump(out, open(os.path.join(ROOT, 'paper/data/a4_first_solve.json'), 'w'), indent=1)
