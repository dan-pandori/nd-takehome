#!/usr/bin/env python3
"""Checker of record for the counted proofs of a lean-only arm: every record of found_<R>.jsonl / found_transfer_<R>.jsonl is re-checked
from scratch — an ND proof through the unmodified nd2lean.py translation + lean_check AND nd_verify; a Lean-text proof (one that
denotes no verifier-valid ND proof) as the literal text + lean_check, with the denotation retried.  Agreement counts ->
artifacts/lo/record_<arm>_<pool>.json.   python3 pod/lo/record.py artifacts/lo/la_T1_free_s0 [more arm dirs...]"""
import sys, os, glob, json, collections
sys.path.insert(0, '.')
from nd2lean import translate, TranslationError
from nd_verify import verify_text
from tokenizer import make_tokenizer
import lean_check

for d in sys.argv[1:]:
    arm = os.path.basename(d.rstrip('/'))
    mode = 'lean_free' if '_free_' in arm or arm.endswith('_free') else 'lean_seq'
    tk = make_tokenizer(mode)
    R = max(int(f.split('_')[-1][:-5]) for f in glob.glob(f'{d}/round_*.json'))
    for pool in ('found', 'found_transfer'):
        src = f'{d}/{pool}_{R}.jsonl'
        if not os.path.exists(src):
            continue
        rows = [json.loads(l) for l in open(src)]
        srcs = []; kind = []; nd_ok = []
        for x in rows:
            p = x['proof']
            if p.startswith('N') and p.rstrip().endswith('QED'):
                kind.append('nd'); nd_ok.append(bool(verify_text(x['prompt'] + ' ' + p)[0]))
                try:
                    srcs.append(translate(x['prompt'], p))
                except TranslationError as e:
                    srcs.append('theorem t : False := sorry')      # structural: will be rejected and counted as a disagreement
            else:
                kind.append('text'); nd = tk.denote(x['prompt'], p); nd_ok.append(bool(nd and verify_text(x['prompt'] + ' ' + nd)[0]))
                srcs.append(tk.statement(x['prompt']) + ' ' + p)
        res, wall, cpu = lean_check.check(srcs)
        c = collections.Counter((k, o, r['ok']) for k, o, r in zip(kind, nd_ok, res))
        size_match = sum(1 for x, r in zip(rows, res) if r['ok'] and x.get('ts') == r['size'])
        out = {'source': src, 'round': R, 'n': len(rows), 'lean_ok': sum(r['ok'] for r in res), 'lean_rej': sum(not r['ok'] for r in res),
               'nd_proofs': kind.count('nd'), 'text_proofs': kind.count('text'),
               'nd_both_accept': c[('nd', True, True)], 'nd_verify_ok_lean_rej': c[('nd', True, False)], 'nd_verify_rej_lean_ok': c[('nd', False, True)],
               'text_lean_ok': c[('text', False, True)] + c[('text', True, True)], 'text_denotes_nd_valid': c[('text', True, True)] + c[('text', True, False)],
               'term_size_matches': size_match, 'lean_wall_s': wall, 'lean_proc_s': cpu}
        with open(f'{d}/record_{pool}_{R}.jsonl', 'w') as f:
            for x, k, o, r in zip(rows, kind, nd_ok, res):
                f.write(json.dumps({'name': x['name'], 'kind': k, 'nd_ok': o, 'lean_ok': r['ok'], 'size': r['size'], 'ts': x.get('ts'), 'reason': r['reason']}) + '\n')
        json.dump(out, open(f'artifacts/lo/record_{arm}_{pool}.json', 'w'), indent=1)
        print(arm, pool, out['n'], 'lean ok', out['lean_ok'], 'rej', out['lean_rej'], 'nd disagreements', out['nd_verify_ok_lean_rej'] + out['nd_verify_rej_lean_ok'], 'size matches', size_match, flush=True)
