#!/usr/bin/env python3
"""Reviewer recount (mcts-a), part 4: value-head calibration recomputed on CPU for one checkpoint's value data.
My own MLP rebuild from the stored state dict, my own AUC (rank-sum with ties), Brier (per state, and weighted by
attempts) against the constant predictor, Spearman of predicted steps-to-go vs observed mean on states with a success.
Held-out = the data file's `heldout_thm` flag (md5(name) % 10 == 0), re-derived here from the theorem names too.
  ~/.venv-torch/bin/python r4_value.py /tmp/vdata_s0_pend.pt ~/review/mcts-a/ckpts/mcts/value_s0_pend.pt s0_pend
Output: r4_value_<tag>.json"""
import sys, json, os, hashlib
import torch, torch.nn as nn
vd, vh, tag = sys.argv[1:4]
D = torch.load(vd, map_location='cpu', weights_only=False)
print({k: (tuple(v.shape) if hasattr(v, 'shape') else type(v).__name__) for k, v in D.items()}, flush=True)
ck = torch.load(vh, map_location='cpu', weights_only=False)
c = ck['cfg']
net = nn.Sequential(nn.LayerNorm(c['d_in']), nn.Linear(c['d_in'], c['hidden']), nn.GELU(), nn.Linear(c['hidden'], c['hidden']),
                    nn.GELU(), nn.Linear(c['hidden'], 2))
net.load_state_dict({k[len('net.'):]: v for k, v in ck['state'].items()})
net.eval()
ti = D['ti'].long(); held_thm = D['heldout_thm'].bool()
out = {}
if 'names' in D or 'thm_names' in D:
    names = D.get('names', D.get('thm_names'))
    mine = torch.tensor([int(hashlib.md5(n.encode()).hexdigest(), 16) % 10 == 0 for n in names])
    out['heldout_flag_matches_md5'] = bool((mine == held_thm).all())
held = held_thm[ti]
X = D['feats'][held].float(); n = D['n'][held].float(); succ = D['succ'][held].float(); stg = D['stg'][held].float()
with torch.no_grad():
    o = torch.cat([net(X[i:i + 65536]) for i in range(0, len(X), 65536)])
p = torch.sigmoid(o[:, 0]); d = o[:, 1]
frac = succ / n; lab = (succ > 0).float()
def auc(s, y):
    r = torch.empty_like(s); order = s.argsort(); r[order] = torch.arange(1, len(s) + 1, dtype=s.dtype)
    # average ranks over ties
    u, inv, cnt = torch.unique(s, return_inverse=True, return_counts=True)
    sums = torch.zeros(len(u), dtype=s.dtype).index_add_(0, inv, r)
    r = (sums / cnt)[inv]
    P = y.sum(); N = len(y) - P
    return float((r[y == 1].sum() - P * (P + 1) / 2) / (P * N))
def spearman(a, b):
    ra = a.argsort().argsort().float(); rb = b.argsort().argsort().float()
    ra -= ra.mean(); rb -= rb.mean()
    return float((ra * rb).sum() / (ra.norm() * rb.norm()))
pos = succ > 0
w = n / n.sum()
out.update(tag=tag, heldout_states=int(held.sum()), heldout_theorems=int(held_thm.sum()), frac_states_solvable=round(float(lab.mean()), 4),
           auc=round(auc(p.double(), lab), 4),
           brier_state=round(float(((p - frac) ** 2).mean()), 5), brier_state_const=round(float(((frac.mean() - frac) ** 2).mean()), 5),
           brier_att=round(float((w * (p - frac) ** 2).sum()), 5), brier_att_const=round(float((w * ((w * frac).sum() - frac) ** 2).sum()), 5),
           stg_spearman=round(spearman(d[pos], stg[pos] / succ[pos]), 4), stg_mae=round(float((d[pos] - stg[pos] / succ[pos]).abs().mean()), 3),
           states_total=int(len(ti)))
# by source if available
if 'src' in D:
    out['src_note'] = 'present'
print(json.dumps(out), flush=True)
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'r4_value_{tag}.json'), 'w'), indent=1)
