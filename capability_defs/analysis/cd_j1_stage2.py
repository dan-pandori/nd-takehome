#!/usr/bin/env python3
"""capability-defs J1 stage 2: choose proofs for exact (33-base) scoring.

  python3 capability_defs/analysis/cd_j1_stage2.py --seed S [--top 20]  -> artifacts/cd/j1/s2targets_s<S>.jsonl

For each theorem of H_S + CAL_S: the top-N known proofs by stage-1 score (T 0.8, b0) under pend_S, under r8_S and under
r16_S (union), plus every distinct proof pend_S itself found in J2 (pulled J2 files) that is not already a J1 target.
Rows keep the J1 tid (prefix k:) or get j2:<name>:<i>.
"""
import argparse, collections, glob, gzip, json, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--top', type=int, default=20)
    a = ap.parse_args()
    s = a.seed
    tgt = {}
    for p in sorted(glob.glob(f'{ROOT}/artifacts/cd/j1/targets_s{s}_p*.jsonl')):
        for l in open(p):
            r = json.loads(l)
            tgt[r['tid']] = r
    by = collections.defaultdict(list)
    for p in sorted(glob.glob(f'{ROOT}/artifacts/cd/j1/b1_s{s}_p*/compact.jsonl.gz')):
        with gzip.open(p, 'rt') as f:
            for l in f:
                r = json.loads(l)
                if r['replay_ok']:
                    by[r['name']].append(r)
    pick = {}
    for n, rs in by.items():
        for lab in (f's{s}_pend', f's{s}_r8', f's{s}_r16'):
            for r in sorted(rs, key=lambda r: -r['sc'][lab][2])[:a.top]:
                pick[r['tid']] = tgt[r['tid']]
    known = {(r['name'], r['proof']) for r in tgt.values()}
    pr = {r['name']: r['prompt'] for r in tgt.values()}
    pool = {r['name']: r['pool'] for r in tgt.values()}
    nj2 = 0
    for p in sorted(glob.glob(f'{ROOT}/artifacts/cd/j2/s{s}_*.jsonl')):
        for l in open(p):
            r = json.loads(l)
            for i, pf in enumerate(sorted(set(r.get('proofs') or []))):
                if (r['name'], pf) not in known and r['name'] in pr:
                    pick[f'j2:{r["name"]}:{i}'] = {'tid': f'j2:{r["name"]}:{i}', 'name': r['name'], 'pool': pool[r['name']],
                                                   'prompt': pr[r['name']], 'kind': 'known', 'proof': pf, 'src': ['j2']}
                    known.add((r['name'], pf)); nj2 += 1
    with open(f'{ROOT}/artifacts/cd/j1/s2targets_s{s}.jsonl', 'w') as f:
        for r in pick.values():
            f.write(json.dumps(r) + '\n')
    print(f's{s}: {len(pick)} stage-2 targets ({nj2} new proofs from J2) for {len(by)} theorems')


if __name__ == '__main__':
    main()
