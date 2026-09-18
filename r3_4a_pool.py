#!/usr/bin/env python3
"""round3-run4a: reconstruct a cap-6 pool from the generator-made training sets that are still reachable, so that an
f = 0 reductio set can be re-assembled with the unchanged assembler (the original train_reductio_f0.jsonl and its pool
were never pulled to this host or the bucket).

  python3 r3_4a_pool.py --sets data/p2/train_depth3_f0_a1.jsonl data/r2/train_r2_*.jsonl --out data/r3_4a/pool_cap6_r4a.jsonl
  python3 make_coverage_sets.py assemble --pool data/r3_4a/pool_cap6_r4a.jsonl --outdir data/r3_4a --patterns reductio --freqs 0 \
      --heldout_file data/p2/heldout.jsonl --exclude <target/transfer pools> --suffix _b1 --seed 41

Every record is generator output (no new proofs are made here). Deduplicated by renaming class (`key`, recomputed with
gen.canon_key and asserted equal to the stored one), validation-36 classes dropped, cap 6 asserted, every proof
re-verified, pattern labels recomputed with patterns.classify (the stored `pat` is not trusted).
"""
import argparse, json, sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text
from gen import canon_key
from patterns import classify, PATTERNS

ap = argparse.ArgumentParser()
ap.add_argument('--sets', nargs='+', required=True); ap.add_argument('--out', required=True)
a = ap.parse_args()
val = {canon_key(json.loads(l)['thm'].strip()) for l in open('targets/validation_36.jsonl')}
seen = set(); stats = collections.Counter(); by_len = collections.Counter(); pat_cnt = collections.Counter()
with open(a.out, 'w') as fo:
    for fn in a.sets:
        n_new = 0
        for l in open(fn):
            if not l.strip():
                continue
            r = json.loads(l); stats['read'] += 1
            key = canon_key(r['thm'])
            assert key == r['key'], (fn, r['name'])
            if key in seen:
                stats['dup'] += 1; continue
            seen.add(key)
            if key in val:
                stats['val36'] += 1; continue
            ok, reason, nl = verify_text(r['prompt'] + ' ' + r['proof'])
            assert ok and nl == r['n_lines'] <= 6, (fn, r['name'], reason)
            cl = classify(r['proof'])
            pat = {p: bool(cl[p]) for p in PATTERNS}
            rec = {'name': f'pool_r4a_{stats["kept"]}', 'thm': r['thm'], 'key': key, 'prompt': r['prompt'], 'proof': r['proof'],
                   'n_lines': nl, 'rules': r.get('rules'), 'n_prem': r.get('n_prem'), 'pat': pat, 'src': os.path.basename(fn)}
            fo.write(json.dumps(rec) + '\n'); stats['kept'] += 1; n_new += 1; by_len[nl] += 1
            for p in PATTERNS:
                pat_cnt[(nl, p)] += pat[p]
        print(fn, 'new classes', n_new, flush=True)
rep = {'stats': dict(stats), 'by_len': dict(sorted(by_len.items())),
       'patterns_by_len': {f'{L}': {p: pat_cnt[(L, p)] for p in PATTERNS} for L in sorted(by_len)}, 'sets': a.sets}
json.dump(rep, open(a.out.replace('.jsonl', '_report.json'), 'w'), indent=1)
print(json.dumps(rep, indent=1))
