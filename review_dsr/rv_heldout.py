import sys, os, json, glob, collections, statistics, re
sys.path.insert(0, os.path.dirname(__file__))
from rv_norm import box_depth

ref = {}
for l in open('data/p2/heldout.jsonl'):
    r = json.loads(l)
    ref[r['name']] = r
DEPTH = {n: box_depth(r['proof']) for n, r in ref.items()}

rows = []
for fn in sorted(glob.glob('artifacts/dsr/*/held_*.jsonl')):
    arm, seed = re.match(r'held_(\w+?)_s(\d)\.jsonl', os.path.basename(fn)).groups()
    n = ok = 0
    bylen = collections.defaultdict(lambda: [0, 0])
    bydep = collections.defaultdict(lambda: [0, 0])
    d3_parse = d3_fail = 0
    for l in open(fn):
        r = json.loads(l)
        rr = ref[r['name']]
        d = DEPTH[r['name']]
        s = bool(r['solved'])
        n += 1; ok += s
        bylen[rr['n_lines']][0] += s; bylen[rr['n_lines']][1] += 1
        bydep[d][0] += s; bydep[d][1] += 1
        if d >= 3 and not s:
            d3_fail += 1
            if any('LEANPARSE' in x for x in r.get('reasons', [])):
                d3_parse += 1
    lo = sum(v[0] for k, v in bydep.items() if k <= 2); lon = sum(v[1] for k, v in bydep.items() if k <= 2)
    hi = sum(v[0] for k, v in bydep.items() if k >= 3); hin = sum(v[1] for k, v in bydep.items() if k >= 3)
    rows.append(dict(arm=arm, seed=int(seed), n=n, ok=ok, rate=ok / n,
                     len6=bylen[6][0] / bylen[6][1],
                     d_le2=lo / lon, d_le2_n=lon, d3=hi / hin, d3_n=hin,
                     d3_parse=d3_parse, d3_fail=d3_fail,
                     bylen={k: v[0] / v[1] for k, v in sorted(bylen.items())}))

print('arm  seed   overall   6-line   depth<=2(%d)  depth3(%d)  d3 LEANPARSE/fail' % (rows[0]['d_le2_n'], rows[0]['d3_n']))
for r in sorted(rows, key=lambda r: (r['arm'], r['seed'])):
    print('%-4s %d     %.4f    %.4f    %.4f        %.4f      %4d/%4d' %
          (r['arm'], r['seed'], r['rate'], r['len6'], r['d_le2'], r['d3'], r['d3_parse'], r['d3_fail']))

print('\nby ND length')
print('arm  seed ' + ' '.join('%6d' % L for L in range(2, 7)))
for r in sorted(rows, key=lambda r: (r['arm'], r['seed'])):
    print('%-4s %d    ' % (r['arm'], r['seed']) + ' '.join('%6.3f' % r['bylen'][L] for L in range(2, 7)))

print('\nsweep summary (mean +- sd over available seeds)')
for arm in ['c0', 'r1', 'r2', 'r3', 'r4']:
    rs = [r for r in rows if r['arm'] == arm]
    if not rs:
        continue
    d3 = [r['d3'] for r in rs]; le2 = [r['d_le2'] for r in rs]; ov = [r['rate'] for r in rs]
    sd = statistics.stdev(d3) if len(d3) > 1 else float('nan')
    print('%-4s n=%d  depth3 mean %.4f sd %.4f  [%s]   depth<=2 mean %.4f   overall mean %.4f'
          % (arm, len(rs), statistics.mean(d3), sd, ' '.join('%.3f' % x for x in d3),
             statistics.mean(le2), statistics.mean(ov)))

# E20: Spearman between depth-3 rate and depth-3 LEANPARSE count over all models
def spearman(a, b):
    def rank(x):
        s = sorted(range(len(x)), key=lambda i: x[i])
        r = [0] * len(x)
        for j, i in enumerate(s):
            r[i] = j
        return r
    ra, rb = rank(a), rank(b)
    n = len(a)
    return 1 - 6 * sum((ra[i] - rb[i]) ** 2 for i in range(n)) / (n * (n * n - 1))

sw = [r for r in rows if r['arm'] != 'r1']
print('\nE20 Spearman(depth-3 rate, depth-3 LEANPARSE count) over %d models: %.3f'
      % (len(sw), spearman([r['d3'] for r in sw], [r['d3_parse'] for r in sw])))
allr = rows
print('     over all %d models incl. r1: %.3f'
      % (len(allr), spearman([r['d3'] for r in allr], [r['d3_parse'] for r in allr])))
