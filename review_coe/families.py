#!/usr/bin/env python3
"""Reviewer recount of the classical families and their member sets (own G4ip, own double-negation checks).

Families = the 19 schemata of data/ladder/rl_targets.jsonl (trained) and data/ladder/transfer.jsonl (held-out; the 832
tracked = data/coe/transfer_track832.jsonl).  Classical family: some trained member is not G4ip-provable.  Key-step
member: classical-only member of a classical family.  Strict sigma-covered (Addendum 2): key-step and no double negation
anywhere in the sequent -- checked both as written ('( ~ ( ~') and semantically (any subformula (X -> F) -> F, which
Lean treats as a double negation: '( ( ~ X ) > F )', '( ~ ( X > F ) )', ...).  Pre-registered (original) sigma-covered:
key-step and no premise is itself a double negation.  Output: review_coe/out_families.json."""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

RV = C.RV
TR = list(C.rows(f'{RV}/data/ladder/rl_targets.jsonl'))
HO = list(C.rows(f'{RV}/data/ladder/transfer.jsonl'))
T832 = list(C.rows(f'{RV}/data/coe/transfer_track832.jsonl'))
R1054 = list(C.rows(f'{RV}/data/coe/read1054.jsonl'))
print('g4ip self-test', C.g4ip_selftest())


def info(r):
    prem, concl = C.sequent_of(r)
    pt = tuple(C.parse(p) for p in prem); ct = C.parse(concl)
    assert C.classical_valid(pt, ct), ('not classically valid', r['name'])
    ic = C.prove(frozenset(pt), ct)
    return {'name': r['name'], 'schema': r.get('schema'), 'prompt': r['prompt'], 'classical_only': not ic,
            'dneg_written': C.has_dneg_syntactic(prem + [concl]), 'dneg_semantic': C.has_dneg_semantic(prem + [concl]),
            'dneg_premise': any(C.is_dneg(C.parse(p)) for p in prem)}


I_TR = [info(r) for r in TR]
I_HO = [info(r) for r in HO]
names832 = {r['name'] for r in T832}
fam_cls = sorted({x['schema'] for x in I_TR if x['schema'] and x['classical_only']})
print('classical families:', fam_cls)
out = {'classical_families': fam_cls, 'per_family': {}}
for fam in fam_cls:
    tr = [x for x in I_TR if x['schema'] == fam]; ho = [x for x in I_HO if x['schema'] == fam]
    d = {}
    for nm, S in (('trained', tr), ('heldout', ho)):
        ks = [x for x in S if x['classical_only']]
        d[nm] = {'all': len(S), 'keystep': len(ks), 'orig_sigma_cov': sum(1 for x in ks if not x['dneg_premise']),
                 'strict_written': sum(1 for x in ks if not x['dneg_written']),
                 'strict_semantic': sum(1 for x in ks if not x['dneg_semantic'])}
    out['per_family'][fam] = d
    print(f'{fam:22s} trained all/key/orig/strict(w)/strict(sem) {d["trained"]["all"]}/{d["trained"]["keystep"]}/{d["trained"]["orig_sigma_cov"]}/'
          f'{d["trained"]["strict_written"]}/{d["trained"]["strict_semantic"]}   held-out {d["heldout"]["all"]}/{d["heldout"]["keystep"]}/'
          f'{d["heldout"]["orig_sigma_cov"]}/{d["heldout"]["strict_written"]}/{d["heldout"]["strict_semantic"]}')
# non-classical families with a classical-only member anywhere (should be none in trained by definition)
other_cls_ho = collections.Counter(x['schema'] for x in I_HO if x['schema'] and x['schema'] not in fam_cls and x['classical_only'])
print('classical-only held-out members of NON-classical families:', dict(other_cls_ho))
gen_tr = [x for x in I_TR if not x['schema'] and x['classical_only']]
gen_ho = [x for x in I_HO if not x['schema'] and x['classical_only']]
gen_ho832 = [x for x in gen_ho if x['name'] in names832]
out['generated'] = {'trained_classical': len(gen_tr), 'trained_orig_sigma_cov': sum(1 for x in gen_tr if not x['dneg_premise']),
                    'trained_strict_written': sum(1 for x in gen_tr if not x['dneg_written']),
                    'trained_strict_semantic': sum(1 for x in gen_tr if not x['dneg_semantic']),
                    'heldout_classical_all2285': len(gen_ho), 'heldout_classical_832': len(gen_ho832),
                    'heldout832_orig_sigma_cov': sum(1 for x in gen_ho832 if not x['dneg_premise']),
                    'heldout832_strict_written': sum(1 for x in gen_ho832 if not x['dneg_written']),
                    'heldout832_strict_semantic': sum(1 for x in gen_ho832 if not x['dneg_semantic'])}
print('generated:', out['generated'])
# the 832 tracked set = 760 schema members + every generated classical-only transfer theorem?
sch = [r for r in HO if r.get('schema')]
print('832 composition: schema members', sum(1 for r in T832 if r.get('schema')), 'of', len(sch), '; generated', sum(1 for r in T832 if not r.get('schema')),
      '; generated classical-only in 2285:', len(gen_ho), 'in 832:', len(gen_ho832),
      '; generated in 832 that are NOT classical-only:', sum(1 for r in T832 if not r.get('schema') and r['name'] not in {x['name'] for x in gen_ho}))
