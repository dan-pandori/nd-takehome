#!/usr/bin/env python3
"""Round 3 run 2: the reductio required pool with a 6-line stratum.
  targets_reductio_req.jsonl (300, run 5, unchanged records + 'stratum' = min_lines_ub)
  + the six-line required candidates of run5_reductio_nec.jsonl (min_lines_ub 6, requires, oracle_ok, no timeout),
    class-disjoint from train_reductio_f0 / f0.1, heldout, validation-36 and from the 300 + 150 run-5 records.
Checks on all 345 (+150 transfer): oracle proof verifies (nd_verify) and contains patterns.reductio; classically valid;
G4ip-unprovable (review_run5_logic). Writes data/r3_2/targets_reductio_req6.jsonl and data/r3_2/pool_report.json.
"""
import json, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import canon_key
from nd_verify import verify_text
from patterns import classify
from normalize import norm
from review_run5_logic import parse_thm, classical_valid, intuitionistic, selftest
from review_run5_recount import thm_of_prompt

MAIN = os.path.expanduser('~/nd-takehome')
old = [json.loads(l) for l in open('data/p2/targets_reductio_req.jsonl')]
transfer = [json.loads(l) for l in open('data/p2/transfer_reductio_req.jsonl')]
nec = [json.loads(l) for l in open('data/p2/run5_reductio_nec.jsonl')]
six = [r for r in nec if r['min_lines_ub'] == 6 and r['requires'] and r['oracle_ok'] and not r['timeout'] and not r['r_timeout']]
print('six-line candidates', len(six), collections.Counter(r['schema'] for r in six))
excl_src = {'val36': 'targets/validation_36.jsonl', 'train_reductio_f0': f'{MAIN}/data/p2/train_reductio_f0.jsonl',
            'train_reductio_f0.1': f'{MAIN}/data/p2/train_reductio_f0.1.jsonl', 'heldout': 'data/p2/heldout.jsonl'}
excl = {}
for tag, fn in excl_src.items():
    ks = set()
    for l in open(fn):
        if l.strip():
            x = json.loads(l); ks.add(x.get('key') or canon_key(x['thm'].strip()))
    excl[tag] = ks; print(tag, len(ks), 'classes')
used = {r['key'] for r in old} | {r['key'] for r in transfer}
rows = []
for r in old:
    o = dict(r); o['stratum'] = r['min_lines_ub']; rows.append(o)
overlap = collections.Counter(); dup = 0
for i, r in enumerate(six):
    key = r.get('key') or canon_key(r['thm'].strip())
    hit = [t for t, ks in excl.items() if key in ks]
    if hit:
        overlap[tuple(hit)] += 1; continue
    if key in used:
        dup += 1; continue
    used.add(key)
    o = {'name': f'targets_reductio_req6_{len(rows)}', 'thm': r['thm'], 'key': key, 'prompt': r['prompt'], 'n_lines': r['min_lines_ub'],
         'n_prem': r.get('n_prem'), 'schema': r.get('schema'), 'source': r.get('source', 'schema'), 'gen_lines': r.get('gen_lines'),
         'min_lines_ub': r['min_lines_ub'], 'r_min_lines_ub': r['r_min_lines_ub'], 'requires': r['requires'], 'uses': None, 'mode': 'requires',
         'oracle_proof': r['proof'], 'proof_pat': r['proof_pat'], 'gen_proof': None,
         'pat': {'derived_ore': False, 'reductio': True, 'depth3': False, 'derived_ore_strict': False}, 'stratum': 6}
    rows.append(o)
print('six-line excluded by class overlap', dict(overlap), 'dup', dup, '-> pool', len(rows))
assert selftest()
rep = {'n': len(rows), 'strata': dict(sorted(collections.Counter(r['stratum'] for r in rows).items())), 'schemata': dict(sorted(collections.Counter(r['schema'] for r in rows).items())),
       'six_overlap_excluded': {str(k): v for k, v in overlap.items()}, 'six_dup': dup, 'checks': {}}
for tag, rs in (('targets', rows), ('transfer', transfer)):
    ok = pat = cv = iv = 0; bad = []
    for r in rs:
        v = verify_text(r['prompt'].strip() + ' ' + r['oracle_proof'].strip())
        good = v[0] if isinstance(v, tuple) else v
        ok += bool(good)
        c = classify(norm(r['oracle_proof'])); pat += bool(c and c['reductio'])
        ps, cc = parse_thm(thm_of_prompt(r['prompt'])); a = classical_valid(ps, cc); b = intuitionistic(ps, cc); cv += a; iv += b
        if not good or not (c and c['reductio']) or not a or b:
            bad.append(r['name'])
    rep['checks'][tag] = {'n': len(rs), 'oracle_proof_verifies': ok, 'oracle_proof_reductio': pat, 'classically_valid': cv, 'g4ip_provable': iv, 'bad': bad}
    print(tag, rep['checks'][tag])
# class disjointness of the whole pool from every exclusion source
rep['pool_overlap'] = {t: sum(r['key'] in ks for r in rows) for t, ks in excl.items()}
rep['pool_dup_keys'] = len(rows) - len({r['key'] for r in rows})
rep['pool_transfer_overlap'] = len({r['key'] for r in rows} & {r['key'] for r in transfer})
print('overlap', rep['pool_overlap'], 'dups', rep['pool_dup_keys'], 'with transfer', rep['pool_transfer_overlap'])
with open('data/r3_2/targets_reductio_req6.jsonl', 'w') as f:
    for r in rows:
        f.write(json.dumps(r) + '\n')
json.dump(rep, open('data/r3_2/pool_report.json', 'w'), indent=1)
print('HAND-CHECK five six-liners:')
for r in [x for x in rows if x['stratum'] == 6][:5]:
    print(' ', r['name'], r['thm']); print('   ', r['oracle_proof'])
