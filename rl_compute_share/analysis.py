#!/usr/bin/env python3
"""Aggregate numbers quoted in REVIEW.md (run rl-compute-share). Reads compute_table.csv and frontier_ranges.csv.
Per row the point value is the geometric mean of the low and high ratio (rows with a ratio range only)."""
import csv, math, os, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
rows = list(csv.DictReader(open(os.path.join(HERE, 'compute_table.csv'))))
front = {r['period']: r for r in csv.DictReader(open(os.path.join(HERE, 'frontier_ranges.csv')))}
f = lambda x: float(x) if x else None
for r in rows:
    r['lo'], r['hi'] = f(r['ratio_low']), f(r['ratio_high'])
    r['mid'] = math.sqrt(r['lo'] * r['hi']) if r['lo'] and r['hi'] else None
OWN_YUE = ('Yue et al. (own', )
pre = lambda r: r['group'] in ('yue', 'lit') and 'from scratch' not in r['model'] and r['ratio_basis'] != 'not computable'


def show(name, rs, key='mid'):
    xs = sorted(r[key] for r in rs if r[key] is not None)
    if not xs:
        print(f'{name}: none'); return None
    print(f'{name}: n {len(xs)}  median {statistics.median(xs):.3g}  min {xs[0]:.3g}  max {xs[-1]:.3g}')
    return statistics.median(xs)


print('== Q1 Yue et al. models (FLOP ratio)')
yue = [r for r in rows if r['group'] == 'yue' and r['hi'] is not None]
show('all, high bound', yue, 'hi'); show('all, low bound', yue, 'lo'); m_yue = show('all, mid', yue)
show('third-party checkpoints, high', [r for r in yue if not r['paper'].startswith(OWN_YUE)], 'hi')
show('own runs (VeRL + EasyR1), high', [r for r in yue if r['paper'].startswith(OWN_YUE)], 'hi')
show('SimpleRL-Zoo, low', [r for r in yue if 'SimpleRL' in r['model']], 'lo')
show('SimpleRL-Zoo, high', [r for r in yue if 'SimpleRL' in r['model']], 'hi')

print('== Q2 literature on pretrained LLMs (Yue + other papers, own RL runs; FLOPs, computed or hw-based)')
lit = [r for r in rows if pre(r) and r['hi'] is not None]
print(f'span: min low {min(r["lo"] for r in lit):.3g}  max high {max(r["hi"] for r in lit):.3g}  '
      f'max low {max(r["lo"] for r in lit):.3g} ({max(lit, key=lambda r: r["lo"])["model"]})')
for v in ('elicit', 'create', 'mixed', 'none'):
    show(f'verdict {v}, mid', [r for r in lit if r['verdict'] == v])
me = statistics.median(r['mid'] for r in lit if r['verdict'] == 'elicit')
mc = statistics.median(r['mid'] for r in lit if r['verdict'] == 'create')
print(f'create / elicit median ratio: {mc / me:.3g}x')
big = sorted(lit, key=lambda r: -r['mid'])[:6]
print('largest by mid:', '; '.join(f"{r['model'][:40]} {r['lo']:.2g}-{r['hi']:.2g}" for r in big))

print('== FLOP ratio vs GPU-hour ratio where both exist')
for r in rows:
    if r['gpu_hour_ratio'] and r['lo'] and r['ratio_basis'].startswith('FLOPs'):
        g = r['gpu_hour_ratio'].replace('>= ', '').split('-')[0]
        try:
            g = float(g)
        except ValueError:
            continue
        print(f"{r['model'][:45]:45} FLOP {r['lo']:.3g}-{r['hi']:.3g}  GPU-h {g:.3g}  GPU-h / FLOP-mid {g / r['mid']:.3g}x")

print('== Gaps to the frontier band (H2 2025-2026 central 0.3-2, range 0.1-5)')
b = front['H2 2025-2026 (band)']
cl, ch, lo_, hi_ = (float(b[k]) for k in ('central_low', 'central_high', 'low', 'high'))
print(f'Yue median mid {m_yue:.3g}: {math.log10(cl / m_yue):.2f}-{math.log10(ch / m_yue):.2f} orders below the central band')
print(f'largest pretrained-LLM paper mid {big[0]["mid"]:.3g}: {math.log10(cl / big[0]["mid"]):.2f} orders below 0.3')
print(f'Yue median mid vs 2024 central (0.01-0.1): {math.log10(0.01 / m_yue):.2f}-{math.log10(0.1 / m_yue):.2f} orders below')

print('== Samples per training prompt (computed rows)')
for r in rows:
    if r['samples_per_train_prompt']:
        print(f"  {r['model'][:50]:50} {r['samples_per_train_prompt']}")

print('== Our runs')
for r in rows:
    if r['group'] == 'ours':
        print(f"  {r['model'][:50]:50} FLOP {r['lo']:.3g}-{r['hi']:.3g}  GPU-s {r['gpu_hour_ratio']}")
