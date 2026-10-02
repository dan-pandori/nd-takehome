#!/usr/bin/env python3
"""Reviewer Lean re-check (rl-from-ckpt).  Renderer/harness = rlean.py (reviewer code from review_tj6 on
dan_trajectory-cap6, itself from review_bs; independent of the executor).  Negative controls first, then per arm
(ladder r8 per start, control r8 per start, ladder r2+r4 pooled; 3 training seeds, sample seed 1): 30 longest
(distinct theorems) + 120 random counted proofs, with term size (Lean elaboration) and ND line count."""
import json, glob, os, random, sys, collections, time, statistics as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rlean
R = os.path.expanduser('~/review/rl-from-ckpt'); E = f'{R}/artifacts/rfc/eval'
def rd(fn): return [json.loads(l) for l in open(fn) if l.strip()]
def nl(p): return p.count(' ; ')
rng = random.Random(20261002)
ARMS = collections.defaultdict(list); REJ = []
for fn in sorted(glob.glob(f'{E}/[sc]?_*__*_x1.jsonl')):
    b = os.path.basename(fn)[:-6]; head = b.split('__')[0]; tag, st_, ck = head.split('_')
    if ck == 'rr': continue
    arm = ('L' if tag[0] == 's' else 'C') + f'_{st_}_' + ('r8' if ck == 'r8' else 'r24')
    for r in rd(fn):
        fe = r.get('fail_example') or ''
        if fe.startswith('LEANREJ '): REJ.append((r['prompt'], fe[8:]))
        for p in r['proofs']: ARMS[arm].append((r['prompt'], p, b, r['name']))
res = {'arms': {}}
pool = ARMS['L_p1600_r8']
unt = rng.sample(pool, 60); rej = rng.sample(REJ, 60)
flip_cand = []
for x in rng.sample(pool, 2000):
    L = rlean.parse_nd(x[1])
    # flip only the ORI line itself (review_bs fix): swap ORI1<->ORI2 on one line in the ND text
    for idx, d, f, rule, refs in L:
        if rule in ('ORI1', 'ORI2'):
            other = 'ORI2' if rule == 'ORI1' else 'ORI1'
            parts = x[1].split(' ; '); k = [i for i, p in enumerate(parts) if p.startswith(f'N{idx} ')][0]
            parts[k] = parts[k].replace(f': {rule} ', f': {other} '); flip_cand.append((x[0], ' ; '.join(parts))); break
    if len(flip_cand) >= 60: break
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
     'flip_pass': run([(p, rlean.render(p, b)) for p, b in flip_cand]),
     'mismatch_pass': run(mis), 'sorry_pass': run([(unt[0][0], 'sorry')]),
     'n': dict(untouched=len(unt), leanrej=len(rej), flip=len(flip_cand), mismatch=len(mis), sorry=1)}
print('controls', c, f'{time.time()-t0:.0f}s', flush=True); res['controls'] = c
for arm, items in sorted(ARMS.items()):
    seen = {}
    for x in sorted(items, key=lambda x: -nl(x[1])): seen.setdefault(x[3], x)
    longest = list(seen.values())[:30]; ls = set(map(id, longest)); rest = [x for x in items if id(x) not in ls]
    pick = longest + rng.sample(rest, min(120, len(rest)))
    good, bad = [], 0
    for x in pick:
        try: good.append((x, rlean.render(x[0], x[1])))
        except Exception: bad += 1
    rr = rlean.check([(x[0], b) for x, b in good], per_file=150, size=True)
    fails = [(x[2], x[3], x[1], i) for (x, _), (o, i, _) in zip(good, rr) if not o]
    sz = [s for (_, _, s) in rr if s is not None and s > 0]; lines = [nl(x[1]) for x, _ in good]
    res['arms'][arm] = dict(n_counted=len(items), n_checked=len(pick), render_fail=bad, lean_ok=sum(o for o, _, _ in rr),
                            size_median=st.median(sz) if sz else None, size_max=max(sz) if sz else None,
                            lines_median=st.median(lines), lines_max=max(lines), fails=fails[:20])
    print(arm, {k: v for k, v in res['arms'][arm].items() if k != 'fails'}, f'{time.time()-t0:.0f}s', flush=True)
json.dump(res, open(f'{R}/review_rfc/rv/recheck.json', 'w'), indent=0)
