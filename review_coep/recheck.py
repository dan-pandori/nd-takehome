"""review_coep/recheck.py -- Lean re-check of this run's counted proofs (own renderer for the ND strings of plain reads;
the literal accepted texts for guided reads), plus line counts and term sizes.

Per read: one random stored proof of EVERY solved member (so every count is backed by a Lean check), then extra random
proofs until each arm has >= 150 (all of them where the arm has fewer)."""
import json, os, sys, random, collections, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
import lean4

rng = random.Random(2026)
ARMS = {
    'knockout_r16_plain': [f'c1_ko_s{s}_{c}' for s in range(6) for c in ('std', 'dbl')],
    'dose1_r16_plain': [f'c1_dose1_s{s}_{c}' for s in range(3) for c in ('std', 'dbl')] + [f'c2_dose1_s{s}_x1' for s in range(3)],
    'full_s4_r16_plain': ['c1_full_s4_std', 'c1_full_s4_dbl'],
    'oldfull_pend_tb72_plain': [f'c3_oldfull_s{s}_pend_tb72' for s in range(3)],
}
items = []          # (arm, read, name, prompt, kind, text)
for arm, reads in ARMS.items():
    pool = []
    for rd in reads:
        rows = read_rows(f'{EVAL}/{rd}.jsonl.gz')
        for n, r in rows.items():
            if r['n_ok'] > 0:
                assert r['proofs'], (rd, n)
                pr = list(r['proofs'])
                k = rng.randrange(len(pr))
                items.append((arm, rd, n, r['prompt'], 'nd', pr[k]))
                pool += [(arm, rd, n, r['prompt'], 'nd', p) for j, p in enumerate(pr) if j != k]
    have = sum(1 for it in items if it[0] == arm)
    extra = max(0, 150 - have)
    items += rng.sample(pool, min(extra, len(pool)))
# guided dose reads: literal accepted texts
for s in range(3):
    rd = f'c2_dose1_s{s}_g0'
    pool = []
    for r in jl(f'{EVAL}/{rd}.rows.jsonl.gz'):
        if r['n_ok'] > 0:
            txt = list(r['accepted'])
            k = rng.randrange(len(txt))
            items.append(('dose1_r16_guided', rd, r['name'], r['prompt'], 'lit', txt[k]))
            pool += [('dose1_r16_guided', rd, r['name'], r['prompt'], 'lit', t) for j, t in enumerate(txt) if j != k]
    items += rng.sample(pool, 30)
# C4: every distinct success
for tag in ('ko_s1', 'ko_s3'):
    inp = {r['name']: r for r in jl(P(f'data/coe_paper/c4_{tag}.jsonl'))}
    acc = collections.Counter()
    for r in jl(P(f'artifacts/coe_paper/c4/{tag}.chunks.jsonl')):
        if r.get('chunk_summary'):
            continue
        for t in r['acc']:
            acc[(r['name'], t)] += 1
    for (n, t) in acc:
        items.append((f'c4_base_{tag}', 'c4', n, inp[n]['prompt'], 'nd', t))


def pruned(lines):
    """indices of lines the conclusion depends on (box citations pull in the whole box's cited lines)"""
    by = {l['idx']: l for l in lines}
    pos = {l['idx']: i for i, l in enumerate(lines)}
    need, stack = set(), [lines[-1]['idx']]
    while stack:
        k = stack.pop()
        if k in need:
            continue
        need.add(k)
        l = by[k]
        refs = list(l['refs'])
        if l['rule'] in ('IMPI', 'NEGI'):
            refs = [l['refs'][0], l['refs'][1]]
        stack += refs
    return [l for l in lines if l['idx'] in need]


def size(nd):
    ls = lean4.parse_nd(nd)
    pl = pruned(ls)
    term = sum(1 for l in pl if l['rule'] not in ('PR', 'R'))       # rule applications + box binders (AS)
    return len(ls), len(pl), term


chk, meta = [], []
render_fail = collections.Counter()
for it in items:
    arm, rd, n, prompt, kind, text = it
    h = lean4.stmt(prompt)
    if kind == 'nd':
        try:
            body = lean4.nd_to_tactic(text, prompt)
        except Exception as e:
            render_fail[arm] += 1
            body = 'sorry'
    else:
        body = text
    chk.append((h, body)); meta.append(it)
res = lean4.check(chk)
by_arm = collections.defaultdict(lambda: dict(n=0, ok=0, members=set(), reads=set(), lines=[], pruned=[], term=[]))
rej = []
for it, ok in zip(meta, res):
    arm, rd, n, prompt, kind, text = it
    a = by_arm[arm]
    a['n'] += 1; a['ok'] += ok; a['members'].add((rd, n)); a['reads'].add(rd)
    if not ok:
        rej.append(dict(arm=arm, read=rd, name=n, text=text[:400]))
    if kind == 'nd':
        L, PL, T = size(text)
        a['lines'].append(L); a['pruned'].append(PL); a['term'].append(T)
    else:
        a['lines'].append(text.count('have '))
med = lambda v: sorted(v)[len(v) // 2] if v else None
print('renderer failures', dict(render_fail))
out = {}
for arm, a in by_arm.items():
    print(f"{arm:26s} checked {a['n']:4d} Lean-accepted {a['ok']:4d}  (read, member) pairs {len(a['members']):4d} "
          f"reads {len(a['reads'])}  lines median {med(a['lines'])} max {max(a['lines'])}  "
          f"pruned median {med(a['pruned'])}  term size median {med(a['term'])} max {max(a['term']) if a['term'] else None}")
    out[arm] = dict(n=a['n'], ok=a['ok'], pairs=len(a['members']), lines_median=med(a['lines']),
                    pruned_median=med(a['pruned']), term_median=med(a['term']),
                    term_max=max(a['term']) if a['term'] else None)
print('rejected:', rej[:10])
json.dump(dict(arms=out, rejected=rej), open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_recheck.json'), 'w'), indent=1)
