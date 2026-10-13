"""A5 (Addendum 3, exploratory, post hoc): the waiting-time null for the knockout ladders.
Null: each knockout ladder samples the 123 strict training targets at k 32 per round at its base's pooled large-k rate r_s
on the 105 strict family members (artifacts/coe/certificates.json = Table 5 / L88), Poisson, constant rate.
Observed: first round with sigma_targets_cum > 0 (artifacts/coe/rounds/la_ko_s*.json).  Output paper/data/a5_waiting.json."""
import json, math, os, itertools
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CERT = {0: (0, 1491420), 1: (6, 1120378), 2: (1, 1338328), 3: (0, 1340640), 4: (3, 1360222), 5: (2, 1419656)}  # L88 / R§6
K_ATT, N_STRICT = 32, 123
out = {'seeds': {}}
ps = []
for s, (c, n) in CERT.items():
    r = c / n
    lam = K_ATT * N_STRICT * r
    p16 = 1 - math.exp(-16 * lam)
    d = json.load(open(os.path.join(ROOT, f'artifacts/coe/rounds/la_ko_s{s}.json')))
    cum = {int(k): v['sigma_targets_cum'] for k, v in d['per_round'].items()}
    first = next((r_ for r_ in sorted(cum) if cum[r_] > 0), None)
    out['seeds'][f'ko_s{s}'] = {'rate': r, 'lambda_per_round': lam, 'expected_first_round': (1 / lam if lam else None),
                               'p_success_by_r16': p16, 'observed_first_round': first,
                               'observed_by_r16': first is not None and first <= 16, 'cum_r16': cum.get(16)}
    ps.append((p16, first is not None and first <= 16))
obs = sum(o for _, o in ps)
# Poisson-binomial P(at least obs successes)
pr = [p for p, _ in ps]
tail = 0.0
for k in range(obs, len(pr) + 1):
    for comb in itertools.combinations(range(len(pr)), k):
        term = 1.0
        for i in range(len(pr)):
            term *= pr[i] if i in comb else (1 - pr[i])
        tail += term
out['expected_seeds_with_success_by_r16'] = sum(pr)
out['observed_seeds_with_success_by_r16'] = obs
out['p_at_least_observed'] = tail
for k, v in out['seeds'].items():
    print(k, {kk: (round(vv, 4) if isinstance(vv, float) else vv) for kk, vv in v.items()})
print('expected seeds with a strict success by r16:', round(sum(pr), 3), ' observed:', obs, ' P(>= observed | null):', round(tail, 4))
json.dump(out, open(os.path.join(ROOT, 'paper/data/a5_waiting.json'), 'w'), indent=1)
