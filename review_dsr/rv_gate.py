import json, glob, os, re, collections
rows = collections.defaultdict(lambda: collections.Counter())
for fn in sorted(glob.glob('artifacts/dsr/*/gate_*.jsonl')):
    if fn.endswith('.disagree.jsonl'):
        continue
    b = os.path.basename(fn)
    m = re.match(r'gate_(\w+)_(c0|r1|r2|r3|r4)_s(\d)\.jsonl', b)
    if not m:
        print('unparsed', b); continue
    stage, arm, seed = m.groups()
    for l in open(fn):
        r = json.loads(l)
        c = rows[arm]
        for k in ['samples', 'parse_fail', 'distinct_checked', 'both_ok', 'nd_ok_lean_rej', 'nd_rej_lean_ok', 'both_rej']:
            c[k] += r[k]
        rows[(arm, stage)] = rows.get((arm, stage), collections.Counter())
        for k in ['distinct_checked', 'nd_ok_lean_rej', 'nd_rej_lean_ok']:
            rows[(arm, stage)][k] += r[k]

print('in-loop lean_gate totals per arm (all stages)')
print('arm    samples   parse-fail   distinct checked   both ok   nd-only(Lean rej)   Lean-only   per-million nd-only')
for arm in ['c0', 'r1', 'r2', 'r3', 'r4']:
    c = rows[arm]
    if not c:
        continue
    d = c['distinct_checked']
    print('%-4s %10d %10d %14d %12d %14d %12d %14.1f' %
          (arm, c['samples'], c['parse_fail'], d, c['both_ok'], c['nd_ok_lean_rej'], c['nd_rej_lean_ok'],
           1e6 * c['nd_ok_lean_rej'] / max(1, d)))
print()
print('per stage')
for k in sorted([k for k in rows if isinstance(k, tuple)]):
    c = rows[k]
    print('%-4s %-8s distinct %8d  nd-only %6d (%.1f/M)  lean-only %5d' %
          (k[0], k[1], c['distinct_checked'], c['nd_ok_lean_rej'],
           1e6 * c['nd_ok_lean_rej'] / max(1, c['distinct_checked']), c['nd_rej_lean_ok']))
print()
print('disagreement files: reasons for nd_ok & lean_rej')
for fn in sorted(glob.glob('artifacts/dsr/*/gate_*.disagree.jsonl')):
    n = nd_only = 0
    for l in open(fn):
        r = json.loads(l); n += 1
        nd_only += r['nd_ok'] and not r['lean_ok']
    if nd_only:
        print('%-46s %5d lines, %5d nd-only' % (os.path.basename(fn), n, nd_only))
