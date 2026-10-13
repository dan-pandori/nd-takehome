#!/usr/bin/env python3
"""Reviewer Lean re-check, step 2: run Lean 4.34.1 (rlean.LEAN_BIN) over recheck_items.json (from recheck_collect.py) with term
sizes, then over every K12- refill record (no size).  Prints per-group pass counts, unexpected verdicts, term sizes."""
import collections, json, os, statistics, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C, rlean
RV = C.RV
t0 = time.time()
D = json.load(open(f'{RV}/review_coe/recheck_items.json'))
allit = [tuple(x) for x in D['allit']]; texts = [tuple(x) for x in D['texts']]; STRICTP = set(D['strictp'])
del D
print('Lean items (counted + controls)', len(texts), 'with', rlean.LEAN_BIN, flush=True)
res = rlean.check_robust(texts, per_file=150, size=True)
print(f'Lean done ({time.time()-t0:.0f}s)', flush=True)
# refill (no size)
KO = list(C.rows(f'{RV}/data/coe/train_k12ko.jsonl.gz'))
K12 = {(r['prompt'], r['proof'].strip()) for r in C.rows(f'{RV}/data/coe/src/train_k12.jsonl.gz')}
refill = [r for r in KO if (r['prompt'], r['proof'].strip()) not in K12]
del KO, K12
rtexts = [(r['prompt'], rlean.render(r['prompt'], r['proof'])) for r in refill]
rres = rlean.check_robust(rtexts, per_file=300, size=False)
for r, (ok, info, sz) in zip(refill, rres):
    allit.append(('refill', r.get('name') or r['thm'][:40], r['prompt'], r['proof'], 'nd', True)); res.append((ok, info, sz))
print(f'refill Lean done ({time.time()-t0:.0f}s)', flush=True)

out = collections.defaultdict(lambda: {'n': 0, 'pass': 0, 'unexpected': []})
sizes = collections.defaultdict(list); lines = collections.defaultdict(list)
for it, (ok, info, sz) in zip(allit, res):
    o = out[it[0]]; o['n'] += 1; o['pass'] += ok
    if ok != it[5]:
        o['unexpected'].append((it[1], it[2], it[3][:300], info))
    if it[5] and not it[0].startswith('ctl') and it[0] != 'refill':
        if ok and it[2] in STRICTP:
            out[it[0]].setdefault('strict_classical', collections.Counter())['Classical.choice' in info] += 1
        if sz is not None and sz >= 0:
            sizes[it[0]].append(sz)
        if it[4] == 'nd':
            lines[it[0]].append(len(C.parse_nd(it[3])))
for k, v in out.items():
    print(f'{k:16s} n {v["n"]:6d} Lean-accepted {v["pass"]:6d}  unexpected {len(v["unexpected"])}' +
          (f'  strict-member proofs using Classical.choice: {dict(v["strict_classical"])}' if 'strict_classical' in v else ''))
    for f in v['unexpected'][:8]:
        print('    ', f)
for k in sizes:
    s = sizes[k]; l = lines[k]
    print(f'{k:12s} term size median {statistics.median(s)} mean {statistics.mean(s):.1f} max {max(s)} (n {len(s)})' +
          (f'; ND lines median {statistics.median(l)} max {max(l)}' if l else ''))
json.dump({k: {'n': v['n'], 'pass': v['pass'], 'unexpected': v['unexpected'], 'strict_classical': dict(v.get('strict_classical', {}))} for k, v in out.items()},
          open(f'{RV}/review_coe/out_recheck.json', 'w'), indent=1)
