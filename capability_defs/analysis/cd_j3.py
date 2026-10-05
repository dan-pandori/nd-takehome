#!/usr/bin/env python3
"""capability-defs Part 3 (J3): plain vs guided read-outs (AGENT_POLICY: every evaluation of a proof-state model
reports both numbers, labelled) and the per-theorem "guided" elicitation for the capability-vs-propensity card.

  python3 capability_defs/analysis/cd_j3.py   -> out/j3.txt (stdout), out/j3.json

Plain = the sample-seed-1 reads already on file (trajectory x1 for pend / r8; rl-continue x1 for r16; trajectory-cap6
x1 / rl-continue-cap6 x1 + J5 at cap 6).  Guided = J3's `guided_eval.py --arm logical` reads (k 256, T 0.8, seed 1,
max_rej 10).  Reported per (cap, seed, checkpoint): solved@256 on textbook72 dev58 / train14 / combined and holdout250,
plain vs guided, and generated tokens per attempt (guided spends more per attempt).
"""
import gzip, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cd_reads as R

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')


def tb_split():
    dev = {json.loads(l)['name'] for l in open(f'{ROOT}/data/gt/tb72_textbook_dev.jsonl')}
    tr = {json.loads(l)['name'] for l in open(f'{ROOT}/data/gt/tb72_textbook_train.jsonl')}
    return dev, tr


def main():
    dev, tr = tb_split()
    h250 = set(R.names('h250'))
    res = {}
    for cap, pre in ((12, ''), (6, 'c6_')):
        for s in (0, 1, 2):
            for ck in ('pend', 'r8', 'r16'):
                p = f'{ROOT}/artifacts/cd/j3/{pre}s{s}_{ck}_logical.rows.jsonl.gz'
                if not os.path.exists(p):
                    continue
                g = {}; toks = att = 0
                for l in gzip.open(p, 'rt'):
                    r = json.loads(l); g[r['name']] = r['n_ok']
                    if 'tokens' in r:
                        toks += sum(r['tokens']); att += len(r['tokens'])
                pl = {}
                for pool in R.POOLS:
                    d = R.read(cap, s, ck, pool, 1)
                    for n, v in (d or {}).items():
                        pl[n] = v[0]
                row = {}
                for lab, S in (('tb72_dev58', dev), ('tb72_train14', tr), ('tb72', dev | tr), ('h250', h250)):
                    row[lab] = {'guided': sum(1 for n in S if g.get(n, 0) > 0),
                                'plain': sum(1 for n in S if pl.get(n, 0) > 0) if pl else None, 'n': len(S)}
                row['guided_tokens_per_attempt'] = toks / att if att else None
                res[f'c{cap}_s{s}_{ck}'] = row
                print(f"cap {cap} s{s} {ck:4s}: " + '; '.join(f"{k} plain {v['plain']} / guided {v['guided']} (of {v['n']})"
                                                       for k, v in row.items() if isinstance(v, dict))
                      + (f"; guided tokens / attempt {row['guided_tokens_per_attempt']:.0f}" if row['guided_tokens_per_attempt'] else ''))
    json.dump(res, open(f'{OUT}/j3.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
