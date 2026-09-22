#!/usr/bin/env python3
"""Checker of record for ds-composition: every counted proof of one arm goes through the UNMODIFIED nd2lean.py --check
(official translation + Lean) and nd_verify; agreement counts -> artifacts/dsc/record_<arm>.json.
  python3 pod/dsc/record.py <arm>      (dial arms dsc/{ei,frozen}_<arm>_s{0,1}, ladder arms la_{T1,frozen}_<arm>_s{0,1}, coverage cov_<arm>_s{0,1}_<pool>)
Coverage records hold every distinct counted proof under `proofs[].proof`; they are flattened to {name, thm, prompt, proof} first."""
import sys, os, glob, json, subprocess, collections
arm = sys.argv[1]
out = {}
srcs = []
for d in sorted(glob.glob(f'artifacts/dsc/ei_{arm}_s*') + glob.glob(f'artifacts/dsc/frozen_{arm}_s*') + glob.glob(f'artifacts/dsc/la_*_{arm}_s*')):
    if not os.path.isdir(d):
        continue
    rs = glob.glob(f'{d}/round_*.json')
    if not rs:
        continue
    R = max(int(f.split('_')[-1][:-5]) for f in rs)
    for pool in ('found', 'found_transfer'):
        if os.path.exists(f'{d}/{pool}_{R}.jsonl'):
            srcs.append((os.path.basename(d) + ':' + pool, f'{d}/{pool}_{R}.jsonl', f'{d}/record_{pool}_{R}.jsonl'))
for fn in sorted(glob.glob(f'artifacts/dsc/cov_{arm}_s*.s0.jsonl')):
    flat = fn.replace('.s0.jsonl', '.flat.jsonl')
    with open(flat, 'w') as f:
        for l in open(fn):
            r = json.loads(l)
            for p in r['proofs']:
                f.write(json.dumps({'name': r['name'], 'thm': r['thm'], 'prompt': r['prompt'], 'proof': p['proof']}) + '\n')
    srcs.append((os.path.basename(fn)[:-9], flat, fn.replace('.s0.jsonl', '.record.jsonl')))
for tag, src, rep in srcs:
    p = subprocess.run(['python3', 'nd2lean.py', '--check', src, '--out', rep], capture_output=True, text=True)
    rows = [json.loads(l) for l in open(rep)] if os.path.exists(rep) else []
    c = collections.Counter((r['nd_ok'], r['lean_ok']) for r in rows)
    out[tag] = {'source': src, 'n': len(rows), 'both_accept': c[(True, True)], 'nd_ok_lean_rej': c[(True, False)], 'nd_rej_lean_ok': c[(False, True)], 'both_reject': c[(False, False)],
                'stdout_tail': p.stdout.strip().splitlines()[-1:] if p.stdout.strip() else [], 'stderr_tail': p.stderr[-300:]}
    print(tag, len(rows), 'both accept', c[(True, True)], 'disagree', c[(True, False)] + c[(False, True)], flush=True)
json.dump(out, open(f'artifacts/dsc/record_{arm}.json', 'w'), indent=1)
print('RECORD DONE', arm)
