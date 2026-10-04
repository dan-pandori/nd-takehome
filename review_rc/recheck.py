#!/usr/bin/env python3
"""Reviewer (rl-continue) Lean re-check with my renderer/harness rlean.py (reviewer code, rl-continue-cap6 kit).
Negative controls first; then per seed:
  new_tg : first-found proof of EVERY target newly solved r9-r16 + 100 random r9-r16 target rows (reservoir);
  new_tr : first-found proof of every transfer theorem newly solved r9-r16 + 30 random r9-r16 transfer rows;
  r16_read: every proof of every group-C theorem solved in the r16 x1 read + 100 random r16 tb72 proofs
            + 50 random rr1316/long2 r16 proofs.
Term sizes (Expr nodes) + line counts for the new-target first proofs and the C proofs."""
import json, os, random, sys, collections, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rlean
R = os.path.expanduser('~/review/rl-continue'); A = f'{R}/artifacts/rc'; D = os.path.expanduser('~/review/rc_data')
rng = random.Random(20261004)
def rd(f):
    for l in open(f):
        if l.strip(): yield json.loads(l)
G = json.load(open(f'{R}/review_rc/rv/groupc.json'))
def nl(p): return p.count(' ; ')
run = lambda it, **kw: rlean.check(it, per_file=100, **kw)
res = {'arms': {}, 'sizes': {}}; t0 = time.time()
ev = {s: {p: {r['name']: r for r in rd(f'{A}/eval/s{s}_r16__{p}_x{x}.jsonl')} for p, x in (('tb72', 1), ('h250', 1), ('rr1316', 0), ('long2', 0))} for s in (0, 1, 2)}
def proofs(r): return r['proofs'] if isinstance(r['proofs'], list) else eval(r['proofs'])
pool = [(r['prompt'], pr) for s in ev for p in ev[s] for r in ev[s][p].values() for pr in proofs(r)]
rej = [(r['prompt'], r['fail_example'][8:]) for s in ev for p in ev[s] for r in ev[s][p].values() if (r.get('fail_example') or '').startswith('LEANREJ ')]
unt = rng.sample(pool, 60)
flip = [x for x in rng.sample(pool, 3000) if 'ORI' in x[1]][:60]
byn = collections.defaultdict(list)
for x in rng.sample(pool, 20000): byn[len(rlean.stmt(x[0])[0])].append(x)
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
rj, rjbad = rend(rng.sample(rej, min(200, len(rej))))
c = {'untouched_pass': cnt(rend(unt)[0]), 'leanrej_pass': cnt(rj), 'leanrej_rendered': len(rj), 'leanrej_render_fail': rjbad,
     'flip_pass': cnt([(p, rlean.render(p, b, flip=('Or.inl', 'Or.inr'))) for p, b in flip]),
     'mismatch_pass': cnt(mis), 'sorry_pass': cnt([(unt[0][0], 'sorry')]),
     'n': dict(untouched=len(unt), leanrej_avail=len(rej), flip=len(flip), mismatch=len(mis), sorry=1)}
print('controls', c, f'{time.time()-t0:.0f}s', flush=True); res['controls'] = c
json.dump(res, open(f'{R}/review_rc/rv/recheck.json', 'w'), indent=0)
if '--controls' in sys.argv: sys.exit()
for s in (0, 1, 2):
    for arm, pre, nrand in (('new_tg', 'found', 100), ('new_tr', 'found_transfer', 30)):
        s8 = {x['name'] for x in rd(f'{D}/s{s}/{pre}_8.jsonl')}
        firsts = {}; res_s = []; n = 0
        for x in rd(f'{D}/s{s}/{pre}_16.jsonl'):
            if x['round'] < 9: continue
            n += 1
            if x['name'] not in s8 and (x['name'] not in firsts or x['round'] < firsts[x['name']]['round']): firsts[x['name']] = x
            if len(res_s) < nrand: res_s.append(x)
            else:
                j = rng.randrange(n)
                if j < nrand: res_s[j] = x
        fl = list(firsts.values()); pick = fl + res_s
        good, bad = rend([(x['prompt'], x['proof']) for x in pick])
        rr = run(good, size=True)
        fails = [(i, g[1][:200]) for g, (o, i, _) in zip(good, rr) if not o]
        res['arms'][f's{s}_{arm}'] = dict(n_rows_r9_16=n, n_firsts=len(firsts), n_checked=len(pick), render_fail=bad, lean_ok=sum(o for o, _, _ in rr), fails=fails[:10])
        res['sizes'][f's{s}_{arm}_first'] = [(x['name'], x.get('L_true'), nl(x['proof']), x['written'], sz) for x, (o, i, sz) in zip(fl, rr[:len(fl)])]
        res['sizes'][f's{s}_{arm}_rand'] = [(x['name'], x.get('L_true'), nl(x['proof']), x['written'], sz) for x, (o, i, sz) in zip(res_s, rr[len(fl):])]
        print(f's{s}_{arm}', {k: v for k, v in res['arms'][f's{s}_{arm}'].items() if k != 'fails'}, f'{time.time()-t0:.0f}s', flush=True)
        json.dump(res, open(f'{R}/review_rc/rv/recheck.json', 'w'), indent=0)
    Cs = G[str(s)]['r16']['C_solved']
    citems = [(n, ev[s][n.split(':')[0]][n.split(':')[1]]['prompt'], pr) for n in Cs for pr in proofs(ev[s][n.split(':')[0]][n.split(':')[1]])]
    tbp = [(r['prompt'], pr) for r in ev[s]['tb72'].values() for pr in proofs(r)]
    rrp = [(r['prompt'], pr) for p in ('rr1316', 'long2') for r in ev[s][p].values() for pr in proofs(r)]
    pick = [(p, b) for _, p, b in citems] + rng.sample(tbp, 100) + rng.sample(rrp, 50)
    good, bad = rend(pick)
    rr = run(good, size=True)
    res['arms'][f's{s}_r16_read'] = dict(n_C_proofs=len(citems), n_checked=len(pick), render_fail=bad, lean_ok=sum(o for o, _, _ in rr),
                                         fails=[(i, g[1][:200]) for g, (o, i, _) in zip(good, rr) if not o][:10])
    res['sizes'][f's{s}_C_r16'] = [(n, nl(b), sz) for (n, _, b), (o, i, sz) in zip(citems, rr[:len(citems)])]
    print(f's{s}_r16_read', {k: v for k, v in res['arms'][f's{s}_r16_read'].items() if k != 'fails'}, f'{time.time()-t0:.0f}s', flush=True)
    json.dump(res, open(f'{R}/review_rc/rv/recheck.json', 'w'), indent=0)
