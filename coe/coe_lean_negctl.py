#!/usr/bin/env python3
"""create-or-elicit: negative / positive control for the refill Lean check (coe_lean_check.py).  200 refill records
(seeded): unchanged (must all be accepted) and with the theorem's conclusion G replaced by ( ~ G ) (the same proof can
no longer prove the statement: must all be rejected).

  LEAN_GATE_WORKERS=2 python3 coe/coe_lean_negctl.py --set data/coe/train_k12ko.jsonl.gz --out artifacts/coe/refill_lean_negctl.json
"""
import argparse, gzip, json, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import lean_judge


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=200)
    a = ap.parse_args()
    recs = [json.loads(l) for l in gzip.open(a.set, 'rt')]
    refill = [r for r in recs if r.get('coe_refill')]
    pick = random.Random(7).sample(refill, a.n)
    pos = [(r['prompt'], r['proof']) for r in pick]
    neg = []
    for r in pick:
        p = r['prompt'].strip()
        body = p[4:-4]
        prem, concl = (' ' + body + ' ').split(' SEQ ')
        neg.append((f"THM {prem.strip()} SEQ ( ~ {concl.strip()} ) PRF".replace('THM  SEQ', 'THM SEQ').replace('THM SEQ', 'THM SEQ'), r['proof']))
    rp = lean_judge.judge_many(pos)
    rn = lean_judge.judge_many(neg)
    out = {'n': a.n, 'positive_accepted': sum(1 for x in rp if x[0]), 'negated_goal_accepted': sum(1 for x in rn if x[0]),
           'example_negated_prompt': neg[0][0]}
    json.dump(out, open(a.out, 'w'), indent=1)
    print(out)


if __name__ == '__main__':
    main()
