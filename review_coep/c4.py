"""review_coep/c4.py -- C4 recount from the per-chunk rows (artifacts/coe_paper/c4/*.chunks.jsonl).

Within reach at K = 17,189 (K_train(16) of knockout s1, from the create-or-elicit review): p_hat >= 1/K, i.e. c >= 2 at
n = 18,432 (c / n >= 1 / K  <=>  c >= n / K = 1.072).
"""
import json, os, sys, collections, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

K = 17189
FAM = families()
out = {}
for tag in ('ko_s1', 'ko_s3'):
    summ = json.load(open(P(f'artifacts/coe_paper/c4/{tag}.json')))
    args = json.load(open(P(f'artifacts/coe_paper/c4/{tag}.json.args.json')))
    inp = jl(P(f'data/coe_paper/c4_{tag}.jsonl'))
    rows = jl(P(f'artifacts/coe_paper/c4/{tag}.chunks.jsonl'))
    per = collections.defaultdict(lambda: dict(tried=0, ok=0, chunks=set(), seeds=set(), acc=collections.Counter()))
    summaries = [r for r in rows if r.get('chunk_summary')]
    rows = [r for r in rows if not r.get('chunk_summary')]
    print(f'  {tag}: {len(rows)} per-theorem chunk rows, {len(summaries)} chunk summaries; peak alloc GB '
          f'{sorted({r["peak_alloc_gb"] for r in summaries})}; GPU {sorted({r["gpu"] for r in summaries})}; '
          f'gen_s total {sum(r["gen_s"] for r in summaries):.0f}')
    for r in rows:
        p = per[r['name']]
        assert r['chunk'] not in p['chunks'], ('duplicate chunk', tag, r['name'], r['chunk'])
        p['chunks'].add(r['chunk']); p['seeds'].add(r['seed'])
        p['tried'] += r['tried']; p['ok'] += r['ok']
        for t, c in r['acc'].items():
            p['acc'][t] += c
        assert sum(r['acc'].values()) == r['ok'], ('acc != ok', tag, r)
    names = [r['name'] for r in inp]
    assert set(per) == set(names), (tag, set(per) ^ set(names))
    seeds_ok = all(p['seeds'] == {9500 + c for c in p['chunks']} for p in per.values())
    print(f'== {tag}: ckpt {summ["ckpt"]}; {len(names)} theorems; chunk seeds = 9500 + chunk: {seeds_ok}; '
          f'stop_successes {args["stop_successes"]}; T {args["temperature"]}; caps {args["max_action"]}/{args["max_steps"]}')
    fam_of = {m: f for f, ms in FAM.items() for m in ms}
    res = {}
    for n in names:
        p = per[n]
        c, t = p['ok'], p['tried']
        res[n] = dict(c=c, n=t, distinct=len(p['acc']), within=c * K >= t, family=fam_of.get(n, '-'),
                      summary_ok=summ['theorems'][n]['ok'], summary_tried=summ['theorems'][n]['tried'])
        assert summ['theorems'][n]['ok'] == c and summ['theorems'][n]['tried'] == t, (n, summ['theorems'][n])
        print(f'  {n:18s} {fam_of.get(n, "-"):20s} c {c:2d} / {t}  distinct {len(p["acc"])}  within reach at K: {c * K >= t}')
    tot_c = sum(v['c'] for v in res.values()); tot_n = sum(v['n'] for v in res.values())
    print(f'  pooled: {tot_c} / {tot_n} = {tot_c / tot_n:.3g}; within reach: {sum(v["within"] for v in res.values())}')
    out[tag] = dict(per=res, pooled=[tot_c, tot_n], attempts=summ['attempts'])
    if tag == 'ko_s1':
        cc = {n: v for n, v in res.items() if v['family'] == 'contraposition_conv'}
        tc = sum(v['c'] for v in cc.values()); tn = sum(v['n'] for v in cc.values())
        print(f'  contraposition_conv members only: {len(cc)} members, {tc} / {tn} = {tc / tn:.3g}')
        out[tag]['cc_pooled'] = [tc, tn]
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_c4.json'), 'w'), indent=1)
