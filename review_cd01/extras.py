#!/usr/bin/env python3
"""Reviewer (coe-dose01): the smaller checks behind numbers quoted in review_coe-dose01.md, in one place
(previously run ad hoc).  Writes out/extras.json and prints a log.
  * pretraining-set composition (own σ predicate: DN citing, after reiteration, a NEGI line) and the dose overlap
  * σ records among the replay records of every 0.1 % mix
  * σ-covered trained targets (strict_trained) per round, knockout s1's contraposition_conv training share
  * share of x due to replay (ourruns' rl_only variant), knockout s1 x at r24 incl. its fine-tune
  * full s5 x with the bucket's round files vs without prefill (the extraction's situation)
  * full-arm per-seed crossings (rl_curve.json), crossing-x Mann-Whitney 0.1 % vs 1 %
  * slowdown excess pod-hours (the executor's method), knockout round seconds, Stage-1 md5s, the numbers.md example
"""
import collections, glob, itertools, json, statistics as st, sys
sys.path.insert(0, '/home/dan/work/coe-dose01/review_cd01')
from common import BIG, REPO, jl
from reductio import parse_nd, origin
from flops import reg, ladder_cells, stage1_D

W = '/home/dan/work'
C = f'{W}/create-or-elicit/data/coe'
out = {}


def sigma(nd):
    L = parse_nd(nd)
    if L is None:
        return False
    by = {l['idx']: l for l in L}
    for l in L:
        if l['rule'] == 'DN' and l['refs']:
            o = origin(by, l['refs'][0])
            if o is not None and o['rule'] == 'NEGI':
                return True
    return False


# 1. composition
sets = {n: collections.Counter((x['prompt'], x['proof']) for x in jl(f'{C}/{f}')) for n, f in
        (('dose01', 'train_k12dose01.jsonl.gz'), ('ko', 'train_k12ko.jsonl.gz'), ('dose1', 'train_k12dose1.jsonl.gz'))}
comp = {n: dict(records=sum(s.values()), sigma=sum(v for (p, nd), v in s.items() if ': DN ' in nd and sigma(nd))) for n, s in sets.items()}
add01 = sets['dose01'] - sets['ko']; rem01 = sets['ko'] - sets['dose01']; add1 = sets['dose1'] - sets['ko']
comp['dose01_minus_ko'] = sum(add01.values()); comp['ko_minus_dose01'] = sum(rem01.values())
comp['added_sigma'] = sum(v for (p, nd), v in add01.items() if sigma(nd))
comp['dose1_minus_ko'] = sum(add1.values()); comp['shared_added_0.1_and_1'] = sum((add01 & add1).values())
out['composition'] = comp
print('composition:', comp)
# the three 0.1 % ladders' train file
out['train_files'] = {S: json.load(open(f'{REPO}/artifacts/coe/ladder/la_dose01_s{S}/args.json'))['train'] for S in range(3)}
print('train files:', out['train_files'])

# 2. replay sigma per round
tg = {x['prompt'] for x in jl(f'{REPO}/data/ladder/rl_targets.jsonl')}
rep = {}
for S in range(3):
    per = []
    for r in range(1, 17):
        n_rep = n_sig = 0
        for x in jl(f'{BIG}/mix/dose01_s{S}_{r}.jsonl.gz'):
            if x['prompt'] in tg:
                continue
            n_rep += 1
            n_sig += ': DN ' in x['proof'] and sigma(x['proof'])
        per.append((r, n_rep, n_sig))
    sig = [c for _, _, c in per]
    rep[f's{S}'] = dict(replay_records=sorted({b for _, b, _ in per}), sigma_per_round=sig, mean=round(st.mean(sig), 2), min=min(sig), max=max(sig))
    print(f'replay σ s{S}:', rep[f's{S}'])
out['replay_sigma'] = rep

# 3. σ-covered trained targets
fam = json.load(open(f'{REPO}/data/coe/families.json'))
tr = {f: set(d['strict_trained']) for f, d in fam['families'].items() if d['classical']}
sig_tr = set().union(*tr.values())
acc = lambda tag, r: json.load(open(f'{BIG}/alloc/{tag}_{r}.json'))['accepted']
out['sigma_targets'] = {f'dose01_s{S}': [sum(1 for t in sig_tr if acc(f'dose01_s{S}', r).get(t, 0) > 0) for r in range(1, 17)] for S in range(3)}
out['sigma_targets']['ko_s1_r24_32'] = [sum(1 for t in sig_tr if acc('ko_s1', r).get(t, 0) > 0) for r in range(24, 33)]
prev = acc('ko_s1', 24); sh = []
for r in range(25, 33):
    a = acc('ko_s1', r)
    succ = {t for t, v in a.items() if v - prev.get(t, 0) > 0}
    sh.append(round(len(succ & tr['contraposition_conv']) / len(tr['contraposition_conv']), 4)); prev = a
out['ko_s1_cc_share_r25_32'] = sh
print('σ-covered trained targets:', out['sigma_targets'], 'ko cc share', sh)

# 4. replay share of x; knockout r24 incl. fine-tune
F = json.load(open(f'{REPO}/review_cd01/out/flops.json'))
red = {}
for lad in ('la_dose01_s0', 'la_dose01_s1', 'la_dose01_s2', 'la_dose1_s0', 'la_dose1_s1', 'la_dose1_s2', 'la_ko_s1'):
    tot = only = 0.0
    for q in F[lad]['rows']:
        s = 2 * (q['gen_sample'] + q['prefill'] * q['gen_sample'] / (q['gen_sample'] + q['gen_eval']))
        tot += s + 6 * q['ft_tokens']; only += s + 6 * q['ft_tokens'] * q['mix_rl'] / (q['mix_rl'] + 20000)
    red[lad] = round(100 * (1 - only / tot), 2)
