#!/usr/bin/env python3
"""create-or-elicit Phase 0.2: the compute-matched budget restated with measured, same-class per-attempt costs.

Inputs (all local after pulls):
  * old ladders' registry rows (trajectory r1-r8 on RTX A6000, rl-continue r9-r16 on A40): per seed, round and phase
    (sample / eval / finetune) GPU-seconds;
  * Phase 0.2 timing (coe-r0, A40, alone on the card): the old pend models on the 322 at k 256, batch 2,048 / 1,024 / 512
    (artifacts/coe/timing/A40_pend_s{S}_b{B}.json: wall_s = sampling + Lean);
  * the round-1 replica (coe-r1, A40): trajectory's round 1 re-run with --no_train (artifacts/coe/replica/rep_best12_s{S}/),
    whose sample-phase GPU-seconds against trajectory's own (RTX A6000) give the class ratio on the same workload.
Budgets per seed and RL round R (8 or 16), all in base attempts per evaluation theorem (322):
  K_pub      capability-defs' published K_eval-set (ladder seconds / (322 x 3.6 ms));
  K_evalset  same ladder seconds, same-class uniform-allocation cost (A6000 rounds at c_A6000, A40 rounds at c_A40);
  K_train    only the sample + fine-tune phases (the eval phase never feeds training), same costs;
  K_att      ladder target attempts / 322 (143,840 per round).
c_A40 = mean seconds per attempt over the 322 at batch 2,048 (the ladders' batch); c_A6000 = c_A40 x (A6000 / A40 sample-
phase seconds of round 1 on the same workload).  The multipliers K / K_pub feed coe/cd_part3_recount.py (compute-matched
set sizes at each budget) and the J9 certificates are re-checked at each budget (UB95 < 0.05 / K).

  python3 coe/coe_budget.py --out artifacts/coe/budget/budget.json
"""
import argparse, collections, glob, json, math, os, sys

LADDER_DIRS = {'trajectory': os.path.expanduser('~/work/trajectory/artifacts/trajectory/registry'),
               'rl-continue': os.path.expanduser('~/work/rl-continue/artifacts/rl-continue/registry')}
K_PUB = {'r8': {0: 19281, 1: 21107, 2: 23310}, 'r16': {0: 47962, 1: 49428, 2: 50447}}
J9 = {  # (seed, theorem): (successes, attempts) from capability-defs REPORT section 3.8
    (0, 'la_transfer_2060'): (0, 1245952), (0, 'la_transfer_205'): (0, 1245952), (0, 'la_transfer_1077'): (0, 1245952),
    (1, 'la_transfer_1648'): (0, 1377024), (1, 'la_transfer_1077'): (1, 1377024), (1, 'la_transfer_2060'): (0, 1377024),
    (2, 'la_transfer_1648'): (1, 1114880), (2, 'la_transfer_1833'): (0, 1508096), (2, 'la_transfer_2060'): (0, 1508096)}


def cp_upper(c, n, a=0.05):
    from scipy.stats import beta
    return 1.0 if c >= n else float(beta.ppf(1 - a, c + 1, n - c))


