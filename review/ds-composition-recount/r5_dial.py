"""Recount 5 — dial (4 rounds, k=32) acquisition: targets with an accepted
depth-3 proof, min round per start-index-normalised proof; EI minus frozen."""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rv
from nd_verify import verify_text

T = {r['name']: r for r in rv.load('data/p2/targets_depth3.jsonl')}
TR = {r['name']: r for r in rv.load('data/p2/transfer_depth3.jsonl')}
res = {}
for mode in ['ei', 'frozen']:
    for arm in ['c0', 'a1', 'a2', 'a3', 'a4']:
        for s in [0, 1]:
            d = 'artifacts/dsc/%s_%s_s%d' % (mode, arm, s)
            o = {}
            for tag, f, pool in [('targets', 'found_4.jsonl', T), ('transfer', 'found_transfer_4.jsonl', TR)]:
                p = os.path.join(d, f)
                if not os.path.exists(p):
                    o[tag] = None; continue
                solved = {}; acq = {}; bad = 0; nrec = 0
                distinct = set(); distinct_d3 = set()
                for r in rv.load(p):
                    nrec += 1
                    g = pool[r['name']]
                    ok, why, _ = verify_text(g['prompt'] + ' ' + r['proof'])
                    if not ok:
                        bad += 1; continue
                    nz = rv.norm(r['proof'])
                    distinct.add((r['name'], nz))
                    rd = r['round']
                    solved[r['name']] = min(solved.get(r['name'], 99), rd)
                    if rv.is_depth3(rv.prune(rv.try_parse(r['proof']))):
                        acq[r['name']] = min(acq.get(r['name'], 99), rd)
                        distinct_d3.add((r['name'], nz))
                N = len(pool)
                o[tag] = {'n_pool': N, 'records': nrec, 'nd_verify_rejects': bad,
                          'solved': len(solved), 'rate_solved': round(len(solved) / N, 5),
                          'acquired_depth3': len(acq), 'acquisition': round(len(acq) / N, 5),
                          'distinct_proofs': len(distinct), 'distinct_depth3_proofs': len(distinct_d3),
                          'acq_by_round': dict(sorted(collections.Counter(acq.values()).items()))}
            res['%s_%s_s%d' % (mode, arm, s)] = o
            print('%s_%s_s%d' % (mode, arm, s), o['targets']['acquisition'], 'bad', o['targets']['nd_verify_rejects'], flush=True)
json.dump(res, open('recount/out_dial.json', 'w'), indent=1)
print()
print('%-6s %-14s %-14s %s' % ('arm', 'EI acq', 'frozen acq', 'EI-frozen'))
for arm in ['c0', 'a1', 'a2', 'a3', 'a4']:
    for s in [0, 1]:
        e = res['ei_%s_s%d' % (arm, s)]['targets']['acquisition']
        f = res['frozen_%s_s%d' % (arm, s)]['targets']['acquisition']
        print('%-6s %-14s %-14s %+0.4f' % ('%s_s%d' % (arm, s), e, f, e - f))
