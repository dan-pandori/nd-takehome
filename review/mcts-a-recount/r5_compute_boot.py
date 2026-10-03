#!/usr/bin/env python3
"""Reviewer recount (mcts-a), part 5: per-arm compute from the per-job files (search: stats wall / gpu_s / gen_tokens /
sampled / lean checks; sample: wall, attempts, Lean-checked `done` attempts, actions and tokens as far as state_eval's env
stats allow) and search/sample ratios; GPU utilisation means; group-C deltas with a stratified (by seed) bootstrap over
theorems, IQM over seeds.  Output: r5.json"""
import json, os, glob, re, random, statistics, collections
W = os.path.expanduser('~/review/mcts-a'); E = f'{W}/artifacts/mcts'; HERE = os.path.dirname(os.path.abspath(__file__))
rd = lambda f: [json.loads(l) for l in open(f) if l.strip()]
out = {}
comp = {}
for f in sorted(glob.glob(f'{E}/eval/*.json') + glob.glob(f'{E}/eval_x10/*.json')):
    lab = os.path.relpath(f, E)[:-5]
    if 'tune' in lab or lab.endswith('args'): continue
    J = json.load(open(f))
    if 'stats' in J:
        st = J['stats']
        comp[lab] = dict(wall=st['wall_s'], gpu_s=st['gpu_s'], lean_s=st.get('lean_s'), gen_tokens=st['gen_tokens'],
                         actions=st['sampled'], lean_checks=J['lean_checks'], util=J.get('gpu_util_mean'))
    else:
        env = J.get('env', {}); ee = env.get('env_end', {})
        steps = env.get('rows')      # sampled actions (= stop_eos + truncated); env['steps'] counts decode waves
        comp[lab] = dict(wall=J['wall_s'], attempts=sum(ee.values()), lean_checks_upper=ee.get('done'), actions=steps,
                         gen_tokens=round((env.get('action_declen_mean') or 0) * (steps or 0)),
                         action_declen_mean=env.get('action_declen_mean'), env_keys=sorted(env.keys())[:30])
        u = f.replace('.json', '.util')
        if os.path.exists(u):
            x = [float(l) for l in open(u) if l.strip()]
            comp[lab]['util'] = statistics.mean(x) if x else None
out['jobs'] = comp
agg = collections.defaultdict(lambda: collections.Counter())
for lab, c in comp.items():
    m = re.search(r'(eval(?:_x10)?)/s\d_(pend|r8)__(\w+?)__(\w+)$', lab)
    k = f'{m[1]}/{m[2]}/{m[3]}/{m[4]}'
    for kk in ('wall', 'gpu_s', 'gen_tokens', 'actions', 'lean_checks', 'attempts', 'lean_checks_upper'):
        if c.get(kk) is not None: agg[k][kk] += c[kk]
out['agg'] = {k: dict(v) for k, v in sorted(agg.items())}
utl = collections.defaultdict(list)
for lab, c in comp.items():
    if c.get('util') is not None: utl[lab.rsplit('__', 1)[1] + ('_x10' if 'x10' in lab else '')].append(c['util'])
out['util'] = {k: dict(n=len(v), mean=round(statistics.mean(v), 1), min=round(min(v), 1), max=round(max(v), 1)) for k, v in utl.items()}

# group C bootstrap
def solved(lab): return {r['name']: bool(r['solved']) for r in rd(f'{E}/{lab}.jsonl')}
bs = {}
for c in ('r8', 'pend'):
    for arm in ('value', 'prior'):
        per = []
        for s in range(3):
            a = solved(f'eval/s{s}_{c}__C__{arm}'); b = solved(f'eval/s{s}_{c}__C__sample')
            per.append([int(a[n]) - int(b[n]) for n in a])
        d = [sum(x) for x in per]
        rng = random.Random(0); boots = []
        for _ in range(10000):
            boots.append(sum(sum(rng.choice(x) for _ in x) for x in per) / 3)
        boots.sort()
        iqm = sorted(d)[1] if len(d) == 3 else None       # IQM of 3 values = the middle one (25 % trimmed each side)
        bs[f'{c}/{arm}-sample'] = dict(per_seed=d, mean=round(sum(d) / 3, 3), iqm_seeds=iqm,
                                       boot95_mean_per_seed=[boots[250], boots[9750]])
for s in range(3):
    pass
x = []
for s in range(3):
    a = solved(f'eval_x10/s{s}_r8__C__value'); b = solved(f'eval_x10/s{s}_r8__C__sample')
    x.append([int(a[n]) - int(b[n]) for n in a])
rng = random.Random(0); boots = sorted(sum(sum(rng.choice(v) for _ in v) for v in x) / 3 for _ in range(10000))
bs['x10/r8/value-sample'] = dict(per_seed=[sum(v) for v in x], mean=round(sum(sum(v) for v in x) / 3, 3), boot95_mean_per_seed=[boots[250], boots[9750]])
out['boot'] = bs
json.dump(out, open(f'{HERE}/r5.json', 'w'), indent=1)
print(json.dumps({k: out[k] for k in ('util', 'boot')}, indent=0)[:3000])
for k, v in out['agg'].items():
    print(k, v)
print(comp['eval/s0_r8__C__sample'])
