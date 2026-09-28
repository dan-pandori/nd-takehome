#!/usr/bin/env python3
"""Reviewer's independent teacher-forced re-score of D proofs (CPU, fp32): log sum_s p(proof_s), all name offsets."""
import json, sys, random, torch, math
from model import load_ckpt
from lean_tok import MAXN
torch.set_grad_enabled(False)
D = [json.loads(l) for l in open('artifacts/sf/d_steps.jsonl')]
THM = {json.loads(l)['name']: json.loads(l) for l in open('data/sc/theorems.jsonl')}
sec = {}
for l in open('artifacts/sc/secondary_logp.jsonl'):
    x = json.loads(l); lp = x['logp']; lp = eval(lp) if isinstance(lp, str) else lp; sec[(x['name'], x['proof'])] = lp
# sample: the 12 largest |d_steps - secondary| disagreements + 18 random (incl. every set)
diffs = sorted(((abs(r['base']['logp_total']['1.0'] - sec[(r['name'], r['proof'])]['base']['logp_T1']), i) for i, r in enumerate(D) if (r['name'], r['proof']) in sec), reverse=True)
idx = [i for _, i in diffs[:12]]
rng = random.Random(7); rest = [i for i in range(len(D)) if i not in idx]; idx += rng.sample(rest, 18)
m, tk, _ = load_ckpt('ckpts/lf/stage1_a1_seq_s0.pt')
out = []
for i in idx:
    r = D[i]
    p = tk.encode_prompt(THM[r['name']]['prompt'])
    q = [tk.stoi[t] for t in r['tokens']]
    assert tk.itos[q[-1]] == '<eos>'
    mx = max(x - tk.ref0 + 1 for x in q if x >= tk.ref0)
    seqs = [p + [x + s if x >= tk.ref0 else x for x in q] for s in range(0, MAXN - mx + 1)]
    X = torch.tensor(seqs)
    logits = m(X[:, :-1])
    logits = logits[0] if isinstance(logits, tuple) else logits
    res = {}
    for T in (1.0, 0.8):
        lp = torch.log_softmax(logits.double() / T, -1).gather(-1, X[:, 1:, None]).squeeze(-1)[:, len(p) - 1:].sum(-1)
        res[T] = torch.logsumexp(lp, 0).item()
    k = (r['name'], r['proof'])
    row = dict(i=i, set=r['set'], name=r['name'], n_shifts=len(seqs), stored_n_shifts=r['base']['n_shifts'],
               mine_T1=res[1.0], d_T1=r['base']['logp_total']['1.0'], sec_T1=sec[k]['base']['logp_T1'] if k in sec else None,
               mine_T08=res[0.8], d_T08=r['base']['logp_total']['0.8'])
    out.append(row); print(json.dumps(row), flush=True)
json.dump(out, open('rev_sf/rescore.json', 'w'), indent=1)
d1 = [abs(r['mine_T1'] - r['d_T1']) for r in out]; d8 = [abs(r['mine_T08'] - r['d_T08']) for r in out]
ds = [abs(r['mine_T1'] - r['sec_T1']) for r in out if r['sec_T1'] is not None]
print('max|mine-d| T1', max(d1), 'T08', max(d8), 'max|mine-sec| T1', max(ds))
