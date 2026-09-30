#!/usr/bin/env python3
"""textbook72 contamination check: the 72 textbook problems against every set the scored models trained on, by
atom-renaming class.  Two keys per theorem: `ordered` = gen.canon_key of `prem , prem |- goal` (atoms relabelled by
first appearance, premise order kept: the project's usual key) and `set` = the minimum ordered key over all premise
orders (premise order and duplicates ignored).  Streams each training file once (plain or .gz).

  python3 tb72_contam.py --out artifacts/textbook72/contam.json NAME=PATH [NAME=PATH ...]
"""
import argparse, gzip, itertools, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import canon_key

TB = ['data/eval_only/textbook72/textbook_dev.jsonl', 'data/eval_only/textbook72/textbook_train.jsonl']


def split_prem(s):
    out, depth, cur = [], 0, []
    for t in s.split():
        if t == ',' and depth == 0:
            out.append(' '.join(cur)); cur = []; continue
        depth += (t == '(') - (t == ')')
        cur.append(t)
    if cur:
        out.append(' '.join(cur))
    return out


def parse(r):
    if r.get('prompt'):
        m = re.match(r'THM\s*(.*?)\s*SEQ (.*?) PRF', r['prompt'])
        return split_prem(m.group(1)), m.group(2).strip()
    pre, goal = r['thm'].split('|-')
    return split_prem(pre), goal.strip()


def keys(prem, goal):
    ordered = canon_key(f"{' , '.join(prem)} |- {goal}")
    ps = sorted(set(prem))
    if len(ps) <= 6:
        st = min(canon_key(f"{' , '.join(p)} |- {goal}") for p in itertools.permutations(ps))
    else:
        st = ordered
    return ordered, st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('sets', nargs='+')
    a = ap.parse_args()
    tb = []
    for fn in TB:
        for l in open(fn):
            r = json.loads(l)
            o, s = keys(*parse(r))
            tb.append({'name': r['name'], 'role': r['role'], 'ref': r.get('reference_lines'), 'ko': o, 'ks': s})
    want_o = {t['ko'] for t in tb}; want_s = {t['ks'] for t in tb}
    res = {}
    for spec in a.sets:
        name, path = spec.split('=', 1)
        op = gzip.open if path.endswith('.gz') else open
        hit_o, hit_s, n = set(), set(), 0
        with op(path, 'rt') as f:
            for l in f:
                if not l.strip():
                    continue
                r = json.loads(l); n += 1
                try:
                    prem, goal = parse(r)
                except Exception:
                    continue
                o = canon_key(f"{' , '.join(prem)} |- {goal}")
                if o in want_o:
                    hit_o.add(o)
                o2, s = keys(prem, goal) if len(prem) > 1 else (o, o)
                if s in want_s:
                    hit_s.add(s)
        res[name] = {'path': path, 'records': n,
                     'overlap_ordered': sorted(t['name'] for t in tb if t['ko'] in hit_o),
                     'overlap_set': sorted(t['name'] for t in tb if t['ks'] in hit_s)}
        print(f"{name:28s} records {n:8d}  overlap ordered {len(res[name]['overlap_ordered']):2d}  "
              f"premise-set {len(res[name]['overlap_set']):2d}", flush=True)
    anyo = sorted({x for v in res.values() for x in v['overlap_set']})
    out = {'sets': res, 'any_overlap_set': anyo,
           'problems': [{k: t[k] for k in ('name', 'role', 'ref')} | {'in': sorted(n for n, v in res.items() if t['name'] in v['overlap_set'])}
                        for t in tb if t['name'] in anyo]}
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(out, open(a.out, 'w'), indent=1)
    print('problems overlapping any set (premise-set key):', len(anyo))


if __name__ == '__main__':
    main()
