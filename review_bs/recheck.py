#!/usr/bin/env python3
"""Reviewer Lean re-check of counted proofs (best-state). Negative controls first, then >= 150 counted proofs per arm
(120 random + the 30 longest, distinct theorems), rendered by the reviewer's own ND->Lean renderer (rlean.py) from the
stored proof text; term size from the elaborated value (rvsize)."""
import json, glob, os, random, sys, collections, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rlean
R = os.path.expanduser('~/review/best-state'); E = f'{R}/artifacts/bs/eval'
def rd(fn): return [json.loads(l) for l in open(fn) if l.strip()]
def nlines(p): return p.count(' ; ')
ARMS = {}
for fn in sorted(glob.glob(f'{E}/*.jsonl')):
    b = os.path.basename(fn)[:-6]
    if b.startswith('heldout_'):
        if b.endswith('b300'): continue
        cell = 'Fz_' + b.split('_')[1]
    else:
        cell = b.split('__')[0].rsplit('_', 1)[0]
    for r in rd(fn):
        for p in r['proofs']:
            ARMS.setdefault(cell, []).append((r['prompt'], p, b, r['name']))
rng = random.Random(20261001)
res = {}
# ---- negative controls (on arm T1_best12)
pool = ARMS['T1_best12']
unt = rng.sample(pool, 60)
rej = []
for fn in sorted(glob.glob(f'{E}/T1_best12_*__*.jsonl')):
    for r in rd(fn):
        fe = r.get('fail_example') or ''
        if fe.startswith('LEANREJ '): rej.append((r['prompt'], fe[len('LEANREJ '):]))
rej = rng.sample(rej, 60)
flip = [x for x in rng.sample(pool, 600) if 'ORI' in x[1]][:60]
byn = collections.defaultdict(list)
for x in pool: byn[rlean.stmt(x[0])[0].__len__()].append(x)
mis = []
for x in rng.sample(pool, 60):
    cands = [y for y in byn[len(rlean.stmt(x[0])[0])] if rlean.stmt(y[0]) != rlean.stmt(x[0])]
    mis.append((rng.choice(cands)[0], rlean.render(x[0], x[1])))
def run(items): return rlean.check(items, per_file=200)
c = {}
t0 = time.time()
c['untouched_pass'] = sum(o for o, _, _ in run([(p, rlean.render(p, b)) for p, b, _, _ in unt]))
c['leanrej_pass'] = sum(o for o, _, _ in run([(p, rlean.render(p, b)) for p, b in rej]))
c['flip_pass'] = sum(o for o, _, _ in run([(p, rlean.render(p, b, flip=('Or.inl', 'Or.inr'))) for p, b, _, _ in flip]))
c['mismatch_pass'] = sum(o for o, _, _ in run(mis))
c['sorry_pass'] = sum(o for o, _, _ in run([(unt[0][0], 'sorry')]))
c['n'] = dict(untouched=len(unt), leanrej=len(rej), flip=len(flip), mismatch=len(mis), sorry=1)
print('controls', c, f'{time.time()-t0:.0f}s', flush=True)
res['controls'] = c
# ---- main pass
res['arms'] = {}
for cell, items in sorted(ARMS.items()):
    seen = {}; 
    for x in sorted(items, key=lambda x: -nlines(x[1])):
        seen.setdefault((x[2], x[3]), x)
    longest = list(seen.values())[:30]
    rest = [x for x in items if x not in longest]
    pick = longest + rng.sample(rest, min(120, len(rest)))
    out = []
    for x in pick:
        try: out.append((x, rlean.render(x[0], x[1])))
        except Exception as e: out.append((x, None))
    good = [(x[0], b) for x, b in out if b is not None]
    rr = rlean.check(good, per_file=100, size=True)
    fails = [(x[2], x[3], x[1], info) for (x, _), (ok, info, _) in zip([o for o in out if o[1] is not None], rr) if not ok]
    sizes = [s for _, _, s in rr]
    res['arms'][cell] = dict(n_counted=len(items), n_checked=len(pick), render_fail=len(out) - len(good),
                             lean_ok=sum(o for o, _, _ in rr), fails=fails[:20],
                             longest_lines=[nlines(x[1]) for x in longest[:5]],
                             longest_sizes=sizes[:5], size_median_random=sorted(sizes[30:])[len(sizes[30:]) // 2] if sizes[30:] else None,
                             longest=[(x[2], x[3], nlines(x[1]), s) for x, s in zip(longest[:5], sizes[:5])])
    print(cell, {k: v for k, v in res['arms'][cell].items() if k not in ('fails', 'longest')}, f'{time.time()-t0:.0f}s', flush=True)
json.dump(res, open(f'{R}/review_bs/recheck.json', 'w'), indent=1)
