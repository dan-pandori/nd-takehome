#!/usr/bin/env python3
"""Shape of K12's own proofs in the state environment (the comparison column for K12-Kalmár's statistics).

  python3 kalmar/k12_stats.py --in data/kh/train_k12.jsonl --out artifacts/kalmar/stats_k12.json [--procs 2]

Same numbers as kalmar/build.py reports for a Kalmár set: lines, actions, ND box depth, longest state / action, pair
tokens (sum over actions of state + action + 1), largest canonical name, term size, canonical lean_seq length.  Also
the longest (state, action) pair of K12 and of a Kalmár file given with --kal (lengths and the record index only).
"""
import argparse, json, os, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from state_env import decompose
from build import term_size


def one(item):
    i, l = item
    r = json.loads(l)
    steps, toks, env = decompose(r['prompt'], r['proof'], canon=True)
    depth = max((ln.count(' | ') + (1 if ' | ' in ln or ln.startswith('| ') else 0) for ln in r['proof'].split(' ; ')), default=0)
    pairs = [(len(s), len(a) + 1) for s, a, h in steps]
    k = max(range(len(pairs)), key=lambda j: sum(pairs[j]))
    return {'i': i, 'n_lines': r['proof'].count(';'), 'n_actions': len(steps),
            'max_depth': max(ln.split(' : ')[0].split()[1:].count('|') for ln in r['proof'][:-4].split(' ; ') if ' : ' in ln),
            'max_state': max(p for p, q in pairs), 'max_action': max(q - 1 for p, q in pairs),
            'pair_tokens': sum(p + q for p, q in pairs), 'longest_pair': pairs[k],
            'max_name': max((int(t[1:]) for t in toks if t[:1] == 'n' and t[1:].isdigit()), default=0),
            'lean_tokens': len(toks), 'term_size': term_size(r['proof'])}


def stats(fn, procs):
    with Pool(procs) as pool:
        res = list(pool.imap(one, enumerate(open(fn)), chunksize=256))
    out = {'in': fn, 'records': len(res)}
    for k in ('n_lines', 'n_actions', 'max_depth', 'max_state', 'max_action', 'pair_tokens', 'max_name', 'lean_tokens', 'term_size'):
        xs = sorted(x[k] for x in res)
        out[k] = {'mean': sum(xs) / len(xs), 'p50': xs[len(xs) // 2], 'p99': xs[int(0.99 * len(xs))], 'max': xs[-1], 'sum': sum(xs)}
    lp = max(res, key=lambda x: sum(x['longest_pair']))
    out['longest_pair'] = {'record_index': lp['i'], 'state_tokens': lp['longest_pair'][0], 'action_tokens_with_eos': lp['longest_pair'][1]}
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--kal', default=None)
    ap.add_argument('--out', required=True)
    ap.add_argument('--procs', type=int, default=2)
    a = ap.parse_args()
    out = {'k12': stats(a.inp, a.procs)}
    if a.kal:
        out['kal'] = stats(a.kal, a.procs)
    json.dump(out, open(a.out, 'w'), indent=1)
    print(json.dumps(out, indent=1))
