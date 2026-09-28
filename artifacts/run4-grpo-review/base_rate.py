import json, sys, collections, rvlib
A = '../artifacts/r4/'
res = {}
for s in range(20, 26):
    f = A + 'cov_depth3_f0_a1_s%d.s0.jsonl' % s
    rows = [json.loads(l) for l in open(f)]
    names = [r['name'] for r in rows]
    tried = sum(r['n_tried'] for r in rows)
    ok = sum(r['n_ok'] for r in rows)
    cnt_sum = sum(p['count'] for r in rows for p in r['proofs'])
    d3_hits = d3_hits_w = d3_distinct = 0; d3_thms = set(); ident = 0; bad = 0; exe = 0
    dhist = collections.Counter()
    for r in rows:
        for p in r['proofs']:
            try:
                d = rvlib.depth(p['proof']); dw = rvlib.depth(p['proof'], False)
            except ValueError:
                bad += 1; continue
            dhist[d] += p['count']
            if rvlib.normalise(p['proof']) == p['proof'].strip(): ident += 1
            exe += p['pat']['depth3']
            if d >= 3:
                d3_hits += p['count']; d3_distinct += 1; d3_thms.add(r['name'])
            if dw >= 3: d3_hits_w += p['count']
    res[s] = dict(file=f, n_targets=len(rows), distinct_names=len(set(names)),
                  first300=names == ['targets_depth3_%d' % i for i in range(300)],
                  tried=tried, n_ok=ok, count_sum=cnt_sum, depth3_hits_pruned=d3_hits,
                  depth3_hits_written=d3_hits_w, depth3_distinct=d3_distinct, depth3_thms=len(d3_thms),
                  exec_flag_depth3=exe, exec_hits_by_pattern=sum(r['hits_by_pattern']['depth3'] for r in rows),
                  solved_thms=sum(r['n_ok'] > 0 for r in rows), parse_fail=bad, depth_hist=dict(sorted(dhist.items())))
    print(s, res[s])
json.dump(res, open('base_rate.json', 'w'), indent=1)
