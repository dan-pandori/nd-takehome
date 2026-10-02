"""C2: survivors reached by state bases (SN: support-state H; S/SH: state-readouts H), recounted (own code) from
(1) per-theorem rows and (2) independently from the Lean-gate dumps (every judged literal text + lean_ok)."""
import json, glob, gzip, collections, hashlib, os, sys, statistics
sys.path.insert(0, os.path.dirname(__file__)); from canon import canon
R = '/home/dan/work/claim-audit/audit/raw/'
surv = open(R + 'support-curves/data/sc/falsifier_survivors.txt').read().split()
th = {json.loads(l)['name']: json.loads(l) for l in open(R + 'support-curves/data/sc/theorems.jsonl')}
bycanon = {}
for n in surv: bycanon.setdefault(canon(th[n]['thm']), []).append(n)
assert all(len(v) == 1 for v in bycanon.values())
byprompt = {th[n]['prompt']: n for n in surv}
ARMS = {('SN', 0): 'support-state/H_base_T{T}_s0.s0.jsonl', ('SN', 1): 'support-state/H_base_T{T}_s1.s0.jsonl',
        ('S', 0): 'state-readouts/H_S_T{T}_s0.s0.jsonl', ('S', 1): 'state-readouts/H_S_T{T}_s1.s0.jsonl',
        ('SH', 0): 'state-readouts/H_SH_T{T}_s0.s0.jsonl', ('SH', 1): 'state-readouts/H_SH_T{T}_s1.s0.jsonl'}
DUMPS = {('SN', 0): 'support-state/dump/H_base_T{T}_s0.jsonl.gz', ('SN', 1): 'support-state/dump/H_base_T{T}_s1.jsonl.gz',
         ('S', 0): 'state-readouts/dump/H_S_T{T}_s0.jsonl.gz', ('S', 1): 'state-readouts/dump/H_S_T{T}_s1.jsonl.gz'}
md5 = {}; table = {}; out = []
print('arm seed | reached rows | reached dumps | at T0.8 (rows) | attempts total | attempts/thm median (max) | median p08 | ckpt md5 | sampling seeds | trunc_action')
for (arm, s), pat in ARMS.items():
    acc = collections.defaultdict(lambda: {0.8: [0, 0], 1.0: [0, 0]}); ck = set(); seeds = set(); trunc = [0, 0]; dup = collections.Counter()
    for T in ('08', '10'):
        f = R + pat.format(T=T)
        md5[f] = hashlib.md5(open(f, 'rb').read()).hexdigest()
        for l in open(f):
            r = json.loads(l)
            sig = (r['name'], r['temperature'], r.get('sampling_seed'), r['n_tried'], r['n_ok']); dup[sig] += 1
            if dup[sig] > 1: continue
            a = acc[r['name']][r['temperature']]; a[0] += r['n_tried']; a[1] += r['n_ok']
            ck.add(r['ckpt_md5'][:8]); seeds.add(r.get('sampling_seed')); trunc[0] += r.get('n_trunc_action', 0); trunc[1] += r['n_tried']
    reached = {n for n in surv if acc[n][0.8][1] + acc[n][1.0][1] > 0}
    r08 = {n for n in surv if acc[n][0.8][1] > 0}
    att = [acc[n][0.8][0] + acc[n][1.0][0] for n in surv]
    p08 = statistics.median(acc[n][0.8][1] / acc[n][0.8][0] if acc[n][0.8][0] else 0 for n in surv)
    dreached = None
    if (arm, s) in DUMPS:
        dreached = set(); ntxt = 0
        for T in ('08', '10'):
            f = R + DUMPS[(arm, s)].format(T=T); md5[f] = hashlib.md5(open(f, 'rb').read()).hexdigest()
            with gzip.open(f, 'rt') as fh:
                for l in fh:
                    d = json.loads(l); ntxt += 1
                    if d.get('lean_ok') is True:
                        n = byprompt.get(d['prompt']) or (bycanon.get(canon(d['prompt'])) or [None])[0]
                        if n: dreached.add(n)
    table[(arm, s)] = {'reached': sorted(reached), 'acc': {n: acc[n] for n in surv}}
    print(arm, s, '|', len(reached), '|', len(dreached) if dreached is not None else '-', ('(agree)' if dreached == reached else f'(DIFF {sorted(dreached ^ reached)})') if dreached is not None else '', '|', len(r08), '|', sum(att), '|', sorted(att)[14], max(att), '|', f'{p08:.4g}', '|', ck, '|', seeds, '|', f'{trunc[0]/max(trunc[1],1):.4%}')
    print('   unreached:', sorted(set(surv) - reached))
json.dump({'md5': md5, 'table': {f'{a}_s{s}': v for (a, s), v in table.items()}}, open('/home/dan/work/claim-audit/audit/out/c2_recount.json', 'w'))
# per-theorem paired p08 S vs SN, same seed
for s in (0, 1):
    pairs = [(table[('S', s)]['acc'][n][0.8], table[('SN', s)]['acc'][n][0.8]) for n in surv]
    ratio = [ (a[1]/a[0]) / (b[1]/b[0]) for a, b in pairs if a[1] and b[1]]
    print(f'seed {s}: S vs SN per-theorem p08 ratio (both>0, n={len(ratio)}): median {statistics.median(ratio):.3g}; S>SN on', sum(r > 1 for r in ratio))
