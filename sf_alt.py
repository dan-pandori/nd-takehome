#!/usr/bin/env python3
"""support-followups D, annex: at each survivor's best-proof worst-3 tokens (artifacts/sf/d_summary.json), what did the
base s0 put its probability on instead?  Teacher-forced at the offset where the base's own log p of the proof is highest,
T 1.0; the EI s0 model's log p of the same token is given alongside.  Writes artifacts/sf/d_alternatives.jsonl."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, torch.nn.functional as F
from model import load_ckpt
from lean_tok import MAXN

dev = 'cuda' if torch.cuda.is_available() else 'cpu'
S = json.load(open('artifacts/sf/d_summary.json'))['primary']['rows']
prompts = {json.loads(l)['name']: json.loads(l)['prompt'] for l in open('data/sc/theorems.jsonl') if l.strip()}
D = {}
for l in open('artifacts/sf/d_steps.jsonl'):
    r = json.loads(l)
    if r['set'] == 'S': D.setdefault(r['name'], []).append(r)
models = {k: load_ckpt(p, dev) for k, p in [('base', 'ckpts/lf/stage1_a1_seq_s0.pt'), ('ei', 'ckpts/ladder/la_T1_sc_s0_r8.pt')]}
out = open('artifacts/sf/d_alternatives.jsonl', 'w')
for row in S:
    r = max(D[row['name']], key=lambda x: x['base']['T1']['total'])
    tok = models['base'][1]
    pid = tok.encode_prompt(prompts[r['name']]); qid = tok.encode_proof(r['proof'])
    mx = max((x - tok.ref0 + 1 for x in qid if x >= tok.ref0), default=0)
    seqs = [pid + [x + s if x >= tok.ref0 else x for x in qid] for s in range(MAXN - mx + 1)]
    x = torch.tensor(seqs, device=dev)
    lps = {}
    with torch.no_grad():
        for k, (m, t, _) in models.items():
            m.eval(); lps[k] = F.log_softmax(m(x[:, :-1]).float(), -1)
    tgt = x[:, 1:]
    seq_lp = lps['base'].gather(-1, tgt[..., None]).squeeze(-1)[:, len(pid) - 1:].sum(1)
    s = int(seq_lp.argmax())
    lp_tok = r['base']['tok_lp']['1.0']
    worst = sorted(range(len(lp_tok)), key=lambda t: lp_tok[t])[:3]
    rec = {'name': r['name'], 'L_true': r['L_true'], 'proof_tokens': r['tokens'], 'best_shift': s, 'worst': []}
    for t in worst:
        pos = len(pid) - 1 + t
        dist = lps['base'][s, pos]
        top = torch.topk(dist, 3)
        rec['worst'].append({'pos': t, 'tok': r['tokens'][t], 'cls': r['token_cls'][t], 'cls_pos': r['token_cls_pos'][t],
                             'context': ' '.join(r['tokens'][max(0, t - 8):t]), 'base_lp_marg': round(lp_tok[t], 3),
                             'base_lp_at_shift': round(float(dist[tgt[s, pos]]), 3), 'ei_lp_at_shift': round(float(lps['ei'][s, pos, tgt[s, pos]]), 3),
                             'base_top3': [(tok.itos[int(i)], round(float(v), 3)) for v, i in zip(top.values, top.indices)]})
    out.write(json.dumps(rec, ensure_ascii=False) + '\n')
print('done')
