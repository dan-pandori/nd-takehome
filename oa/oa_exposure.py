#!/usr/bin/env python3
"""organism-analysis Q2 exposure: per EI round, how many steps of each hard-step class the round's RL training records
contain.  Reads each ladder round's training mix (`mix_<r>.jsonl`: RL records x rl_weight + K12 replay) from the
bucket; RL records = prompt in the ladder's RL target set; deduplicated on (prompt, proof).

  python3 oa/oa_exposure.py --ladder trajectory/artifacts/tj/la_T1_best12_s0 --out artifacts/oa/exposure/c12_s0.json
"""
import argparse, collections, json, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from state_env import decompose
from oa_common import step_class

ap = argparse.ArgumentParser()
ap.add_argument('--ladder', required=True)
ap.add_argument('--targets', default='data/ladder/rl_targets.jsonl')
ap.add_argument('--rounds', type=int, default=8)
ap.add_argument('--out', required=True)
a = ap.parse_args()
tp = {json.loads(l)['prompt'] for l in open(a.targets) if l.strip()}
res = json.load(open(a.out)) if os.path.exists(a.out) else {}
for r in range(1, a.rounds + 1):
    if str(r) in res:
        continue
    with tempfile.TemporaryDirectory() as td:
        f = os.path.join(td, 'm.jsonl')
        p = subprocess.run(['hf', 'buckets', 'cp', f'hf://buckets/dan-pandori/nd-rl/{a.ladder}/mix_{r}.jsonl', f],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if p.returncode or not os.path.exists(f):
            print(f'round {r}: no mix file', flush=True); continue
        seen, n_all, fail = set(), 0, 0
        cls, cls_thm = collections.Counter(), collections.Counter()
        for l in open(f):
            d = json.loads(l); n_all += 1
            if d['prompt'] not in tp or (d['prompt'], d['proof']) in seen:
                continue
            seen.add((d['prompt'], d['proof']))
            try:
                steps, _, _ = decompose(d['prompt'], d['proof'], canon=True)
            except Exception:
                fail += 1; continue
            ks = [step_class(' '.join(act)) for _, act, _ in steps]
            cls.update(ks)
    thms = len({p for p, _ in seen})
    res[str(r)] = {'mix_records': n_all, 'rl_distinct': len(seen), 'rl_theorems': thms, 'decompose_fail': fail,
                   'class_steps': dict(cls)}
    print(f'round {r}: mix {n_all}, RL distinct {len(seen)} on {thms} theorems, fail {fail}', flush=True)
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(res, open(a.out + '.tmp', 'w')); os.replace(a.out + '.tmp', a.out)