out['replay_share_of_x_pct'] = red
r24 = next(q for q in F['la_ko_s1']['rows'] if q['round'] == 24)
out['ko_s1_x_r24'] = dict(after_sampling=round(r24['x'], 4), incl_ft=round(r24['x'] + r24['ft_tokens'] / F['la_ko_s1']['D'][-1], 4))
print('replay share of x (%):', red, '| ko s1 r24:', out['ko_s1_x_r24'])

# 5. full s5 with / without prefill
rows = reg('create-or-elicit'); cells = ladder_cells(rows, 'la_full_s5'); D = stage1_D(rows, 'ckpts/coe/stage1_full_s5.pt')[-1]
cw = cn = 0.0; xs = []
for r in range(1, 17):
    g = cells[('sample', r, 'gen_tokens')][-1][0]; e = cells.get(('eval', r, 'gen_tokens'), [(0, None)])[-1][0]
    f = cells.get(('ft', r, 'train_tokens'), [(0, None)])[-1][0]
    pre = json.load(open(f'{BIG}/full_s5/round_{r}.json'))['env']['prompt_tokens']
    cw += 2 * (g + pre * g / (g + e)); cn += 2 * g
    xs.append((r, round(cw / (6 * D), 4), round(cn / (6 * D), 4)))
    cw += 6 * f; cn += 6 * f
out['full_s5'] = dict(with_prefill_r1=xs[0][1], with_prefill_r16=xs[-1][1], incl_ft_with=round(cw / (6 * D), 4),
                      without_prefill_r1=xs[0][2], without_prefill_r16=xs[-1][2], incl_ft_without=round(cn / (6 * D), 4))
RC = {o['name']: o for o in json.load(open(f'{REPO}/rl_needed/rl_curve.json'))}
out['full_s5']['rl_curve_r1_r16_inclft'] = (RC['la_full_s5']['rounds'][0]['x_train'], RC['la_full_s5']['rounds'][-1]['x_train'], RC['la_full_s5']['x_train_total_incl_last_ft'])
out['full_siblings_r16'] = {n: round(RC[n]['rounds'][-1]['x_train'], 3) for n in ('la_full_s3', 'la_full_s4', 'old_full_s0', 'old_full_s1', 'old_full_s2')}
print('full s5:', out['full_s5'], '| siblings r16:', out['full_siblings_r16'])

# 6. full-arm crossings; crossing-x MW
fc = {}
for n, o in RC.items():
    if o['arm'] == 'full':
        c = next((q for q in o['rounds'] if q['heldout_cum'] >= 14), None)
        fc[n] = dict(y_r1=o['rounds'][0]['heldout_cum'], cross_round=c['round'] if c else None, cross_x=round(c['x_train'], 3) if c else None)
out['full_crossings'] = fc
print('full crossings:', fc)
a = [0.6898, 1.3726, 2.5764]; b = [0.3870, 0.4053, 0.7289]
U = lambda x, y: sum((u > v) + 0.5 * (u == v) for u in x for v in y)
u0 = U(a, b); allv = a + b; n = c = 0
for idx in itertools.combinations(range(6), 3):
    x = [allv[i] for i in idx]; y = [allv[i] for i in range(6) if i not in idx]; n += 1; c += U(x, y) >= u0
out['crossing_x_mw_dose01_gt_dose1'] = c / n
print('crossing-x MW p:', c / n)

# 7. slowdown, round seconds, md5s, example
def secs(lad, r):
    import os
    d = f'{REPO}/artifacts/coe/ladder' if os.path.exists(f'{REPO}/artifacts/coe/ladder/{lad}/round_{r}.json') else f'{W}/create-or-elicit/artifacts/coe/ladder'
    return json.load(open(f'{d}/{lad}/round_{r}.json'))['secs']
slow = {}
for lad, rr in (('la_dose01_s0', (12, 13)), ('la_dose01_s1', (11,)), ('la_dose01_s2', (10, 11)), ('la_ko_s1', (32,))):
    ex = sum(secs(lad, r) - st.median([secs(lad, r - k) for k in (1, 2, 3) if r - k not in rr]) for r in rr)
    slow[lad] = round(ex / 3600, 3)
out['slowdown_excess_h'] = slow; out['slowdown_total_h'] = round(sum(slow.values()), 3)
out['ko_round_secs_r25_32'] = [round(secs('la_ko_s1', r)) for r in range(25, 33)]
rr = [json.loads(l) for f in sorted(glob.glob(f'{REPO}/artifacts/coe-dose01/registry/*.jsonl')) for l in open(f)]
out['stage1_md5'] = sorted({(r['ckpt'], r['ckpt_md5'][:8]) for r in rr if r.get('role') == 'stage1' and r['metric'] == 'ckpt_saved'})
y1 = json.load(open(f'{REPO}/review_cd01/out/y_la_dose01_s1.json'))['first_round_strict']
out['example_la_transfer_400'] = dict(first_round_s1=y1.get('la_transfer_400'), members_first_at_r6=sum(1 for v in y1.values() if v == 6))
print('slowdown h:', slow, out['slowdown_total_h'], '| ko secs', out['ko_round_secs_r25_32'], '| md5', out['stage1_md5'], '| example', out['example_la_transfer_400'])
json.dump(out, open(f'{REPO}/review_cd01/out/extras.json', 'w'), indent=1)
