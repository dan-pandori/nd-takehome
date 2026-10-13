"""Pre-registered checks C1-C3 of this writing run (preregistration/create-or-elicit-paper.md).

Reads the rows pulled from the pod into artifacts/coe_paper/eval/ and prints / writes paper/data/checks_c1c3.json:
  C1  paired plain reads of the 106 strict held-out members, sample seed 0, standard caps (512 tokens / 96 steps) vs
      doubled caps (1,024 / 192): solved, per-family, families at the bar, cut-off share of attempts.
  C2  dose r16: plain x1 and guided (logical, <= 10 redraws) reads of the 106, standard caps.
  C3  old full s0-s2 pend on textbook72 (scoring only), plain x0, batch 512.
Parsing follows review_coe/acq.py (cut-off = a failed attempt whose reason is a truncated action or the step cap).
Models: r16 checkpoints of create-or-elicit (9,560,832 params, lean_staten, from scratch; knockout K12-, dose K12^1%,
full K12) and trajectory's pend checkpoints for full s0-s2.  Lean alone (the in-loop gate).
"""
import ast, gzip, json, os, sys, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
EV = os.path.join(ROOT, 'artifacts/coe_paper/eval')
strict = [l.strip() for l in open(os.path.join(ROOT, 'data/coe/sigma_heldout_strict.txt')) if l.strip()]
fams = json.load(open(os.path.join(ROOT, 'data/coe/families.json')))['families']
fam_of = {m['name']: f for f, v in fams.items() for m in v.get('heldout', [])}
FAMS = ['contraposition_conv', 'negated_conditional', 'peirce', 'peirce_sequent', 'excluded_middle', 'demorgan_nand_to_or']
n_fam = collections.Counter(fam_of.get(m, 'generated') for m in strict)


def L(x):
    return x if isinstance(x, (list, dict)) else ast.literal_eval(x)


def rows(p):
    with gzip.open(p, 'rt') as f:
        for line in f:
            yield json.loads(line)


def load(tag):
    """name -> (n_ok, n_tried, n_cut) for a plain (.jsonl.gz) or guided (.rows.jsonl.gz) read."""
    out = {}
    pp, pg = os.path.join(EV, f'{tag}.jsonl.gz'), os.path.join(EV, f'{tag}.rows.jsonl.gz')
    if os.path.exists(pp):
        for r in rows(pp):
            cut = sum(1 for x in L(r.get('reasons') or []) if ('truncated' in x or 'step cap' in x))
            out[r['name']] = (int(r['n_ok']), int(r['n_tried']), cut)
    elif os.path.exists(pg):
        for r in rows(pg):
            st = L(r['status'])
            cut = sum(1 for s in st if ('trunc' in s or 'step' in s or 'max_steps' in s))
            out[r['name']] = (int(r['n_ok']), int(r['k']), cut)
    else:
        return None
    return out


def summarise(tag):
    d = load(tag)
    if d is None:
        return None
    miss = [m for m in strict if m not in d]
    solved = [m for m in strict if m in d and d[m][0] > 0]
    pf = {f: sum(1 for m in solved if fam_of.get(m) == f) for f in FAMS}
    at_bar = [f for f in FAMS if n_fam[f] and pf[f] / n_fam[f] >= 0.5]
    att = sum(d[m][1] for m in strict if m in d)
    cut = sum(d[m][2] for m in strict if m in d)
    return {'tag': tag, 'solved': len(solved), 'missing': len(miss), 'per_family': pf, 'at_bar': at_bar,
            'cut_share': cut / att if att else None, 'attempts': att, 'solved_names': solved,
            'gen916': 'la_transfer_916' in solved}


def summary_json(tag):
    p = os.path.join(EV, f'{tag}.json')
    return json.load(open(p)) if os.path.exists(p) else None


