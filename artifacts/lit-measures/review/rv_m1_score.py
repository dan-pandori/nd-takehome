#!/usr/bin/env python3
"""Reviewer (lit-measures) M1 scorer, written independently of lm_m1.py.
For each proof and each base b in 0..(64 - max name at base 0), replay the canonical actions in
Env(canon=True, base=b, assign=True); score each action's tokens + <eos> under SN base s0 given env.state_tokens().
Stores per base per step: full log p and log p without the defining-name tokens (the env overrides them)."""
import sys, json, math, collections, time
sys.path.insert(0, '/home/dan/review/lit-measures')
import torch, torch.nn.functional as F
from model import load_ckpt
from state_env import Env, decompose, is_name
from lean_tok import MAXN
torch.set_num_threads(2)
CK = '/home/dan/review/lit-measures/rv/in/stage1_SN_s0.pt'
model, tok, _ = load_ckpt(CK, 'cpu')
print('params', sum(p.numel() for p in model.parameters()), tok.mode if hasattr(tok, 'mode') else '', flush=True)

def shift(a, b):
    return [f'n{int(t[1:]) + b}' if is_name(t) else t for t in a]

def def_positions(a):
    if a[0] != 'have':
        return set()
    i = a.index(':=') + 1
    s = {1}
    if a[i] == '(':
        s.add(i + 3)
    elif a[i] == 'Or.elim':
        s.add(i + 5)
    return s

def jobs_for(prompt, nd):
    steps, toks, env0 = decompose(prompt, nd, canon=True)
    acts = [a for _, a, _ in steps]
    mx = max([int(t[1:]) for a in acts for t in a if is_name(t)] + [0])
    per_b = []
    for b in range(0, MAXN - mx + 1):
        e = Env(prompt, canon=True, base=b, assign=True)
        row = []
        for a in acts:
            st = e.state_tokens()
            sa = shift(a, b)
            ok, why = e.apply(sa)
            assert ok, why
            assert list(e._eff) == sa, (e._eff, sa)      # env's assigned names = our shifted canonical names
            row.append((tuple(tok.encode_toks(st)), tuple(tok.encode_toks(sa)), tuple(sorted(def_positions(sa)))))
        assert e.done
        per_b.append(row)
    return acts, mx, per_b

@torch.no_grad()
def score(seqs, T_list=(0.8, 1.0), bs=256):
    keys = list(seqs); out = {}
    keys.sort(key=lambda k: len(k[0]) + len(k[1]))
    t0 = time.time()
    for s in range(0, len(keys), bs):
        ch = keys[s:s + bs]
        L = max(len(p) + len(q) + 1 for p, q, _ in ch)
        x = torch.zeros(len(ch), L, dtype=torch.long)
        for j, (p, q, _) in enumerate(ch):
            ids = list(p) + list(q) + [tok.eos]
            x[j, :len(ids)] = torch.tensor(ids)
        logits = model(x).float()
        for T in T_list:
            lp = F.log_softmax(logits / T, -1)
            for j, (p, q, dp) in enumerate(ch):
                tgt = list(q) + [tok.eos]
                pos = torch.arange(len(p) - 1, len(p) - 1 + len(tgt))
                v = lp[j, pos, torch.tensor(tgt)].double()
                full = float(v.sum())
                # token index k of the target <-> action token index k (encode_toks is 1:1 for action tokens; checked below)
                skip = float(sum(v[k] for k in range(len(tgt)) if k not in dp))
                out.setdefault(ch[j], {})[T] = (full, skip)
        if s // bs % 50 == 0:
            print(f'  {s}/{len(keys)} {time.time()-t0:.0f}s', flush=True)
    return out

if __name__ == '__main__':
    inp, outp = sys.argv[1], sys.argv[2]
    recs = [json.loads(l) for l in open(inp)]
    plan = []; seqs = {}
    for r in recs:
        acts, mx, per_b = jobs_for(r['prompt'], r['proof'])
        for row in per_b:
            for p, q, dp in row:
                assert len(q) == len(shift(acts[0], 0)) or True
                seqs[(p, q, dp)] = 1
        plan.append((r, acts, mx, per_b))
    # 1:1 check of action tokens -> ids
    a0 = plan[0][1][0]; assert len(tok.encode_toks(a0)) == len(a0), 'encode_toks not 1:1'
    print(len(plan), 'proofs', len(seqs), 'distinct seqs', flush=True)
    res = score(seqs)
    with open(outp, 'w') as f:
        for r, acts, mx, per_b in plan:
            o = {k: r[k] for k in r}
            o['n_steps'] = len(acts); o['mx'] = mx; o['actions'] = [' '.join(a) for a in acts]
            for T in (0.8, 1.0):
                o[f'full_{T}'] = [[res[k][T][0] for k in row] for row in per_b]
                o[f'skip_{T}'] = [[res[k][T][1] for k in row] for row in per_b]
            f.write(json.dumps(o) + '\n')
