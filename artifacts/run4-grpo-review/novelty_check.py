import json, collections, rvlib, math
A = '../artifacts/r4/'
res = {}
for s in range(20, 26):
    rows = [json.loads(l) for l in open(A + 'novelty_depth3_f0_a1_s%d_proofs.jsonl' % s)]
    by = collections.defaultdict(list)
    for r in rows: by[r['src']].append(r)
    res[s] = {}
    for src, L in sorted(by.items()):
        d3 = [r for r in L if rvlib.is_d3(r['proof'])]
        keys = set((r['name'], rvlib.normalise(r['proof'])) for r in L)
        first = {}
        for r in d3: first[r['name']] = min(first.get(r['name'], 99), int(r['round']))
        R = max([int(r['round']) for r in L] or [0])
        by_r = [sum(1 for v in first.values() if v <= k) for k in range(1, R + 1)]
        lp = [r['base_logp_T08'] for r in d3]
        res[s][src] = dict(n=len(L), distinct_norm=len(keys), n_d3=len(d3), d3_thms=len(first), max_round=R, d3_by_round=by_r,
                           ign=next((k + 1 for k, n in enumerate(by_r) if n >= 20), None),
                           frac_logp_below_log1_256=(sum(x < -math.log(256) for x in lp) / len(lp)) if lp else None,
                           max_logp=max(lp) if lp else None)
        print(s, src, res[s][src])
json.dump(res, open('novelty_recount.json', 'w'), indent=1)
