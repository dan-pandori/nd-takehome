"""C1: recount support-curves survivors from raw per-theorem records (own code).
Inputs: audit/raw/support-curves/artifacts/sc/*.jsonl (bucket support-curves/artifacts/sc/)."""
import json, glob, collections, hashlib, os, math
R = '/home/dan/work/claim-audit/audit/raw/support-curves/'
surv = open(R + 'data/sc/falsifier_survivors.txt').read().split()
thm = {json.loads(l)['name']: json.loads(l) for l in open(R + 'data/sc/theorems.jsonl')}
# acc[(model_ckpt, T, stagegroup)][name] = [tried, ok]
acc = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
md5 = {}
for f in sorted(glob.glob(R + 'artifacts/sc/s*.jsonl')):
    if 'secondary' in f: continue
    md5[os.path.basename(f)] = hashlib.md5(open(f, 'rb').read()).hexdigest()
    for l in open(f):
        r = json.loads(l)
        st = r['stage']
        key = (r['ckpt'].split('/')[-1], r['temperature'], 'stage1' if st in ('s1', 's3') else 'stage2+')
        a = acc[key][r['name']]; a[0] += r['n_tried']; a[1] += r['n_ok']
        b = acc[(r['ckpt'].split('/')[-1], r['temperature'], 'all')][r['name']]; b[0] += r['n_tried']; b[1] += r['n_ok']
B = 'stage1_a1_seq_s0.pt'; E = 'la_T1_sc_s0_r8.pt'; E1 = 'la_T1_sc_s1_r8.pt'; B1 = 'stage1_a1_seq_s1.pt'
rows = []
for n in surv:
    b8 = acc[(B, 0.8, 'all')][n]; b10 = acc[(B, 1.0, 'all')][n]
    e8 = acc[(E, 0.8, 'stage1')][n]; e10 = acc[(E, 1.0, 'all')][n]; es1 = acc[(E1, 0.8, 'stage1')][n]
    b1 = acc[(B1, 0.8, 'stage1')][n]
    rows.append((n, thm[n]['L_true'], b8[0], b8[1], b10[0], b10[1], e8[0], e8[1], e10[0], e10[1], es1[0], es1[1], b1[0], b1[1]))
hdr = 'name Ltrue base_T08_tried base_T08_ok base_T10_tried base_T10_ok EIs0_T08_tried EIs0_T08_ok EIs0_T10_tried EIs0_T10_ok EIs1lost_T08_tried EIs1lost_T08_ok bases1_tried bases1_ok'.split()
with open('/home/dan/work/claim-audit/audit/out/c1_survivors.tsv', 'w') as fo:
    fo.write('\t'.join(hdr) + '\n')
    for r in rows: fo.write('\t'.join(map(str, r)) + '\n')
print('\t'.join(['name', 'L', 'b08', 'b08ok', 'b10', 'b10ok', 'pEI08', 'pEI10(heldout)', 'pEIs1lost', 'bs1ok']))
for r in rows:
    print(r[0][12:], r[1], r[2], r[3], r[4], r[5], f'{r[7]/max(r[6],1):.4f}({r[7]}/{r[6]})', f'{r[9]/max(r[8],1):.4f}({r[9]}/{r[8]})' if r[8] else 'NA', f'{r[11]/max(r[10],1):.4f}', r[13], sep='\t')
print('survivors', len(rows), 'base total attempts min/max', min(r[2] + r[4] for r in rows), max(r[2] + r[4] for r in rows), 'base ok sum', sum(r[3] + r[5] for r in rows))
print('EI s0 T0.8 p>=0.01:', sum(r[7] / r[6] >= 0.01 for r in rows), ' EI s0 T1.0 heldout rows:', sum(1 for r in rows if r[8]), ' heldout p>=0.01:', sum(1 for r in rows if r[8] and r[9] / r[8] >= 0.01), ' heldout >=1 success:', sum(1 for r in rows if r[9] > 0))
# Re-derive survivor set from scratch: forward crux = base s0 stage1 0 & EI s0 stage1 >=1;
cand = [n for n in thm if acc[(B, 0.8, 'stage1')][n][1] == 0 and acc[(E, 0.8, 'stage1')][n][1] > 0]
for depth in (40000, 200000):
    s = [n for n in cand if acc[(B, 0.8, 'all')][n][1] == 0 and acc[(B, 1.0, 'all')][n][1] == 0 and acc[(B, 0.8, 'all')][n][0] >= depth and acc[(B, 1.0, 'all')][n][0] >= depth and acc[(E, 0.8, 'stage1')][n][1] / acc[(E, 0.8, 'stage1')][n][0] >= 0.01]
    print('forward crux', len(cand), f'survivors at >= {depth}/temp:', len(s), 'match file' if set(s) == set(surv) else f'diff {sorted(set(s) ^ set(surv))[:10]}')
json.dump(md5, open('/home/dan/work/claim-audit/audit/out/c1_recount_md5.json', 'w'), indent=0)
