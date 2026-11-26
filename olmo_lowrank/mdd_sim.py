"""Pre-registration power check (VPS, numpy): 95 % prompt-bootstrap half-width of G at the planned draws.
Inputs: olmo-ifcurve's results.csv (stored per-prompt rates; models: Olmo-3-32B-Think-DPO `dpo`, Olmo-3.1-32B-Think
step_2300 `s2300`). True per-prompt rates are taken as the stored estimates; arms are simulated as
a_p = d_p + G (s_p - d_p) with binomial draws at this run's counts. Prints a table."""
import csv, numpy as np
R = list(csv.DictReader(open('olmo_ifcurve/results.csv')))
reach_s = {r['pid']: float(r['rate_est']) for r in R if r['arm'] == 'B' and r['ckpt'] == 's2300'}
strict = {}
for r in R:
    if r['arm'] == 'A' and r['ckpt'] in ('dpo', 's2300'):
        strict.setdefault(r['ckpt'], {})[r['pid']] = int(r['strict']) / int(r['n'])
pidsA = sorted(strict['dpo']); reach = sorted(reach_s)
rng = np.random.default_rng(4949)
def sim(true_a, true_d, true_s, n_a, n_d, n_s, G=0.5, reps=300, boots=1000):
    out = []
    for _ in range(reps):
        a = rng.binomial(n_a, true_a) / n_a; d = rng.binomial(n_d, true_d) / n_d; s = rng.binomial(n_s, true_s) / n_s
        P = len(a); g = []
        for _ in range(boots):
            i = rng.integers(0, P, P)
            g.append((a[i].mean() - d[i].mean()) / (s[i].mean() - d[i].mean()))
        lo, hi = np.percentile(g, [2.5, 97.5]); out.append((hi - lo) / 2)
    return np.median(out)
s = np.array([reach_s[p] for p in reach]); d = np.zeros_like(s)
for G in (0.2, 0.5, 0.75):
    a = d + G * (s - d)
    print(f"reach genuine  G={G:.2f}  48 prompts x16 (arm, dpo) x32 (s2300): half-width {sim(a, d, s, 16, 16, 32, G):.3f}")
reachA = set(reach)
nA = np.array([16 if p in reachA else 4 for p in pidsA]); nD = np.array([16 if p in reachA else 20 for p in pidsA])
nS = np.array([32 if p in reachA else 8 for p in pidsA])
sA = np.array([strict['s2300'][p] for p in pidsA]); dA = np.array([strict['dpo'][p] for p in pidsA])
for G in (0.2, 0.5, 0.75):
    a = dA + G * (sA - dA)
    print(f"218 strict     G={G:.2f}  arm 4 (16 reach), dpo 20 (16), s2300 8 (32): half-width {sim(a, dA, sA, nA, nD, nS, G):.3f}")
print("stored means: reach s2300 genuine %.3f; 218 strict dpo %.3f s2300 %.3f" % (s.mean(), dA.mean(), sA.mean()))
