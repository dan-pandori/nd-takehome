#!/usr/bin/env python3
"""Secondary (forward passes only): the BASE model's teacher-forced log-probability of each distinct
EI-found proof on the forward crux, marginalised over the random name offset.

  python3 sc_secondary.py --base ckpts/lf/stage1_a1_seq_s0.pt --ei ckpts/ladder/la_T1_sc_s0_r8.pt \
      --summary artifacts/sc/summary.json --names data/sc/crux_forward.txt \
      --out artifacts/sc/secondary_logp.jsonl

**What this is a bound on.**  logp is a LOWER BOUND on the base model's per-sample probability of the
THEOREM: it is the probability of producing *this particular proof*, and other proofs of the same theorem may
exist that the base finds more easily.  It is NOT an estimate of p_base.  Read it only as: "even the specific
proof the EI model found has base log-probability at most this."

Marginalisation.  `lean_seq` numbers hypotheses in order of first appearance plus a **random start offset**
(`lean_tok.LeanTokenizer.shift_abs`), so one proof has up to 64 - (names used) + 1 token realisations.  The
reported logp is log sum_s p(proof shifted by s | prompt) over every allowed offset -- the project's standing
base-reachability quantity, computed by `novelty.score`, which is reused here unchanged.  T = 1 is the model's
own distribution; T = 0.8 is the sampling distribution every arm of this project uses.
"""
import argparse, json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from model import load_ckpt
from novelty import score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True)
    ap.add_argument('--ei', default=None, help='optional: score the same proofs under the EI model too')
    ap.add_argument('--summary', default='artifacts/sc/summary.json')
    ap.add_argument('--names', required=True, help='file of theorem names (the forward crux)')
    ap.add_argument('--theorems', default='data/sc/theorems.jsonl')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--temperature', type=float, default=0.8, help='which EI cell to take the found proofs from')
    ap.add_argument('--out', required=True)
    ap.add_argument('--batch', type=int, default=768)
    a = ap.parse_args()
    dev = 'cuda' if torch.cuda.is_available() else 'cpu'
    prompts = {json.loads(l)['name']: json.loads(l)['prompt'] for l in open(a.theorems) if l.strip()}
    want = {l.strip() for l in open(a.names) if l.strip()}
    cells = json.load(open(a.summary))
    recs, seen = [], set()
    for c in cells:
        if c['model'] != 'ei' or c['name'] not in want or c['seed'] != a.seed:
            continue
        for p in c['proofs']:
            k = (c['name'], p['proof'])
            if k in seen:
                continue
            seen.add(k)
            recs.append({'name': c['name'], 'prompt': prompts[c['name']], 'proof': p['proof'],
                         'L_true': c['L_true'], 'n_lines': p['n_lines'], 'term_size': p['term_size'],
                         'ei_count': p['count'], 'ei_first': p['first'], 'ei_T': c['temperature'],
                         'ei_p_hat': c['p_hat'], 'ei_n': c['n'], 'ei_c': c['c']})
    print(f'{len(recs)} distinct EI-found proofs over {len({r["name"] for r in recs})} forward-crux theorems', flush=True)
    if not recs:
        print('nothing to score'); return
    out = {}
    for label, path in [('base', a.base)] + ([('ei', a.ei)] if a.ei else []):
        model, tok, _ = load_ckpt(path, dev)
        assert hasattr(tok, 'statement') and tok.mode == 'lean_seq', f'{path}: expected a lean_seq checkpoint'
        print(f'scoring under {label} ({path}), ref0={tok.ref0}', flush=True)
        score(model, tok, recs, batch=a.batch, want_tokens=False, dev=dev)
        out[label] = [r.pop('res') for r in recs]
        del model; torch.cuda.empty_cache()
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    with open(a.out, 'w') as f:
        for i, r in enumerate(recs):
            r['logp'] = {lab: out[lab][i] for lab in out}
            r['base_ckpt'] = a.base; r['ei_ckpt'] = a.ei
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    lps = sorted(r['logp']['base']['logp_T08'] for r in recs)
    print(f'-> {a.out}\nbase logp_T08 over {len(lps)} proofs: min {lps[0]:.2f}, median {lps[len(lps)//2]:.2f}, max {lps[-1]:.2f}')
    print(f'  i.e. base per-sample probability of the EI proof itself: median {2.718281828**lps[len(lps)//2]:.3e}, max {2.718281828**lps[-1]:.3e}')


if __name__ == '__main__':
    main()
