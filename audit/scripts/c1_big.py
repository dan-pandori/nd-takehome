"""C1(d) + (a): 8x base (support-followups C) and EI s1rerun (A) on the 29 survivors, from raw rows (own code)."""
import json, glob, collections, hashlib, os
R = '/home/dan/work/claim-audit/audit/raw/'
surv = open(R + 'support-curves/data/sc/falsifier_survivors.txt').read().split()
acc = collections.defaultdict(lambda: [0, 0]); seen = collections.Counter(); md5 = {}
for f in sorted(glob.glob(R + 'support-followups/*.jsonl')):
    md5[os.path.basename(f)] = hashlib.md5(open(f, 'rb').read()).hexdigest()
    for l in open(f):
        r = json.loads(l)
        if r['name'] not in surv: continue
        sig = (r['name'], r['ckpt'], r['temperature'], r.get('sampling_seed'), r['stage'], r['n_tried'], r['n_ok'])
        seen[sig] += 1
        if seen[sig] > 1: continue
        k = (r['ckpt'].split('/')[-1], r['temperature'], r['name']); acc[k][0] += r['n_tried']; acc[k][1] += r['n_ok']
dups = sum(v - 1 for v in seen.values()); print('duplicate rows skipped', dups)
same_seed = collections.Counter((s[0], s[1], s[2], s[3]) for s in seen); print('rows sharing (name,ckpt,T,sampling_seed):', sum(v > 1 for v in same_seed.values()))
out = []
for ck in ('stage1_big_seq_s0.pt', 'stage1_big_seq_s1.pt'):
    reached = [n for n in surv if acc[(ck, 0.8, n)][1] + acc[(ck, 1.0, n)][1] > 0]
    tr = [acc[(ck, 0.8, n)][0] + acc[(ck, 1.0, n)][0] for n in surv]
    print(ck, 'reached', len(reached), reached, [(n, acc[(ck, .8, n)], acc[(ck, 1.0, n)]) for n in reached], 'attempts/thm min', min(tr), 'max', max(tr))
    low = [(n, acc[(ck, .8, n)][0], acc[(ck, 1.0, n)][0]) for n in surv if n not in reached and (acc[(ck, .8, n)][0] < 200000 or acc[(ck, 1.0, n)][0] < 200000)]
    print('  unreached with <200k at a temperature:', low)
    out.append({'ckpt': ck, 'reached': reached, 'attempts_min': min(tr)})
ck = 'la_T1_sc_s1rerun_r8.pt'
ps = sorted((acc[(ck, .8, n)][1] / acc[(ck, .8, n)][0], n) for n in surv)
print('EI s1rerun (heldout model, T0.8): solved', sum(p > 0 for p, _ in ps), 'p>=0.01', sum(p >= .01 for p, _ in ps), 'min p', ps[:3])
ck = 'stage1_a1_seq_s0.pt'
print('B base s0 T1.0 10^7:', [(n, acc[(ck, 1.0, n)]) for n in surv if acc[(ck, 1.0, n)][0]])
json.dump({'md5': md5, 'big': out}, open('/home/dan/work/claim-audit/audit/out/c1_big.json', 'w'), indent=1)
