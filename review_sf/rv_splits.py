"""Reviewer's own renaming-class canonicaliser + disjointness check (state-frontier)."""
import json, itertools, os, sys
def thm_of(r):
    if 'thm' in r: return r['thm']
    raise KeyError
def parts(thm):
    lhs, goal = thm.split('|-')
    prems = [p.strip() for p in lhs.split(' , ')] if lhs.strip() else []
    return prems, goal.strip()
def rename(fs):
    m = {}; out = []
    for f in fs:
        toks = []
        for t in f.split():
            if t in 'PQRST' and len(t) == 1:
                if t not in m: m[t] = 'abcde'[len(m)]
                toks.append(m[t])
            else: toks.append(t)
        out.append(' '.join(toks))
    return out
def canon_ordered(thm):
    p, g = parts(thm); return ' ; '.join(rename(p + [g]))
def canon_set(thm):
    """premise-order- and duplicate-insensitive: min over permutations of the distinct premises"""
    p, g = parts(thm); p = sorted(set(p))
    if len(p) > 6: return canon_ordered(thm)
    return min(' ; '.join(rename(list(q) + [g])) for q in itertools.permutations(p))
def load(fn):
    op = __import__('gzip').open if fn.endswith('.gz') else open
    return [json.loads(l) for l in op(fn, 'rt')]
if __name__ == '__main__':
    H = os.path.expanduser('~')
    train = {'stage1 train_depth3_f0_a1': f'{H}/work/state-env/data/p2/train_depth3_f0_a1.jsonl',
             'ladder rl_targets': f'{H}/review/state-frontier/data/ladder/rl_targets.jsonl',
             'G1 train_g1': f'{H}/work/noise-floor/data/dsg/train_g1.jsonl'}
    evals = {'long (sf2)': f'{H}/review/state-frontier/data/sf2/long.jsonl',
             'transfer': f'{H}/review/state-frontier/data/ladder/transfer.jsonl',
             'heldout p2': f'{H}/review/state-frontier/data/p2/heldout.jsonl'}
    E = {k: load(v) for k, v in evals.items()}
    Ec = {k: ({canon_ordered(r['thm']) for r in v}, {canon_set(r['thm']) for r in v}) for k, v in E.items()}
    for tk, tf in train.items():
        T = load(tf)
        To = {canon_ordered(r['thm']) for r in T}; Ts = {canon_set(r['thm']) for r in T}
        for ek, (eo, es) in Ec.items():
            print(f'{tk:28s} ({len(T)}) vs {ek:12s} ({len(E[ek])}): ordered-class overlap {len(To & eo)}, set-class overlap {len(Ts & es)}')
    for a, b in itertools.combinations(E, 2):
        print(f'eval {a} vs {b}: set-class overlap {len(Ec[a][1] & Ec[b][1])}')
