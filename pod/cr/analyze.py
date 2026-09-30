#!/usr/bin/env python3
"""compute-record: re-derive every number of the GPU check from the pulled files (no torch needed).
    python3 pod/cr/analyze.py [artifacts/compute-record]   -> stdout table + <dir>/gpu/analysis.json
Per job of pod/cr/gpu_job.sh: its own wall-clock (walls.jsonl: date before / after the python process) vs the sum of
the gpu_seconds rows written inside that window (a job's child processes included), and each counter vs its
independent count (expect.json from the data; sample_check.json from the sampled ids; the Lean gate logs)."""
import glob, json, os, re, sys, calendar, time
D = sys.argv[1] if len(sys.argv) > 1 else 'artifacts/compute-record'
G = os.path.join(D, 'gpu')
rows = [json.loads(l) for f in sorted(glob.glob(os.path.join(D, 'registry', '*.jsonl'))) for l in open(f) if l.strip()]
comp = [r for r in rows if 'compute_id' in (r.get('labels') or {})]
walls = [json.loads(l) for l in open(os.path.join(G, 'walls.jsonl'))]
ex = json.load(open(os.path.join(G, 'expect.json')))
utc = lambda r: calendar.timegm(time.strptime(r['utc'], '%Y-%m-%dT%H:%M:%SZ'))
out = {'jobs': {}}
print('job\twall_s\tgpu_seconds\tcpu_seconds\tratio\ttrain_steps\ttrain_tokens\tgen_tokens\tattempts\tlean_checks\tgpu')
for w in walls:
    rs = [r for r in comp if w['t0'] - 1 <= utc(r) <= w['t1'] + 1]
    s = lambda m, dev=None: sum(r['value'] for r in rs if r['metric'] == m and (dev is None or r['labels']['device'] == dev))
    wall = w['t1'] - w['t0']
    j = {'wall_s': round(wall, 2), 'gpu_seconds': round(s('gpu_seconds', 'cuda'), 2), 'cpu_seconds': round(s('gpu_seconds', 'cpu'), 2),
         **{m: s(m) for m in ('train_steps', 'train_tokens', 'gen_tokens', 'attempts', 'lean_checks')}, 'rc': w['rc'],
         'gpu': sorted({r['labels']['gpu'] for r in rs if r['labels'].get('gpu')}), 'n_rows': len(rs),
         'phases': sorted({(r['labels']['phase'], r['labels'].get('round')) for r in rs}, key=str)}
    j['ratio'] = round(j['gpu_seconds'] / wall, 4) if j['gpu_seconds'] else None
    out['jobs'][w['job']] = j
    print('\t'.join(str(x) for x in (w['job'], j['wall_s'], j['gpu_seconds'], j['cpu_seconds'], j['ratio'], j['train_steps'],
                                     j['train_tokens'], j['gen_tokens'], j['attempts'], j['lean_checks'], ','.join(j['gpu']))))
J = out['jobs']
secs = {}
for k in J:
    if k.startswith('legacy_'):
        m = re.search(r'saved \S+ \((\d+)s total', open(os.path.join(G, k + '.log')).read())
        secs[k] = int(m.group(1)) if m else None
ck = {}
ck['train_fast tokens = 1,000 epochs'] = (J['train_fast']['train_tokens'], ex['train_fast_expected'])
ck['train_fast steps'] = (J['train_fast']['train_steps'], 6000)
for i in (1, 2):
    ck[f'legacy_on_{i} tokens = 100 epochs'] = (J[f'legacy_on_{i}']['train_tokens'], ex['legacy_600_expected'])
    ck[f'legacy_off_{i} writes no rows (ND_COMPUTE=0)'] = (J[f'legacy_off_{i}']['n_rows'], 0)
sc = json.load(open(os.path.join(G, 'sample_check.json')))
ck['sample gen_tokens = sampled ids through <eos>'] = (sc['gen_tokens'], sc['independent_tokens'])
ck['sample attempts'] = (sc['attempts'], sc['prompts'])
ck['sample lean_checks = gate lean_texts'] = (sc['lean_checks'], sc['gate_lean_texts'])
gl = [json.loads(l) for l in open(os.path.join(G, 'ladder_gate.jsonl'))]
ck['ladder lean_checks = gate lean_texts'] = (J['ladder']['lean_checks'], sum(g['lean_texts'] for g in gl))
if 'ladder2' in J:
    gl2 = [json.loads(l) for l in open(os.path.join(G, 'ladder2_gate.jsonl'))]
    ck['ladder2 lean_checks = gate lean_texts'] = (J['ladder2']['lean_checks'], sum(g['lean_texts'] for g in gl2))
    ck['ladder2 train_steps = 2 rounds x 300 fine-tune steps'] = (J['ladder2']['train_steps'], 600)
    ck['train_fast_short steps'] = (J['train_fast_short']['train_steps'], 600)
    ck['train_fast_short tokens = 100 epochs'] = (J['train_fast_short']['train_tokens'], ex['legacy_600_expected'])
out['checks'] = {k: {'counter': a, 'independent': b, 'equal': a == b} for k, (a, b) in ck.items()}
print('\ncheck\tcounter\tindependent\tequal')
for k, v in out['checks'].items():
    print(f"{k}\t{v['counter']}\t{v['independent']}\t{v['equal']}")
on = [secs[f'legacy_on_{i}'] for i in (1, 2)]; off = [secs[f'legacy_off_{i}'] for i in (1, 2)]
out['overhead'] = {'legacy_secs_on': on, 'legacy_secs_off': off, 'counter_us_per_step_bs500': ex['counter_us_per_step_bs500'],
                   'legacy_step_ms': 1000 * sum(on + off) / 4 / 600}
out['overhead']['counter_frac_of_step'] = ex['counter_us_per_step_bs500'] / 1000 / out['overhead']['legacy_step_ms']
print('\noverhead', json.dumps(out['overhead']))
out['sample'] = sc
json.dump(out, open(os.path.join(G, 'analysis.json'), 'w'), indent=1, default=str)
