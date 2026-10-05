#!/usr/bin/env python3
"""Reviewer Lean re-check of counted proofs, capability-defs.  Arms: J2 (standard caps, all stages), J2 doubled caps,
J9, J10, J3 guided (literal Lean text) cap 12 / cap 6, J4, J5, J6, J6b, J7, known proofs F(t) that carry pend's
known-proof sum on created-set theorems (top 3 per theorem), references, and r8's x0 proofs on B (the counted RL
successes that define the equal-k set).  Controls first: untouched (pass), the run's recorded LEANREJ samples (fail),
Or.inl<->Or.inr flip at the ORI line (mostly fail), proof paired with another theorem of equal premise count (fail),
sorry (fail); for literal texts: literal paired with another theorem (fail).  Term size + ND line count of each."""
import json, os, sys, random, glob, gzip, collections, math, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rlean, rv_load as L
CD = L.CD; rng = random.Random(20261005)
PR = L.prompts()
LN33 = math.log(33)
S = json.load(open(f'{L.RV}/review_cd/out_sets.json'))
Bset = {s: set(S['eqk'][f's{s}_r8_x0']) | set(S['eqk'][f's{s}_r16_x1']) for s in (0, 1, 2)}
items = []          # (arm, tag, prompt, text, kind 'nd'|'lit', expect)
rej = []            # recorded LEANREJ samples (prompt, nd)
def add_reads(arm, files, need, prefer=lambda s, n: False):
    pref, other = [], []
    for p in files:
        s = int(os.path.basename(p).split('_')[0][-1]) if os.path.basename(p)[0] == 's' else int(os.path.basename(p).split('_')[1][-1])
        for r in L.rows(p):
            pr = r.get('prompt') or PR[r['name']]
            for pf in r.get('proofs') or []:
                (pref if prefer(s, r['name']) else other).append((arm, f'{os.path.basename(p)}:{r["name"]}', pr, pf, 'nd', True))
            fe = r.get('fail_example') or ''
            if fe.startswith('LEANREJ '):
                rej.append((pr, fe[len('LEANREJ '):], f'{arm}:{os.path.basename(p)}:{r["name"]}'))
    pref = list({(x[2], x[3]): x for x in pref}.values()); other = list({(x[2], x[3]): x for x in other}.values())
    take = pref + rng.sample(other, max(0, min(len(other), need - len(pref))))
    items.extend(take)
    print(f'{arm:8s}: preferred {len(pref)}, others {len(other)} -> {len(take)}', file=sys.stderr)
j2files = [p for p in glob.glob(f'{CD}/j2/s*_*.jsonl') if not os.path.basename(p).split('_')[1].startswith('t')]
add_reads('j2', j2files, 200, prefer=lambda s, n: n in Bset[s])
add_reads('j2t', glob.glob(f'{CD}/j2/s*_t*.jsonl'), 10)
add_reads('j9', [p for p in glob.glob(f'{CD}/j9/s*_k*.jsonl') if not p.endswith('.full.jsonl')], 10)
add_reads('j10', glob.glob(f'{CD}/j10/s*_c*.jsonl'), 150)
add_reads('j4', glob.glob(f'{CD}/j4/s*__*.jsonl'), 150)
add_reads('j5', glob.glob(f'{CD}/j5/*.jsonl'), 150, prefer=lambda s, n: False)
add_reads('j6', glob.glob(f'{CD}/j6/s*__*.jsonl'), 150)
add_reads('j6b', glob.glob(f'{CD}/j6b/s*__*.jsonl'), 120)
add_reads('j7', glob.glob(f'{CD}/j7/s*__*.jsonl'), 150, prefer=lambda s, n: n in set(S['eqk'][f's{s}_r8_x0']))
# r8 x0 proofs on B (one per theorem-seed, the counted RL success that puts t in B)
for s in (0, 1, 2):
    d = L.both(12, s, 'r8', 0)
    for n in S['eqk'][f's{s}_r8_x0']:
        items.append(('eqk_r8', f's{s}_r8_x0:{n}', PR[n], rng.choice(d[n][2]), 'nd', True))
# J3 guided literal texts
for arm, pat in (('j3c12', 's*_logical.rows.jsonl.gz'), ('j3c6', 'c6_s*_logical.rows.jsonl.gz')):
    pref, other = [], []
    for p in glob.glob(f'{CD}/j3/{pat}'):
        b = os.path.basename(p)
        if arm == 'j3c12' and b.startswith('c6_'): continue
        s = int(b.split('_')[1 if b.startswith('c6_') else 0][-1]); ck = b.split('_')[2 if b.startswith('c6_') else 1]
        for r in L.rows(p):
            for t in r.get('accepted') or {}:
                x = (arm, f'{b}:{r["name"]}', r['prompt'], t, 'lit', True)
                (pref if (arm == 'j3c12' and ck == 'pend' and r['name'] in Bset[s]) else other).append(x)
    take = pref + rng.sample(other, max(0, 200 - len(pref)))
    items.extend(take); print(f'{arm}: preferred {len(pref)} others {len(other)} -> {len(take)}', file=sys.stderr)