out = {'C1': {}, 'C2': {}, 'C3': {}}
print('C1  paired standard vs doubled caps, strict 106, seed 0')
for ck in [f'ko_s{s}' for s in range(6)] + ['dose1_s2', 'dose1_s0', 'dose1_s1', 'full_s4']:
    a, b = summarise(f'c1_{ck}_std'), summarise(f'c1_{ck}_dbl')
    if a is None or b is None:
        print(f'  {ck}: pending'); continue
    only_dbl = sorted(set(b['solved_names']) - set(a['solved_names']))
    only_std = sorted(set(a['solved_names']) - set(b['solved_names']))
    sa, sb = summary_json(f'c1_{ck}_std'), summary_json(f'c1_{ck}_dbl')
    out['C1'][ck] = {'std': a, 'dbl': b, 'only_dbl': only_dbl, 'only_std': only_std,
                     'wall_s': [round(sa.get('wall_s', 0)), round(sb.get('wall_s', 0))],
                     'peak_gb': [sa.get('env', {}).get('peak_alloc_gb'), sb.get('env', {}).get('peak_alloc_gb')]}
    print(f"  {ck}: solved std {a['solved']} -> dbl {b['solved']} (only dbl {len(only_dbl)}, only std {len(only_std)}); "
          f"at bar {a['at_bar']} -> {b['at_bar']}; cut {100*a['cut_share']:.2f}% -> {100*b['cut_share']:.2f}%; missing {a['missing']}/{b['missing']}")
print('C2  dose r16, plain x1 and guided g0 (standard caps)')
for s in range(3):
    for kind in ('x1', 'g0'):
        a = summarise(f'c2_dose1_s{s}_{kind}')
        if a is None:
            print(f'  dose1_s{s} {kind}: pending'); continue
        out['C2'][f'dose1_s{s}_{kind}'] = a
        print(f"  dose1_s{s} {kind}: solved {a['solved']} at bar {a['at_bar']} cut {100*a['cut_share']:.2f}% per family {a['per_family']}")
print('C3  old full pend on textbook72, plain x0, batch 512')
for s in range(3):
    sj = summary_json(f'c3_oldfull_s{s}_pend_tb72')
    if sj is None:
        print(f'  s{s}: pending'); continue
    out['C3'][f's{s}'] = {'solved': sj.get('solved'), 'n': 72, 'wall_s': sj.get('wall_s'), 'peak_gb': sj.get('env', {}).get('peak_alloc_gb')}
    print(f"  s{s}: {sj.get('solved')} / 72")
# C3's second expectation: the 6-vs-6 full-minus-knockout r0 gap on all 72 at the knockout's settings, in [4, 9].
# Full s3-s5 and knockout s0-s5 r0 x0 fractions from the review's recount (review_coe/out_general.json, batch 512).
if all(f's{s}' in out['C3'] for s in range(3)):
    G = json.load(open(os.path.join(ROOT, 'review_coe/out_general.json')))
    def tb(k):
        v = G[k]['pend_x0']['tb72'] if isinstance(G[k].get('pend_x0'), dict) else None
        return round(72 * v) if v is not None else None
    full = [out['C3'][f's{s}']['solved'] for s in range(3)] + [tb(f'full_s{s}') for s in (3, 4, 5)]
    ko = [tb(f'ko_s{s}') for s in range(6)]
    if None not in full + ko:
        gap = sum(full) / 6 - sum(ko) / 6
        out['C3']['gap_6v6'] = {'full': full, 'knockout': ko, 'full_mean': sum(full) / 6, 'ko_mean': sum(ko) / 6,
                                'gap': gap, 'prereg_range': [4, 9], 'hit': 4 <= gap <= 9}
        print(f'  6-vs-6 r0 gap on all 72: full {full} mean {sum(full)/6:.2f}, knockout {ko} mean {sum(ko)/6:.2f}, gap {gap:.2f}')
for k in out['C1'].values():
    for side in ('std', 'dbl'):
        k[side].pop('solved_names', None)
json.dump(out, open(os.path.join(ROOT, 'paper/data/checks_c1c3.json'), 'w'), indent=1)
