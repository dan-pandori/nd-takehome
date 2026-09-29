#!/usr/bin/env python3
"""state-cap12: build a literal-text Lean re-check set from LEAN_GATE_DUMP files.

  python3 sc12_recheck.py --dumps artifacts/sc12/dump/rr_T1_SN12_s0__rr600.jsonl ... --out artifacts/sc12/recheck/x.jsonl
  python3 lean_check.py --texts artifacts/sc12/recheck/x.jsonl --out artifacts/sc12/recheck/x_lean.jsonl

For every prompt the gate accepted (lean_ok True), the shortest accepted literal text (fewest `have`s, then
characters) -> kind 'acc'.  Negative control: up to --neg rejected texts (in these runs all rejected by the gate's pre-Lean filter) -> kind 'rej'.
The ND decode is dropped (only Lean judges); `L_true` from the long pool is kept for the term-size table.
"""
import argparse, json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import record

LT = {}
for f in ('data/ladder/transfer_long_rr600.jsonl', 'data/ladder/transfer_long_ge17.jsonl', 'data/ladder/transfer.jsonl'):
    if os.path.exists(f):
        for l in open(f):
            r = json.loads(l); LT.setdefault(r['prompt'], int(r['L_true']) if r.get('L_true') not in (None, 'None') else 17)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dumps', nargs='+', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--neg', type=int, default=300); ap.add_argument('--seed', type=int, default=0)
    a = ap.parse_args()
    record.save_config(vars(a), a.out)
    best, rej = {}, []
    for fn in a.dumps:
        for l in open(fn):
            r = json.loads(l)
            ok = str(r.get('lean_ok')) == 'True'
            if ok:
                t = r['lean_text']; k = (t.count('have '), len(t))
                if r['prompt'] not in best or k < best[r['prompt']][0]:
                    best[r['prompt']] = (k, t)
            else:
                rej.append(r)
    rng = random.Random(a.seed); rng.shuffle(rej)
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    with open(a.out, 'w') as f:
        for p, (k, t) in best.items():
            f.write(json.dumps({'prompt': p, 'lean_text': t, 'kind': 'acc', 'L_true': LT.get(p), 'haves': k[0]}, ensure_ascii=False) + '\n')
        for r in rej[:a.neg]:
            f.write(json.dumps({'prompt': r['prompt'], 'lean_text': r['lean_text'], 'kind': 'rej', 'L_true': LT.get(r['prompt'])},
                               ensure_ascii=False) + '\n')
    print(f'{len(best)} accepted prompts, {min(len(rej), a.neg)} negative controls (of {len(rej)} rejected) -> {a.out}')


if __name__ == '__main__':
    main()
