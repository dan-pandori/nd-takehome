#!/usr/bin/env python3
"""create-or-elicit: classical key-step families and their members (trained-on rl_targets / held-out transfer).

A member is CLASSICAL-ONLY if G4ip (intuit.intuit_provable) cannot prove it intuitionistically.  A family is classical
if any of its rl_targets members is classical-only; classical families keep only their classical-only (key-step)
members, as in capability-defs' cd_schema.py --keystep.
sigma-covered member: classical-only AND no premise is itself a double negation ( ~ ( ~ X ) ), so a DN step cannot cite a
premise line; DN must then cite a derived line (σ+) or a box hypothesis ¬¬X (the "lemma route", 0 times in K12).
We also flag members whose sequent contains a ( ~ ( ~ subformula anywhere.
Also lists every classical-only rl_target / transfer theorem outside the schema families ("generated classical").

  python3 coe/coe_families.py --out data/coe/families.json
"""
import argparse, collections, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from intuit import intuit_provable


def prem_list(prompt):
    body = ' ' + prompt.strip()[4:-4] + ' '
    prem, concl = body.split(' SEQ ')
    return [p.strip() for p in prem.split(' , ') if p.strip()], concl.strip()


def has_dn_premise(prompt):
    ps, _ = prem_list(prompt)
    return any(p.startswith('( ~ ( ~ ') for p in ps)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--targets', default='data/ladder/rl_targets.jsonl')
    ap.add_argument('--transfer', default='data/ladder/transfer.jsonl')
    ap.add_argument('--holdout250', default='data/bs/holdout250.jsonl')
    ap.add_argument('--out', default='data/coe/families.json')
    a = ap.parse_args()
    rl = [json.loads(l) for l in open(a.targets)]
    tr = [json.loads(l) for l in open(a.transfer)]
    h250 = {json.loads(l)['name'] for l in open(a.holdout250)}
    fams = sorted({r['schema'] for r in rl if r.get('schema')})
    co = {}
    for r in rl + tr:
        co[r['name']] = not intuit_provable(r['prompt'])
    out = {'families': {}, 'generated_classical': {}}
    rows = []
    for f in fams:
        mem_rl = [r for r in rl if r.get('schema') == f]
        mem_tr = [r for r in tr if r.get('schema') == f]
        classical = any(co[r['name']] for r in mem_rl)
        def info(rs):
            return [{'name': r['name'], 'classical_only': co[r['name']], 'dn_premise': has_dn_premise(r['prompt']),
                     'dn_anywhere': '( ~ ( ~' in r['prompt'], 'h250': r['name'] in h250, 'L_true': r.get('L_true', r.get('n_lines'))} for r in rs]
        d = {'classical': classical, 'trained': info(mem_rl), 'heldout': info(mem_tr)}
        if classical:
            d['keystep_trained'] = [x['name'] for x in d['trained'] if x['classical_only']]
            d['keystep_heldout'] = [x['name'] for x in d['heldout'] if x['classical_only']]
            d['sigma_covered_trained'] = [x['name'] for x in d['trained'] if x['classical_only'] and not x['dn_premise']]
            d['sigma_covered_heldout'] = [x['name'] for x in d['heldout'] if x['classical_only'] and not x['dn_premise']]
        out['families'][f] = d
        if classical:
            rows.append((f, len(mem_rl), len(d['keystep_trained']), len(d['sigma_covered_trained']), len(mem_tr), len(d['keystep_heldout']),
                         len(d['sigma_covered_heldout']), sum(1 for x in d['heldout'] if x['classical_only'] and x['h250']),
                         sum(1 for x in d['heldout'] if x['classical_only'] and x['dn_anywhere'])))
    for pool, rs in (('rl_targets', rl), ('transfer', tr)):
        gc = [r for r in rs if not r.get('schema') and co[r['name']]]
        out['generated_classical'][pool] = {'n': len(gc), 'names': [r['name'] for r in gc],
                                            'dn_premise': sum(has_dn_premise(r['prompt']) for r in gc),
                                            'sigma_covered': [r['name'] for r in gc if not has_dn_premise(r['prompt'])]}
    json.dump(out, open(a.out, 'w'), indent=1)
    print('| family | trained: all / classical-only / σ-covered | held-out transfer: all / classical-only / σ-covered | of which in holdout250 | held-out key-step with ¬¬ anywhere |')
    print('|---|---|---|---|---|')
    for f, a1, b1, c1, a2, b2, c2, h, dn in rows:
        print(f'| {f} | {a1} / {b1} / {c1} | {a2} / {b2} / {c2} | {h} | {dn} |')
    for pool in ('rl_targets', 'transfer'):
        g = out['generated_classical'][pool]
        print(f"generated (non-schema) classical-only {pool}: {g['n']} (with a ¬¬ premise {g['dn_premise']}, σ-covered {len(g['sigma_covered'])})")
    print('intuitionistic families:', [f for f in fams if not out['families'][f]['classical']])


if __name__ == '__main__':
    main()
