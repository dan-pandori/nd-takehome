"""Recount 8 — term size beside line count, and frontiers."""
import sys, os, json, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rv

LTR = {r['name']: r for r in rv.load('data/ladder/transfer.jsonl')}
res = {}
for arm in ['c0', 'a1', 'a2', 'a3', 'a4']:
    o = {}
    # ladder T1 / frozen transfer proofs, seed 0
    for mode in ['T1', 'frozen']:
        f = 'artifacts/dsc/la_%s_%s_s0/found_transfer_8.jsonl' % (mode, arm)
        if not os.path.exists(f):
            continue
        sizes, lens, best = [], [], {}
        for r in rv.load(f):
            L = rv.try_parse(r['proof']); p = rv.prune(L)
            sizes.append(rv.term_size(p)); lens.append(len(p))
            n = r['name']
            if n not in best or len(p) < best[n][0]:
                best[n] = (len(p), rv.term_size(p))
        o['ladder_%s' % mode] = {
            'proofs': len(sizes), 'targets': len(best),
            'median_term_size': statistics.median(sizes), 'max_term_size': max(sizes),
            'median_pruned_lines': statistics.median(lens), 'max_pruned_lines': max(lens),
            'frontier_L_true': max(LTR[n]['L_true'] for n in best),
            'median_best_term_size_per_target': statistics.median(v[1] for v in best.values()),
        }
    # coverage frontier
    for pool in ['d3sub', 'd3req', 'redreq']:
        sizes, lens = [], []
        for s in [0, 1]:
            f = 'artifacts/dsc/cov_%s_s%d_%s.s0.jsonl' % (arm, s, pool)
            if not os.path.exists(f):
                continue
            for r in rv.load(f):
                for pf in r['proofs']:
                    L = rv.try_parse(pf['proof']); p = rv.prune(L)
                    sizes.append(rv.term_size(p)); lens.append(len(p))
        if sizes:
            o['cov_%s' % pool] = {'proofs': len(sizes),
                                  'median_term_size': statistics.median(sizes), 'max_term_size': max(sizes),
                                  'max_pruned_lines': max(lens),
                                  'line_hist': dict(sorted(collections.Counter(lens).items()))}
    res[arm] = o
json.dump(res, open('recount/out_size.json', 'w'), indent=1)
for arm in res:
    print(arm, {k: (v.get('median_term_size'), v.get('max_pruned_lines') or v.get('max_pruned_lines')) for k, v in res[arm].items()})
