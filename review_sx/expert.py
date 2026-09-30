#!/usr/bin/env python3
"""Reviewer recount of the expert (per-round) quantities and budget matching, from alloc_r.json / found_r.jsonl / round_r.json."""
import json, os, collections, statistics as S
A = os.path.expanduser('~/review/search-expert/artifacts/sx')
def J(f): return json.load(open(f))
def load(f): return [json.loads(l) for l in open(f) if l.strip()]
Lt = {json.loads(l)['name']: json.loads(l)['L_true'] for l in open(os.path.expanduser('~/review/search-expert/data/ladder/rl_targets.jsonl'))}
def per_round(tag):
    """-> list over r of (solved-this-round set, per-target actions dict, round json)"""
    out = []; prev = None; prevact = None
    for r in range(1, 9):
        al = J(f'{A}/{tag}/alloc_{r}.json'); rj = J(f'{A}/{tag}/round_{r}.json')
        acc = al['accepted']; act = al['actions']
        if r == 1:
            cum_act_check = sum(act.values())
        sol = {t for t, v in acc.items() if v - (prev or {}).get(t, 0) > 0}
        # are actions cumulative? compare with round json
        s_act = sum(act.values()) - (sum(prevact.values()) if prevact else 0)
        out.append(dict(r=r, solved=sol, act=act, rj=rj, sum_act=sum(act.values()), round_actions=rj['actions'],
                        budget=rj.get('budget_actions')))
        prev = acc; prevact = act
    return out
res = {}
for tag in [f'{a}_s{s}' for a in ('A', 'B') for s in range(6)] + [f'{a}_s{s}' for a in ('A2', 'C') for s in range(2)]:
    res[tag] = per_round(tag)
# actions: cumulative or per round?
for tag in ('A_s0', 'B_s0'):
    print(tag, [(x['sum_act'], x['round_actions'], x['budget']) for x in res[tag]][:3])
print('--- budget matching (B vs A same seed/round/target; C vs A2) ---')
for ex, base, seeds in (('B', 'A', range(6)), ('C', 'A2', range(2))):
    for s in seeds:
        over = 0; tot_e = 0; tot_b = 0; ratio = []
        for xe, xb in zip(res[f'{ex}_s{s}'], res[f'{base}_s{s}']):
            for t, v in xe['act'].items():
                b = xb['act'].get(t, 0)
                if v > b: over += 1
            tot_e += xe['sum_act']; tot_b += xb['sum_act']
            assert xe['budget'] == xb['sum_act'], (ex, s, xe['r'], xe['budget'], xb['sum_act'])
        print(f'{ex}_s{s}: targets-rounds over budget {over}; actions {tot_e} vs {base} {tot_b} = {tot_e/tot_b:.3f}')
print('--- H1: per round, solves by X in round r on targets Y never solved in rounds 1..r ---')
tabs = collections.defaultdict(list)
for ex, base, seeds in (('B', 'A', range(6)), ('C', 'A2', range(2))):
    for s in seeds:
        E = res[f'{ex}_s{s}']; Bb = res[f'{base}_s{s}']
        cumE = set(); cumB = set(); rowsE = []; rowsB = []; totE = []; totB = []
        for r in range(8):
            cumE |= E[r]['solved']; cumB |= Bb[r]['solved']
            rowsE.append(len(E[r]['solved'] - cumB)); rowsB.append(len(Bb[r]['solved'] - cumE))
            totE.append(len(E[r]['solved'])); totB.append(len(Bb[r]['solved']))
        # 'new target solves' = first-ever solve of a target by that arm in round r
        firstE = []; firstB = []; cE = set(); cB = set()
        for r in range(8):
            firstE.append(len(E[r]['solved'] - cE)); cE |= E[r]['solved']
            firstB.append(len(Bb[r]['solved'] - cB)); cB |= Bb[r]['solved']
        print(f's{s} {ex}-only-past-{base}: {rowsE} sum {sum(rowsE)} | {base}-only-past-{ex}: {rowsB} sum {sum(rowsB)}')
        print(f'    first-ever solves {ex} {firstE} (tot {sum(firstE)}) {base} {firstB} (tot {sum(firstB)}); cum r8 {ex} {len(cE)} {base} {len(cB)}; '
              f'L>=13 cum {ex} {sum(Lt[t]>=13 for t in cE)} {base} {sum(Lt[t]>=13 for t in cB)}')
        tabs[ex].append((sum(rowsE), sum(rowsB), sum(firstE), sum(firstB), len(cE), len(cB)))
for ex in tabs:
    a = [x[0] for x in tabs[ex]]; b = [x[1] for x in tabs[ex]]
    print(ex, 'sum over seeds: X-only', sum(a), 'base-only', sum(b), 'ratio', round(sum(a)/max(1, sum(b)), 2))
print('--- per-round solved totals & per-round time ---')
for tag in res:
    print(tag, [len(x['solved']) for x in res[tag]], 'secs', round(sum(x['rj']['secs'] for x in res[tag])), 'actions', sum(x['sum_act'] for x in res[tag]),
          'mix_rl', [x['rj']['mix_rl_records'] for x in res[tag]][-1])
