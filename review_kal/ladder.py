#!/usr/bin/env python3
"""Addendum 1 / 3 recount: the EI ladder from KAL-D s0 and its frozen arm (artifacts/kalmar/ladder/la_kal_{ei,frozen}_s0),
from the cumulative found_<r>.jsonl (distinct accepted target proofs, `round` = first-found round), against the reviewer's
own algorithm proof (kc.kalmar).  Per round: new proofs, exact-Kalmár share (ND string equal), mean actions vs the
algorithm's, share of deviations shorter than the algorithm's; cumulative solved; per-round reads from round_<r>.json.
Addendum 3: the anneal arm's targets read (eval/kalDA_s0_targets_k16) against the base re-read (eval/kalD_s0_targets_k16).

  python3 review_kal/ladder.py -> out/ladder.json
"""
import collections, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc

L = os.path.join(kc.ROOT, 'artifacts', 'kalmar', 'ladder')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
tg = {r['name']: r for r in kc.rows(os.path.join(kc.ROOT, 'data', 'kalmar', 'ei_targets1000.jsonl'))}
ALG = {}


def alg(prompt):
    if prompt not in ALG:
        ALG[prompt] = kc.kalmar(prompt)
    return ALG[prompt]


res = {}
for arm in ('ei', 'frozen'):
    d = os.path.join(L, f'la_kal_{arm}_s0')
    rounds = sorted(int(re.search(r'found_(\d+)', f).group(1)) for f in glob.glob(d + '/found_[0-9]*.jsonl'))
    last = rounds[-1]
    per = collections.defaultdict(collections.Counter)
    first = {}
    for x in kc.rows(f'{d}/found_{last}.jsonl'):
        assert x['name'] in tg and x['prompt'] == tg[x['name']]['prompt']
        m = alg(x['prompt'])
        r = x['round']
        na = x['proof'].count(';') + 1
        exact = x['proof'] == m['proof']
        c = per[r]
        c['new'] += 1; c['exact'] += exact; c['actions'] += na; c['algo_actions'] += len(m['acts'])
        c['dev_shorter'] += (not exact) and na < len(m['acts'])
        c['dev_longer'] += (not exact) and na > len(m['acts'])
        c['dev_same_len'] += (not exact) and na == len(m['acts'])
        first[x['name']] = min(first.get(x['name'], 99), r)
    cum = {r: sum(1 for v in first.values() if v <= r) for r in rounds}
    # consistency: each found_r's cumulative content equals found_last restricted to round <= r
    cons = {}
    for r in rounds:
        n = sum(1 for _ in kc.rows(f'{d}/found_{r}.jsonl'))
        cons[r] = (n, sum(per[q]['new'] for q in rounds if q <= r))
    rj = {}
    for f in sorted(glob.glob(d + '/round_*.json')):
        j = json.load(open(f))
        rj[j['round']] = {'ckpt': j['ckpt'], 'seed': j['seed'], 'targets_round_solved': j['targets_round']['solved'],
                          'target_sample_acc': j['target_sample_acc'], 'heldout_greedy': j['heldout_greedy']['rate'],
                          'transfer_greedy': j['transfer_greedy']['rate'], 'transfer_round_solved': j['transfer_round']['solved'],
                          'targets_cum': j['targets_cum']['solved'], 'transfer_cum': j['transfer_cum']['solved'], 'secs': j.get('secs'),
                          'mix_rl_records': j.get('mix_rl_records'), 'env_end': j['env'].get('env_end')}
    res[arm] = {'rounds_found': rounds, 'per_round': {r: dict(per[r]) for r in sorted(per)}, 'cum_solved': cum,
                'found_file_consistency': cons, 'round_json': rj}
    print(arm, 'cum solved', cum, 'consistency', cons, flush=True)
    for r in sorted(per):
        c = per[r]
        print(f"   r{r}: new {c['new']:5d} exact {c['exact'] / c['new']:.3f} actions/algo {c['actions'] / c['algo_actions']:.3f} "
              f"dev shorter {c['dev_shorter'] / c['new']:.3f} longer {c['dev_longer'] / c['new']:.3f} same-len {c['dev_same_len']}", flush=True)
    for r, j in rj.items():
        print('   round json', r, j, flush=True)

# Addendum 3 targets reads (k 16, seed 2): base re-read and the anneal arm
for t in ('kalD_s0_targets_k16', 'kalDA_s0_targets_k16'):
    rows = list(kc.rows(os.path.join(kc.ROOT, 'artifacts', 'kalmar', 'eval', t + '.rows.jsonl.gz')))
    res[t] = {'n': len(rows), 'solved': sum(r['n_ok'] > 0 for r in rows), 'attempt_acc': sum(r['n_ok'] for r in rows) / sum(r['k'] for r in rows),
              'trunc': sum(s == 'fail:truncated' for r in rows for s in r['status']), 'attempts': sum(r['k'] for r in rows)}
    print(t, res[t], flush=True)
json.dump(res, open(os.path.join(OUT, 'ladder.json'), 'w'), indent=1)
