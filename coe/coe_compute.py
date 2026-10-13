#!/usr/bin/env python3
"""Compute per arm, seed and activity for run create-or-elicit, from the registry's compute rows.

    python3 coe/coe_compute.py [--registry artifacts/create-or-elicit/registry] [--pods artifacts/coe/pod_hours.tsv]
                               [--out artifacts/coe/compute]

Rows: every `gpu_seconds` / `gen_tokens` / `attempts` / `train_steps` / `lean_checks` row the run's scripts wrote
(REGISTRY.md, "Compute rows"). GPU-seconds are each process's wall-clock on one GPU, so processes that shared a card
(reads beside a ladder) are each counted in full: the sum is process time, not pod time. What the run paid is pod
time: `--pods` is a TSV of `pod  hours  dollars  gpu  role` (from ~/podhours.log; see the end of this run's log).
The model (arm, seed) of a row comes from its ladder name, checkpoint or output path; the activity from its script,
phase and output path. Writes <out>.json and <out>.md."""
import argparse, collections, glob, json, os, re

METRICS = ('gpu_seconds', 'gen_tokens', 'attempts', 'train_steps', 'lean_checks')
ACTS = ('pretrain', 'heldout_greedy', 'rl', 'read_plain', 'read_guided', 'timing', 'certificate', 'stdA',
        'large_k_t916', 'phase2_power', 'phase3a', 'scoring', 'phase0_replica', 'other')


def model_of(x):
    cfg = x.get('config') or {}
    for s in (cfg.get('name'), x.get('ckpt'), cfg.get('out'), cfg.get('save'), cfg.get('summary'), cfg.get('init')):
        s = str(s or '')
        m = re.search(r'(?:stage1|la|p3a/ko)_(ko|full|dose1|dose01)_s(\d+)', s) or re.search(r'p3a/(ko)_s(\d+)_', s)
        if m:
            return m.group(1), int(m.group(2))
        m = re.search(r'best12_s(\d+)', s)
        if m:
            return 'full', int(m.group(1))
    return None, None


def activity(x):
    sc, ph = x.get('script') or '', (x.get('labels') or {}).get('phase')
    cfg = x.get('config') or {}
    out = str(cfg.get('out') or cfg.get('outdir') or cfg.get('save') or '')
    name = str(cfg.get('name') or '')
    if 'p3a' in out or str(x.get('arm') or '').startswith('p3a'):
        return 'phase3a'
    if sc == 'state_ladder_ei.py':
        return 'phase0_replica' if name.startswith('rep_') else 'rl'
    if sc == 'state_train.py':
        return 'rl' if ph == 'finetune' else 'pretrain'
    if sc == 'state_eval.py':
        if 'timing/' in str(cfg.get('summary') or ''):
            return 'timing'
        return 'heldout_greedy' if '/heldout_' in out else 'read_plain'
    if sc == 'guided_eval.py':
        return 'read_guided'
    if sc == 'coe_bigk.py':
        return 'stdA' if 'stdA_' in out else 'large_k_t916' if 't916' in out else 'certificate'
    if sc == 'power_sample.py':
        return 'phase2_power'
    if sc == 'cd_score.py':
        return 'scoring'
    return 'other'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--registry', default='artifacts/create-or-elicit/registry')
    ap.add_argument('--pods', default='artifacts/coe/pod_hours.tsv')
    ap.add_argument('--out', default='artifacts/coe/compute')
    a = ap.parse_args()
    tot = collections.defaultdict(lambda: collections.Counter())
    n = 0
    for f in sorted(glob.glob(os.path.join(a.registry, '*.jsonl'))):
        for line in open(f):
            x = json.loads(line)
            if x.get('run_id') != 'create-or-elicit' or x.get('metric') not in METRICS:
                continue
            arm, seed = model_of(x)
            key = (f'{arm}_s{seed}' if arm else 'other', activity(x))
            tot[key][x['metric']] += x['value'] or 0
            n += 1
    models = sorted({k[0] for k in tot}, key=lambda m: (m.split('_')[0] != 'full', m))
    table = {m: {act: dict(tot[(m, act)]) for act in ACTS if (m, act) in tot} for m in models}
    pods = []
    if os.path.exists(a.pods):
        for line in open(a.pods):
            if line.strip() and not line.startswith('#'):
                p, h, d, g, role = line.rstrip('\n').split('\t')
                pods.append({'pod': p, 'hours': float(h), 'usd': float(d), 'gpu': g, 'role': role})
    json.dump({'rows': n, 'gpu_hours_by_model_activity': {m: {k: round(v.get('gpu_seconds', 0) / 3600, 3)
               for k, v in t.items()} for m, t in table.items()}, 'by_model_activity': table, 'pods': pods},
              open(a.out + '.json', 'w'), indent=1)
    cols = [c for c in ACTS if any(c in table[m] for m in models)]
    L = ['# create-or-elicit — compute (`coe/coe_compute.py`)', '',
         f'GPU-hours (process wall-clock on one NVIDIA A40, from {n:,} registry rows; processes sharing a card each count in '
         'full, so the sum exceeds pod time). Model = the checkpoint family the process ran (full s0–s2 = the old '
         'best-cap12 seeds, read here only).', '',
         '| model | ' + ' | '.join(cols) + ' | total | gen tokens (M) | attempts (M) | Lean checks (M) |',
         '|---|' + '---:|' * (len(cols) + 4)]
    for m in models:
        t = table[m]
        g = [t.get(c, {}).get('gpu_seconds', 0) / 3600 for c in cols]
        s = lambda k: sum(v.get(k, 0) for v in t.values())
        L.append(f'| {m} | ' + ' | '.join(f'{v:.2f}' if v else '–' for v in g) +
                 f' | {sum(g):.1f} | {s("gen_tokens") / 1e6:.0f} | {s("attempts") / 1e6:.2f} | {s("lean_checks") / 1e6:.2f} |')
    gs = [sum(table[m].get(c, {}).get('gpu_seconds', 0) for m in models) / 3600 for c in cols]
    L.append('| **all** | ' + ' | '.join(f'{v:.1f}' for v in gs) + f' | {sum(gs):.1f} | | | |')
    if pods:
        L += ['', '## Pod time (what the run paid; `~/podhours.log` and live pods at the time of writing)', '',
              '| pod | GPU | role | hours | $ |', '|---|---|---|---:|---:|']
        for p in pods:
            L.append(f"| {p['pod']} | {p['gpu']} | {p['role']} | {p['hours']:.2f} | {p['usd']:.2f} |")
        L.append(f"| **total** | | | {sum(p['hours'] for p in pods):.2f} | {sum(p['usd'] for p in pods):.2f} |")
    open(a.out + '.md', 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
