#!/usr/bin/env python3
"""Reviewer: the knockout (and dose) fine-tune mixes, round by round, from the bucket's mix_<r>.jsonl.gz.  Every record is
attributed by identity: replay (in the arm's own pretraining set), k12_only (in K12 but not in the arm's set: a removed
record leaking in), rl (prompt is an rl_target and the record is in neither set).  sigma+ / free-positive counts per source.
Pre-registered check: in the knockout, sigma+ only in RL proofs; no K12-only record in any mix."""
import collections, hashlib, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

RV = C.RV
BK = 'hf://buckets/dan-pandori/nd-rl/create-or-elicit/artifacts/coe/ladder'


def ident(p, q):
    return hashlib.blake2b((p + ' || ' + q.strip()).encode(), digest_size=12).digest()


K12 = {ident(r['prompt'], r['proof']) for r in C.rows(f'{RV}/data/coe/src/train_k12.jsonl.gz')}
SETS = {'ko': {ident(r['prompt'], r['proof']) for r in C.rows(f'{RV}/data/coe/train_k12ko.jsonl.gz')},
        'dose1': {ident(r['prompt'], r['proof']) for r in C.rows(f'{RV}/data/coe/train_k12dose1.jsonl.gz')}}
TP = {r['prompt'] for r in C.rows(f'{RV}/data/ladder/rl_targets.jsonl')}
tmp = os.path.expanduser('~/review/coe_big/tmp_mix.jsonl.gz')
out = {}
for arm, seeds in (('ko', range(6)), ('dose1', range(3))):
    own = SETS[arm]
    for s in seeds:
        rounds = 24 if (arm, s) == ('ko', 1) else 16
        tot = collections.Counter()
        per_round = {}
        for r in range(1, rounds + 1):
            subprocess.run(['hf', 'buckets', 'cp', f'{BK}/la_{arm}_s{s}/mix_{r}.jsonl.gz', tmp], capture_output=True)
            if not os.path.exists(tmp):
                tot['missing_round'] += 1; continue
            c = collections.Counter()
            for x in C.rows(tmp):
                i = ident(x['prompt'], x['proof'])
                src = 'replay' if i in own else ('k12_only' if i in K12 else ('rl' if x['prompt'] in TP else 'other'))
                c[src] += 1
                if ': DN ' in x['proof']:
                    fl = C.sigma_flags(x['proof'])
                    if fl['sigma_plus']:
                        c[f'sigma_plus:{src}'] += 1
                    if fl['sigma']:
                        c[f'sigma:{src}'] += 1
            os.unlink(tmp)
            per_round[r] = dict(c); tot.update(c)
        out[f'{arm}_s{s}'] = {'total': dict(tot), 'per_round': per_round}
        print(f'{arm}_s{s} r1-{rounds}: ' + ', '.join(f'{k} {v}' for k, v in sorted(tot.items())), flush=True)
json.dump(out, open(f'{RV}/review_coe/out_mixcheck.json', 'w'), indent=1)
