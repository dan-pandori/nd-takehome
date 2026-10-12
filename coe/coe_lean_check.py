#!/usr/bin/env python3
"""create-or-elicit: Lean-check every refill record of K12- (the record's ND proof translated by nd2lean, checked by
Lean 4 core through lean_judge.judge_many -- Lean alone decides).  Writes a JSON report with the rejected names.

  LEAN_GATE_WORKERS=2 python3 coe/coe_lean_check.py --set data/coe/train_k12ko.jsonl.gz --out artifacts/coe/refill_lean_check.json
"""
import argparse, gzip, json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import lean_judge


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--all', action='store_true', help='check every record, not only the refill')
    a = ap.parse_args()
    t0 = time.time()
    recs = [json.loads(l) for l in gzip.open(a.set, 'rt')]
    todo = [r for r in recs if a.all or r.get('coe_refill')]
    res = []
    B = 2000
    for i in range(0, len(todo), B):
        chunk = todo[i:i + B]
        res += lean_judge.judge_many([(r['prompt'], r['proof']) for r in chunk])
        print(f'{i + len(chunk)}/{len(todo)} checked, {sum(1 for x in res if not x[0])} rejected, {time.time() - t0:.0f}s', flush=True)
    bad = [(r.get('name') or r['thm'], x[1]) for r, x in zip(todo, res) if not x[0]]
    nl_mismatch = sum(1 for r, x in zip(todo, res) if x[0] and x[2] != r['n_lines'])
    rep = {'set': a.set, 'checked': len(todo), 'accepted': len(todo) - len(bad), 'rejected': bad, 'n_lines_mismatch': nl_mismatch,
           'judge_stats': lean_judge.stats(), 'secs': round(time.time() - t0, 1)}
    json.dump(rep, open(a.out, 'w'), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != 'rejected'}), 'rejected:', bad[:10])


if __name__ == '__main__':
    main()
