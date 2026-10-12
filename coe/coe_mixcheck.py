#!/usr/bin/env python3
"""create-or-elicit: the knockout's fine-tune mixes, round by round -- every record classified (sigma / sigma+ / lemma /
DN on premise or hypothesis / no DN) and attributed to its source: an RL proof (in the ladder's last found file) or a
replay record (in the arm's pretraining set).  Pre-registered check: in the knockout arm sigma / sigma+ appear only in RL
proofs, never in replay.

  python3 coe/coe_mixcheck.py --dir artifacts/coe/ladder/la_ko_s0 --train data/coe/train_k12ko.jsonl --out artifacts/coe/rounds/mix_la_ko_s0.json
"""
import argparse, collections, glob, gzip, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from coe.coe_rounds import classify, last_file, read_jsonl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', required=True)
    ap.add_argument('--train', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    train = set()
    for x in read_jsonl(a.train):
        train.add((x['prompt'], x['proof']))
    lf = last_file(a.dir, 'found')
    rl = set()
    if lf:
        for x in read_jsonl(lf[1]):
            rl.add((x['prompt'], x['proof']))
    out = {}
    for fn in sorted(glob.glob(os.path.join(a.dir, 'mix_*.jsonl*')), key=lambda f: int(re.search(r'mix_(\d+)', f).group(1))):
        r = int(re.search(r'mix_(\d+)', fn).group(1))
        c = collections.Counter()
        cache = {}
        for x in read_jsonl(fn):
            key = (x['prompt'], x['proof'])
            src = 'rl' if key in rl else ('replay' if key in train else 'other')
            if x['proof'] not in cache:
                cache[x['proof']] = classify(x['proof'])
            c[(src, cache[x['proof']])] += 1
        out[r] = {f'{s}:{k}': v for (s, k), v in sorted(c.items())}
        sig_replay = c[('replay', 'sigma')] + c[('replay', 'sigma_plus_only')] + c[('replay', 'lemma_route')]
        print(f"round {r}: records {sum(c.values())}; rl sigma {c[('rl', 'sigma')]}, rl sigma+ {c[('rl', 'sigma_plus_only')]}, "
              f"replay sigma/sigma+/lemma {sig_replay}, unattributed {sum(v for (s, _), v in c.items() if s == 'other')}", flush=True)
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(out, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
