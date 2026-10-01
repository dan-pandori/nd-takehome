#!/usr/bin/env python3
"""Reviewer: (a) candidate set == distinct accepted proofs of r8 x0 per theorem; (b) eventual proof == argmax total
T1.0 log p among scored candidates; (c) replay failures among candidates; (d) eventual proofs are r8-x0 accepted."""
import json, os, collections
R = os.path.expanduser('~/review/trajectory'); A = f'{R}/artifacts/tj'
for s in (0, 1, 2):
    ev0 = {}
    for pool in ('tb72', 'h250'):
        for l in open(f'{A}/eval/s{s}_r8__{pool}_x0.jsonl'):
            r = json.loads(l)
            if r['proofs']: ev0[(pool, r['name'])] = set(r['proofs'])
    cand = collections.defaultdict(set); ctid = {}
    for l in open(f'{A}/targets/cand_s{s}.jsonl'):
        r = json.loads(l); cand[(r['pool'], r['name'])].add(r['proof']); ctid[r['tid']] = r
    sc = {}
    for l in open(f'{A}/score/cand_s{s}/s{s}_r8.jsonl'):
        r = json.loads(l); sc[r['tid']] = sum(r['T1.0']['step_lp'])
    meta = {json.loads(l)['tid']: json.loads(l) for l in open(f'{A}/score/cand_s{s}/targets.jsonl')}
    nfail = [t for t, m in meta.items() if not m['replay_ok']]
    diff = [k for k in set(ev0) | set(cand) if ev0.get(k, set()) != cand.get(k, set())]
    best = {}
    for t, v in sc.items():
        k = (ctid[t]['pool'], ctid[t]['name'])
        if k not in best or v > best[k][0]: best[k] = (v, ctid[t]['proof'])
    evt = {(json.loads(l)['pool'], json.loads(l)['name']): json.loads(l)['proof'] for l in open(f'{A}/targets/eventual_s{s}.jsonl')}
    mism = [k for k in evt if best.get(k, (0, None))[1] != evt[k]]
    notacc = [k for k in evt if evt[k] not in ev0.get(k, set())]
    # ties within 1e-6
    print(f'seed {s}: theorems r8x0 solved {len(ev0)}, cand theorems {len(cand)}, cand proofs {sum(map(len, cand.values()))} '
          f'(distinct accepted r8x0 {sum(map(len, ev0.values()))}); set mismatches {len(diff)}; cand replay failures {len(nfail)} {[meta[t].get("why","")[:60] for t in nfail[:4]]}; '
          f'eventual {len(evt)}; not argmax {len(mism)}; eventual not r8x0-accepted {len(notacc)}; theorems whose every cand failed replay {len(set(ev0) - set(best))}')
    for k in mism[:5]: print('   mism', k, best.get(k, (None,))[0])
