#!/usr/bin/env python3
"""Compute per arm from the run's results-registry rows (artifacts/kalmar-pretrain/registry/*.jsonl), own grouping:
arm from the checkpoint read or written (config.ckpt / config.init / config.out / ckpt), phase from script.
Also the Stage-1 training logs (START/END stamps, final step lines) for KAL-C / KAL-D.

  python3 review_kal/compute.py -> out/compute.json, stdout table
"""
import collections, glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc

REG = os.path.join(kc.ROOT, 'artifacts', 'kalmar-pretrain', 'registry')
LOG = os.path.join(kc.ROOT, 'artifacts', 'kalmar', 'logs')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
METRICS = ('gpu_seconds', 'gen_tokens', 'train_steps', 'train_tokens', 'lean_checks', 'attempts', 'actions')


def arm_of(row):
    cfg = row.get('config') or {}
    s = ' '.join(str(x) for x in (cfg.get('out'), cfg.get('ckpt'), cfg.get('init'), row.get('ckpt'), cfg.get('name'), row.get('arm')) if x)
    if 'la_kal_frozen' in s:
        return 'frozen ladder'
    if 'la_kal_ei' in s and row.get('script') == 'state_train.py':
        return 'EI ladder (fine-tune child)'
    if 'la_kal_ei' in s:
        return 'EI ladder' if row.get('script') == 'state_ladder_ei.py' else 'EI r1/r2 reads'
    if 'kalDA' in s or 'anneal' in s:
        return 'KAL-D+A'
    if 'stage1_kalD' in s:
        return 'KAL-D'
    if 'stage1_kalC' in s:
        return 'KAL-C'
    if 'ctl/' in s or 'best12' in s:
        return 'control'
    return 'other:' + (row.get('script') or '?')


tot = collections.defaultdict(collections.Counter)
gpus = collections.defaultdict(collections.Counter)
phase = collections.defaultdict(collections.Counter)
nrows = 0
for fn in sorted(glob.glob(os.path.join(REG, '*.jsonl'))):
    for r in kc.rows(fn):
        nrows += 1
        if r['metric'] not in METRICS:
            continue
        arm = arm_of(r)
        sub = 'train' if r.get('script') in ('state_train.py',) else 'read'
        tot[(arm, sub)][r['metric']] += r['value'] or 0
        if r['metric'] == 'gpu_seconds':
            gpus[(arm, sub)][(r.get('labels') or {}).get('gpu')] += r['value']
            phase[(arm, sub)][r.get('script')] += r['value']
res = {'n_rows': nrows, 'by_arm': {}}
print('registry rows', nrows)
print(f"{'arm':34s} {'gpu_h':>8s} {'gen_tok':>14s} {'train_steps':>12s} {'train_tok':>14s} {'lean_checks':>12s} {'attempts':>10s}  gpus")
for k in sorted(tot):
    t = tot[k]
    res['by_arm'][' / '.join(k)] = {**{m: t[m] for m in METRICS}, 'gpus': dict(gpus[k]), 'scripts_gpu_s': dict(phase[k])}
    print(f"{' / '.join(k):34s} {t['gpu_seconds'] / 3600:8.2f} {int(t['gen_tokens']):14,d} {int(t['train_steps']):12,d} {int(t['train_tokens']):14,d} "
          f"{int(t['lean_checks']):12,d} {int(t['attempts']):10,d}  {dict((g, round(v / 3600, 2)) for g, v in gpus[k].items())}")
# Stage-1 training logs
tr = {}
for fn in sorted(glob.glob(os.path.join(LOG, 'train_kal*_s*.log'))):
    txt = open(fn, errors='replace').read()
    st = re.search(r'START (\S+)', txt); en = re.search(r'END (\S+)', txt)
    done = re.findall(r'best: done (\d+) steps, ([\d.]+) epochs of pairs, (\d+)s, final val (\S+)', txt)
    be = re.findall(r'--best_epochs ([\d.]+) x (\d+) batches per epoch -> --best_steps (\d+)', txt)
    pairs = re.findall(r'train records (\d+) \(skipped (\d+)\); pairs (\d+)', txt)
    tr[os.path.basename(fn)] = {'start': st and st.group(1), 'end': en and en.group(1), 'done': done[-1] if done else None,
                                'best_epochs': be[-1] if be else None, 'records_pairs': pairs[-1] if pairs else None}
    print(os.path.basename(fn), tr[os.path.basename(fn)])
res['train_logs'] = tr
json.dump(res, open(os.path.join(OUT, 'compute.json'), 'w'), indent=1)
