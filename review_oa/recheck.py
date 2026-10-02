"""Reviewer Lean re-check (organism-analysis). Harness = rlean.py (reviewer kit, review_rfc on dan_rl-from-ckpt).
Controls first (untouched / ORI-line flip / statement mismatch / sorry), then per arm 30 longest-distinct + 120 random
counted proofs (r8 x0 reads of Q1-positive units), the 315 reference proofs (with term size), and r8 eventual proofs."""
import json, random, collections, statistics as st, time, sys
import rlean, rvc
rng = random.Random(20261002); P = rvc.prompts()
rows = json.load(open('rv/q1_rows_x0.json'))
ARMS = collections.defaultdict(list)
for r in rows:
    if not r['y']: continue
    if r['run'] == 'rfc': rd = rvc.rd('rfc', f"s{r['seed']}_{r['start']}_r8", 0)
    else: rd = rvc.rd(r['run'], f"s{r['seed']}_r8", 0)
    for p in rd[r['name']]['proofs']: ARMS[r['run']].append((P[r['name']], p, r['name']))
nl = lambda p: p.count(' : ')
res = {'arms': {}}
pool = ARMS['c12']
unt = rng.sample(pool, 60); flip = []
for x in rng.sample(pool, len(pool)):
    for idx, d, f, rule, refs in rlean.parse_nd(x[1]):
        if rule in ('ORI1', 'ORI2'):
            o = 'ORI2' if rule == 'ORI1' else 'ORI1'; parts = x[1].split(' ; ')
            k = [i for i, q in enumerate(parts) if q.startswith(f'N{idx} ')][0]; parts[k] = parts[k].replace(f': {rule} ', f': {o} ')
            flip.append((x[0], ' ; '.join(parts))); break
    if len(flip) >= 60: break
byn = collections.defaultdict(list)
for x in pool: byn[len(rlean.stmt(x[0])[0])].append(x)
mis = []
for x in rng.sample(pool, 60):
    c = [y for y in byn[len(rlean.stmt(x[0])[0])] if rlean.stmt(y[0]) != rlean.stmt(x[0])]
    mis.append((rng.choice(c)[0], rlean.render(x[0], x[1])))
run = lambda it: sum(o for o, _, _ in rlean.check(it, per_file=200))
t0 = time.time()
c = dict(untouched_pass=run([(p, rlean.render(p, b)) for p, b, _ in unt]), flip_pass=run([(p, rlean.render(p, b)) for p, b in flip]),
         mismatch_pass=run(mis), sorry_pass=run([(unt[0][0], 'sorry')]), n=dict(untouched=len(unt), flip=len(flip), mismatch=len(mis), sorry=1))
print('controls', c, f'{time.time()-t0:.0f}s', flush=True); res['controls'] = c
def do(arm, pick):
    good, bad = [], 0
    for x in pick:
        try: good.append((x, rlean.render(x[0], x[1])))
        except Exception: bad += 1
    rr = rlean.check([(x[0], b) for x, b in good], per_file=150, size=True)
    sz = [s for (_, _, s) in rr]
    res['arms'][arm] = dict(n_counted=None, n_checked=len(pick), render_fail=bad, lean_ok=sum(o for o, _, _ in rr),
                            size_median=st.median([s for s in sz if s and s > 0]), lines_median=st.median(nl(x[1]) for x, _ in good),
                            fails=[(x[2], x[1], i) for (x, _), (o, i, _) in zip(good, rr) if not o][:10])
    print(arm, {k: v for k, v in res['arms'][arm].items() if k != 'fails'}, f'{time.time()-t0:.0f}s', flush=True)
    return [(x, s) for (x, _), (_, _, s) in zip(good, rr)]
for arm, items in sorted(ARMS.items()):
    seen = {}
    for x in sorted(items, key=lambda x: -nl(x[1])): seen.setdefault(x[2], x)
    longest = list(seen.values())[:30]; ids = set(map(id, longest)); rest = [x for x in items if id(x) not in ids]
    do(arm, longest + rng.sample(rest, min(120, len(rest)))); res['arms'][arm]['n_counted'] = len(items); print(arm, 'n_counted', len(items))
REF = [json.loads(l) for l in open('rv/ref_targets.jsonl')]
out = do('ref315', [(d['prompt'], d['proof'], d['name']) for d in REF])
tm = rvc.tmeta('c12', 0); res['ref_sizes'] = {x[2]: s for x, s in out}
pairs = [(s, tm['ref:' + x[2]]['term_size']) for x, s in out if s]
import numpy as np
from scipy.stats import spearmanr
res['ref_size_vs_tjscore'] = dict(n=len(pairs), spearman=round(float(spearmanr(*zip(*pairs))[0]), 3),
                                   ge9_agree=sum((a >= np.median([p[0] for p in pairs])) == (b >= 9) for a, b in pairs))
print('ref size vs tj_score', res['ref_size_vs_tjscore'])
EV = []
for run, sub in (('c12', 'tj'), ('c6', 'tj6')):
    for s in range(3):
        f = f'{rvc.D}/{sub}/targets/eventual_s{s}.jsonl'
        try: EV += [(d['prompt'], d['proof'], d['name']) for d in map(json.loads, open(f))]
        except FileNotFoundError: print('no', f)
do('eventual', rng.sample(EV, min(150, len(EV))))
json.dump(res, open('rv/recheck.json', 'w'), indent=0, default=int)
