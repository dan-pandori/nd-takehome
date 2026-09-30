#!/usr/bin/env python3
"""frontier-supply analysis: read-outs (primary / secondary quantities, paired by seed and by theorem), the supply
filter, and per-arm compute.  Everything from pulled files under artifacts/fsup/ (and artifacts/frontier-supply/registry/).

  python3 fsup_analysis.py [--term]      -> artifacts/fsup/summary.json and tables on stdout

Model: SN-cap12 (lean_staten, 3,216,384 params, from scratch, Stage-1 on K12); arms C (control; s0-s3 = state-cap12's
la_T1_SN12_s*), S (supply 25 %), R (= C', control rerun with EI seed + 100); stage1 = the frozen Stage-1 base.
"""
import argparse, collections, glob, json, os, random, statistics

RR = 'artifacts/fsup/rr'
ARMS = ['C', 'S', 'R', 'stage1']


def read(fn):
    return [json.loads(l) for l in open(fn) if l.strip()]


def label(arm, s):
    return f'stage1_s{s}' if arm == 'stage1' else f'la_{arm}_s{s}'


def solved_sets(lab):
    """-> dict quantity -> set of solved theorem names, or None if the read-out is missing."""
    f1, f2 = f'{RR}/{lab}__lp2.jsonl', f'{RR}/{lab}__rr.jsonl'
    if not (os.path.exists(f1) and os.path.exists(f2)):
        return None
    lp2, rr = read(f1), read(f2)
    q = {'lp2_91': {r['name'] for r in lp2 if r['solved']},
         'exact17': {r['name'] for r in lp2 if r['solved'] and r['L_true_lb'] == 17},
         'ge18': {r['name'] for r in lp2 if r['solved'] and r['L_true_lb'] >= 18},
         'rr15_16': {r['name'] for r in rr if r['solved'] and r['L_true_lb'] in (15, 16)},
         'rr13_14': {r['name'] for r in rr if r['solved'] and r['L_true_lb'] in (13, 14)}}
    q['primary'] = q['lp2_91'] | q['rr15_16']
    return q


def iqm(xs):
    xs = sorted(xs); n = len(xs); lo, hi = n // 4, n - n // 4
    mid = xs[lo:hi] if hi > lo else xs
    return sum(mid) / len(mid)


def boot_ci(xs, B=20000, seed=0):
    rng = random.Random(seed)
    v = sorted(iqm([rng.choice(xs) for _ in xs]) for _ in range(B))
    return [v[int(0.025 * B)], v[int(0.975 * B) - 1]]


def readouts():
    out = {'per_seed': {}, 'paired': {}}
    S = {}
    for arm in ARMS:
        for s in range(6):
            q = solved_sets(label(arm, s))
            if q is not None:
                S[(arm, s)] = q
                out['per_seed'][f'{arm}_s{s}'] = {k: len(v) for k, v in q.items()}
    for a, b in (('S', 'C'), ('R', 'C'), ('C', 'stage1'), ('S', 'stage1')):
        seeds = [s for s in range(6) if (a, s) in S and (b, s) in S]
        if not seeds:
            continue
        res = {'seeds': seeds}
        for qn in ('primary', 'lp2_91', 'exact17', 'ge18', 'rr15_16', 'rr13_14'):
            d = [len(S[(a, s)][qn]) - len(S[(b, s)][qn]) for s in seeds]
            flips = [[len(S[(a, s)][qn] - S[(b, s)][qn]), len(S[(b, s)][qn] - S[(a, s)][qn])] for s in seeds]
            res[qn] = {'diff': d, 'mean': sum(d) / len(d), 'iqm': iqm(d), 'ci95': boot_ci(d) if len(d) > 1 else None,
                       'flips_a_only_b_only': flips}
        out['paired'][f'{a}-{b}'] = res
    rc = out['paired'].get('R-C')
    if rc:
        d = rc['primary']['diff']
        sd = (sum(x * x for x in d) / len(d)) ** 0.5
        out['mdd'] = {'sd_d_from_C_vs_Cprime': sd, 'mdd_paired_n6': 1.425 * sd, 'provisional_sd_d': 16, 'provisional_mdd': 23}
    return out


