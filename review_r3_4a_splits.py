#!/usr/bin/env python3
"""Reviewer's independent training-set and split checks for round3-run4a (phase 1).
  - train_reductio_f0_b1.jsonl: size, per-length counts, cap 6, f = 0 under my strict-reductio predicate (written and pruned
    form), DN usage, verifier pass on every record, prompt/thm/text consistency
  - renaming-class disjointness (my canonicaliser: min over the 24 atom bijections; also a stricter premise-order-free
    variant) between every training file (the Stage-1 set and the RL rows of every mix_*.jsonl) and every evaluation pool
  - mix files: RL rows are target prompts only; replay rows are training-set rows
  - provenance: every training record is present, as (prompt, proof), in a generator-made source set available locally
usage: python3 review_r3_4a_splits.py <root> <out.json>"""
import json, sys, os, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from review_r3_4a_lib import classify, canon, thm_of_prompt, parse
from nd_verify import verify_text

ROOT, OUT = sys.argv[1], sys.argv[2]
rd = lambda fn: [json.loads(l) for l in open(fn) if l.strip()]
res = {}

train = rd(f'{ROOT}/data/r3_4a/train_reductio_f0_b1.jsonl')
o = {'n': len(train), 'by_len': collections.Counter(), 'max_len': 0, 'strict_pruned': 0, 'strict_written': 0, 'uses_dn': 0,
     'negi_any': 0, 'verify_fail': 0, 'n_lines_field_mismatch': 0, 'thm_prompt_mismatch': 0, 'text_mismatch': 0, 'max_depth': collections.Counter()}
train_keys, train_keys_s = set(), set()
train_pairs = set()
for r in train:
    c = classify(r['proof'])
    assert c, r['name']
    o['by_len'][c['written']] += 1
    o['max_len'] = max(o['max_len'], c['written'])
    o['strict_pruned'] += c['reductio']; o['strict_written'] += c['reductio_written']; o['uses_dn'] += c['uses_dn']
    o['negi_any'] += any(l['rule'] == 'NEGI' for l in parse(r['proof']))
    o['max_depth'][c['max_depth']] += 1
    o['n_lines_field_mismatch'] += (r.get('n_lines') != c['written'])
    o['thm_prompt_mismatch'] += (thm_of_prompt(r['prompt']) != r['thm'])
    o['text_mismatch'] += (r.get('text', r['prompt'] + ' ' + r['proof']) != r['prompt'] + ' ' + r['proof'])
    o['verify_fail'] += (not verify_text(r['prompt'] + ' ' + r['proof'])[0])
    train_keys.add(canon(r['thm'])); train_keys_s.add(canon(r['thm'], True))
    train_pairs.add((r['prompt'], r['proof']))
o['distinct_classes'] = len(train_keys)
o['by_len'] = dict(sorted(o['by_len'].items())); o['max_depth'] = dict(sorted(o['max_depth'].items()))
res['train_set'] = o
print(json.dumps(o, indent=1), flush=True)

POOLS = {'targets_reductio_req': 'data/p2/targets_reductio_req.jsonl', 'transfer_reductio_req': 'data/p2/transfer_reductio_req.jsonl',
         'heldout': 'data/p2/heldout.jsonl', 'validation_36': 'targets/validation_36.jsonl',
         'targets_reductio': 'data/p2/targets_reductio.jsonl', 'transfer_reductio': 'data/p2/transfer_reductio.jsonl',
         'targets_reductio2': 'data/p2/targets_reductio2.jsonl', 'transfer_reductio2': 'data/p2/transfer_reductio2.jsonl',
         'targets_reductio_req6': 'data/r3_2/targets_reductio_req6.jsonl'}
pk, pks = {}, {}
for name, fn in POOLS.items():
    rows = rd(f'{ROOT}/{fn}')
    pk[name] = {canon(r['thm'].strip()) for r in rows}
    pks[name] = {canon(r['thm'].strip(), True) for r in rows}
    res.setdefault('disjoint', {})[name] = {'n': len(rows), 'classes': len(pk[name]), 'overlap_train': len(pk[name] & train_keys),
                                            'overlap_train_premise_order_free': len(pks[name] & train_keys_s)}
ev = ['targets_reductio_req', 'transfer_reductio_req', 'heldout', 'validation_36']
res['pool_vs_pool'] = {f'{a}&{b}': [len(pk[a] & pk[b]), len(pks[a] & pks[b])] for i, a in enumerate(ev) for b in ev[i + 1:]}
print(json.dumps(res['disjoint'], indent=1)); print(res['pool_vs_pool'], flush=True)

# mix files: RL rows (everything not in the training set as a (prompt, proof) pair) must carry target prompts only
T = rd(f'{ROOT}/data/p2/targets_reductio_req.jsonl')
tprompts = {t['prompt'] for t in T}
other_eval_prompts = set()
for name in ('transfer_reductio_req', 'heldout', 'validation_36'):
    other_eval_prompts |= {r['prompt'] for r in rd(f'{ROOT}/{POOLS[name]}')}
mx = {'files': 0, 'rows': 0, 'rl_rows': 0, 'rl_rows_not_target_prompt': 0, 'rows_with_other_eval_prompt': 0, 'replay_rows': 0,
      'rl_rows_fail_verify': 0, 'rl_rows_not_strict': 0, 'rl_rows_over_cap6': 0}
seen_rl = {}
for fn in sorted(glob.glob(f'{ROOT}/artifacts/r3_4a/*/mix_*.jsonl')):
    mx['files'] += 1
    for r in rd(fn):
        mx['rows'] += 1
        pair = (r['prompt'], r['proof'])
        mx['rows_with_other_eval_prompt'] += (r['prompt'] in other_eval_prompts)
        if pair in train_pairs:
            mx['replay_rows'] += 1; continue
        mx['rl_rows'] += 1
        if r['prompt'] not in tprompts:
            mx['rl_rows_not_target_prompt'] += 1
        if pair not in seen_rl:
            c = classify(r['proof'])
            seen_rl[pair] = (verify_text(r['prompt'] + ' ' + r['proof'])[0], bool(c and c['reductio']), c['written'] if c else -1)
        ok, st, w = seen_rl[pair]
        mx['rl_rows_fail_verify'] += (not ok); mx['rl_rows_not_strict'] += (not st); mx['rl_rows_over_cap6'] += (w > 6)
mx['distinct_rl_pairs'] = len(seen_rl)
res['mix'] = mx
print(json.dumps(mx, indent=1), flush=True)

# provenance against locally available generator-made source sets
src = [f for f in [f'{ROOT}/data/p2/train_depth3_f0_a1.jsonl'] + sorted(glob.glob(f'{ROOT}/data/r2/train_r2_*.jsonl')) + sorted(glob.glob('/tmp/r4a_src/*.jsonl')) if os.path.exists(f)]
left = set(train_pairs)
prov = {}
for fn in src:
    before = len(left)
    for l in open(fn):
        if l.strip():
            x = json.loads(l); left.discard((x['prompt'], x['proof']))
    prov[os.path.basename(fn)] = before - len(left)
res['provenance'] = {'sources': prov, 'train_pairs': len(train_pairs), 'unaccounted': len(left)}
print(res['provenance'])
json.dump(res, open(OUT, 'w'), indent=1)
