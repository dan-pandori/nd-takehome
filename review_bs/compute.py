#!/usr/bin/env python3
"""Reviewer per-arm compute from job logs: ladder seconds (sum of 'round r done in Xs'), Lean-checked texts (sum of
'lean on X texts' in [lean_gate] lines), ladder fine-tune steps and pairs (pairs/batch x 200-step intervals), generated
action tokens from round_<r>.json env stats (rows x action_declen_mean); Stage-1 from checkpoint extras (stage1_ckpts.log)
and logs; read-out GPU-seconds from eval summaries (wall_s)."""
import re, json, glob, os, collections
R = os.path.expanduser('~/review/best-state'); A = f'{R}/artifacts/bs'
def parse(fn):
    t = open(fn).read()
    secs = [float(x) for x in re.findall(r'=== round \d+ done in (\d+)s', t)]
    lean = [int(x) for x in re.findall(r'lean on (\d+) texts', t)]
    samples = [int(x) for x in re.findall(r'\[lean_gate\] (\d+) samples', t)]
    pb = [float(x) for x in re.findall(r'pairs/batch (\d+)', t)]
    steps = [int(x) for x in re.findall(r'^step (\d+) loss', t, re.M)]
    return dict(rounds=len(secs), ladder_s=sum(secs), lean_texts=sum(lean), gate_samples=sum(samples),
                ft_steps_logged=len(steps) * 200, ft_pairs=sum(pb) * 200)
out = {}
for fn in sorted(glob.glob(f'{A}/logs/seed_best*.log')):
    k = os.path.basename(fn)[5:-4]; d = parse(fn)
    lad = f'{A}/la_T1_{k}'; g = 0
    for r in range(1, 9):
        e = json.load(open(f'{lad}/round_{r}.json'))['env']; g += e['rows'] * e['action_declen_mean']
    d['gen_action_tokens'] = g; out['T1_' + k] = d
for fn in sorted(glob.glob(f'{A}/inh_logs/*.log')):
    out['inh_' + os.path.basename(fn)[:-4]] = parse(fn)
# read-outs
ro = collections.defaultdict(float); rog = collections.defaultdict(float); rol = collections.defaultdict(int)
for fn in glob.glob(f'{A}/eval/*.json'):
    if fn.endswith('args.json'): continue
    s = json.load(open(fn)); b = os.path.basename(fn)[:-5]
    cell = ('Fz_' + b.split('_')[1]) if b.startswith('heldout') else b.split('__')[0].rsplit('_', 1)[0]
    ro[cell] += s.get('wall_s') or 0
    e = s.get('env') or {}; rog[cell] += (e.get('rows', 0) * e.get('action_declen_mean', 0))
out['readout_wall_s'] = dict(ro); out['readout_gen_tokens'] = dict(rog)
json.dump(out, open(f'{R}/review_bs/compute.json', 'w'), indent=1)
for k, v in out.items(): print(k, v)
