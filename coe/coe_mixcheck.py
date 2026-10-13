#!/usr/bin/env python3
"""create-or-elicit: the knockout's fine-tune mixes, round by round -- every record classified (sigma / sigma_impi /
sigma+ / lemma / DN on premise or hypothesis / no DN) and attributed by source: `replay` (the record is in the arm's
pretraining set), `k12_only` (in K12 but not in the arm's set: a removed record leaking in), or `rl` (in neither: the
ladder's own accepted proofs; with --found, those absent from the last found file are reported as `other`).
Pre-registered check: in the knockout arm sigma / sigma+ appear only in RL proofs, never in replay, and no K12-only
record enters a mix.

  python3 coe/coe_mixcheck.py --dir artifacts/coe/ladder/la_ko_s0 --train data/coe/train_k12ko.jsonl.gz \
      --k12 data/coe/src/train_k12.jsonl.gz --out artifacts/coe/rounds/mix_la_ko_s0.json
"""
import argparse, collections, glob, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from coe.coe_rounds import classify, last_file, read_jsonl

SIGMA = ('sigma', 'sigma_impi', 'sigma_plus_only', 'lemma_route')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', required=True)
    ap.add_argument('--train', required=True)
    ap.add_argument('--k12', default=None)
    ap.add_argument('--found', action='store_true', help='attribute RL records to the last found file')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    train = {(x['prompt'], x['proof']) for x in read_jsonl(a.train)}
    k12 = {(x['prompt'], x['proof']) for x in read_jsonl(a.k12)} - train if a.k12 else set()
    rl = None
    if a.found:
        lf = last_file(a.dir, 'found')
        rl = {(x['prompt'], x['proof']) for x in read_jsonl(lf[1])} if lf else set()
    out = {'dir': a.dir, 'train': a.train, 'k12': a.k12, 'rounds': {}}
    files = {}
    for fn in glob.glob(os.path.join(a.dir, 'mix_*.jsonl*')):
        r = int(re.search(r'mix_(\d+)', fn).group(1))
        if r not in files or fn.endswith('.gz'):
            files[r] = fn
    tot = collections.Counter()
    cache = {}
    for r in sorted(files):
        c = collections.Counter()
        for x in read_jsonl(files[r]):
            key = (x['prompt'], x['proof'])
            if key in train:
                src = 'replay'
            elif key in k12:
                src = 'k12_only'
            else:
                src = 'rl' if rl is None or key in rl else 'other'
            if x['proof'] not in cache:
                cache[x['proof']] = classify(x['proof'])
            c[(src, cache[x['proof']])] += 1
        tot.update(c)
        out['rounds'][r] = {f'{s}:{k}': v for (s, k), v in sorted(c.items())}
        print(f"round {r}: records {sum(c.values())}; replay {sum(v for (s, _), v in c.items() if s == 'replay')}, "
              f"rl {sum(v for (s, _), v in c.items() if s == 'rl')}; rl sigma-like "
              f"{sum(c[('rl', k)] for k in SIGMA)}; replay sigma-like {sum(c[('replay', k)] for k in SIGMA)}; "
              f"k12-only {sum(v for (s, _), v in c.items() if s == 'k12_only')}", flush=True)
    out['check'] = {'replay_sigma_like': sum(tot[('replay', k)] for k in SIGMA),
                    'k12_only_records': sum(v for (s, _), v in tot.items() if s == 'k12_only'),
                    'rl_sigma_like': sum(tot[('rl', k)] for k in SIGMA),
                    'records': sum(tot.values()), 'rounds': sorted(files)}
    out['check']['passed'] = out['check']['replay_sigma_like'] == 0 and out['check']['k12_only_records'] == 0
    print(json.dumps(out['check']))
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(out, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
