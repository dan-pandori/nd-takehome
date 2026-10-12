#!/usr/bin/env python3
"""create-or-elicit: collect known accepted proofs of the strict sigma-covered members (families.json strict_trained /
strict_heldout) from ladder found files, as cd_score.py targets ({tid, name, prompt, kind, proof, src}).

  python3 coe/coe_known.py --found F1.jsonl [F2 ...] --src old_full_s0 --out artifacts/coe/known/old_full_s0.jsonl
"""
import argparse, gzip, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from coe.coe_rounds import classify


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--found', nargs='+', required=True)
    ap.add_argument('--src', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--families', default='data/coe/families.json')
    a = ap.parse_args()
    fam = json.load(open(a.families))
    want = set()
    for f, d in fam['families'].items():
        if d['classical']:
            want |= set(d['strict_trained']) | set(d['strict_heldout'])
    want |= set(fam['generated_classical']['transfer']['strict'])
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    n = 0
    seen = set()
    with open(a.out, 'w') as fo:
        for fn in a.found:
            op = gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)
            for l in op:
                x = json.loads(l)
                if x['name'] not in want or (x['name'], x['proof']) in seen:
                    continue
                seen.add((x['name'], x['proof']))
                fo.write(json.dumps({'tid': f"{a.src}:{n}", 'name': x['name'], 'prompt': x['prompt'], 'kind': classify(x['proof']),
                                     'proof': x['proof'], 'src': a.src, 'round': x.get('round')}) + '\n')
                n += 1
    print(a.src, 'known strict-member proofs', n)


if __name__ == '__main__':
    main()
