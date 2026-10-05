#!/usr/bin/env python3
"""capability-defs J1: target proofs for teacher-forced scoring (pure python; VPS).

  python3 capability_defs/analysis/cd_j1_targets.py            -> artifacts/cd/j1/targets_s<S>.jsonl, sets.json

Per seed S (cap-12 best-cap12, trajectory's seeds):
  H_S     = {t in tb72 + h250 : pend_S solves t in neither x0 nor x1}               (the hard set)
  CAL_S   = 30 theorems drawn (random.Random(S)) from {t : 3 <= pooled pend_S n_ok (x0 + x1) <= 100 of 512}
  J2_S    = {t in H_S : r8_S (x0, x1, x2) or r16_S (x1) solves t}                     (J2's large-k set, with CAL_S)
  F(t)    = every distinct Lean-accepted ND proof of t in any read of any model (cap 12 and cap 6, all checkpoints and
            draws, rl-continue(-cap6) r12 / r16, mcts-a x2 / C reads) plus the reference proof.
Targets for seed S = F(t) for t in H_S + CAL_S, one row per proof:
  {tid, name, pool, prompt, kind: 'known', proof, src}  with src flags: ref, pend_S (any pend_S draw), pt_S (a
  pretraining checkpoint of seed S), rl_S (an RL checkpoint of seed S), other (another seed or cap 6).
"""
import collections, json, os, random, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cd_reads as R

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'artifacts', 'cd', 'j1')


def all_reads():
    """yield (cap, s, ck, pool, x, d) for every read we have."""
    for cap in (12, 6):
        for s in R.SEEDS:
            for ck in R.CKS + ['r12', 'r16']:
                for pool in R.POOLS:
                    for x in (0, 1):
                        d = R.read(cap, s, ck, pool, x)
                        if d is not None:
                            yield cap, s, ck, pool, x, d
    for s in R.SEEDS:
        for ck in ('pend', 'r8'):
            for pool, x in (('tb72', 2), ('h250', 2), ('C', 4)):
                d = R.read(12, s, ck, pool, x)
                if d is not None:
                    yield 12, s, ck, pool, x, d
        d = R.read(12, s, 'r8', 'C', 10)
        if d is not None:
            yield 12, s, 'r8', 'C', 10, d


def main():
    os.makedirs(OUT, exist_ok=True)
    pool_of, prompts, refs = R.pool_of(), R.prompts(), R.refs()
    F = collections.defaultdict(dict)            # name -> {proof: set of src tags}
    for cap, s, ck, pool, x, d in all_reads():
        for n, (ok, tr, pr) in d.items():
            if n not in pool_of:
                continue
            for p in pr:
                tags = F[n].setdefault(p, set())
                if cap == 12:
                    tags.add(f'pend{s}' if ck == 'pend' else f'pt{s}' if ck.startswith('p') else f'rl{s}')
                else:
                    tags.add('cap6')
    for n, p in refs.items():
        F[n].setdefault(p, set()).add('ref')
    sets = {}
    for s in R.SEEDS:
        def pooled(ck, xs):
            out = collections.Counter()
            for x in xs:
                for pool in R.POOLS:
                    d = R.read(12, s, ck, pool, x)
                    for n, v in (d or {}).items():
                        out[n] += v[0]
            return out
        p01 = pooled('pend', (0, 1))
        H = [n for n in pool_of if p01[n] == 0]
        rl = {n for n, c in pooled('r8', (0, 1, 2)).items() if c > 0} | {n for n, c in pooled('r16', (1,)).items() if c > 0}
        J2 = [n for n in H if n in rl]
        cal_pool = sorted(n for n in pool_of if 3 <= p01[n] <= 100)
        CAL = sorted(random.Random(s).sample(cal_pool, min(30, len(cal_pool))))
        sets[s] = {'H': H, 'J2': J2, 'CAL': CAL, 'cal_pool_size': len(cal_pool)}
        rows = []
        for n in H + CAL:
            for i, (p, tags) in enumerate(sorted(F[n].items())):
                src = sorted(t for t in tags if t in ('ref', f'pend{s}', f'pt{s}', f'rl{s}'))
                if not src:
                    src = ['other']
                rows.append({'tid': f'k:{n}:{i}', 'name': n, 'pool': pool_of[n], 'prompt': prompts[n], 'kind': 'known',
                             'proof': p, 'src': src})
        with open(f'{OUT}/targets_s{s}.jsonl', 'w') as f:
            for r in rows:
                f.write(json.dumps(r) + '\n')
        print(f's{s}: H {len(H)}  J2 {len(J2)}  CAL {len(CAL)} (of {len(cal_pool)})  targets {len(rows)}  '
              f'(H {sum(len(F[n]) for n in H)}, CAL {sum(len(F[n]) for n in CAL)}); H theorems with a pend proof '
              f'from x2/x4 draws: {sum(1 for n in H if any(f"pend{s}" in t for t in F[n].values()))}')
    json.dump({str(k): v for k, v in sets.items()}, open(f'{OUT}/sets.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
