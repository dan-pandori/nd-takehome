"""C2(e)/C1 cross-run pairs (own code).
(1) SN base s0 (ec3888d9) on the 29: support-state H (T0.8 phase) vs support-state S1 (k 10,000, T0.8): per-theorem z.
(2) state-env frozen ladder (k 32 x 8 rounds = 256 attempts/theorem, T0.8) found_transfer_8 vs H/state-readouts p08:
    expected #reached = sum 1-(1-p)^256 vs observed, for SN s0/s1, S s0/s1.
(3) C1: WP base s1 (fc27e52d) support-curves s3 vs support-followups A re-draw on 383 theorems."""
import json, glob, math, collections, hashlib
R = '/home/dan/work/claim-audit/audit/raw/'
surv = open(R + 'support-curves/data/sc/falsifier_survivors.txt').read().split()
rc = json.load(open('/home/dan/work/claim-audit/audit/out/c2_recount.json'))['table']
def rows(f):
    for l in open(f): yield json.loads(l)
def z2(k1, n1, k2, n2):
    p = (k1 + k2) / (n1 + n2)
    if p in (0, 1): return 0.0
    return (k1 / n1 - k2 / n2) / math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
s1 = {r['name']: (r['n_tried'], r['n_ok'], r.get('sampling_seed')) for r in rows(R + 'support-state/S1_base_T08_s0.s0.jsonl') if r['name'] in surv}
print('(1) SN s0 H(T0.8) vs S1(k10k): S1 sampling seeds', {v[2] for v in s1.values()}, 'H seeds 1/2')
zs = []; reachedS1 = 0
for n in surv:
    hn, hk = rc['SN_s0']['acc'][n]['0.8']; sn, sk = s1[n][0], s1[n][1]
    zs.append((z2(hk, hn, sk, sn), n, hk, hn, sk, sn)); reachedS1 += sk > 0
big = [z for z in zs if abs(z[0]) > 3]
print(f'  S1 reached {reachedS1}/29 at <=10k; |z|>3 on {len(big)} of 29 (two-proportion; note both arms stop early, ok/tried biased up slightly):', [(z[1][12:], round(z[0], 1), f'{z[2]}/{z[3]}', f'{z[4]}/{z[5]}') for z in big])
print('  |z|>2:', sum(abs(z[0]) > 2 for z in zs))
print('(2) state-env frozen ladder 256 attempts vs H p08')
for lab, f in [('SN_s0', 'SN_s0'), ('SN_s1', 'SN_s1'), ('S_s0', 'S_s0'), ('S_s1', 'S_s1')]:
    found = {r['name'] for r in rows(R + f'state-env/{f}_found_transfer_8.jsonl')}
    acc = rc[lab]['acc']
    p = {n: acc[n]['0.8'][1] / acc[n]['0.8'][0] for n in surv}
    exp = sum(1 - (1 - p[n]) ** 256 for n in surv); var = sum((1 - (1 - p[n]) ** 256) * (1 - p[n]) ** 256 for n in surv)
    obs = sum(n in found for n in surv)
    odd = [n[12:] for n in surv if n in found and p[n] < 1e-3]
    print(f'  {lab}: observed {obs}/29 reached in 256, expected {exp:.1f} +- {math.sqrt(var):.1f}; reached in ladder though p08<1e-3: {odd}')
print('(3) WP base s1: support-curves s3 vs support-followups A')
a = {r['name']: (r['n_tried'], r['n_ok']) for r in rows(R + 'support-followups/a_base_T08_s1.s0.jsonl')}
b = collections.defaultdict(lambda: [0, 0])
for f in glob.glob(R + 'support-curves/artifacts/sc/s3_base_T08_s1.*.jsonl'):
    for r in rows(f): b[r['name']][0] += r['n_tried']; b[r['name']][1] += r['n_ok']
sa = {n for n in a if a[n][1]}; sb = {n for n in b if b[n][1]}
agree = sum((n in sa) == (n in sb) for n in a)
zz = [z2(a[n][1], a[n][0], b[n][1], b[n][0]) for n in a if a[n][1] or b[n][1]]
print(f'  solved A {len(sa)} vs sc {len(sb)}; agreement {agree}/{len(a)}; |z|>3 on {sum(abs(x) > 3 for x in zz)} of {len(zz)} solved-by-either; on survivors A solves {sorted(x[12:] for x in sa & set(surv))}, sc solves {sorted(x[12:] for x in sb & set(surv))}')