def phase_seconds():
    """-> {seed: {round: {phase: (gpu_seconds, gpu name)}}} for the best12 T1 ladders."""
    out = collections.defaultdict(lambda: collections.defaultdict(dict))
    for run, d in LADDER_DIRS.items():
        for f in glob.glob(os.path.join(d, '*.jsonl')):
            for l in open(f):
                r = json.loads(l)
                lab = r.get('labels') or {}
                if r.get('metric') != 'gpu_seconds' or lab.get('phase') not in ('sample', 'eval', 'finetune'):
                    continue
                if not (r.get('arm') == 'best12' and r.get('script') == 'state_train.py') and not str(r.get('arm', '')).startswith('la_T1_best12_s'):
                    continue      # ladder phase rows (arm la_T1_best12_s<S>) + the fine-tune child process (arm best12, state_train.py)
                rd = lab.get('round')
                if rd is None:
                    continue
                rd = int(rd); s = int(r['seed'])
                prev = out[s][rd].get(lab['phase'])
                # a round that failed (s2 r2 OOM at batch 2,048) and was re-run: both rows are real GPU time; keep the sum
                v = r['value'] + (prev[0] if prev else 0.0)
                out[s][rd][lab['phase']] = (v, lab.get('gpu'))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--timing', default='artifacts/coe/timing')
    ap.add_argument('--replica', default='artifacts/coe/replica')
    ap.add_argument('--out', default='artifacts/coe/budget/budget.json')
    a = ap.parse_args()
    ph = phase_seconds()
    res = {'per_seed': {}, 'notes': []}
    c40 = {}
    for s in (0, 1, 2):
        for B in (2048, 1024, 512):
            fn = f'{a.timing}/A40_pend_s{s}_b{B}.json'
            if os.path.exists(fn):
                d = json.load(open(fn))
                c40[(s, B)] = d['wall_s'] / (d['n'] * d['k'])
    ratio = {}
    for s in (0, 1, 2):
        fn = f'{a.replica}/rep_best12_s{s}/round_1.json'
        a6 = ph[s][1].get('sample')
        if os.path.exists(fn) and a6:
            # replica sample-phase seconds from its own registry rows if present, else round secs minus nothing (flagged)
            rep = None
            for f in glob.glob('artifacts/create-or-elicit/registry/*.jsonl') + glob.glob(f'{a.replica}/../registry/*.jsonl'):
                for l in open(f):
                    r = json.loads(l); lab = r.get('labels') or {}
                    if r.get('arm') == 'replica_r1' and int(r.get('seed', -1)) == s and lab.get('phase') == 'sample' and r.get('metric') == 'gpu_seconds':
                        rep = (rep or 0) + r['value']
            if rep:
                ratio[s] = a6[0] / rep
    res['c_A40_322'] = {f's{s}_b{B}': round(v * 1000, 3) for (s, B), v in c40.items()}
    res['ratio_A6000_over_A40_round1_sample'] = {f's{s}': round(v, 4) for s, v in ratio.items()}
    r_mean = sum(ratio.values()) / len(ratio) if ratio else None
    res['ratio_used'] = r_mean
    for s in (0, 1, 2):
        rows = {}
        c_a40 = c40.get((s, 2048))
        c_a6 = c_a40 * r_mean if (c_a40 and r_mean) else None
        for R in (8, 16):
            tot = {'all': 0.0, 'train': 0.0}
            K_ev = K_tr = 0.0
            ok = c_a40 is not None
            for rd in range(1, R + 1):
                p = ph[s].get(rd, {})
                gpu = next((g for _, g in p.values()), None)
                c = c_a6 if gpu and 'A6000' in gpu else c_a40
                allv = sum(v for v, _ in p.values())
                trv = sum(p[k][0] for k in ('sample', 'finetune') if k in p)
                tot['all'] += allv; tot['train'] += trv
                if c:
                    K_ev += allv / (322 * c); K_tr += trv / (322 * c)
                else:
                    ok = False
            rows[f'r{R}'] = {'ladder_s_all': round(tot['all']), 'ladder_s_train': round(tot['train']),
                             'K_pub': K_PUB[f'r{R}'][s], 'K_att': round(143840 * R / 322),
                             'K_evalset_sameclass': round(K_ev) if ok else None, 'K_train_sameclass': round(K_tr) if ok else None}
            if ok:
                rows[f'r{R}']['mul_evalset'] = round(K_ev / K_PUB[f'r{R}'][s], 4)
                rows[f'r{R}']['mul_train'] = round(K_tr / K_PUB[f'r{R}'][s], 4)
                rows[f'r{R}']['mul_att'] = round(rows[f'r{R}']['K_att'] / K_PUB[f'r{R}'][s], 4)
        res['per_seed'][s] = rows
    # J9 certificates at each r8 budget
    cert = {}
    for (s, t), (c, n) in J9.items():
        ub = cp_upper(c, n)
        r8 = res['per_seed'][s]['r8']
        cert[f's{s}_{t}'] = {'c': c, 'n': n, 'UB95': ub,
                             **{k: (ub < 0.05 / r8[k]) if r8.get(k) else None for k in ('K_pub', 'K_evalset_sameclass', 'K_train_sameclass', 'K_att')}}
    res['j9_certified_at_r8_budgets'] = cert
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, 'w'), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != 'j9_certified_at_r8_budgets'}, indent=1))
    for k, v in cert.items():
        print(k, v)


if __name__ == '__main__':
    main()
