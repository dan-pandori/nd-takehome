"""review_coep/checks.py -- C1 (paired caps), C2 (dose x1 + guided), C3 (textbook72 pend) recounted from the raw read rows.

Reference x0 / pend values: the create-or-elicit reviewer's own outputs (review_coe/out_acq.json, out_general.json).
"""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

S = strict_names()
SS = set(S)
FAM = families()
gen = SS - set().union(*map(set, FAM.values()))
print('strict', len(S), 'distinct', len(SS), 'family members', sum(map(len, FAM.values())), 'non-family', sorted(gen))
print('bars', {f: (len(m), bar(len(m))) for f, m in FAM.items()})

# strict106.jsonl = the 106 strict members of read1054 (same prompts)
r1054 = {r['name']: r for r in jl(P('data/coe/read1054.jsonl'))}
s106 = jl(P('data/coe_paper/strict106.jsonl'))
names106 = [r['name'] for r in s106]
assert len(names106) == 106 and set(names106) == SS, 'strict106 != sigma_heldout_strict'
mism = [r['name'] for r in s106 if r['prompt'] != r1054[r['name']]['prompt']]
print('strict106: 106 names == sigma_heldout_strict.txt; prompt mismatches vs read1054:', len(mism))

acq = json.load(open(P('review_coe/out_acq.json')))['reads']
out = {'C1': {}, 'C2': {}, 'C3': {}}


def summarise(path):
    rows = read_rows(path)
    assert set(rows) == SS, path
    sol = solved_set(rows)
    c, t, ne = cutoffs(rows)
    ntr = collections.Counter(r['n_tried'] for r in rows.values())
    return rows, sol, dict(solved=len(sol), fam=fam_counts(sol, FAM), bar=at_bar(sol, FAM), cut=c, att=t,
                           cut_share=c / t, names_exh=ne, n_tried=dict(ntr),
                           attempts_ok=sum(r['n_ok'] for r in rows.values()))


print('\n== C1: standard (512 / 96) vs doubled (1,024 / 192) caps, sample seed 0, strict106')
print(f"{'ckpt':14s} {'x0(coe)':>7s} {'std':>4s} {'dbl':>4s} {'std-only':>8s} {'dbl-only':>8s} {'cut std':>9s} {'cut dbl':>9s} {'ratio':>6s}  bar std / dbl")
for arm, seeds in (('ko', range(6)), ('dose1', range(3)), ('full', (4,))):
    for s in seeds:
        tag = f'{arm}_s{s}'
        a = json.load(open(f'{EVAL}/c1_{tag}_std.jsonl.args.json'))
        b = json.load(open(f'{EVAL}/c1_{tag}_dbl.jsonl.args.json'))
        assert (a['max_action'], a['max_steps'], b['max_action'], b['max_steps']) == (512, 96, 1024, 192), tag
        assert a['seed'] == b['seed'] == 0 and a['batch'] == b['batch'] == 512 and a['k'] == b['k'] == 256
        assert a['temperature'] == b['temperature'] == 0.8 and a['inp'] == b['inp'] == 'data/coe_paper/strict106.jsonl'
        assert a['ckpt'] == b['ckpt'] and a['ckpt'].endswith(f'la_{tag}_r16.pt'), (a['ckpt'], tag)
        _, ss, sa = summarise(f'{EVAL}/c1_{tag}_std.jsonl.gz')
        _, sd, sb = summarise(f'{EVAL}/c1_{tag}_dbl.jsonl.gz')
        x0 = acq[f'r16_{tag}_x0']['strict']['solved']
        ratio = (sa['cut'] / sb['cut']) if sb['cut'] else float('inf')
        print(f"{tag:14s} {x0:7d} {sa['solved']:4d} {sb['solved']:4d} {len(ss - sd):8d} {len(sd - ss):8d} "
              f"{100 * sa['cut_share']:8.3f}% {100 * sb['cut_share']:8.3f}% {ratio:6.1f}  {sa['bar']} / {sb['bar']}")
        out['C1'][tag] = dict(x0_coe=x0, std=sa, dbl=sb, std_only=sorted(ss - sd), dbl_only=sorted(sd - ss),
                              cut_ratio=ratio, ckpt=a['ckpt'])
for tag, v in out['C1'].items():
    print(f"  {tag}: fam std {v['std']['fam']}\n  {'':{len(tag)}}  fam dbl {v['dbl']['fam']}  names-exhausted std/dbl "
          f"{v['std']['names_exh']}/{v['dbl']['names_exh']}")

