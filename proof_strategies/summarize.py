#!/usr/bin/env python3
"""Summarise a label file written by strategies.py: shares of every strategy ("uses", primary, curried primary),
sub-types, dead-line-only strategies, and breakdowns by written length, pruned length and box depth.

  python3 proof_strategies/summarize.py --labels artifacts/ps/labels/k12.jsonl.gz --name K12 --out artifacts/ps/summary/k12.json
  [--keep FILE]  a text file of record indices (one per line) to restrict to
"""
import argparse, collections, gzip, json, os, statistics, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from strategies import STRATS, PRIMARY, SUBTYPES, NAME      # noqa: E402


def load(fn, keep=None):
    out = []
    with (gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)) as f:
        for line in f:
            r = json.loads(line)
            if keep is None or r['i'] in keep:
                out.append(r)
    return out


def summarize(rows, name):
    ok = [r for r in rows if not r.get('parse_fail')]
    n = len(ok)
    uses = collections.Counter(s for r in ok for s in r['u'])
    pri = collections.Counter(r['pri'] for r in ok)
    pric = collections.Counter(r['pric'] for r in ok)
    sub = collections.Counter(s for r in ok for s in r['sub'])
    wonly = collections.Counter(s for r in ok for s in r.get('w_only', []))
    n_wonly = sum(1 for r in ok if r.get('w_only'))
    n_none = sum(1 for r in ok if not r['u'])
    box_free = sum(1 for r in ok if r.get('box_free'))
    by = {}
    for key, f in (('L', lambda r: r['L']), ('Lp', lambda r: r['Lp']), ('dep', lambda r: r['dep'])):
        groups = collections.defaultdict(list)
        for r in ok:
            groups[f(r)].append(r)
        by[key] = {str(k): {'n': len(g), 'uses': {s: sum(s in r['u'] for r in g) for s in STRATS},
                            'pri': dict(collections.Counter(r['pri'] for r in g))} for k, g in sorted(groups.items())}
    size = {}
    for s in STRATS:
        g = [r for r in ok if s in r['u']]
        if g:
            size[s] = {'Lp_mean': round(statistics.mean(r['Lp'] for r in g), 2), 'ts_mean': round(statistics.mean(r['ts'] for r in g), 2),
                       'dep_mean': round(statistics.mean(r['dep'] for r in g), 2)}
    return {'name': name, 'n': n, 'parse_fail': len(rows) - n,
            'uses': {s: uses[s] for s in STRATS}, 'primary': {s: pri[s] for s in PRIMARY},
            'curried_primary': {s: pric[s] for s in PRIMARY}, 'sub': {s: sub[s] for s in SUBTYPES},
            'written_only': {s: wonly[s] for s in STRATS}, 'n_written_only_any': n_wonly, 'n_no_strategy': n_none,
            'box_free': box_free, 'size_by_strategy': size,
            'all_Lp_mean': round(statistics.mean(r['Lp'] for r in ok), 2) if ok else None,
            'all_ts_mean': round(statistics.mean(r['ts'] for r in ok), 2) if ok else None,
            'p1_derived_ore': sum(r['p1'] for r in ok), 'p1_strict': sum(r['p1s'] for r in ok), 'p2_reductio': sum(r['p2'] for r in ok),
            'nested_ore': sum(r['nest'] >= 2 for r in ok), 'by': by}


def show(S):
    n = S['n']
    pc = lambda c: f'{c:7d} {100 * c / n:6.2f} %' if n else f'{c:7d}'
    print(f"== {S['name']}: {n} proofs ({S['parse_fail']} unparsable); box-free {pc(S['box_free'])}; no strategy {pc(S['n_no_strategy'])}; "
          f"a strategy only in dead lines {pc(S['n_written_only_any'])}")
    print(f"{'strategy':40s} {'uses':>16s} {'primary':>16s} {'curried prim.':>16s}")
    for s in PRIMARY + ('lemma_reuse',):
        if s == 'lemma_reuse' and s in PRIMARY:
            continue
        u = S['uses'].get(s)
        print(f"{NAME[s]:40s} {pc(u) if u is not None else '':>16s} {pc(S['primary'].get(s, 0)) if s in S['primary'] else '':>16s} "
              f"{pc(S['curried_primary'].get(s, 0)) if s in S['curried_primary'] else '':>16s}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--labels', required=True)
    ap.add_argument('--name', required=True)
    ap.add_argument('--out')
    ap.add_argument('--keep')
    ap.add_argument('--subs', action='store_true')
    a = ap.parse_args()
    keep = set(int(x) for x in open(a.keep)) if a.keep else None
    S = summarize(load(a.labels, keep), a.name)
    show(S)
    if a.subs:
        for k, v in S['sub'].items():
            print(f'  {k:38s} {v:7d} {100 * v / S["n"]:6.2f} %')
    if a.out:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        json.dump(S, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
