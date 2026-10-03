#!/usr/bin/env python3
"""Reviewer recount (mcts-a), part 1, written for this review: per-job solved counts from the per-theorem jsonl,
group C rebuilt from trajectory's per-theorem k 256 files (bucket), the gate, budget matching, truncation, tuning.
Reads only raw per-job files (eval/*.jsonl, per-job *.json for budget / wall / cfg); not summary.json / analysis.md.
Output: r1_counts.json"""
import json, os, glob, collections, re
W = os.path.expanduser('~/review/mcts-a'); E = f'{W}/artifacts/mcts'; TJ = os.path.join(os.path.dirname(__file__), 'tj')
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
out = {}

# ---- group C from trajectory: tb72 + h250, unsolved by pend and r8 at k 256 sample seed 0
def tjsolved(s, c, p, x):
    return {r['name']: bool(r['solved']) for r in rd(f'{TJ}/s{s}_{c}__{p}_x{x}.jsonl')}
gc = {}
for s in range(3):
    C = set()
    for p in ('tb72', 'h250'):
        a, b = tjsolved(s, 'pend', p, 0), tjsolved(s, 'r8', p, 0)
        assert set(a) == set(b)
        C |= {n for n in a if not a[n] and not b[n]}
    mine = {r['name'] for r in rd(f'{W}/data/mcts/groupC_s{s}.jsonl')}
    r8x1 = {**tjsolved(s, 'r8', 'tb72', 1), **tjsolved(s, 'r8', 'h250', 1)}
    pex1 = {**tjsolved(s, 'pend', 'tb72', 1), **tjsolved(s, 'pend', 'h250', 1)}
    gc[s] = dict(n_mine=len(C), n_file=len(mine), equal=C == mine,
                 tj_r8_x1_solved_on_C=sum(r8x1[n] for n in C), tj_pend_x1_solved_on_C=sum(pex1[n] for n in C),
                 tj_r8_x1_names=sorted(n for n in C if r8x1[n]))
out['groupC'] = gc

# ---- pools: tb72 / h250 identical to trajectory's inputs (by prompt)
for p in ('tb72', 'h250'):
    a = {r['prompt'] for r in rd(f'{W}/data/mcts/{p}.jsonl')}
    b = {r['prompt'] for r in rd(f'{TJ}/s0_r8__{p}_x0.jsonl')}
    out[f'pool_{p}'] = dict(n=len(a), equal_to_trajectory=a == b)

# ---- every job
jobs = {}
for f in sorted(glob.glob(f'{E}/eval/*.jsonl')) + sorted(glob.glob(f'{E}/eval_x10/*.jsonl')):
    lab = os.path.relpath(f, E)[:-6]
    R = rd(f); js = f[:-6] + '.json'
    J = json.load(open(js)) if os.path.exists(js) else {}
    arm = lab.rsplit('__', 1)[1]
    d = dict(n=len(R), solved=sum(bool(r['solved']) for r in R), json_solved=J.get('solved'), json_n=J.get('n'),
             solved_names=sorted(r['name'] for r in R if r['solved']))
    if arm.startswith('sample'):
        d['wall_s'] = J.get('wall_s')
        bad = [r['name'] for r in R if bool(r['solved']) != (r['n_ok'] > 0) or bool(r['solved']) != bool(r['proofs'])]
        d['solved_flag_inconsistent'] = len(bad)
        d['n_tried'] = sorted({r['n_tried'] for r in R})
        ee = J.get('env', {}).get('env_end', {})
        tot = sum(ee.values())
        d['env_end'] = ee; d['trunc_frac'] = ee.get('truncated', 0) / tot if tot else None
        d['counted_proofs'] = sum(len(r['proofs']) for r in R)
    else:
        st = J.get('stats', {})
        d.update(budget_s=J.get('budget_s'), wall_s=st.get('wall_s'), gpu_s=st.get('gpu_s'), lean_s=st.get('lean_s'),
                 gpu=J.get('gpu'), cfg={k: J['cfg'][k] for k in ('K', 'temp', 'max_action')} if 'cfg' in J else None,
                 seed=J.get('seed'), gpu_util=J.get('gpu_util_mean'), peak_gb=J.get('peak_alloc_gb'),
                 trunc_frac=(st.get('truncated', 0) / st['sampled']) if st.get('sampled') else None,
                 dup_action_frac=(st.get('dup_action', 0) / st['sampled']) if st.get('sampled') else None,
                 lean_checks=sum(r['lean_checks'] for r in R), proof_ok=st.get('proof_ok'), proof_rej=st.get('proof_rej'),
                 max_t_found=max([r['t_found'] for r in R if r['solved']] or [None], key=lambda x: x or 0),
                 solved_without_text=sum(1 for r in R if r['solved'] and not r.get('text')))
    jobs[lab] = d
out['jobs'] = jobs

# budget: search budget == its own sample job's wall clock
bm = []
for lab, d in jobs.items():
    if 'budget_s' in d:
        base = re.sub(r'__(prior|value)(_t\d)?$', '__sample', lab)
        if base in jobs:
            bm.append(dict(job=lab, budget=d['budget_s'], sample_wall=jobs[base]['wall_s'],
                           equal=abs(d['budget_s'] - jobs[base]['wall_s']) < 1e-6, search_wall=d['wall_s'],
                           overrun=d['wall_s'] / d['budget_s'] if d['wall_s'] else None))
