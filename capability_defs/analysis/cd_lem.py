#!/usr/bin/env python3
"""capability-defs Part 3: excluded-middle teachability (J4, J6, J6b) — elicit-finetune and schema-acquisition cards.

  python3 capability_defs/analysis/cd_lem.py   -> out/lem.txt (stdout), out/lem.json

Evaluation set: the 40 premise-free A v ~A instances of transfer (never trained on by any ladder); the 39 that are not
intuitionistically provable (G4ip, `intuit.py`) are the "classical-only" set the verdicts use.  Per read: solved (>= 1 of
256) and mean pass@1 on the 39.  Models: cap-12 best-cap12 pend / r16 (trajectory, rl-continue); J4 fine-tunes of pend
(A0 replay only, A4 / A16 LEM demonstrations, C16 matched non-LEM, all with K12 replay); J6 no-DN knockout (pend-recipe
Stage 1 on K12 minus DN records) and its A0 / A16 fine-tunes (K12 replay, which re-teaches DN: see the critic);
J6b fine-tunes of pend and of the knockout on knockout-corpus replay (A16n / C16n, two fine-tune seeds).
Decision quantity (J6b, pre-registered in log.md): gain = mean held-out pass@256 (= share solved at k 256) of A16n minus
C16n, pend vs knockout; computed on the 39 classical-only instances (all 40 printed too); mean pass@1 printed as a secondary.
"""
import glob, json, os, sys, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
from intuit import intuit_provable

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')


def summarise(path, cls):
    rows = [json.loads(l) for l in open(path)]
    rc = [r for r in rows if r['name'] in cls]
    return {'solved39': sum(r['n_ok'] > 0 for r in rc), 'pass1_39': sum(r['n_ok'] / r['n_tried'] for r in rc) / len(rc),
            'solved40': sum(r['n_ok'] > 0 for r in rows), 'k': rows[0]['n_tried']}


def main():
    src = {json.loads(l)['name']: json.loads(l) for l in open(f'{ROOT}/data/cd/j4/lem_transfer40.jsonl')}
    cls = {n for n, r in src.items() if not intuit_provable(r['prompt'])}
    res = {}
    for d in ('j4', 'j6', 'j6b'):
        for p in sorted(glob.glob(f'{ROOT}/artifacts/cd/{d}/*lem*.jsonl')):
            if p.endswith('.args.json'):
                continue
            res[f'{d}/{os.path.basename(p)}'] = summarise(p, cls)
    print(f'classical-only held-out A v ~A instances: {len(cls)} of 40')
    for k, v in sorted(res.items()):
        print(f"  {k:52s} solved {v['solved39']:2d}/39  mean pass@1 {v['pass1_39']:.3f}  (all 40: {v['solved40']}; k {v['k']})")
    # J6b decision quantity per training seed
    print('\nJ6b gain = mean pass@256 (A16n) - mean pass@256 (C16n), averaged over fine-tune seeds; pend vs no-DN knockout'
          ' (pre-registered: latent if pend - knockout >= 0.3 on >= 2/3 seeds; teachable if within 0.2):')
    out = {}
    for s in (0, 1, 2):
        g = {}
        for q, n in (('solved39', 39), ('solved40', 40), ('pass1_39', 1)):
            for m in ('pend', 'nodn'):
                a = [res[k][q] / n for k in res if k.startswith(f'j6b/s{s}_{m}_A16n')]
                c = [res[k][q] / n for k in res if k.startswith(f'j6b/s{s}_{m}_C16n')]
                if a and c:
                    g[f'{m}_{q}'] = sum(a) / len(a) - sum(c) / len(c)
                    g[f'{m}_n'] = (len(a), len(c))
        if 'pend_solved39' in g and 'nodn_solved39' in g:
            out[s] = g
            for q, lab in (('solved39', 'pass@256, 39 classical-only (decision)'), ('solved40', 'pass@256, all 40'),
                           ('pass1_39', 'mean pass@1, 39 (secondary)')):
                diff = g[f'pend_{q}'] - g[f'nodn_{q}']
                verdict = 'latent in pend' if diff >= 0.3 else 'teachable from scratch' if abs(diff) <= 0.2 else 'between'
                print(f"  s{s} {lab:40s}: pend gain {g[f'pend_{q}']:.3f}, knockout gain {g[f'nodn_{q}']:.3f}, "
                      f"difference {diff:+.3f} -> {verdict}")
                g[f'verdict_{q}'] = verdict
        elif g:
            print(f'  s{s}: incomplete ({sorted(g)})')
    json.dump({'reads': res, 'j6b': out}, open(f'{OUT}/lem.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
