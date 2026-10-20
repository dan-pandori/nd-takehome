#!/usr/bin/env python3
"""B2 by step type (run kalmar-complexity): per-type code per loss token, summed over the model-coded blocks of
[64, max_thm) (the uniform first block and the asymptote block excluded), and per-type absorbed bits = that code minus
the type's tokens x its per-token code on the asymptote block.  -> artifacts/kc/q4/b2_per_type.json (Q4 predictors
b2_bits_<size>) and artifacts/kc/b2_per_type_table.json."""
import collections, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = lambda p: os.path.join(ROOT, p)
group = lambda t: 'close' if t.startswith('close:') else t
pred, table = collections.defaultdict(dict), {}
for size in ('S', 'M', 'L'):
    f = A(f'artifacts/kc/b2/kal_{size}_s0.json')
    if not os.path.exists(f):
        continue
    R = json.load(open(f))
    if 'summary' not in R:
        continue
    bits, tok, abits, atok = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    for b in R['blocks'][1:]:
        dst = (abits, atok) if b.get('asymptote_block') else (bits, tok)
        for t, v in b['per_tag_bits'].items():
            dst[0][group(t)] += v
        for t, v in b['per_tag_tokens'].items():
            dst[1][group(t)] += v
    rows = {}
    for g in tok:
        linf = abits[g] / atok[g] if atok[g] else None
        rows[g] = {'bits': bits[g], 'loss_tokens': tok[g], 'bits_per_token': bits[g] / tok[g],
                   'asym_bits_per_token': linf, 'excess_bits': bits[g] - tok[g] * linf if linf is not None else None}
        pred[g][f'b2_bits_{size}'] = bits[g] / tok[g]
    table[size] = {'file': os.path.relpath(f, ROOT), 'theorems': R['summary']['theorems'], 'types': rows}
json.dump(pred, open(A('artifacts/kc/q4/b2_per_type.json'), 'w'), indent=1)
json.dump(table, open(A('artifacts/kc/b2_per_type_table.json'), 'w'), indent=1)
for size, T in table.items():
    print(size, T['theorems'], {g: round(r['bits_per_token'], 4) for g, r in sorted(T['types'].items(), key=lambda kv: -kv[1]['bits_per_token'])})
