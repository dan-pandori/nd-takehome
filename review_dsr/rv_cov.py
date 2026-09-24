import sys, os, json, glob, collections, re
sys.path.insert(0, os.path.dirname(__file__))
from rv_norm import norm_proof, nd_len, box_depth

POOLS = {'d3': 'data/p2/targets_depth3.jsonl',
         'd3req': 'data/r3_1/depth3_req.jsonl',
         'red': 'data/p2/targets_reductio_req.jsonl'}
pools = {}
for k, fn in POOLS.items():
    pools[k] = {json.loads(l)['name']: json.loads(l) for l in open(fn)}

rows = []
for fn in sorted(glob.glob('artifacts/dsr/*/cov_*.s0.jsonl')):
    m = re.match(r'cov_(d3req|d3|red)_(\w+?)_s(\d)\.s0\.jsonl', os.path.basename(fn))
    pool, arm, seed = m.groups()
    n = hit = 0; tried = ok = 0
    deep = set(); deepthm = set(); long8 = set()
    bystrat = collections.defaultdict(lambda: [0, 0])
    for l in open(fn):
        r = json.loads(l); n += 1
        s = r['n_ok'] > 0
        hit += s
        tried += r['n_tried']; ok += r['n_ok']
        ub = pools[pool][r['name']].get('min_lines_ub')
        bystrat[ub][0] += s; bystrat[ub][1] += 1
        for p in r.get('proofs', []):
            pf = p['proof']
            if box_depth(pf) >= 3:
                deep.add((r['name'], norm_proof(pf))); deepthm.add(r['name'])
            if nd_len(pf) >= 8:
                long8.add((r['name'], norm_proof(pf)))
    rows.append(dict(pool=pool, arm=arm, seed=int(seed), n=n, hit=hit, rate=hit / n,
                     samp=ok / tried, deep=len(deep), deepthm=len(deepthm), long8=len(long8),
                     strat={k: (v[0], v[1]) for k, v in sorted(bystrat.items(), key=lambda kv: (kv[0] is None, kv[0]))}))

for pool in ['d3', 'd3req', 'red']:
    rs = [r for r in rows if r['pool'] == pool]
    if not rs:
        continue
    print('=== pool %s (%s, n=%d), pass@2000, sampler batch 2048 T0.8' % (pool, POOLS[pool], rs[0]['n']))
    print('arm seed   hit    rate    per-sample   depth>=3 thms  distinct depth>=3  distinct >=8-line')
    for r in sorted(rs, key=lambda r: (r['arm'], r['seed'])):
        print('%-3s  %d   %5d  %.4f   %.5f      %8d       %10d         %10d' %
              (r['arm'], r['seed'], r['hit'], r['rate'], r['samp'], r['deepthm'], r['deep'], r['long8']))
    print()
print('hits by min_lines_ub stratum, pool d3req')
for r in sorted([r for r in rows if r['pool'] == 'd3req'], key=lambda r: (r['arm'], r['seed'])):
    print('%-3s %d  %s' % (r['arm'], r['seed'], '  '.join('%s:%d/%d' % (k, v[0], v[1]) for k, v in r['strat'].items())))
print()
print('ratios to C0 at the same seed')
c0 = {(r['pool'], r['seed']): r for r in rows if r['arm'] == 'c0'}
for r in sorted(rows, key=lambda r: (r['pool'], r['arm'], r['seed'])):
    if r['arm'] == 'c0':
        continue
    b = c0[(r['pool'], r['seed'])]
    print('%-6s %-3s s%d  hit %4d vs %4d   x%.2f   %+.1f pp' %
          (r['pool'], r['arm'], r['seed'], r['hit'], b['hit'], r['hit'] / max(1, b['hit']),
           100 * (r['rate'] - b['rate'])))
