"""Reviewer: Lean re-check of the numpy-regenerated greedy samples of the 8 fast-arm checkpoints, vs the executor's flags."""
import json, sys, collections, os
sys.path.insert(0, 'rv'); sys.path.insert(0, '.')
from leanrc import check
recs = [json.loads(l) for l in open('data/p2/heldout.jsonl')]
S = [json.loads(l) for l in open('rv/np_samples.jsonl')]
ev = {}
for s in S:
    ck = s['ckpt']
    if ck not in ev:
        ev[ck] = [json.loads(l) for l in open('artifacts/fs/ev/' + os.path.basename(ck)[:-3] + '.jsonl')]
it = [s for s in S if s['text']]
res = check([(recs[s['i']]['prompt'], s['text']) for s in it])
mine = {(s['ckpt'], s['i']): False for s in S}
for s, ok in zip(it, res):
    mine[(s['ckpt'], s['i'])] = ok
tab = collections.Counter(); per_ck = collections.Counter(); dis = []
for s in S:
    th = ev[s['ckpt']][s['i']]; assert th['name'] == s['name']
    m = mine[(s['ckpt'], s['i'])]
    tab[(th['lean_ok'], m)] += 1
    if th['lean_ok']: per_ck[s['ckpt']] += 1
    if th['lean_ok'] and m:
        # their term size vs mine for the same theorem (identical decode => equal)
        tab['ntok_equal'] += (th['n_tok'] == len(s['text'].split()))
    if th['lean_ok'] != m:
        dis.append((s['ckpt'], s['i'], s['n_lines'], s['depth3'], th['lean_ok'], m, round(s['min_margin'], 4)))
print('samples', len(S), 'ended', len(it))
print('(executor lean_ok, reviewer Lean accepts):', {k: v for k, v in tab.items() if k != 'ntok_equal'})
print('both accept and identical term size:', tab['ntok_equal'])
print('executor-counted in subset, per checkpoint:', dict(per_ck))
print('disagreements (ckpt, i, lines, depth3, theirs, mine, min greedy margin):')
for d in dis: print('  ', d)
