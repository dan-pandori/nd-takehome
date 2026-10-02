#!/usr/bin/env python3
"""C3/C4 accounting: solved set of a read's rows == set of prompts with >= 1 Lean-accepted literal text in its gate dump."""
import gzip, json, os

H = os.path.expanduser('~')
R = f'{H}/work/claim-audit/audit/raw'
pairs = []
for s in range(4):
    pairs.append((f'{R}/state-cap12/artifacts/sc12/dump/rr_T1_SN12_s{s}__ge17.jsonl.gz', f'{R}/state-cap12/artifacts/sc12/rr/T1_SN12_s{s}__ge17.jsonl'))
    pairs.append((f'{R}/long-pool-2/artifacts/lpool2/dump/rr_T1_SN12_s{s}__new.jsonl', f'{R}/long-pool-2/artifacts/lpool2/rr/T1_SN12_s{s}__new.jsonl'))
pairs += [(f'{R}/state-cap12/artifacts/sc12/dump/rr_stage1_SN12_s0__ge17.jsonl.gz', f'{R}/state-cap12/artifacts/sc12/rr/stage1_SN12_s0__ge17.jsonl'),
          (f'{R}/state-cap12/artifacts/sc12/dump/rr_T1_K12_s0__rr600.jsonl.gz', f'{R}/state-cap12/artifacts/sc12/rr/T1_K12_s0__rr600.jsonl'),
          (f'{R}/state-cap12/artifacts/sc12/dump/rr_T1_SN12_s0__rr600.jsonl.gz', f'{R}/state-cap12/artifacts/sc12/rr/T1_SN12_s0__rr600.jsonl'),
          (f'{R}/state-cap12/artifacts/sc12/dump/rr_stage1_SN12_s0__rr600.jsonl.gz', f'{R}/state-cap12/artifacts/sc12/rr/stage1_SN12_s0__rr600.jsonl')]
for c in ('Fz_best6', 'T1_best6', 'Fz_best12', 'T1_best12'):
    for s in range(3):
        pairs.append((f'{R}/best-state/artifacts/bs/dump/{c}_s{s}__tb72.jsonl.gz', f'{H}/work/best-state/artifacts/bs/eval/{c}_s{s}__tb72.jsonl'))
op = lambda p: gzip.open(p, 'rt') if p.endswith('.gz') else open(p)
print('dump\trows_solved\tdump_prompts_ok\tequal\trow_only\tdump_only')
for d, r in pairs:
    ok = set()
    with op(d) as f:
        for l in f:
            x = json.loads(l)
            if x.get('lean_ok'):
                ok.add(x['prompt'].strip())
    sol = {x['prompt'].strip() for x in map(json.loads, open(r)) if x.get('n_ok', 0) > 0 and x.get('proofs')}
    print(f'{os.path.basename(d)}\t{len(sol)}\t{len(ok)}\t{sol == ok}\t{len(sol - ok)}\t{len(ok - sol)}')
