#!/usr/bin/env python3
"""Reviewer Lean re-check of counted proofs (grpo-best).  Per arm: every distinct counted proof of a group-C theorem in
the arm's last read (r8; distinct r4), both sample seeds, plus a seeded random sample of other counted proofs, to
>= 150 per arm.  Controls first: untouched (pass), recorded Lean-rejected samples (fail), Or.inl<->Or.inr flip at the
ORI line (mostly fail), proof paired with another theorem of equal premise count (fail), sorry (fail).
Also: term size (Expr nodes) and ND line count of every re-checked proof."""
import json, os, random, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rlean
R = os.path.expanduser('~/review/grpo-best/artifacts/gb')
rng = random.Random(20261002)
groups = {}
exec(open(os.path.join(os.path.dirname(__file__), 'groups_only.py')).read())   # defines groups[s][name]

def files(arm, s, ck, x):
    if arm == 'EI':
        return [f'{R}/ei_eval/s{s}_{ck}__{p}_x{x}.jsonl' for p in ('tb72', 'h250')]
    return [f'{R}/eval/gb_{arm}_s{s}_{ck}__{p}_x{x}.jsonl' for p in ('tb72', 'h250')]

items = []      # (arm, tag, prompt, nd, expect, stored_len)
fails_lean = []
for arm in ('EI', 'default', 'unlikely', 'passk', 'distinct'):
    ck = 'r4' if arm == 'distinct' else 'r8'
    cpool, opool = [], []
    for s in (0, 1, 2):
        for x in (0, 1):
            for f in files(arm, s, ck, x):
                for l in open(f):
                    r = json.loads(l)
                    for p, wl in zip(r['proofs'], r['written_lens']):
                        (cpool if groups[s][r['name']] == 'C' else opool).append((r['prompt'], p, wl, f'{arm} s{s} {ck} x{x} {r["name"]}'))
                    if r['fail_example'] and r['reasons'] and r['reasons'][0] == 'lean rejected' and len(fails_lean) < 400:
                        fails_lean.append((r['prompt'], r['fail_example'].split('LEANREJ ', 1)[-1]))
    need = max(150 - len(cpool), 100)
    pick = cpool + rng.sample(opool, need)
    for pr, p, wl, tag in pick:
        items.append((arm, tag, pr, p, True, wl))
    print(arm, 'C proofs', len(cpool), 'other sampled', need, file=sys.stderr)

# controls
ctrl = []
base = [it for it in items if it[0] != 'EI']
for it in rng.sample(base, 60):
    ctrl.append(('ctl_untouched', it[1], it[2], it[3], True, it[5]))
# recorded lean-rejected fail_example: only those whose first reason is 'lean rejected' AND fail_example is that sample
# (fail_example is the first failing sample; reasons[0] is its reason)
for pr, p in rng.sample(fails_lean, 60):
    ctrl.append(('ctl_leanrej', '', pr, p, False, None))
flips = [it for it in base if ' ORI1 ' in it[3] or ' ORI2 ' in it[3]]
for it in rng.sample(flips, 60):
    ctrl.append(('ctl_flip', it[1], it[2], it[3], False, None))
bynp = collections.defaultdict(list)
for it in base:
    bynp[len(rlean.stmt(it[2])[0])].append(it)
for it in rng.sample(base, 60):
    other = [o for o in bynp[len(rlean.stmt(it[2])[0])] if o[2] != it[2]]
    o = rng.choice(other)
    ctrl.append(('ctl_mismatch', it[1], o[2], it[3], False, None))

def body(it):
    if it[0] == 'ctl_flip':
        return rlean.render(it[2], it[3], flip=('Or.inl', 'Or.inr'))
    return rlean.render(it[2], it[3])

allit = ctrl + items
texts = []
for it in allit:
    try:
        texts.append((it[2], body(it)))
    except Exception as e:
        texts.append((it[2], 'exact sorry'))   # unrenderable -> fails (sorryAx)
        print('render fail', it[0], it[1], e, file=sys.stderr)
texts.append(('THM SEQ ( P > P ) PRF', 'exact sorry')); allit.append(('ctl_sorry', '', '', '', False, None))
res = rlean.check_robust(texts, per_file=150, size=True)
out = collections.defaultdict(lambda: {'n': 0, 'pass': 0, 'fails': []})
sizes = collections.defaultdict(list); lines = collections.defaultdict(list); lenmis = 0
for it, (ok, info, sz) in zip(allit, res):
    o = out[it[0]]; o['n'] += 1; o['pass'] += ok
    if ok != it[4]: o['fails'].append((it[1], it[2], it[3], info))
    if it[4] and it[0] in ('EI', 'default', 'unlikely', 'passk', 'distinct'):
        sizes[it[0]].append(sz); nl = it[3].count(';'); lines[it[0]].append(nl)
        if it[5] is not None and nl != it[5]: lenmis += 1
for k, v in out.items():
    print(f'{k:14s} n {v["n"]:4d} Lean-accepted {v["pass"]:4d}  unexpected {len(v["fails"])}')
    for f in v['fails'][:5]: print('   ', f)
import statistics
for k in sizes:
    s = [x for x in sizes[k] if x is not None and x >= 0]
    print(f'{k:9s} term size median {statistics.median(s)} max {max(s)} (n {len(s)});  ND lines median {statistics.median(lines[k])} max {max(lines[k])}')
print('stored written_len != own ND line count:', lenmis)
json.dump({k: {'n': v['n'], 'pass': v['pass'], 'unexpected': v['fails']} for k, v in out.items()},
          open(os.path.expanduser('~/review/grpo-best/review_gb/recheck.json'), 'w'), indent=0)
