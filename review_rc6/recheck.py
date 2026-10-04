#!/usr/bin/env python3
"""Reviewer (rl-continue-cap6) Lean re-check.  Renderer/harness = reviewer code rlean.py (review_tj6 kit; independent of the
executor).  Negative controls first; then per seed:
  new_tg: the first-found proof of EVERY target newly solved in r9-r16, + 100 random r9-r16 target proofs;
  new_tr: the first-found proof of every transfer theorem newly solved in r9-r16 (cap 120) + 30 random;
  r16_read: every proof of every group-C theorem solved in the r16 read (tb72 + h250C), + 100 random r16 tb72 proofs.
Term size (Expr nodes of the elaborated theorem value) and line counts for new_tg first proofs and C proofs."""
import json, os, random, sys, collections, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rlean
R = os.path.expanduser('~/review/rl-continue-cap6'); A = f'{R}/artifacts/rc6'; D = os.path.expanduser('~/review/rc6_data')
rng = random.Random(20261004)
def rd(f): return [json.loads(l) for l in open(f) if l.strip()]
G = json.load(open(f'{R}/review_rc6/rv/groupc.json'))
def nl(p): return p.count(' ; ')
run = lambda it, **kw: rlean.check(it, per_file=100, **kw)
res = {'arms': {}, 'sizes': {}}
t0 = time.time()
# --- controls
evrows = {s: {p: {r['name']: r for r in rd(f'{A}/eval/s{s}_r16__{p}_x1.jsonl')} for p in ('tb72', 'h250C')} for s in (0, 1, 2)}
pool = [(r['prompt'], pr) for s in (0, 1, 2) for p in evrows[s] for r in evrows[s][p].values() for pr in r['proofs']]
rej = [(r['prompt'], r['fail_example'][8:]) for s in (0, 1, 2) for p in evrows[s] for r in evrows[s][p].values() if (r.get('fail_example') or '').startswith('LEANREJ ')]
unt = rng.sample(pool, 60)
flip = [x for x in rng.sample(pool, 1500) if 'ORI' in x[1]][:60]
byn = collections.defaultdict(list)
for x in pool: byn[len(rlean.stmt(x[0])[0])].append(x)
mis = []
for x in rng.sample(pool, 60):
    c = [y for y in byn[len(rlean.stmt(x[0])[0])] if rlean.stmt(y[0]) != rlean.stmt(x[0])]
    if c: mis.append((rng.choice(c)[0], rlean.render(x[0], x[1])))
def rend(items):
    good, bad = [], 0
    for p, b in items:
        try: good.append((p, rlean.render(p, b)))
        except Exception: bad += 1
    return good, bad
cnt = lambda it: sum(o for o, _, _ in run(it))
rj, rjbad = rend(rej)
c = {'untouched_pass': cnt(rend(unt)[0]), 'leanrej_pass': cnt(rj), 'leanrej_render_fail': rjbad,
     'flip_pass': cnt([(p, rlean.render(p, b, flip=('Or.inl', 'Or.inr'))) for p, b in flip]),
     'mismatch_pass': cnt(mis), 'sorry_pass': cnt([(unt[0][0], 'sorry')]),
     'n': dict(untouched=len(unt), leanrej=len(rej), flip=len(flip), mismatch=len(mis), sorry=1)}
print('controls', c, f'{time.time()-t0:.0f}s', flush=True); res['controls'] = c
if '--controls' in sys.argv: sys.exit()
# --- arms
for s in (0, 1, 2):
    for arm, pre in (('new_tg', 'found'), ('new_tr', 'found_transfer')):
        s8 = {x['name'] for x in rd(f'{D}/s{s}/{pre}_8.jsonl')}
        f16 = [x for x in rd(f'{D}/s{s}/{pre}_16.jsonl') if x['round'] >= 9]
        firsts = {}
        for x in sorted(f16, key=lambda x: x['round']):
            if x['name'] not in s8: firsts.setdefault(x['name'], x)
        fl = list(firsts.values())
        if arm == 'new_tr': fl = fl[:120]
        rest = [x for x in f16 if x is not firsts.get(x['name'])]
        pick = fl + rng.sample(rest, 100 if arm == 'new_tg' else 30)
        good, bad = rend([(x['prompt'], x['proof']) for x in pick])
        rr = run(good, size=(arm == 'new_tg'))
        fails = [(i, g[1][:200]) for g, (o, i, _) in zip(good, rr) if not o]
        res['arms'][f's{s}_{arm}'] = dict(n_rows_r9_16=len(f16), n_firsts=len(firsts), n_checked=len(pick), render_fail=bad, lean_ok=sum(o for o, _, _ in rr), fails=fails[:10])
        if arm == 'new_tg':
            res['sizes'][f's{s}_new_tg_first'] = [(x['name'], x['L_true'], nl(x['proof']), x['written'], sz) for x, (o, i, sz) in zip(pick[:len(fl)], rr[:len(fl)])]
        print(f's{s}_{arm}', {k: v for k, v in res['arms'][f's{s}_{arm}'].items() if k != 'fails'}, f'{time.time()-t0:.0f}s', flush=True)
    # r16 read: every proof of each solved C theorem, + 100 random tb72 proofs
    Cs = G[str(s)]['r16']['C_solved']
    cp = [(n, evrows[s]['tb72' if n.startswith('tb72:') else 'h250C'][n.split(':')[1]]) for n in Cs]
    citems = [(n, r['prompt'], pr) for n, r in cp for pr in r['proofs']]
    tbp = [(r['prompt'], pr) for r in evrows[s]['tb72'].values() for pr in r['proofs']]
    pick = [(p, b) for _, p, b in citems] + rng.sample(tbp, min(100, len(tbp)))
    good, bad = rend(pick)
    rr = run(good, size=True)
    res['arms'][f's{s}_r16_read'] = dict(n_C_proofs=len(citems), n_checked=len(pick), render_fail=bad, lean_ok=sum(o for o, _, _ in rr),
                                         fails=[(i, g[1][:200]) for g, (o, i, _) in zip(good, rr) if not o][:10])
    res['sizes'][f's{s}_C_r16'] = [(n, nl(b), sz) for (n, _, b), (o, i, sz) in zip(citems, rr[:len(citems)])]
    print(f's{s}_r16_read', {k: v for k, v in res['arms'][f's{s}_r16_read'].items() if k != 'fails'}, f'{time.time()-t0:.0f}s', flush=True)
    json.dump(res, open(f'{R}/review_rc6/rv/recheck.json', 'w'), indent=0)
