#!/usr/bin/env python3
"""Print a few pruned proofs matching a label filter, compactly (one ND line per row), for refining the taxonomy.
Never use on textbook72 (sealed; it is not a source file here anyway).

  python3 proof_strategies/peek.py --src data/ps/in/train_k12.jsonl.gz --labels artifacts/ps/labels/k12.jsonl.gz \
      --expr "'ex_falso.other' in sub" -k 3 [--seed 0] [--maxlen 12]
The expression sees: u (uses list), sub (sub-type list), pri, pric, L, Lp, dep, ts, r (the label row).
"""
import argparse, gzip, json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from patterns import parse, prune_lines, lines_to_text      # noqa: E402
from strategies import get_proof                            # noqa: E402


def show(prompt, proof):
    lines = prune_lines(parse(proof))
    txt = lines_to_text(lines)
    print('   ', prompt)
    for part in txt.replace(' QED', '').split(' ; '):
        print('     ', part.strip().rstrip(';').strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True)
    ap.add_argument('--labels', required=True)
    ap.add_argument('--expr', required=True)
    ap.add_argument('-k', type=int, default=3)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--maxlen', type=int, default=99)
    a = ap.parse_args()
    op = lambda f: gzip.open(f, 'rt') if f.endswith('.gz') else open(f)
    hits = []
    with op(a.labels) as f:
        for line in f:
            r = json.loads(line)
            if r.get('parse_fail'):
                continue
            env = {'u': r['u'], 'sub': r['sub'], 'pri': r['pri'], 'pric': r['pric'], 'L': r['L'], 'Lp': r['Lp'], 'dep': r['dep'], 'ts': r['ts'], 'r': r}
            if r['Lp'] <= a.maxlen and eval(a.expr, {}, env):
                hits.append(r['i'])
    print(f'{len(hits)} matches')
    pick = sorted(random.Random(a.seed).sample(hits, min(a.k, len(hits))))
    want = set(pick)
    with op(a.src) as f:
        for i, line in enumerate(f):
            if i in want:
                r = json.loads(line)
                print(f'-- record {i}')
                show(r['prompt'], get_proof(r))


if __name__ == '__main__':
    main()
