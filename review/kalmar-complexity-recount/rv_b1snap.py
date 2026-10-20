#!/usr/bin/env python3
"""Reviewer recount of B1-snap's per-type integration (b1_snap.json raw per-tag nats; my per-tag token counts).
~/.venv-torch/bin/python rv_b1snap.py"""
import json, math, os, collections
import torch
HERE = os.path.dirname(os.path.abspath(__file__)); WS = os.path.expanduser('~/review/kalmar-complexity')
LN2 = math.log(2); T0 = 24020
g = lambda t: 'close' if t.startswith('close:') else t
snap = json.load(open(os.path.join(WS, 'artifacts/kc/b1_snap.json')))['models']
tk = json.load(open(os.path.join(HERE, 'out/b1_tokens_kal.json')))['per_tag']
N = collections.Counter()
for t, (p, k) in tk.items():
    N[g(t)] += k
b1 = json.load(open(os.path.join(HERE, 'out/b1_recount.json')))
out = {}
for s in range(3):
    ex = torch.load(os.path.join(WS, f'ckpts/kc_src/stage1_kalD_s{s}.pt'), map_location='cpu', weights_only=False)['extra']
    E1 = ex['batches_per_epoch']
    def per(ck):
        d = collections.defaultdict(lambda: [0.0, 0])
        for t, v in snap[ck]['per_tag'].items():
            d[g(t)][0] += v['nats']; d[g(t)][1] += v['loss_tokens']
        return {k: a / b for k, (a, b) in d.items()}
    C = lambda x: f'ckpts/kc_src/stage1_kalD_s{s}{x}.pt'
    L24, L100, L200, Lf = (per(C(x)) for x in ('_step24020', '_step100000', '_step200000', ''))
    rows = {}
    for k in Lf:
        le = L100[k] + (L200[k] - L100[k]) * (E1 - 100000) / 100000
        integ = (L24[k] + L100[k]) / 2 * (100000 - T0) + (L100[k] + le) / 2 * (E1 - 100000)
        rate = N[k] / E1
        code = integ * rate / LN2
        res = (E1 - T0) * rate * Lf[k] / LN2
        rows[k] = {'code': code, 'excess': code - res, 'excess_per_tok': (code - res) / ((E1 - T0) * rate),
                   'L24': L24[k], 'L100': L100[k], 'L200': L200[k], 'Lf': Lf[k]}
    # logged curve over the same window (steps T0 .. E1): intervals weighted by overlap
    ck = sorted(ex['curve'], key=lambda p: p['step'])
    Ntot = sum(N.values())
    logged = 0.0; prev = 0
    for p in ck:
        lo, hi = max(prev, T0), min(p['step'], E1)
        if hi > lo:
            logged += p['train_loss'] * (hi - lo) * Ntot / E1 / LN2
        prev = p['step']
        if p['step'] >= E1:
            break
    out[f'KAL-D s{s}'] = {'E1': E1, 'types': rows, 'sum_code': sum(r['code'] for r in rows.values()),
                          'sum_excess': sum(r['excess'] for r in rows.values()), 'logged_same_window': logged,
                          'heldout_nats_per_tok': {x: snap[C(x)]['nats_per_token'] for x in ('_step24020', '_step100000', '_step200000', '')}}
    o = out[f'KAL-D s{s}']
    print(f"s{s}: E1 {E1} sum code {o['sum_code']:.4g} logged same window {logged:.4g} sum excess {o['sum_excess']:.4g}; held-out nats/tok {o['heldout_nats_per_tok']}")
types = sorted(out['KAL-D s0']['types'], key=lambda k: -out['KAL-D s0']['types'][k]['excess'])
for k in types:
    print(f"{k:12}", ' '.join(f"{out[f'KAL-D s{s}']['types'][k]['excess']:10.4g} ({out[f'KAL-D s{s}']['types'][k]['excess_per_tok']:+.4f}/tok)" for s in range(3)))
json.dump(out, open(os.path.join(HERE, 'out/b1snap_recount.json'), 'w'), indent=1)