out['budget_match'] = dict(n=len(bm), all_equal=all(x['equal'] for x in bm),
                           overrun_max=max(x['overrun'] for x in bm), overrun_min=min(x['overrun'] for x in bm),
                           over_1p05=[(x['job'], round(x['overrun'], 3)) for x in bm if x['overrun'] > 1.05])

# ---- tables
T = collections.defaultdict(dict)
for lab, d in jobs.items():
    if not lab.startswith('eval/'):
        continue
    m = re.fullmatch(r'eval/s(\d)_(pend|r8)__(\w+?)__(sample|prior|value)', lab)
    if m:
        T[f's{m[1]}_{m[2]}_{m[3]}'][m[4]] = d['solved']
out['table'] = dict(sorted(T.items()))

# ---- gate
spread1 = {s: gc[s]['tj_r8_x1_solved_on_C'] for s in range(3)}
g = {}
for s in range(3):
    smp = jobs[f'eval/s{s}_r8__C__sample']['solved']; val = jobs[f'eval/s{s}_r8__C__value']['solved']
    pri = jobs[f'eval/s{s}_r8__C__prior']['solved']
    spread = abs(smp - spread1[s]); delta = val - smp
    g[s] = dict(sample=smp, prior=pri, value=val, delta=delta, seed1=spread1[s], spread=spread,
                passes=delta >= 3 and delta > spread)
g['verdict'] = 'PASS' if sum(g[s]['passes'] for s in range(3)) >= 2 else 'FAIL'
out['gate'] = g

# group C solved-set overlaps (r8 and pend)
ov = {}
for s in range(3):
    for c in ('r8', 'pend'):
        S = {a: set(jobs[f'eval/s{s}_{c}__C__{a}']['solved_names']) for a in ('sample', 'prior', 'value')}
        ov[f's{s}_{c}'] = dict(value_only=sorted(S['value'] - S['sample']), sample_only=sorted(S['sample'] - S['value']),
                               both=sorted(S['sample'] & S['value']), prior_only_vs_sample=sorted(S['prior'] - S['sample']),
                               union=len(S['sample'] | S['prior'] | S['value']))
out['groupC_overlap'] = ov

# x10
x = {}
for s in range(3):
    a = jobs[f'eval_x10/s{s}_r8__C__sample']; b = jobs[f'eval_x10/s{s}_r8__C__value']
    k256 = set(jobs[f'eval/s{s}_r8__C__sample']['solved_names'])
    x[s] = dict(sample_k2560=a['solved'], value=b['solved'], budget=b['budget_s'], wall=a['wall_s'],
                n_tried=a['n_tried'], value_minus_sample=b['solved'] - a['solved'],
                k2560_superset_of_k256=k256 <= set(a['solved_names']),
                value_only=sorted(set(b['solved_names']) - set(a['solved_names'])))
out['x10'] = x

# tuning winners by the pre-registered rule over t0..t7
tu = {}
for arm in ('prior', 'value'):
    v = [jobs[f'eval/s0_pend__tune200__{arm}_t{i}']['solved'] for i in range(8)]
    tu[arm] = dict(solved=v, winner=v.index(max(v)), cfg=jobs[f'eval/s0_pend__tune200__{arm}_t{v.index(max(v))}']['cfg'])
tu['sample'] = jobs['eval/s0_pend__tune200__sample']['solved']
tu['cfg_final'] = json.load(open(f'{E}/cfg_final.json'))
tu['readout_cfgs'] = sorted({(lab.split('__')[-1], json.dumps(d['cfg'], sort_keys=True)) for lab, d in jobs.items()
                             if 'cfg' in d and d['cfg'] and 'tune' not in lab})
inv = {}
for f in glob.glob(f'{E}/invalid_maxaction64/*.jsonl'):
    J = json.load(open(f[:-6] + '.json')); inv[os.path.basename(f)] = dict(solved=J['solved'], cfg_max_action=J['cfg'].get('max_action'),
                                                                         K=J['cfg'].get('K'), temp=J['cfg'].get('temp'))
tu['invalid_maxaction64'] = inv
out['tuning'] = tu

# duplicate s0 pend draw (quarantined copy) vs the counted copy
dq = {}
for f in sorted(glob.glob(f'{E}/dup_s0_pend_mc0/*.jsonl')):
    b = os.path.basename(f)[:-6]
    R = rd(f); c = jobs.get(f'eval/{b}')
    J = json.load(open(f[:-6] + '.json'))
    dq[b] = dict(dup_solved=sum(bool(r['solved']) for r in R), counted_solved=c['solved'] if c else None,
                 dup_wall=J.get('wall_s') or J.get('stats', {}).get('wall_s'), counted_wall=c and c['wall_s'],
                 dup_budget=J.get('budget_s'))
out['dup_s0_pend'] = dq

json.dump(out, open(os.path.join(os.path.dirname(__file__), 'r1_counts.json'), 'w'), indent=1, default=list)
for k in ('groupC', 'pool_tb72', 'pool_h250', 'budget_match', 'table', 'gate', 'groupC_overlap', 'x10', 'tuning', 'dup_s0_pend'):
    print(k, json.dumps(out[k], default=list)[:3000])
