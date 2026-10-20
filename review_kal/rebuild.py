#!/usr/bin/env python3
"""Rebuild K12-Kalmár (and every read set's algorithm proof) with the reviewer's own construction (kc.kalmar) and compare
with the stored records: ND proof string equality, per-action step-type tags, line / action counts.  Also dataset
statistics from the reviewer's own parse of the stored proofs.

  python3 review_kal/rebuild.py [--n 3000] [--all]   -> out/rebuild.json
"""
import argparse, ast, collections, json, os, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc

ap = argparse.ArgumentParser()
ap.add_argument('--n', type=int, default=3000)
ap.add_argument('--all', action='store_true')
ap.add_argument('--out', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'rebuild.json'))
a = ap.parse_args()
D = os.path.join(kc.ROOT, 'data', 'kalmar')


def tags_of(r):
    t = r.get('kal_tags') or r.get('tags')
    return ast.literal_eval(t) if isinstance(t, str) else t


def compare(r, res):
    """-> dict of mismatches (empty = identical)"""
    bad = {}
    mine = kc.kalmar(r['prompt'])
    if mine is None:
        return {'invalid': True}, None
    if mine['proof'] != r['proof']:
        bad['proof'] = True
    tg = tags_of(r)
    if tg is not None and [t for t, d in mine['acts']] != list(tg):
        bad['tags'] = True
    return bad, mine


res = {}
t0 = time.time()
# 1. the training set: a seeded sample (or all)
n_train = 155000
pick = set(range(n_train)) if a.all else set(random.Random(20261020).sample(range(n_train), a.n))
c = collections.Counter(); ex = []
st = collections.defaultdict(list)
k12_lines = []
nseen = 0
for i, line in enumerate(kc.opener(os.path.join(D, 'train_kal_sl.jsonl.gz'))):
    nseen += 1
    if i not in pick:
        continue
    r = json.loads(line)
    bad, mine = compare(r, res)
    c['n'] += 1
    for k in bad:
        c['bad_' + k] += 1
    if bad and len(ex) < 5:
        ex.append({'i': i, 'bad': list(bad)})
    if mine:
        st['lines'].append(mine['n_lines']); st['acts'].append(len(mine['acts'])); st['depth'].append(mine['max_depth'])
        st['atoms'].append(mine['n_atoms'])
    k12_lines.append(r['k12_proof'].count(';'))
    # stored stats consistency
    if r['n_lines'] != r['proof'].count(';'):
        c['stored_n_lines_mismatch'] += 1
    if r['n_actions'] != r['n_lines'] + 1:
        c['stored_actions_not_lines+1'] += 1
assert nseen == n_train, nseen


def summ(x):
    x = sorted(x)
    if not x:
        return None
    return {'n': len(x), 'mean': round(sum(x) / len(x), 2), 'p50': x[len(x) // 2], 'p99': x[min(len(x) - 1, int(0.99 * len(x)))],
            'max': x[-1]}


res['train'] = {'n_file': n_train, 'checked': dict(c), 'examples': ex, 'secs': round(time.time() - t0, 1),
                'lines': summ(st['lines']), 'actions': summ(st['acts']), 'nd_depth': summ(st['depth']),
                'atoms': dict(collections.Counter(st['atoms'])), 'k12_lines': summ(k12_lines)}
print('train', json.dumps(res['train']), flush=True)

# 2. every read set's records
for fn in sorted(os.listdir(D)):
    if not fn.endswith('.jsonl') or fn.startswith('train') or fn.startswith('textbook72'):
        continue
    c = collections.Counter(); ex = []
    acts = []
    for r in kc.rows(os.path.join(D, fn)):
        if 'proof' not in r or 'prompt' not in r:
            c['no_proof'] += 1
            continue
        bad, mine = compare(r, res)
        c['n'] += 1
        for k in bad:
            c['bad_' + k] += 1
        if bad and len(ex) < 3:
            ex.append({'name': r.get('name'), 'bad': list(bad)})
        if mine:
            acts.append(len(mine['acts']))
            if r.get('kal_actions') is not None and r['kal_actions'] != len(mine['acts']):
                c['kal_actions_mismatch'] += 1
            if r.get('n_atoms') is not None and r['n_atoms'] != mine['n_atoms']:
                c['n_atoms_mismatch'] += 1
    res[fn] = {'checked': dict(c), 'examples': ex, 'actions': summ(acts)}
    print(fn, json.dumps(res[fn]), flush=True)
json.dump(res, open(a.out, 'w'), indent=1)