# known proofs carrying pend's sum on B theorems: top 3 per (seed, theorem) by pend T0.8 term
for s in (0, 1, 2):
    tg = {}
    for p in sorted(glob.glob(f'{CD}/j1/targets_s{s}_p*.jsonl')) + [f'{CD}/j1/s2targets_s{s}.jsonl']:
        for r in L.rows(p):
            tg[r['tid']] = r['proof']
    sc = collections.defaultdict(dict)
    for p in sorted(glob.glob(f'{CD}/j1/b1_s{s}_p*/compact.jsonl.gz')):
        for r in L.rows(p):
            if r['replay_ok']: sc[r['name']][r['tid']] = r['sc'][f's{s}_pend'][2] - LN33
    for r in L.rows(f'{CD}/j1/b33_s{s}/compact.jsonl.gz'):
        if r['replay_ok']: sc[r['name']][r['tid']] = r['sc'][f's{s}_pend'][2]
    for n in sorted(Bset[s]):
        if n not in sc: continue
        for tid, v in sorted(sc[n].items(), key=lambda kv: -kv[1])[:3]:
            items.append(('ftop', f's{s}:{n}:{tid}:{v:.2f}', PR[n], tg[tid], 'nd', True))
for r in L.rows(os.path.expanduser('~/work/trajectory/data/tj/ref_targets.jsonl')):
    items.append(('ref', r['name'], PR[r['name']], r['proof'], 'nd', True))
print('items', len(items), collections.Counter(i[0] for i in items), file=sys.stderr)
# ---------- controls
ctrl = []
nd_items = [it for it in items if it[4] == 'nd']
for it in rng.sample(nd_items, 60):
    ctrl.append(('ctl_untouched', it[1], it[2], it[3], 'nd', True))
j9rej = [x for x in rej if x[2].startswith('j9:')]
rest = [x for x in rej if x not in j9rej]
for pr, nd, tag in j9rej + rng.sample(rest, min(len(rest), 150 - len(j9rej))):
    ctrl.append(('ctl_leanrej', tag, pr, nd, 'nd', False))
flips = [it for it in nd_items if ' ORI1 ' in it[3] or ' ORI2 ' in it[3]]
for it in rng.sample(flips, 60):
    ctrl.append(('ctl_flip', it[1], it[2], it[3], 'flip', False))
bynp = collections.defaultdict(list)
for it in items:
    bynp[len(rlean.stmt(it[2])[0])].append(it)
for it in rng.sample(nd_items, 60):
    o = rng.choice([o for o in bynp[len(rlean.stmt(it[2])[0])] if o[2] != it[2]])
    ctrl.append(('ctl_mismatch', it[1], o[2], it[3], 'nd', False))
lit = [it for it in items if it[4] == 'lit']
for it in rng.sample(lit, 40):
    o = rng.choice([o for o in bynp[len(rlean.stmt(it[2])[0])] if o[2] != it[2]])
    ctrl.append(('ctl_lit_mismatch', it[1], o[2], it[3], 'lit', False))
allit = ctrl + items
texts = []
for it in allit:
    try:
        if it[4] == 'lit': body = it[3]
        elif it[4] == 'flip': body = rlean.render(it[2], it[3], flip=('Or.inl', 'Or.inr'))
        else: body = rlean.render(it[2], it[3])
    except Exception as e:
        body = 'exact sorry'; print('render fail', it[0], it[1], repr(e)[:80], file=sys.stderr)
    texts.append((it[2], body))
texts.append(('THM SEQ ( P > P ) PRF', 'exact sorry')); allit.append(('ctl_sorry', '', '', '', 'nd', False))
print('Lean items', len(texts), file=sys.stderr, flush=True)
res = rlean.check_robust(texts, per_file=150, size=True)
out = collections.defaultdict(lambda: {'n': 0, 'pass': 0, 'unexpected': []})
sizes = collections.defaultdict(list); lines = collections.defaultdict(list)
rows = []
for it, (ok, info, sz) in zip(allit, res):
    o = out[it[0]]; o['n'] += 1; o['pass'] += ok
    if ok != it[5]: o['unexpected'].append((it[1], it[2], it[3][:300], info))
    if it[5] and not it[0].startswith('ctl'):
        if sz is not None and sz >= 0: sizes[it[0]].append(sz)
        lines[it[0]].append(it[3].count(';') if it[4] == 'nd' else None)
    rows.append({'arm': it[0], 'tag': it[1], 'ok': ok, 'info': info, 'size': sz})
for k, v in out.items():
    print(f'{k:16s} n {v["n"]:4d} Lean-accepted {v["pass"]:4d}  unexpected {len(v["unexpected"])}')
    for f in v['unexpected'][:6]: print('    ', f)
for k in sizes:
    s = sizes[k]; l = [x for x in lines[k] if x is not None]
    print(f'{k:8s} term size median {statistics.median(s)} max {max(s)} (n {len(s)})' + (f'; ND lines median {statistics.median(l)} max {max(l)}' if l else ''))
json.dump({'summary': {k: {'n': v['n'], 'pass': v['pass'], 'unexpected': v['unexpected']} for k, v in out.items()}, 'rows': rows},
          open(f'{L.RV}/review_cd/out_recheck.json', 'w'))
