#!/usr/bin/env python3
"""Reviewer Lean re-check (trajectory).  Renderer/harness = reviewer code rlean.py (from review_bs on dan_best-state,
written by an earlier reviewer, independent of the executor).  Negative controls first; then per training seed:
r0 (pend) x0, r8 x0, and a pooled sample of intermediate checkpoints (x1): 30 longest (distinct theorems) + 120 random
counted proofs each; then EVERY eventual and reference target with term size."""
import json, glob, os, random, sys, collections, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rlean
R = os.path.expanduser('~/review/trajectory'); E = f'{R}/artifacts/tj/eval'
def rd(fn): return [json.loads(l) for l in open(fn) if l.strip()]
def nl(p): return p.count(' ; ')
rng = random.Random(20261001)
ARMS = collections.defaultdict(list); REJ = collections.defaultdict(list)
for fn in sorted(glob.glob(f'{E}/s?_*__*_x?.jsonl')):
    b = os.path.basename(fn)[:-6]; s, ck = b.split('__')[0].split('_'); xs = b[-2:]
    arm = f'{s}_{ck}' if ck in ('pend', 'r8') and xs == 'x0' else (f'{s}_mid' if ck not in ('p0', 'pend', 'r8') and xs == 'x1' else None)
    for r in rd(fn):
        fe = r.get('fail_example') or ''
        if fe.startswith('LEANREJ '): REJ[s].append((r['prompt'], fe[8:]))
        if arm:
            for p in r['proofs']: ARMS[arm].append((r['prompt'], p, b, r['name']))
res = {'arms': {}}
pool = ARMS['s0_r8']
unt = rng.sample(pool, 60); rej = rng.sample(REJ['s0'] + REJ['s1'] + REJ['s2'], 60)
flip = [x for x in rng.sample(pool, 800) if 'ORI' in x[1]][:60]
byn = collections.defaultdict(list)
for x in pool: byn[len(rlean.stmt(x[0])[0])].append(x)
mis = []
for x in rng.sample(pool, 60):
    c = [y for y in byn[len(rlean.stmt(x[0])[0])] if rlean.stmt(y[0]) != rlean.stmt(x[0])]
    mis.append((rng.choice(c)[0], rlean.render(x[0], x[1])))
run = lambda it: sum(o for o, _, _ in rlean.check(it, per_file=200))
t0 = time.time()
c = {'untouched_pass': run([(p, rlean.render(p, b)) for p, b, _, _ in unt]),
     'leanrej_pass': run([(p, rlean.render(p, b)) for p, b in rej]),
     'flip_pass': run([(p, rlean.render(p, b, flip=('Or.inl', 'Or.inr'))) for p, b, _, _ in flip]),
     'mismatch_pass': run(mis), 'sorry_pass': run([(unt[0][0], 'sorry')]),
     'n': dict(untouched=len(unt), leanrej=len(rej), flip=len(flip), mismatch=len(mis), sorry=1)}
print('controls', c, f'{time.time()-t0:.0f}s', flush=True); res['controls'] = c
for arm, items in sorted(ARMS.items()):
    seen = {}
    for x in sorted(items, key=lambda x: -nl(x[1])): seen.setdefault(x[3], x)
    longest = list(seen.values())[:30]; rest = [x for x in items if x not in longest]
    pick = longest + rng.sample(rest, min(120, len(rest)))
    good, bad = [], 0
    for x in pick:
        try: good.append((x, rlean.render(x[0], x[1])))
        except Exception: bad += 1
    rr = rlean.check([(x[0], b) for x, b in good], per_file=150)
    fails = [(x[2], x[3], x[1], i) for (x, _), (o, i, _) in zip(good, rr) if not o]
    res['arms'][arm] = dict(n_counted=len(items), n_checked=len(pick), render_fail=bad, lean_ok=sum(o for o, _, _ in rr), fails=fails[:20])
    print(arm, {k: v for k, v in res['arms'][arm].items() if k != 'fails'}, f'{time.time()-t0:.0f}s', flush=True)
# every target, with term size
T = {}
for s in (0, 1, 2):
    for f in (f'{R}/artifacts/tj/targets/targets_s{s}.jsonl', f'{R}/data/tj/ref_new8.jsonl'):
        for l in open(f):
            t = json.loads(l); T[(t['prompt'], t['proof'])] = t
keys = list(T)
rr = rlean.check([(p, rlean.render(p, b)) for p, b in keys], per_file=100, size=True)
res['targets'] = {'n': len(keys), 'lean_ok': sum(o for o, _, _ in rr),
                  'fails': [(T[k]['tid'], i) for k, (o, i, _) in zip(keys, rr) if not o][:30]}
res['target_size'] = {T[k]['tid'] + '|' + T[k]['proof']: s for k, (o, i, s) in zip(keys, rr)}
print('targets', {k: v for k, v in res['targets'].items()}, f'{time.time()-t0:.0f}s', flush=True)
json.dump(res, open(f'{R}/rv/recheck.json', 'w'), indent=0)
