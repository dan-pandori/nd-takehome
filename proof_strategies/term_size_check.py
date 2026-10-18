#!/usr/bin/env python3
"""Validate strategies.Proof.term_size (per-rule weights on the pruned ND proof) against lean_check.py's elaborated
inference-node count (the project's "term size") on a sample of pruned proofs: nd2lean.translate -> lean_check.check.

  python3 proof_strategies/term_size_check.py --out artifacts/ps/term_size_check.json
"""
import argparse, gzip, json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..')); sys.path.insert(0, HERE)
from patterns import parse, prune_lines, lines_to_text        # noqa: E402
from strategies import Proof, get_proof                       # noqa: E402
from nd2lean import translate                                 # noqa: E402
import lean_check                                             # noqa: E402


def sample(fn, k, seed, op=open):
    rows = [json.loads(l) for l in op(fn)]
    rows = [r for r in rows if get_proof(r) and (r.get('lean_ok', True))]
    return random.Random(seed).sample(rows, min(k, len(rows)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    gz = lambda f: gzip.open(f, 'rt')
    recs = [('k12', r) for r in sample('data/ps/in/train_k12.jsonl.gz', 300, 0, gz)]
    recs += [('charles_base', r) for r in sample('data/ps/in/charles/charles_base_full.jsonl', 50, 0)]
    recs += [('tb_schema', r) for r in sample('data/ps/search/tb_schema.checked.jsonl', 50, 0)]
    srcs, mine = [], []
    for tag, r in recs:
        pl = prune_lines(parse(get_proof(r)))
        srcs.append(translate(r['prompt'], lines_to_text(pl), require_all_pr=False))
        mine.append(Proof(pl).term_size())
    res, wall, proc = lean_check.check(srcs)
    rows = [{'set': tag, 'ok': x['ok'], 'lean_size': x.get('size'), 'formula_size': m, 'reason': (x.get('reason') or '')[:120]}
            for (tag, _), x, m in zip(recs, res, mine)]
    agree = sum(1 for r in rows if r['ok'] and r['lean_size'] == r['formula_size'])
    out = {'n': len(rows), 'lean_ok': sum(r['ok'] for r in rows), 'size_equal': agree,
           'mismatch': [r for r in rows if not (r['ok'] and r['lean_size'] == r['formula_size'])][:20],
           'wall_s': round(wall, 1), 'lean_process_s': round(proc, 1)}
    json.dump(out, open(a.out, 'w'), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'mismatch'}), 'first mismatches:', out['mismatch'][:3])


if __name__ == '__main__':
    main()
