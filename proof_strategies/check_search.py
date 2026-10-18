#!/usr/bin/env python3
"""Lean-check the proofs in a search / necessity output (pods have no Lean), then write the Lean-accepted proofs as
records {name, prompt, proof, ...} for strategies.py.  Lean alone decides; nothing else is counted.

  python3 proof_strategies/check_search.py --in data/ps/search/X.jsonl --out data/ps/search/X.checked.jsonl
  python3 proof_strategies/check_search.py --nec --in data/ps/nec/X.jsonl --out data/ps/nec/X.checked.jsonl
"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
from nd2lean import translate, lean_check, TranslationError      # noqa: E402


def check(pairs):
    """pairs: list of (prompt, proof) -> list of (ok, msg)"""
    out, idx, srcs = [None] * len(pairs), [], []
    for k, (p, pr) in enumerate(pairs):
        try:
            srcs.append(translate(p, pr)); idx.append(k)
        except TranslationError as e:
            out[k] = (False, f'translation: {e}')
    for k, r in zip(idx, lean_check(srcs)):
        out[k] = r
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--nec', action='store_true')
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.inp)]
    pairs, where = [], []
    for i, r in enumerate(rows):
        if a.nec:
            for key, v in [('free', r['free'])] + list((r.get('ban') or {}).items()):
                if v and v.get('proof'):
                    pairs.append((r['prompt'], v['proof'])); where.append((i, key))
        elif r.get('proof'):
            pairs.append((r['prompt'], r['proof'])); where.append((i, None))
    res = check(pairs)
    bad = 0
    for (i, key), (ok, msg) in zip(where, res):
        if a.nec:
            rows[i]['free' if key == 'free' else 'ban'] if key == 'free' else None
            tgt = rows[i]['free'] if key == 'free' else rows[i]['ban'][key]
            tgt['lean_ok'] = ok
        else:
            rows[i]['lean_ok'], rows[i]['lean_msg'] = ok, msg[:200]
        bad += not ok
    with open(a.out, 'w') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
    print(json.dumps({'in': a.inp, 'proofs_checked': len(pairs), 'lean_rejected': bad}))


if __name__ == '__main__':
    main()
