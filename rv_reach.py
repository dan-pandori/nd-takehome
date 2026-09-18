#!/usr/bin/env python3
"""Reviewer: base reachability. (1) classify every counted transfer proof from the executor's novelty files with my own
thresholds, after checking the novelty file covers exactly my counted (theorem, normalised proof) set; (2) re-score a
random sample per arm with my own teacher-forced scorer (CPU) and compare log p."""
import json, sys, os, math, random, collections
from rv_recount import rv_norm, ARMS, A, rd
LN1e5 = math.log(1e-5); LN256 = math.log(1 / 256)

def my_score(model, tok, prompt, proof, T=0.8):
    import torch
    toks = rv_norm(proof).split()
    isN = [len(t) > 1 and t[0] == 'N' and t[1:].isdigit() for t in toks]
    mx = max(int(t[1:]) for t, n in zip(toks, isN) if n)
    pid = [tok.stoi[t] for t in prompt.split()]
    seqs = []
    for s in range(0, 64 - mx + 1):
        seqs.append(pid + [tok.stoi['N%d' % (int(t[1:]) + s)] if n else tok.stoi[t] for t, n in zip(toks, isN)])
    x = torch.tensor(seqs)
    with torch.no_grad():
        lg = model(x[:, :-1]).float() / T
    lp = torch.log_softmax(lg, -1).gather(2, x[:, 1:, None]).squeeze(2)[:, len(pid) - 1:].sum(1)
    return torch.logsumexp(lp, 0).item(), len(seqs)

def main():
    T = {r['name']: r for r in rd('data/ladder/transfer.jsonl')}
    rng = random.Random(12345)
    out = {}; sample = []
    for arm, dirs in ARMS.items():
        counted = {}
        for d in dirs:
            for x in rd(f'{A}/{d}/found_transfer_8.jsonl'):
                counted.setdefault((x['name'], rv_norm(x['proof'])), x)
        nov = {}
        for d in dirs:
            for x in rd(f'{A}/{d}/novelty_proofs.jsonl'):
                if x['src'] == 'transfer':
                    nov.setdefault((x['name'], rv_norm(x['proof'])), x)
        missing = [k for k in counted if k not in nov]; extra = [k for k in nov if k not in counted]
        res = {'counted': len(counted), 'scored': len(nov), 'missing': len(missing), 'extra': len(extra), 'bins': {}}
        for L in (7, 8, 9, 10, 11):
            ks = [k for k in counted if k in nov and T[k[0]]['L_true'] == L]
            lps = [nov[k]['base_logp_T08'] for k in ks]
            res['bins'][L] = {'n': len(ks), 'ge_1e-5': sum(1 for v in lps if v >= LN1e5), 'ge_1/256': sum(1 for v in lps if v >= LN256)}
        ks9 = [k for k in counted if k in nov and T[k[0]]['L_true'] >= 9]
        res['ge9'] = {'n': len(ks9), 'lt_1e-5': sum(1 for k in ks9 if nov[k]['base_logp_T08'] < LN1e5)}
        # per theorem: best proof
        bt = collections.defaultdict(lambda: -1e9)
        for k in counted:
            if k in nov:
                bt[k[0]] = max(bt[k[0]], nov[k]['base_logp_T08'])
        res['theorems'] = {L: {'n': sum(1 for n in bt if T[n]['L_true'] == L), 'best_ge_1e-5': sum(1 for n, v in bt.items() if T[n]['L_true'] == L and v >= LN1e5)} for L in (7, 8, 9, 10, 11)}
        out[arm] = res
        ks = sorted(k for k in counted if k in nov); rng.shuffle(ks)
        sample += [(arm, k, counted[k]['prompt'], nov[k]['base_logp_T08'], nov[k]['base_n_shifts']) for k in ks[:110]]
        b = res['bins']
        print(f"{arm:10s} counted {res['counted']} scored {res['scored']} missing {res['missing']} extra {res['extra']} | proofs p>=1e-5 by L: " +
              ' '.join(f"{L}:{b[L]['ge_1e-5']}/{b[L]['n']}" for L in b) + f" | L>=9 below 1e-5: {res['ge9']['lt_1e-5']}/{res['ge9']['n']}", flush=True)
    json.dump(out, open('review_out/reach.json', 'w'), indent=1)
    if '--rescore' in sys.argv:
        import torch
        from model import load_ckpt
        torch.set_num_threads(2)
        model, tok, _ = load_ckpt('ckpts/stage1_abs.pt', 'cpu')
        diffs = []; flips = 0
        for i, (arm, k, prompt, lp_exec, nsh) in enumerate(sample):
            lp, n = my_score(model, tok, prompt, k[1])
            diffs.append((arm, k[0], lp, lp_exec, n, nsh))
            flips += ((lp >= LN1e5) != (lp_exec >= LN1e5))
            if i % 200 == 0:
                print(i, arm, k[0], round(lp, 3), round(lp_exec, 3), n, nsh, flush=True)
        mad = max(abs(a[2] - a[3]) for a in diffs)
        print('rescored', len(diffs), 'max |dlogp|', mad, 'threshold flips', flips, 'shift-count mismatches', sum(1 for a in diffs if a[4] != a[5]))
        json.dump(diffs, open('review_out/reach_rescore.json', 'w'))

if __name__ == '__main__':
    main()
