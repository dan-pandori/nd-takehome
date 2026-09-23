#!/usr/bin/env python3
"""Run efficiency, step 5: the correctness gate.

Takes the raw token dumps of two sampling configurations over the SAME fixed workload, decodes each row to its
literal Lean text, sends every distinct text of the union to Lean once, and compares the two accepted sets:
identical (the pure-speed claim) or a strict superset (the terminator claim).  Also reports, for the reference
run, the decoded length of every accepted row — the evidence for or against a `max_new` cap.

  python3 ef_gate_compare.py --a base_rr --b f2_goal --out artifacts/ef/gate_compare_base_rr__f2_goal.json
"""
import os, sys, json, gzip, argparse, collections
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import load_ckpt
from lean_check import check
import lean_free
from nd_verify import verify_text

ap = argparse.ArgumentParser()
ap.add_argument('--a', required=True)
ap.add_argument('--b', required=True)
ap.add_argument('--ckpt', default='ckpts/ef/stage1_full_seq_s0.pt')
ap.add_argument('--targets', default='artifacts/ef/targets200.jsonl')
ap.add_argument('--k', type=int, default=256)
ap.add_argument('--out', default=None)
a = ap.parse_args()
out = a.out or f'artifacts/ef/gate_compare_{a.a}__{a.b}.json'

_, tok, _ = load_ckpt(a.ckpt, 'cpu')
tg = [json.loads(l) for l in open(a.targets)]
prompts = [t['prompt'] for t in tg for _ in range(a.k)]
names = [t['name'] for t in tg for _ in range(a.k)]


def texts_of(tag):
    d = np.load(f'artifacts/ef/{tag}_tokens.npz', allow_pickle=True)
    ids, dl = d['ids'], d['declen']
    tx = []
    for i in range(ids.shape[0]):
        tok.decode([int(x) for x in ids[i]])
        tx.append(tok.last_text)
    return tx, np.asarray(dl)


ta, da = texts_of(a.a)
tb, db = texts_of(a.b)
assert len(ta) == len(tb) == len(prompts), (len(ta), len(tb), len(prompts))

uni = {}
for p, t in list(zip(prompts, ta)) + list(zip(prompts, tb)):
    if t is not None:
        uni.setdefault((p, lean_free.canonical(t)), t)
items = list(uni.items())
print('distinct (prompt, canonical text) in the union:', len(items), flush=True)
res, wall, cpu = check([tok.statement(p) + ' ' + t for (p, _), t in items])
ok = {k: r for (k, _), r in zip(items, res)}
print(f'lean: {sum(1 for r in res if r["ok"])} accepted of {len(res)}; {wall:.1f}s wall {cpu:.1f}s proc', flush=True)

# nd_verify beside Lean, on the union (the agreement table the policy asks for)
agree = collections.Counter()
for ((p, ctx), t), r in zip(items, res):
    nd = tok.denote(p, t)
    nd_ok = bool(verify_text(p + ' ' + nd)[0]) if nd else False
    agree[(nd_ok, r['ok'])] += 1


def accepted(tx):
    s = set(); rows = []
    for i, t in enumerate(tx):
        if t is None:
            continue
        key = (prompts[i], lean_free.canonical(t))
        if ok[key]['ok']:
            s.add(key); rows.append(i)
    return s, rows


sa, ra = accepted(ta)
sb, rb = accepted(tb)
rec = {'a': a.a, 'b': a.b, 'n_samples': len(prompts), 'union_distinct_checked': len(items),
       'a_accepted_samples': len(ra), 'b_accepted_samples': len(rb),
       'a_accepted_distinct': len(sa), 'b_accepted_distinct': len(sb),
       'a_targets': len(set(names[i] for i in ra)), 'b_targets': len(set(names[i] for i in rb)),
       'identical': sa == sb, 'a_minus_b': len(sa - sb), 'b_minus_a': len(sb - sa),
       'a_targets_lost': sorted(set(names[i] for i in ra) - set(names[i] for i in rb)),
       'lean_wall_s': round(wall, 1), 'lean_proc_s': round(cpu, 1),
       'nd_verify_agreement': {'both_ok': agree[(True, True)], 'nd_ok_lean_rej': agree[(True, False)],
                               'lean_ok_nd_rej': agree[(False, True)], 'both_rej': agree[(False, False)]},
       'a_accept_declen': {'max': int(da[ra].max()) if ra else 0, 'p99': int(np.percentile(da[ra], 99)) if ra else 0,
                           'p95': int(np.percentile(da[ra], 95)) if ra else 0, 'mean': round(float(da[ra].mean()), 1) if ra else 0},
       'b_accept_declen': {'max': int(db[rb].max()) if rb else 0, 'p99': int(np.percentile(db[rb], 99)) if rb else 0,
                           'p95': int(np.percentile(db[rb], 95)) if rb else 0, 'mean': round(float(db[rb].mean()), 1) if rb else 0},
       'a_declen_max_all': int(da.max()), 'b_declen_max_all': int(db.max())}
ex = sorted(sb - sa)[:3]
rec['examples_new_in_b'] = [{'prompt': p, 'text': uni[(p, c)]} for p, c in ex]
json.dump(rec, open(out, 'w'), indent=1)
print(json.dumps({k: v for k, v in rec.items() if k != 'examples_new_in_b'}, indent=1))
print('wrote', out)