def supply_filter():
    out = {}
    tot = collections.defaultdict(lambda: {'made': 0, 'zero': 0, 'pass': 0, 'easy': 0})
    for d in sorted(glob.glob('artifacts/fsup/la_S_s*')):
        name = os.path.basename(d); per = []
        for r in range(1, 9):
            fn = f'{d}/round_{r}.json'
            if not os.path.exists(fn):
                break
            x = json.load(open(fn)); s = x['supply']
            per.append({'round': r, 'window': s['window'], 'made': s['made'], 'a_made': s['a_made'], 'b_made': s['b_made'],
                        'pass': s['filter'].get('all', {}).get('pass', 0), 'a_pass': s['filter'].get('a', {}).get('pass', 0),
                        'b_pass': s['filter'].get('b', {}).get('pass', 0), 'zero': s['filter'].get('all', {}).get('zero', 0),
                        'easy': s['filter'].get('all', {}).get('easy', 0), 'leak': s['a_leak'] + s['b_leak'],
                        'pool': s['pool'], 'pool_proofs': s['pool_proofs'], 'shortfall_attempts': s['shortfall_attempts'],
                        'total_attempts': x['total_attempts']})
            for k, v in s['filter'].items():
                for c in v:
                    tot[k][c] += v[c]
        out[name] = per
    out['_total'] = {k: dict(v, pass_rate=v['pass'] / v['made'] if v['made'] else None) for k, v in sorted(tot.items())}
    return out


def ladder_compute():
    """per ladder, from round jsons: attempts, env actions (steps), prompt tokens, decoded action tokens, wall s,
    fine-tune records; and GPU-seconds by phase from the registry rows."""
    out = {}
    dirs = sorted(glob.glob('artifacts/fsup/la_*_s*'))
    for d in dirs:
        name = os.path.basename(d); acc = collections.Counter()
        for r in range(1, 9):
            fn = f'{d}/round_{r}.json'
            if not os.path.exists(fn):
                continue
            x = json.load(open(fn)); e = x['env']
            acc['rounds'] += 1; acc['attempts'] += x.get('total_attempts', x['target_samples'])
            acc['actions'] += e.get('rows', 0); acc['prompt_tokens'] += e.get('prompt_tokens', 0)
            acc['gen_tokens_est'] += int(e.get('rows', 0) * e.get('action_declen_mean', 0))
            acc['wall_s'] += int(x['secs']); acc['mix_rl_records'] += x.get('mix_rl_records', 0)
        out[name] = dict(acc)
    reg = collections.defaultdict(collections.Counter)
    for fn in glob.glob('artifacts/frontier-supply/registry/*.jsonl'):
        for row in read(fn):
            arm = (row.get('labels') or {}).get('arm') or row.get('arm')
            if row.get('metric') in ('gpu_seconds', 'gen_tokens', 'train_steps', 'train_tokens', 'lean_checks', 'attempts', 'actions'):
                reg[arm][row['metric']] += row['value'] or 0
    out['_registry'] = {k: dict(v) for k, v in sorted(reg.items(), key=lambda kv: str(kv[0]))}
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default='artifacts/fsup/summary.json')
    a = ap.parse_args()
    res = {'model': 'SN-cap12 (lean_staten, 3,216,384 params, from scratch, Stage-1 K12 cap 12)',
           'readouts': readouts(), 'supply': supply_filter(), 'compute': ladder_compute()}
    json.dump(res, open(a.out, 'w'), indent=1)
    ro = res['readouts']
    print('per seed (primary = lp2_91 + rr15_16 of 291):')
    for k, v in sorted(ro['per_seed'].items()):
        print(f'  {k:10s} ' + ' '.join(f'{q} {n}' for q, n in v.items()))
    for k, v in ro['paired'].items():
        p = v['primary']
        print(f"{k}: seeds {v['seeds']} primary diff {p['diff']} IQM {p['iqm']:.1f} CI {p['ci95']} flips {p['flips_a_only_b_only']}")
    print('mdd', ro.get('mdd'))
    print('filter total', {k: v for k, v in res['supply']['_total'].items() if ':' not in k})
    for k, v in res['compute'].items():
        if not k.startswith('_'):
            print(f'  {k}: {v}')


if __name__ == '__main__':
    main()
