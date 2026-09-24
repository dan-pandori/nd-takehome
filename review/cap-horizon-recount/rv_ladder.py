"""Reviewer recount 3: ladder T1 / frozen.  Solved sets rebuilt from the found_* pools with
nd_verify re-run here, L_true joined from the pool file by name, L* = max L with >= 5 solved
at L_true >= L (the convention the pre-registration states)."""
import sys, os, json, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/home/dan/review/cap-horizon')
import rvlib
from nd_verify import verify_text

ROOT = '/home/dan/review/cap-horizon'
POOLS = {
    'found_transfer': {r['name']: r for r in rvlib.rd(f'{ROOT}/data/ladder/transfer.jsonl')},
    'found': {r['name']: r for r in rvlib.rd(f'{ROOT}/data/ladder/rl_targets.jsonl')},
}
LKEY = {'found_transfer': 'L_true', 'found': 'gen_lines'}


def lstar(solved_L):
    ge = collections.Counter()
    for L in solved_L:
        for k in range(2, L + 1):
            ge[k] += 1
    return max([L for L, c in ge.items() if c >= 5], default=0), dict(sorted(ge.items()))


def do(d):
    res = {}
    for pool in ('found_transfer', 'found'):
        cand = sorted(glob.glob(f'{d}/{pool}_*.jsonl'))
        cand = [c for c in cand if 'record' not in os.path.basename(c)]
        if not cand:
            continue
        fn = max(cand, key=lambda f: int(f.rsplit('_', 1)[1][:-6]))
        info = POOLS[pool]
        key = LKEY[pool]
        solved, nd_bad, lens = {}, 0, collections.Counter()
        n = 0
        for r in rvlib.rd(fn):
            n += 1
            if not verify_text(r['prompt'] + ' ' + r['proof'])[0]:
                nd_bad += 1
                continue
            nm = r['name']
            L = info[nm][key]
            if L is None:
                L = info[nm].get('n_lines')
            solved[nm] = L
            lens[rvlib.pruned_length(r['proof'])] += 1
        ls, ge = lstar(solved.values())
        res[pool] = {'file': os.path.relpath(fn, ROOT), 'records': n,
                     'nd_verify_rejects': nd_bad,
                     'distinct_theorems_solved': len(solved), 'pool_n': len(info),
                     'lstar': ls, 'ge': ge,
                     'solved_by_L': dict(sorted(collections.Counter(solved.values()).items())),
                     'accepted_pruned_hist': dict(sorted(lens.items()))}
    return res


if __name__ == '__main__':
    out = {}
    dirs = sorted(glob.glob(f'{ROOT}/artifacts/kh/la_*')) + sorted(glob.glob(f'{ROOT}/artifacts/dsc_inherited/la_*'))
    for d in dirs:
        if not os.path.isdir(d):
            continue
        name = os.path.basename(d)
        out[name] = do(d)
        print(name, json.dumps(out[name]))
        sys.stdout.flush()
    json.dump(out, open(f'{ROOT}/rv/out_ladder.json', 'w'), indent=1)