# strict held-out set (families) + generated strict
strict_fam_ho = [x for x in I_HO if x['schema'] in fam_cls and x['classical_only'] and not x['dneg_written']]
strict_gen_ho = [x for x in gen_ho832 if not x['dneg_written']]
strict_sem_fam_ho = [x for x in I_HO if x['schema'] in fam_cls and x['classical_only'] and not x['dneg_semantic']]
mine = {x['name'] for x in strict_fam_ho + strict_gen_ho}
out['strict_heldout'] = sorted(mine)
out['strict_heldout_family'] = sorted(x['name'] for x in strict_fam_ho)
out['strict_heldout_semantic_family'] = sorted(x['name'] for x in strict_sem_fam_ho)
out['strict_trained'] = sorted(x['name'] for x in I_TR if x['schema'] in fam_cls and x['classical_only'] and not x['dneg_written'])
out['strict_trained_semantic'] = sorted(x['name'] for x in I_TR if x['schema'] in fam_cls and x['classical_only'] and not x['dneg_semantic'])
out['keystep_trained'] = sorted(x['name'] for x in I_TR if x['schema'] in fam_cls and x['classical_only'])
out['keystep_heldout'] = sorted(x['name'] for x in I_HO if x['schema'] in fam_cls and x['classical_only'])
out['orig_sigma_heldout'] = sorted([x['name'] for x in I_HO if x['schema'] in fam_cls and x['classical_only'] and not x['dneg_premise']] +
                                   [x['name'] for x in gen_ho832 if not x['dneg_premise']])
out['orig_sigma_trained'] = sorted([x['name'] for x in I_TR if x['schema'] in fam_cls and x['classical_only'] and not x['dneg_premise']] +
                                   [x['name'] for x in gen_tr if not x['dneg_premise']])
out['gen_strict_heldout'] = sorted(x['name'] for x in strict_gen_ho)
out['family_of'] = {x['name']: x['schema'] for x in I_HO + I_TR if x['schema']}
print(f'strict held-out: families {len(strict_fam_ho)} + generated {len(strict_gen_ho)} = {len(mine)};  semantic-strict family members {len(strict_sem_fam_ho)}')
print('strict trained:', len(out['strict_trained']), ' semantic:', len(out['strict_trained_semantic']), ' key-step trained:', len(out['keystep_trained']),
      ' orig sigma-cov held-out:', len(out['orig_sigma_heldout']), ' orig trained:', len(out['orig_sigma_trained']))
print('written-strict but semantic double negation (held-out families):', sorted(set(x['name'] for x in strict_fam_ho) - set(out['strict_heldout_semantic_family'])))
print('  their sequents:', [x['prompt'] for x in strict_fam_ho if x['name'] not in out['strict_heldout_semantic_family']][:10])
# compare with the run's own name lists (data files the reads / certificates used)
for fn in ('sigma_heldout_strict.txt', 'sigma_heldout_family105.txt', 'sigma_heldout_strict_no916.txt', 'sigma_heldout178.txt'):
    theirs = {l.strip() for l in open(f'{RV}/data/coe/{fn}') if l.strip()}
    ref = mine if 'strict' in fn and '105' not in fn and 'no916' not in fn else (
        {x['name'] for x in strict_fam_ho} if ('105' in fn or 'no916' in fn) else set(out['orig_sigma_heldout']))
    print(f'  data/coe/{fn}: {len(theirs)}; mine {len(ref)}; only theirs {sorted(theirs - ref)[:6]}; only mine {sorted(ref - theirs)[:6]}')
# holdout250 key-step members per family (prompt identity with read1054's h250 rows)
h250p = {r['prompt'] for r in R1054 if r['set'] == 'h250'}
out['keystep_in_h250'] = {fam: sum(1 for x in I_HO if x['schema'] == fam and x['classical_only'] and x['prompt'] in h250p) for fam in fam_cls}
out['strict_in_h250'] = {fam: sum(1 for x in strict_fam_ho if x['schema'] == fam and x['prompt'] in h250p) for fam in fam_cls}
print('key-step held-out members in holdout250:', out['keystep_in_h250'], sum(out['keystep_in_h250'].values()))
print('strict held-out members in holdout250:', out['strict_in_h250'], sum(out['strict_in_h250'].values()))
# read1054 coverage of the strict set (by prompt)
p1054 = collections.Counter(r['prompt'] for r in R1054)
pm = {x['name']: x['prompt'] for x in I_HO}
print('strict held-out members present in read1054 by prompt:', sum(1 for n in mine if p1054[pm[n]] >= 1), 'of', len(mine),
      '; read1054 duplicate prompts:', sum(1 for v in p1054.values() if v > 1))
json.dump(out, open(f'{RV}/review_coe/out_families.json', 'w'), indent=1)
