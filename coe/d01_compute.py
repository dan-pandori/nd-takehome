#!/usr/bin/env python3
"""coe-dose01 compute per arm, seed and activity, from this run's registry rows (create-or-elicit's coe/coe_compute.py
attribution: model from the ladder name / checkpoint / output path, activity from script, phase and output path), plus
`train_tokens`.  The RL ladders are compared with the 1 % arm's (create-or-elicit's registry, same functions): the policy
flags any quantity above 1.25x its comparator.  Knockout s1's rounds 25-32 are this run's rows of ladder la_ko_s1.
  python3 coe/d01_compute.py [--pods artifacts/coe-dose01/pod_hours.tsv] [--out artifacts/coe-dose01/compute]"""
import argparse, collections, glob, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from coe.coe_compute import model_of, activity, ACTS

METRICS = ('gpu_seconds', 'gen_tokens', 'attempts', 'train_steps', 'train_tokens', 'lean_checks')


def load(reg, run_id):
    tot = collections.defaultdict(collections.Counter); per_round = collections.defaultdict(collections.Counter); n = 0
    for f in sorted(glob.glob(os.path.join(reg, '*.jsonl'))):
        for line in open(f):
            x = json.loads(line)
            if x.get('run_id') != run_id or x.get('metric') not in METRICS:
                continue
            arm, seed = model_of(x)
            m = f'{arm}_s{seed}' if arm else 'other'
            act = activity(x)
            tot[(m, act)][x['metric']] += x['value'] or 0
            rd = (x.get('labels') or {}).get('round')
            if act == 'rl' and rd is not None:
                per_round[(m, int(rd))][x['metric']] += x['value'] or 0
            n += 1
    return tot, per_round, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--registry', default='artifacts/coe-dose01/registry')
    ap.add_argument('--ref_registry', default='/home/dan/work/create-or-elicit/artifacts/create-or-elicit/registry')
    ap.add_argument('--pods', default='artifacts/coe-dose01/pod_hours.tsv')
    ap.add_argument('--out', default='artifacts/coe-dose01/compute')
    a = ap.parse_args()
    tot, per_round, n = load(a.registry, 'coe-dose01')
    rtot, _, rn = load(a.ref_registry, 'create-or-elicit')
    models = sorted({k[0] for k in tot})
    table = {m: {act: dict(tot[(m, act)]) for act in ACTS if (m, act) in tot} for m in models}
    ref = {m: dict(rtot[(m, 'rl')]) for m in ('dose1_s0', 'dose1_s1', 'dose1_s2') if (m, 'rl') in rtot}
    ref_mean = {k: sum(v.get(k, 0) for v in ref.values()) / len(ref) for k in METRICS} if ref else {}
    flags = {}
    for m in models:
        if m.startswith('dose01') and 'rl' in table[m]:
            flags[m] = {k: round(table[m]['rl'].get(k, 0) / ref_mean[k], 3) for k in METRICS if ref_mean.get(k)}
    pods = []
    if os.path.exists(a.pods):
        for line in open(a.pods):
            if line.strip() and not line.startswith('#'):
                p, h, d, g, role = line.rstrip('\n').split('\t')
                pods.append({'pod': p, 'hours': float(h), 'usd': float(d), 'gpu': g, 'role': role})
    ko_rounds = {rd: dict(v) for (m, rd), v in sorted(per_round.items()) if m == 'ko_s1'}
    json.dump({'rows': n, 'ref_rows': rn, 'by_model_activity': table, 'dose1_rl_per_ladder': ref,
               'dose01_rl_over_dose1_mean': flags, 'ko_s1_rounds': ko_rounds, 'pods': pods}, open(a.out + '.json', 'w'), indent=1)
    cols = [c for c in ACTS if any(c in table[m] for m in models)]
    L = ['# coe-dose01 — compute (`coe/d01_compute.py`)', '',
         f'GPU-hours (process wall-clock on one NVIDIA A40, from {n:,} registry rows; processes sharing a card each count in '
         'full, so the sum exceeds pod time).', '',
         '| model | ' + ' | '.join(cols) + ' | total | gen tokens (M) | attempts (M) | train steps | train tokens (M) | Lean checks (M) |',
         '|---|' + '---:|' * (len(cols) + 6)]
    for m in models:
        t = table[m]
        g = [t.get(c, {}).get('gpu_seconds', 0) / 3600 for c in cols]
        s = lambda k: sum(v.get(k, 0) for v in t.values())
        L.append(f'| {m} | ' + ' | '.join(f'{v:.2f}' if v else '–' for v in g) +
                 f' | {sum(g):.1f} | {s("gen_tokens") / 1e6:.0f} | {s("attempts") / 1e6:.2f} | {s("train_steps"):,.0f} | '
                 f'{s("train_tokens") / 1e6:.0f} | {s("lean_checks") / 1e6:.2f} |')
    L += ['', '## RL ladder vs the 1 % arm (policy flag at 1.25×)', '',
          '| ladder | ' + ' | '.join(METRICS) + ' |', '|---|' + '---:|' * len(METRICS)]
    for m, f in flags.items():
        L.append(f'| {m} ÷ mean(dose1 s0–s2) | ' + ' | '.join(f"{f.get(k, float('nan')):.3f}" for k in METRICS) + ' |')
    L.append('| dose1 mean (absolute) | ' + ' | '.join(f'{ref_mean.get(k, 0):,.0f}' for k in METRICS) + ' |')
    if ko_rounds:
        L += ['', '## Knockout s1, rounds 25–32 (this run)', '', '| round | ' + ' | '.join(METRICS) + ' |', '|---|' + '---:|' * len(METRICS)]
        for rd, v in ko_rounds.items():
            L.append(f'| {rd} | ' + ' | '.join(f'{v.get(k, 0):,.0f}' for k in METRICS) + ' |')
    if pods:
        L += ['', '## Pod time (what the run paid)', '', '| pod | GPU | role | hours | $ |', '|---|---|---|---:|---:|']
        for p in pods:
            L.append(f"| {p['pod']} | {p['gpu']} | {p['role']} | {p['hours']:.2f} | {p['usd']:.2f} |")
        L.append(f"| **total** | | | {sum(p['hours'] for p in pods):.2f} | {sum(p['usd'] for p in pods):.2f} |")
    open(a.out + '.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
