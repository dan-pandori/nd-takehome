#!/usr/bin/env python3
"""RL's own proofs, recounted from the ladders' cumulative found files (replaces the mix-based counts of rl_mix.py,
which were capped samples; log.md 2026-10-18, claim check #30/#31).

found_<R>.jsonl (create-or-elicit, bucket create-or-elicit/artifacts/coe/ladder/la_<arm>/) holds every distinct
(normalised) Lean-accepted proof of an RL target found in rounds 1..R, each with the round it was first found.  Round 1
= samples of the pretrained model.  Per ladder and round: new distinct proofs, those with a proof by contradiction, with
a working one; σ-covered targets proved with a working reductio (first round).  Streams one file at a time (download,
count, delete; DN lines only are parsed and classified).  Models: create-or-elicit's 9.56 M ALiBiGPT `lean_staten`,
from scratch on K12 (full) / K12⁻ (knockout) / K12 + 1 % σ (dose1), T1 expert iteration on A40, Lean alone.

  python3 proof_strategies/rl_found.py      # -> artifacts/ps/rl_found.json
"""
import collections, gzip, json, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..')); sys.path.insert(0, HERE)
from strategies import analyse                         # noqa: E402

ARMS = ['full_s3', 'full_s4', 'full_s5', 'dose1_s0', 'dose1_s1', 'dose1_s2', 'ko_s0', 'ko_s1', 'ko_s2', 'ko_s3', 'ko_s4', 'ko_s5']
BK = 'hf://buckets/dan-pandori/nd-rl/create-or-elicit/artifacts/coe/ladder'
RND = re.compile(r'"round": (\d+)')


def main():
    tg = [json.loads(l) for l in open('data/ladder/rl_targets.jsonl')]
    th = [json.loads(l) for l in gzip.open('artifacts/ps/theorem/rl_targets.jsonl.gz', 'rt')]
    by_name = {r['name']: (r['prompt'], t) for r, t in zip(tg, th)}
    out = json.load(open('artifacts/ps/rl_found.json')) if os.path.exists('artifacts/ps/rl_found.json') else {}
    tmp = 'artifacts/ps/scratch/found_tmp.jsonl'
    for arm in ARMS:
        if arm in out:
            continue
        t0 = time.time()
        subprocess.run(['hf', 'buckets', 'cp', f'{BK}/la_{arm}/found_16.jsonl', tmp], check=True, capture_output=True)
        new, red, work, temp, free, neg, unp = (collections.Counter() for _ in range(7))
        first_sc = {}                   # σ-covered target -> first round with a working reductio
        keys = None
        with open(tmp) as f:
            for line in f:
                m = RND.search(line)
                r = int(m.group(1)) if m else -1
                if r > 16:
                    continue
                new[r] += 1
                if ' : DN ' not in line:
                    continue
                x = json.loads(line)
                keys = keys or sorted(x)
                prompt, t = by_name[x['name']]
                a = analyse(x['proof'], prompt, written=False)
                if a is None:
                    unp[r] += 1
                    continue
                if 'contradiction' not in a['u']:
                    continue
                red[r] += 1
                if 'contradiction.working' in a['sub']:
                    work[r] += 1
                    free[r] += 'contradiction.free' in a['sub']        # positive goal, no ¬¬G supplied (never a template)
                    neg[r] += 'contradiction.neg_goal' in a['sub']
                    if t['sigma_cov']:
                        first_sc[x['name']] = min(r, first_sc.get(x['name'], 99))
                else:
                    temp[r] += 1
        os.remove(tmp)
        rounds = range(1, 17)
        out[arm] = {'keys': keys, 'new_by_round': {r: new[r] for r in rounds}, 'reductio_by_round': {r: red[r] for r in rounds},
                    'working_by_round': {r: work[r] for r in rounds}, 'template_only_by_round': {r: temp[r] for r in rounds},
                    'free_working_by_round': {r: free[r] for r in rounds}, 'neg_goal_working_by_round': {r: neg[r] for r in rounds},
                    'unparsable_dn_lines': sum(unp.values()),
                    'sigma_cov_first_working_round': first_sc, 'secs': round(time.time() - t0, 1)}
        w = out[arm]['working_by_round']
        sc1 = sum(1 for v in first_sc.values() if v == 1)
        print(f"{arm:9s} new r1 {new[1]:7d} total r1-16 {sum(new[r] for r in rounds):8d} | working r1 {w[1]:5d} r2-16 {sum(w[r] for r in range(2, 17)):6d} "
              f"| σ-cov targets with a working reductio: r1 {sc1:3d}, by r16 {len(first_sc):3d} | {out[arm]['secs']} s", flush=True)
        json.dump(out, open('artifacts/ps/rl_found.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
