#!/usr/bin/env python3
"""Reviewer: the ladder's LEAN_GATE_DUMP of knockout s1 (every distinct checked sample: prompt, literal lean_text, nd,
lean_ok, filter, lean).  (a) Lean-accepted literal texts: every one of a strict member + a seeded sample -> must pass;
(b) Lean-rejected texts (lean false) -> must fail; (c) PREFILTER-rejected texts (lean null: Lean never saw them), seeded
sample stratified by filter reason -> any Lean acceptance is a false reject of the run's gate.  Lean 4.34.1, literal text."""
import collections, gzip, json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C, rlean

RV = C.RV
fn = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/review/coe_big/dump_ko_s1.jsonl.gz')
FAM = json.load(open(f'{RV}/review_coe/out_families.json'))
HO = {r['name']: r for r in C.rows(f'{RV}/data/ladder/transfer.jsonl')}
TR = {r['name']: r for r in C.rows(f'{RV}/data/ladder/rl_targets.jsonl')}
STRICTP = {HO[n]['prompt'] for n in FAM['strict_heldout']} | {TR[n]['prompt'] for n in FAM['strict_trained']}
rng = random.Random(7)
K = {'acc': 400, 'rej': 400}
res_acc, res_rej = [], []
filt = collections.defaultdict(list)
cnt = collections.Counter(); strict_acc = []
seen = collections.Counter()
n = 0
with gzip.open(fn, 'rt') as f:
    for l in f:
        n += 1
        r = json.loads(l)
        lean = r.get('lean'); ok = r.get('lean_ok'); fr = r.get('filter')
        cnt[(str(lean), str(ok), str(fr)[:30])] += 1
        item = (r['prompt'], r['lean_text'])
        if lean is True:
            if r['prompt'] in STRICTP:
                strict_acc.append(item)
            seen['acc'] += 1
            if len(res_acc) < K['acc']:
                res_acc.append(item)
            elif rng.random() < K['acc'] / seen['acc']:
                res_acc[rng.randrange(K['acc'])] = item
        elif lean is False:
            seen['rej'] += 1
            if len(res_rej) < K['rej']:
                res_rej.append(item)
            elif rng.random() < K['rej'] / seen['rej']:
                res_rej[rng.randrange(K['rej'])] = item
        elif lean is None and fr:
            key = str(fr)
            seen['f:' + key] += 1
            L = filt[key]
            cap = 150
            if len(L) < cap:
                L.append(item)
            elif rng.random() < cap / seen['f:' + key]:
                L[rng.randrange(cap)] = item
print('dump lines', n)
for k, v in sorted(cnt.items(), key=lambda kv: -kv[1])[:25]:
    print('   lean/lean_ok/filter', k, v)
print('Lean-accepted texts of strict members:', len(strict_acc))
groups = [('acc_strict', x, True) for x in strict_acc] + [('acc_sample', x, True) for x in res_acc] + [('rej_sample', x, False) for x in res_rej]
for k, L in filt.items():
    groups += [(f'filter:{k}', x, False) for x in L]
texts = [g[1] for g in groups]
print('Lean items', len(texts), flush=True)
res = rlean.check_robust(texts, per_file=150, size=False)
out = collections.defaultdict(lambda: [0, 0, []])
for (g, (p, t), exp), (ok, info, sz) in zip(groups, res):
    o = out[g]; o[0] += 1; o[1] += ok
    if ok != exp:
        o[2].append((p, t[:400], info))
for g, (nn, acc, unexp) in sorted(out.items()):
    print(f'{g:40s} n {nn:5d} Lean-accepted {acc:5d} unexpected {len(unexp)}')
    for u in unexp[:5]:
        print('     ', u)
json.dump({g: {'n': v[0], 'accepted': v[1], 'unexpected': v[2]} for g, v in out.items()}, open(f'{RV}/review_coe/out_dumpcheck.json', 'w'), indent=1)
