"""Reviewer (olmo-weights): is 32B/sft5e-5/8000 (= released SFT main) a soup of other SFT checkpoints? Affine fits of
the reference by every pair (and the best triple) of the 21 other SFT checkpoints, from the p32_sft Gram set (offsets
from 32B/sft5e-5/8000). Usage: python3 rv_soup.py ROOT"""
import itertools, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rv_load import load
D, J = load(sys.argv[1])
G, oth = None, None
for r in D["p32_sft"]["gram"]:
    o = r["members"].split("|"); v = [float(x) for x in r["gram_upper"].split()]; n = len(o)
    M = np.zeros((n, n)); k = 0
    for i in range(n):
        for j in range(i, n):
            M[i, j] = M[j, i] = v[k]; k += 1
    G = M if G is None else G + M; oth = o
sft = [i for i, x in enumerate(oth) if "sft" in x]
def fit(idx):
    """min || sum_k w_k x_k || with sum w = 1 (affine soup of the chosen checkpoints reproducing the ref, offset 0)."""
    Gs = G[np.ix_(idx, idx)]
    one = np.ones(len(idx))
    w = np.linalg.solve(Gs, one); w = w / (one @ w)
    return math.sqrt(max(w @ Gs @ w, 0)), w
res = []
for i, j in itertools.combinations(sft, 2):
    r, w = fit([i, j]); res.append((r, [oth[i], oth[j]], w.round(4).tolist()))
res.sort()
print("nearest single:", sorted((math.sqrt(G[i, i]), oth[i]) for i in sft)[:3])
print("best pairs:"); [print(" ", round(r, 3), m, w) for r, m, w in res[:6]]
best3 = min(((fit(list(c))[0], c) for c in itertools.combinations(sft, 3)), key=lambda x: x[0])
r3, w3 = fit(list(best3[1])); print("best triple:", round(r3, 3), [oth[i] for i in best3[1]], w3.round(4).tolist())
# the 7000 -> 9000 chord of the 5e-5 run, without the 8000 detour
i7, i9 = oth.index("32B/sft5e-5/7000"), oth.index("32B/sft5e-5/9000")
print("||5e-5/9000 - 5e-5/7000|| =", round(math.sqrt(G[i7, i7] + G[i9, i9] - 2 * G[i7, i9]), 3),
      " ||8000-7000|| =", round(math.sqrt(G[i7, i7]), 3), " ||9000-8000|| =", round(math.sqrt(G[i9, i9]), 3))
