#!/usr/bin/env python3
"""Theorems a k-32 read left unsolved, as per-file subsets for the k extension (run kalmar-pretrain).

  python3 kalmar/unsolved.py <read>.rows.jsonl.gz <outdir> <set file> [<set file> ...]

Writes <outdir>/<basename>.jsonl (the original records, file order) for every set file with an unsolved theorem, and
prints the comma-separated list of written files (the --sets of the extension read; the basenames keep the row labels).
"""
import gzip, json, os, sys

rows, outdir, sets = sys.argv[1], sys.argv[2], sys.argv[3:]
uns = {}
for l in gzip.open(rows, 'rt'):
    r = json.loads(l)
    if r['n_ok'] == 0:
        uns.setdefault(r['file'], set()).add(r['name'])
os.makedirs(outdir, exist_ok=True)
written = []
for fn in sets:
    b = os.path.basename(fn).replace('.jsonl', '')
    if b not in uns:
        continue
    out = os.path.join(outdir, b + '.jsonl')
    n = 0
    with open(out, 'w') as f:
        for l in open(fn):
            if l.strip() and json.loads(l).get('name') in uns[b]:
                f.write(l if l.endswith('\n') else l + '\n'); n += 1
    assert n == len(uns[b]), (b, n, len(uns[b]))
    written.append(out)
print(','.join(written))
