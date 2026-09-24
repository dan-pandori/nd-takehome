"""Recount 6 — ladder T1 / frozen: transfer solved, L*, by L_true bin, textbook
schemata.  Every stored transfer proof re-verified with nd_verify."""
import sys, os, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rv
from nd_verify import verify_text

TR = {r['name']: r for r in rv.load('data/ladder/transfer.jsonl')}
TG = {r['name']: r for r in rv.load('data/ladder/rl_targets.jsonl')}
LT = collections.Counter(r['L_true'] for r in TR.values())


def lstar(solved_names):
    """max L such that >= 5 transfer targets with L_true >= L are solved."""
    best = 0
    for L in sorted({r['L_true'] for r in TR.values()}):
        n = sum(1 for nm in solved_names if TR[nm]['L_true'] >= L)
        if n >= 5:
            best = L
    return best


res = {}
for mode in ['T1', 'frozen']:
    for arm in ['c0', 'a1', 'a2', 'a3', 'a4']:
        for s in [0, 1]:
            d = 'artifacts/dsc/la_%s_%s_s%d' % (mode, arm, s)
            if not os.path.isdir(d):
                continue
            rounds = sorted(int(f.split('_')[1].split('.')[0]) for f in os.listdir(d) if f.startswith('round_'))
            if not rounds:
                res['%s_%s_s%d' % (mode, arm, s)] = {'rounds_done': 0}
                continue
            R = rounds[-1]
            ft = os.path.join(d, 'found_transfer_%d.jsonl' % R)
            if not os.path.exists(ft):
                cand = sorted(f for f in os.listdir(d) if f.startswith('found_transfer_'))
                ft = os.path.join(d, cand[-1]) if cand else None
            o = {'rounds_done': R, 'found_transfer_file': os.path.basename(ft) if ft else None}
            if ft and os.path.exists(ft):
                solved = {}; bad = 0; distinct = set()
                for r in rv.load(ft):
                    g = TR[r['name']]
                    ok, why, _ = verify_text(g['prompt'] + ' ' + r['proof'])
                    if not ok:
                        bad += 1; continue
                    distinct.add((r['name'], rv.norm(r['proof'])))
                    solved[r['name']] = min(solved.get(r['name'], 99), r['round'])
                names = set(solved)
                bylt = collections.Counter(TR[n]['L_true'] for n in names)
                sch_all = collections.Counter(r['schema'] for r in TR.values() if r.get('source') == 'textbook')
                sch_ok = collections.Counter(TR[n]['schema'] for n in names if TR[n].get('source') == 'textbook')
                o.update({'transfer_pool': len(TR), 'transfer_solved': len(names),
                          'nd_verify_rejects': bad, 'distinct_transfer_proofs': len(distinct),
                          'L_star': lstar(names),
                          'by_L_true': {str(k): [bylt[k], LT[k]] for k in sorted(LT)},
                          'textbook_schema_solved': {k: [sch_ok[k], sch_all[k]] for k in sorted(sch_all)}})
            # training-target solves at the last round
            rj = json.load(open(os.path.join(d, 'round_%d.json' % R)))
            o['targets_round_solved'] = rj['targets_round']['solved']
            o['targets_n'] = rj['targets_round']['n']
            o['init'] = json.load(open(os.path.join(d, 'args.json')))['init']
            res['%s_%s_s%d' % (mode, arm, s)] = o
            print(mode, arm, s, 'R', R, 'transfer', o.get('transfer_solved'), 'L*', o.get('L_star'), 'bad', o.get('nd_verify_rejects'), flush=True)
res['_pool'] = {'transfer_n': len(TR), 'L_true_hist': dict(sorted(LT.items())),
                'textbook_n': sum(1 for r in TR.values() if r.get('source') == 'textbook'),
                'rl_targets_n': len(TG)}
json.dump(res, open('recount/out_ladder.json', 'w'), indent=1)
