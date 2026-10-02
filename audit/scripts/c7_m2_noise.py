"""C7 audit: re-derive lit-measures M2 replicate-vs-grid spread from raw per-item held-out eval files.
Source: ~/work/lit-measures/artifacts/lit-measures/m2/heldout_i*_d*{,_r*}.jsonl (pulled run files, branch dan_lit-measures)
depth-3 slice = held-out items with pat.depth3 true (data/p2/heldout.jsonl, md5 ae6daf49)."""
import json, glob, os, re, random, statistics as st, hashlib
W = os.path.expanduser('~/work/lit-measures')
M2 = W + '/artifacts/lit-measures/m2'
H = [json.loads(l) for l in open(W + '/data/p2/heldout.jsonl')]
d3 = {r['name'] for r in H if r['pat']['depth3']}
print('depth3 items', len(d3))
cells = {}
for f in sorted(glob.glob(M2 + '/heldout_i*_d*.jsonl')):
    tag = re.search(r'heldout_(i\d+_d\d+(?:_r\d)?)\.jsonl', f).group(1)
    ok = {}; n = 0
    for l in open(f):
        r = json.loads(l); ok[r['name']] = bool(r['solved']); n += 1
    assert n == 5000, (f, n)
    met = [json.loads(l) for l in open(M2 + f'/metrics_{tag}.jsonl')]
    steps = [m for m in met if m.get('kind') == 'step']
    host = json.load(open(f + '.args.json'))['_meta']['host']
    a = json.load(open(f + '.args.json'))
    cells[tag] = dict(d3=sum(ok[n] for n in d3) / len(d3), ov=sum(ok.values()) / 5000, val=steps[-1]['val2k'],
                      loss200=steps[0]['loss'], host=host, seed=met[0]['args']['seed'], ds=met[0]['args']['data_seed'])
grid = {k: v for k, v in cells.items() if '_r' not in k}
reps = {k: v for k, v in cells.items() if k == 'i0_d100' or '_r' in k}
print('grid', len(grid), 'reps(incl grid cell)', len(reps))
print('rep args seeds', {(v['seed'], v['ds']) for v in reps.values()})
print('rep loss@200', sorted(round(v['loss200'], 6) for v in reps.values()))
print('rep hosts', sorted({v['host'] for v in reps.values()}), 'grid hosts', sorted({v['host'] for v in grid.values()}))
out = {}
for q in ('d3', 'ov', 'val'):
    g = [v[q] for v in grid.values()]; r = [v[q] for v in reps.values()]
    vr, vg = st.variance(r), st.variance(g)
    rng = random.Random(0); B = []
    for _ in range(4000):
        rb = [rng.choice(r) for _ in r]; gb = [rng.choice(g) for _ in g]
        if st.variance(gb) > 0: B.append(st.variance(rb) / st.variance(gb))
    B.sort(); lo, hi = B[int(.025 * len(B))], B[int(.975 * len(B))]
    out[q] = dict(sd_rep=st.stdev(r), sd_grid=st.stdev(g), var_ratio=vr / vg, sd_ratio=(vr / vg) ** .5, ci_var=[lo, hi],
                  ci_sd=[lo ** .5, hi ** .5], rep_vals=[round(x, 4) for x in r], mad_rep=st.median([abs(x - st.median(r)) for x in r]),
                  mad_grid=st.median([abs(x - st.median(g)) for x in g]))
    print(f"{q}: sd_rep {out[q]['sd_rep']:.4g} sd_grid {out[q]['sd_grid']:.4g} var ratio {vr/vg:.2f} [{lo:.2f},{hi:.2f}] "
          f"sd ratio {(vr/vg)**.5:.2f} [{lo**.5:.2f},{hi**.5:.2f}]  MAD rep/grid {out[q]['mad_rep']:.4g}/{out[q]['mad_grid']:.4g}")
# robustness: drop the single outlier replicate (lowest d3)
r = sorted(v['d3'] for v in reps.values()); g = [v['d3'] for v in grid.values()]
for drop in (1, 2):
    rr = r[drop:]; print(f'd3 drop {drop} lowest reps: var ratio {st.variance(rr)/st.variance(g):.2f}  sd ratio {(st.variance(rr)/st.variance(g))**.5:.2f}')
# grid by host
byh = {}
for v in grid.values(): byh.setdefault(v['host'], []).append(v['d3'])
print({h: (len(x), round(st.mean(x), 3)) for h, x in byh.items()})
json.dump({'cells': cells, 'summary': out}, open('/home/dan/work/claim-audit/audit/out/c7_m2_noise.json', 'w'), indent=1)
