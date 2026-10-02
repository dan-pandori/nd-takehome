#!/usr/bin/env python3
"""organism-analysis: compact one stored sampled read (state_eval jsonl) to the fields the analysis uses.

  python3 oa/oa_compact_read.py <bucket path under nd-rl/> <out .jsonl.gz>

Keeps per theorem: name, n_ok, n_tried, proofs (the read's distinct Lean-accepted ND proofs), pruned_lens.
Drops the per-attempt failure reasons (the bulk of the file).  The raw file stays in the bucket.
"""
import gzip, json, os, subprocess, sys, tempfile

src, out = sys.argv[1], sys.argv[2]
if os.path.exists(out):
    sys.exit(0)
os.makedirs(os.path.dirname(out), exist_ok=True)
with tempfile.TemporaryDirectory(dir='/tmp') as td:
    tmp = os.path.join(td, 'r.jsonl')
    subprocess.run(['hf', 'buckets', 'cp', f'hf://buckets/dan-pandori/nd-rl/{src}', tmp], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
    rows = []
    for l in open(tmp):
        if l.strip():
            d = json.loads(l)
            rows.append({k: d.get(k) for k in ('name', 'n_ok', 'n_tried', 'proofs', 'pruned_lens')})
    with gzip.open(out + '.tmp', 'wt') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
    os.replace(out + '.tmp', out)
