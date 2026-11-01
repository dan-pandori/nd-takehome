#!/usr/bin/env python3
"""Reviewer (coe-dose01): y per round = strict sigma-covered held-out members (106, see common.strict_members) with an
accepted proof in any round <= r of the ladder's per-round k 32 transfer sample, re-derived from the ladder's LAST
cumulative found_transfer file (streamed from the bucket; each row carries the round the proof was first found).
Also: first-solve round of every one of the 832 tracked theorems (cross-check against the round files' transfer_cum),
per-family cumulative counts, and the strict-member rows saved for the Lean re-check.

  python3 ycurve.py la_dose01_s0 16      (bucket coe-dose01)
"""
import collections, gzip, json, subprocess, sys
sys.path.insert(0, '/home/dan/work/coe-dose01/review_cd01')
from common import BIG, REPO, strict_members

import os
BK = os.environ.get('YC_BK', 'hf://buckets/dan-pandori/nd-rl/coe-dose01/artifacts/coe/ladder')
TAG = os.environ.get('YC_TAG', '')


def main(lad, last):
    SM = strict_members()
    url = f'{BK}/{lad}/found_transfer_{last}.jsonl'
    p = subprocess.Popen(['hf', 'buckets', 'cp', url, '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1 << 20)
    first = {}                      # name -> min round
    nrows = collections.Counter()   # round -> rows first found in that round
    keep = gzip.open(f'{BIG}/ft/{TAG}{lad}_strict.jsonl.gz', 'wt')
    n = 0
    for line in p.stdout:
        x = json.loads(line)
        n += 1
        r = x['round']
        nrows[r] += 1
        first[x['name']] = min(first.get(x['name'], 999), r)
        if x['name'] in SM:
            keep.write(json.dumps({k: x[k] for k in ('name', 'prompt', 'proof', 'norm', 'written', 'pruned', 'round')}) + '\n')
    keep.close()
    rc = p.wait()
    rounds = sorted(nrows)
    fam_sizes = collections.Counter(SM.values())
    out = {'ladder': lad, 'file': url, 'rows': n, 'rc': rc, 'rounds': rounds, 'per_round': {}}
    for r in range(1, last + 1):
        y = sorted(nm for nm in SM if first.get(nm, 999) <= r)
        fam = collections.Counter(SM[nm] for nm in y)
        tc = sum(1 for nm, fr in first.items() if fr <= r)
        out['per_round'][r] = {'y': len(y), 'by_family': dict(sorted(fam.items())), 'transfer_cum_solved_832': tc,
                               'new_rows': nrows.get(r, 0)}
    out['first_round_strict'] = {nm: first[nm] for nm in sorted(SM) if nm in first}
    out['family_sizes'] = dict(fam_sizes)
    json.dump(out, open(f'/home/dan/work/coe-dose01/review_cd01/out/y_{TAG}{lad}.json', 'w'), indent=1)
    cross = next((r for r in range(1, last + 1) if out['per_round'][r]['y'] >= 14), None)
    print(f"{lad}: rows {n} (rc {rc}); y by round: " + ' '.join(f"r{r}:{out['per_round'][r]['y']}" for r in range(1, last + 1)) +
          f"; first round y>=14: {cross}")


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))