print('\n== C2: dose1 r16, plain x1 (seed 1, standard caps) and guided g0 (logical, <= 10 rejections, seed 0)')
for s in range(3):
    tag = f'dose1_s{s}'
    a = json.load(open(f'{EVAL}/c2_{tag}_x1.jsonl.args.json'))
    assert a['seed'] == 1 and (a['max_action'], a['max_steps'], a['batch'], a['k']) == (512, 96, 512, 256), a
    _, sx, sa = summarise(f'{EVAL}/c2_{tag}_x1.jsonl.gz')
    g = json.load(open(f'{EVAL}/c2_{tag}_g0.json.args.json'))
    assert g['seed'] == 0 and g['arm'] == 'logical' and g['max_rej'] == 10 and g['k'] == 256 and g['batch'] == 512, g
    grows = jl(f'{EVAL}/c2_{tag}_g0.rows.jsonl.gz')
    assert {r['name'] for r in grows} == SS and len(grows) == 106
    gs = {r['name'] for r in grows if r['n_ok'] > 0}
    st = collections.Counter(x for r in grows for x in r['status'])
    nok = sum(r['n_ok'] for r in grows)
    # consistency: n_ok == number of 'done' statuses == sum of accepted-text counts
    bad = [r['name'] for r in grows if r['n_ok'] != sum(1 for x in r['status'] if x == 'done')
           or (isinstance(r['accepted'], dict) and sum(r['accepted'].values()) != r['n_ok'])]
    x0 = acq[f'r16_{tag}_x0']['strict']
    print(f"{tag}: x0(coe) {x0['solved']} bar {x0['acquired']} | x1 {sa['solved']} bar {at_bar(sx, FAM)} "
          f"cut {100 * sa['cut_share']:.3f}% | guided {len(gs)} bar {at_bar(gs, FAM)} fam {fam_counts(gs, FAM)} "
          f"statuses {dict(st)} | rows with n_ok/status/accepted mismatch {len(bad)}")
    out['C2'][tag] = dict(x0_coe=x0['solved'], x1=sa, guided=dict(solved=len(gs), fam=fam_counts(gs, FAM),
                          bar=at_bar(gs, FAM), status=dict(st), attempts_ok=nok, cut_share_step=st['fail:step_cap'] / sum(st.values())))

print('\n== C3: old full s0-s2 pend on textbook72, plain x0, batch 512, standard caps')
gen_ = json.load(open(P('review_coe/out_general.json')))
for s in range(3):
    tag = f'oldfull_s{s}'
    a = json.load(open(f'{EVAL}/c3_{tag}_pend_tb72.jsonl.args.json'))
    rows = read_rows(f'{EVAL}/c3_{tag}_pend_tb72.jsonl.gz')
    assert len(rows) == 72 and all(n.startswith('textbook_') for n in rows)
    sol = solved_set(rows)
    c, t, ne = cutoffs(rows)
    ref = round(gen_[f'full_s{s}']['pend_x0']['tb72'] * 72)
    print(f"{tag}: ckpt {a['ckpt']} seed {a['seed']} batch {a['batch']} caps {a['max_action']}/{a['max_steps']}: "
          f"{len(sol)} / 72 (coe pend x0 {ref}); cut-off {c}/{t} = {100 * c / t:.3f}%")
    out['C3'][tag] = dict(solved=len(sol), ref=ref, cut=c, att=t, ckpt=a['ckpt'])
ko = [round(gen_[f'ko_s{s}']['pend_x0']['tb72'] * 72) for s in range(6)]
full_old = [out['C3'][f'oldfull_s{s}']['solved'] for s in range(3)]
full_new = [round(gen_[f'full_s{s}']['pend_x0']['tb72'] * 72) for s in (3, 4, 5)]
full_ref = [round(gen_[f'full_s{s}']['pend_x0']['tb72'] * 72) for s in range(6)]
m = lambda x: sum(x) / len(x)
print(f'knockout pend x0 tb72 {ko} mean {m(ko):.2f}')
print(f'full pend tb72: on-file {full_ref} mean {m(full_ref):.2f}; with C3 for s0-s2 {full_old + full_new} mean {m(full_old + full_new):.2f}')
print(f'gap full - knockout: on-file {m(full_ref) - m(ko):+.2f}; with C3 {m(full_old + full_new) - m(ko):+.2f}')
out['C3']['gap'] = dict(ko=ko, full_onfile=full_ref, full_c3=full_old + full_new,
                        gap_onfile=m(full_ref) - m(ko), gap_c3=m(full_old + full_new) - m(ko))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_checks.json'), 'w'), indent=1)
