#!/usr/bin/env python3
"""Reviewer recount of Phase 0.2 for the old full seeds (M12 s0-s2, r8):
  * K_train(8) and the uniform K_eval-set from trajectory's registry rows (r1-r8 on RTX A6000; sample / eval / ladder
    finetune rows + the fine-tune child state_train.py rows), converted to A40 seconds at A6000 / A40 = 0.932 (the
    replica's ratio, recounted below from this run's replica rows and trajectory's round-1 rows), divided by 322 x the
    seed's A40 per-attempt cost at batch 2,048 (artifacts/coe/timing/A40_pend_s<S>_b2048.json);
  * the compute-matched r8 set at each allocation, from the reviewer's OWN capability-defs outputs
    (~/review/capability-defs/review_cd/out_sets.json: eqk r8 x0 = r8 x0 solves that pend x0 fails;
    out_bracket.json: pooled pend attempts per theorem): cm(K) = eqk and pooled n >= K and c / n < 1 / K;
    undetermined = eqk with c = 0 and n < K; cm0 = eqk with 0 successes in >= 66,304."""
import collections, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

RV = C.RV
reg = []
for f in sorted(glob.glob(os.path.expanduser('~/work/trajectory/artifacts/trajectory/registry/*.jsonl'))):
    reg += list(C.rows(f))
ph = collections.defaultdict(float)
for r in reg:
    if r['metric'] != 'gpu_seconds':
        continue
    lab = r.get('labels') or {}; cfg = r.get('config') or {}
    m = re.match(r'la_T1_best12_s(\d)$', str(r.get('arm')))
    if m and r.get('script') == 'state_ladder_ei.py' and lab.get('round') and lab['round'] <= 8:
        ph[(int(m.group(1)), lab['phase'])] += r['value']
        if lab['round'] == 1 and lab['phase'] == 'sample':
            ph[(int(m.group(1)), 'r1_sample')] += r['value']
    m2 = re.match(r'ckpts/tj/ladder/la_T1_best12_s(\d)_r(\d+)\.pt$', cfg.get('out') or '')
    if m2 and r.get('script') == 'state_train.py' and int(m2.group(2)) <= 8:
        ph[(int(m2.group(1)), 'child')] += r['value']
# replica (this run's registry): round-1 sample on an A40
rep = {}
for f in sorted(glob.glob(f'{RV}/artifacts/create-or-elicit/registry/*.jsonl')):
    for r in C.rows(f):
        m = re.match(r'rep_best12_s(\d)$', str(r.get('arm')))
        if m and r['metric'] == 'gpu_seconds' and (r.get('labels') or {}).get('phase') == 'sample':
            rep[int(m.group(1))] = r['value']
ratios = {s: ph[(s, 'r1_sample')] / rep[s] for s in rep}
print('round-1 sample seconds A6000 (trajectory) / A40 (replica):', {s: (round(ph[(s, 'r1_sample')], 1), round(rep[s], 1), round(v, 3)) for s, v in ratios.items()},
      'mean', round(sum(ratios.values()) / len(ratios), 4))
for s in (0, 1):
    rr = json.load(open(f'{RV}/artifacts/coe/replica/rep_best12_s{s}/round_1.json'))
    print(f'   replica s{s} round 1: targets solved {rr["targets_cum"]["solved"]}')
CONV = 0.932
cost = {s: float(json.load(open(f'{RV}/artifacts/coe/timing/A40_pend_s{s}_b2048.json'))['wall_s']) / (322 * 256) for s in (0, 1, 2)}
K = {}
for s in (0, 1, 2):
    a40 = lambda x: x / CONV
    ktr = a40(ph[(s, 'sample')] + ph[(s, 'finetune')] + ph[(s, 'child')]) / (322 * cost[s])
    kuni = a40(ph[(s, 'sample')] + ph[(s, 'finetune')] + ph[(s, 'child')] + ph[(s, 'eval')]) / (322 * cost[s])
    K[s] = {'K_att': 8 * 4495 * 32 / 322, 'K_train': ktr, 'K_uni': kuni, 'K_pub': {0: 19281, 1: 21107, 2: 23310}[s],
            'K_adapt(executor)': {0: 44570, 1: 43427, 2: 56509}[s]}
    print(f's{s}: A6000 r1-8 sample {ph[(s, "sample")]:,.0f} eval {ph[(s, "eval")]:,.0f} ladder-ft {ph[(s, "finetune")]:,.0f} ft-child {ph[(s, "child")]:,.0f} s; '
          f'A40 cost {1e3 * cost[s]:.3f} ms -> K_train(8) {ktr:,.0f}, K_uni(8) {kuni:,.0f}')
S = json.load(open(os.path.expanduser('~/review/capability-defs/review_cd/out_sets.json')))
B = json.load(open(os.path.expanduser('~/review/capability-defs/review_cd/out_bracket.json')))
out = {}
for s in (0, 1, 2):
    E = S['eqk'][f's{s}_r8_x0']; ps = B[str(s)]['ps']
    row = {}
    for nm, k in K[s].items():
        cm = [n for n in E if ps[n][1] >= k and ps[n][0] / ps[n][1] < 1 / k]
        und = [n for n in E if ps[n][1] < k and ps[n][0] == 0]
        row[nm] = (round(k), len(cm), len(und))
    cm0 = [n for n in E if ps[n][0] == 0 and ps[n][1] >= 66304]
    allK = [n for n in E if all(ps[n][1] >= k and ps[n][0] / ps[n][1] < 1 / k for k in K[s].values())]
    out[s] = {'eqk': len(E), 'sets': row, 'cm0_66304': len(cm0), 'in_all_five': len(allK)}
    print(f's{s}: eqk r8 x0 {len(E)}; cm (K, size, undetermined): ' + '; '.join(f'{k} {v}' for k, v in row.items()) +
          f'; 0 successes in >= 66,304: {len(cm0)}; compute-matched at all five: {len(allK)}')
json.dump({'K': K, 'sets': out}, open(f'{RV}/review_coe/out_budget08.json', 'w'), indent=1)
