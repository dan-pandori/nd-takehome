#!/usr/bin/env python3
"""Term size of every stream proof (run `style-edl`; the policy's length measure besides lines / actions).

  python3 style_edl/term_sizes.py      -> artifacts/style_edl/term_sizes.json

term size = inference nodes of the elaborated value of the proof's literal canonical lean_seq text (`lean_check.check`,
Lean 4 core).  Also re-confirms that Lean accepts every stream proof (the builder checked them with lean_gate).
Output: per seed / stream / part: mean and max term size, mean ND lines, n accepted.
"""
import collections, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
from tokenizer import make_tokenizer
sys.path.insert(0, C.ROOT)
from lean_check import check


def main():
    tok = make_tokenizer('lean_staten')
    files = sorted(glob.glob(f'{C.ROOT}/data/style_edl/streams/s*/*.jsonl'))
    keys, srcs, where = {}, [], collections.defaultdict(list)
    for fn in files:
        tag = os.path.relpath(fn, f'{C.ROOT}/data/style_edl/streams').replace('.jsonl', '')
        for l in open(fn):
            r = json.loads(l)
            k = (r['prompt'], r['nd'])
            if k not in keys:
                keys[k] = len(srcs)
                srcs.append(tok.statement(r['prompt']) + ' ' + tok.text(C.decompose(r['prompt'], r['nd'], canon=True)[1]))
            where[tag].append((keys[k], r['nd'].count(';')))
    res, wall, cpu = check(srcs)
    out = {'n_distinct': len(srcs), 'n_accepted': sum(1 for x in res if x['ok']), 'lean_wall_s': round(wall, 1), 'by': {}}
    for tag, items in sorted(where.items()):
        sz = [res[i]['size'] for i, _ in items if res[i]['ok']]
        out['by'][tag] = {'n': len(items), 'accepted': len(sz), 'term_size_mean': sum(sz) / max(1, len(sz)),
                          'term_size_max': max(sz) if sz else None, 'nd_lines_mean': sum(n for _, n in items) / len(items)}
    json.dump(out, open(f'{C.ROOT}/artifacts/style_edl/term_sizes.json', 'w'), indent=1)
    print(json.dumps({k: out[k] for k in ('n_distinct', 'n_accepted', 'lean_wall_s')}))
    for tag, v in out['by'].items():
        if tag.startswith('s0/'):
            print(tag, json.dumps({k: (round(x, 2) if isinstance(x, float) else x) for k, x in v.items()}))


if __name__ == '__main__':
    main()
