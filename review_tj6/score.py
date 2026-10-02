#!/usr/bin/env python3
"""Reviewer (trajectory-cap6; copied from review_tj/score.py) teacher-forced scorer, written independently of tj_score.py (CPU, unpadded, one sequence
per forward).  For a target ND proof: canonical actions via state_env.decompose; for each name base b with all names
<= MAXN, replay in Env(canon=True, assign=True, base=b); per step log p(action tokens + <eos> | state tokens) at T 1,
skipping the name tokens the action introduces (token 1 of a `have`, and the name right after `fun (`), which the
env overwrites.  Marginal over b ~ U{0..32}: L(t) = logsumexp_b cum_b(t) - ln 33; step t = L(t) - L(t-1).
  usage: score.py <ckpt> <targets.jsonl> <tid,tid,...|@file> <out.jsonl> [b0]"""
import sys, json, math
sys.path.insert(0, '/home/dan/review/trajectory-cap6')
import torch, torch.nn.functional as F
from model import load_ckpt
from state_env import Env, decompose, is_name
from lean_tok import MAXN
torch.set_num_threads(1)
ck, tf, tids, outf = sys.argv[1:5]; b0only = len(sys.argv) > 5
model, tok, _ = load_ckpt(ck, 'cpu')
T = {json.loads(l)['tid']: json.loads(l) for l in open(tf)}
tids = [x.strip() for x in open(tids[1:])] if tids.startswith('@') else tids.split(',')
def sh(a, b): return [f'n{int(x[1:]) + b}' if is_name(x) else x for x in a]
def skip(a):
    s = {1} if a[0] == 'have' else set()
    for i in range(len(a) - 2):
        if a[i] == 'fun' and a[i + 1] == '(' and is_name(a[i + 2]): s.add(i + 2)
    return s
cache = {}
@torch.no_grad()
def lp(state, act):
    key = (tuple(state), tuple(act))
    if key in cache: return cache[key]
    p = tok.encode_toks(state); q = tok.encode_toks(act) + [tok.eos]
    x = torch.tensor([p + q])
    lg = model(x[:, :-1]).float()
    v = F.log_softmax(lg, -1)[0, len(p) - 1:].gather(-1, x[0, len(p):, None]).squeeze(-1).double()
    sk = skip(act)
    r = float(sum(v[i] for i in range(len(act)) if i not in sk) + v[len(act)])
    cache[key] = r; return r
with open(outf, 'a') as fo:
    for tid in tids:
        t = T[tid]
        steps, toks, _ = decompose(t['prompt'], t['proof'], canon=True)
        acts = [a for _, a, _ in steps]
        mx = max([int(x[1:]) for a in acts for x in a if is_name(x)] + [0])
        rows = []
        for b in ([0] if b0only else range(33)):
            if mx + b > MAXN: continue
            e = Env(t['prompt'], canon=True, base=b, assign=True); row = []
            for a in acts:
                st = e.state_tokens(); aa = sh(a, b); row.append(lp(st, aa))
                ok, why = e.apply(aa); assert ok, why
            assert e.done and not e.renamed
            rows.append(row)
        M = torch.tensor(rows, dtype=torch.float64)
        L = torch.logsumexp(M.cumsum(1), 0) - (0 if b0only else math.log(33))
        c = torch.diff(L, prepend=torch.zeros(1, dtype=L.dtype)).tolist()
        fo.write(json.dumps({'tid': tid, 'ckpt': ck.split('/')[-1], 'b0only': b0only, 'step_lp': c, 'total': sum(c),
                             'b0_steps': rows[0], 'nb': len(rows),
                             'base_spread_total': float(M.sum(1).max() - M.sum(1).min())}) + '\n'); fo.flush()
        print(tid, len(acts), f'{sum(c):.4f}', flush=True)
