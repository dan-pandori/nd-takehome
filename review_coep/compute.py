"""review_coep/compute.py -- compute behind each pod check, from the read summaries and logs (no registry rows exist for
this run's reads in git).  GPU-seconds = each process's wall seconds on its A40 (two processes shared a card, so both
count in full); generated tokens = sum of decoded action lengths (plain) or `sampled_tokens` (guided, C4 n/a)."""
import json, os, sys, re, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

rows = collections.OrderedDict()
for f in sorted(glob.glob(f'{EVAL}/c*_*.json')):
    if f.endswith('.args.json'):
        continue
    tag = os.path.basename(f)[:-5]
    d = json.load(open(f))
    log = open(f'{EVAL}/{tag}.log').read() if os.path.exists(f'{EVAL}/{tag}.log') else ''
    lean_texts = sum(int(m) for m in re.findall(r'lean on (\d+) texts', log))
    if 'env' in d and d['env']:
        e = d['env']
        gen = sum(int(k) * v for k, v in e['action_declen_hist'].items())
        att = d['k'] * d['n']
        peak = e.get('peak_alloc_gb')
    else:
        st = d['stats']
        gen = st['sampled_tokens']; att = d['attempts']; peak = st.get('peak_alloc_gb')
    rows[tag] = dict(check=tag.split('_')[0].upper(), gpu_s=d['wall_s'], attempts=att, gen_tokens=gen,
                     lean_texts=lean_texts, peak_gb=peak)
for tag in ('ko_s1', 'ko_s3'):
    d = json.load(open(P(f'artifacts/coe_paper/c4/{tag}.json')))
    peak = max(t['peak_alloc_gb'] for t in d['timing'])
    rows[f'c4_{tag}'] = dict(check='C4', gpu_s=d['wall_s'], attempts=d['attempts'], gen_tokens=None, lean_texts=None, peak_gb=peak)
for f in ('prefilter_ko_s1', 'control_ko_s1'):
    d = json.load(open(P(f'artifacts/coe_paper/c5/{f}.json')))
    rows[f'c5_{f}'] = dict(check='C5', gpu_s=0, cpu_s=d['seconds'], attempts=None, gen_tokens=None,
                           lean_texts=d.get('n_prefilter_rejections') or (d['positive_n'] + d['negative_n']), peak_gb=None)
tot = collections.defaultdict(lambda: collections.Counter())
for t, r in rows.items():
    print(f"{t:28s} {r['check']}  GPU-s {r['gpu_s']:8.0f}  attempts {r['attempts'] or 0:8d}  gen tokens {r['gen_tokens'] or 0:10d}  "
          f"Lean texts {r['lean_texts'] or 0:7d}  peak GB {r['peak_gb']}")
    for k in ('gpu_s', 'attempts', 'gen_tokens', 'lean_texts'):
        tot[r['check']][k] += r[k] or 0
for c, v in tot.items():
    print(f'{c}: ' + ', '.join(f'{k} {v[k]:,.0f}' for k in v))
print('all GPU-s', sum(v['gpu_s'] for v in tot.values()), '= A40-hours', sum(v['gpu_s'] for v in tot.values()) / 3600)
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out_compute.json'), 'w'), indent=1)
