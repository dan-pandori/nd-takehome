#!/usr/bin/env python3
"""run1-lean analysis: step 2 (forms) and step 3 (scale). Every number is derived from the judged files.

  python r1_analysis.py --judged artifacts/r1/judged_coder30b.jsonl --scale 'artifacts/r1/judged_scale_*.jsonl' \
      --theorems data/r1/scale_theorems.jsonl --out artifacts/r1/summary.json --fig figures

Step 2: per form: greedy accuracy, pass@1 (mean over 8 samples), pass@8; by stratum; averaged over draws.
Paired deltas (lean - tokens, english - tokens) per (theorem, draw) on greedy and pass@8; 95 % bootstrap CI
with the theorem as the resampling unit (10,000 resamples, seed 0); by stratum group.
Step 3: per model per class: greedy / pass@16 solve rate; per theorem the smallest scale with >= 1 Lean-accepted
proof; Spearman rho between that rank and the base log-prob of the RL-found proof (per class and pooled).
"""
import argparse, json, glob, os, sys, collections, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

SCALES = ['Qwen3-0.6B', 'Qwen3-1.7B', 'Qwen3-4B', 'Qwen3-8B', 'Qwen3-14B', 'Qwen3-32B']
SCALE_B = {'Qwen3-0.6B': 0.6, 'Qwen3-1.7B': 1.7, 'Qwen3-4B': 4, 'Qwen3-8B': 8, 'Qwen3-14B': 14, 'Qwen3-32B': 32}


def load(fn):
    return [json.loads(l) for l in open(fn) if l.strip()]


def group_of(stratum):
    if stratum.startswith('val36'):
        return stratum
    n = int(stratum[1:])
    return 'L7-8' if n <= 8 else 'L9-11' if n <= 11 else 'L12-16'


GROUPS = ['val36 <=6', 'val36 >6', 'L7-8', 'L9-11', 'L12-16']


def boot_ci(x_by_thm, n=10000, seed=0):
    """x_by_thm: dict theorem -> list of per-draw values. Bootstrap over theorems of the mean."""
    rng = np.random.default_rng(seed)
    thms = list(x_by_thm)
    means = np.array([np.mean(x_by_thm[t]) for t in thms])
    if len(means) == 0:
        return float('nan'), (float('nan'), float('nan'))
    bs = rng.choice(means, size=(n, len(means)), replace=True).mean(axis=1)
    return float(means.mean()), (float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))


def step2(recs):
    forms = sorted({r['form'] for r in recs})
    draws = sorted({r['draw'] for r in recs})
    metric = {}
    for r in recs:
        g = bool(r['greedy_ok'])
        s = r['sample_ok']
        gl = bool(r.get('greedy_ok_lenient', g))
        sl = r.get('sample_ok_lenient', s)
        metric[(r['form'], r['draw'], r['name'])] = {'greedy': float(g), 'pass1': float(np.mean(s)) if s else float('nan'),
                                                    'pass8': float(any(s)), 'greedy_len': float(gl), 'pass8_len': float(any(sl)),
                                                    'group': group_of(r['stratum']), 'stratum': r['stratum']}
    out = {'n_records': len(recs), 'forms': forms, 'draws': draws, 'by_form': {}, 'by_form_group': {}, 'delta': {}, 'by_form_draw': {}}
    for f in forms:
        for m in ('greedy', 'pass1', 'pass8', 'greedy_len', 'pass8_len'):
            vals = [v[m] for (ff, d, nm), v in metric.items() if ff == f]
            out['by_form'][f'{f}/{m}'] = float(np.nanmean(vals))
            for d in draws:
                out['by_form_draw'][f'{f}/{m}/d{d}'] = float(np.nanmean([v[m] for (ff, dd, nm), v in metric.items() if ff == f and dd == d]))
            for g in GROUPS:
                vv = [v[m] for (ff, d, nm), v in metric.items() if ff == f and v['group'] == g]
                out['by_form_group'][f'{f}/{m}/{g}'] = float(np.nanmean(vv)) if vv else float('nan')
    # paired deltas vs tokens
    for f in forms:
        if f == 'tokens':
            continue
        for m in ('greedy', 'pass8', 'pass1', 'greedy_len', 'pass8_len'):
            for g in ['all'] + GROUPS:
                by_thm = collections.defaultdict(list)
                for (ff, d, nm), v in metric.items():
                    if ff != f or (g != 'all' and v['group'] != g):
                        continue
                    t = metric.get(('tokens', d, nm))
                    if t is None:
                        continue
                    by_thm[nm].append(v[m] - t[m])
                mean, (lo, hi) = boot_ci(by_thm)
                out['delta'][f'{f}-tokens/{m}/{g}'] = {'mean': mean, 'ci95': [lo, hi], 'n_theorems': len(by_thm)}
    # failure reasons per form (greedy)
    reasons = collections.defaultdict(collections.Counter)
    for r in recs:
        j = r['judged'].get('greedy')
        if j and not j['ok']:
            reasons[r['form']][short_reason(j['reason'], r['form'])] += 1
    out['greedy_failure_reasons'] = {f: dict(c.most_common(12)) for f, c in reasons.items()}
    return out, metric


def short_reason(reason, form):
    if reason is None:
        return 'none'
    if form == 'lean':
        r = reason
        if 'unknown identifier' in r:
            return 'unknown identifier'
        if 'type mismatch' in r or 'has type' in r:
            return 'type mismatch'
        if 'unexpected token' in r or 'expected' in r:
            return 'parse error'
        if 'forbidden' in r or 'tactic' in r:
            return 'forbidden/tactic'
        if 'no proof' in r:
            return 'no proof found'
        if 'application type mismatch' in r:
            return 'application type mismatch'
        return r.split('|')[0][:40]
    r = reason.split('(')[0].strip()
    return r


def step3(files, theorems):
    thm = {t['name']: t for t in theorems}
    per_model = {}
    for fn in files:
        recs = load(fn)
        if not recs:
            continue
        model = recs[0]['model'].split('/')[-1]
        per_model[model] = {r['name']: r for r in recs}
    models = [m for m in SCALES if m in per_model] + [m for m in per_model if m not in SCALES]
    out = {'models': models, 'rates': {}, 'first_scale': {}, 'spearman': {}, 'n': {}}
    classes = sorted({t['cls'] for t in theorems})
    for m in models:
        for c in classes + ['all']:
            names = [n for n, t in thm.items() if (c == 'all' or t['cls'] == c) and n in per_model[m]]
            if not names:
                continue
            g = np.mean([bool(per_model[m][n]['greedy_ok']) for n in names])
            p = np.mean([any(per_model[m][n]['sample_ok']) or bool(per_model[m][n]['greedy_ok']) for n in names])
            p16 = np.mean([any(per_model[m][n]['sample_ok']) for n in names])
            out['rates'][f'{m}/{c}'] = {'greedy': float(g), 'pass16': float(p16), 'any17': float(p), 'n': len(names)}
    ladder = [m for m in SCALES if m in per_model]
    first = {}
    for n, t in thm.items():
        fs = None
        for k, m in enumerate(ladder):
            r = per_model[m].get(n)
            if r and (any(r['sample_ok']) or bool(r['greedy_ok'])):
                fs = k
                break
        first[n] = fs
    out['ladder'] = ladder
    out['first_scale'] = {n: (ladder[k] if k is not None else None) for n, k in first.items()}
    from scipy.stats import spearmanr
    for c in classes + ['all']:
        names = [n for n, t in thm.items() if (c == 'all' or t['cls'] == c)]
        rank = np.array([first[n] if first[n] is not None else len(ladder) for n in names], dtype=float)
        for key in ('rl_logp_T08', 'thm_logp_T08_any', 'rl_written'):
            x = np.array([thm[n][key] for n in names], dtype=float)
            if len(names) > 2 and np.std(rank) > 0 and np.std(x) > 0:
                rho, pv = spearmanr(rank, x)
            else:
                rho, pv = float('nan'), float('nan')
            out['spearman'][f'{c}/{key}'] = {'rho': float(rho), 'p': float(pv), 'n': len(names),
                                             'n_unsolved': int(sum(first[n] is None for n in names))}
        out['n'][c] = len(names)
        out['first_scale_hist'] = out.get('first_scale_hist', {})
        out['first_scale_hist'][c] = dict(collections.Counter(out['first_scale'][n] or 'none' for n in names))
    return out


def figures(s2, metric, s3, theorems, figdir):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    os.makedirs(figdir, exist_ok=True)
    C = {'tokens': '#4C72B0', 'lean': '#DD8452', 'english': '#55A868'}
    if s2:
        fig, axes = plt.subplots(1, 2, figsize=(11, 4))
        for ax, m in zip(axes, ('greedy', 'pass8')):
            for f in s2['forms']:
                ys = [s2['by_form_group'].get(f'{f}/{m}/{g}', float('nan')) for g in GROUPS]
                ax.plot(range(len(GROUPS)), ys, 'o-', color=C.get(f, 'k'), label=f)
            ax.set_xticks(range(len(GROUPS)))
            ax.set_xticklabels(GROUPS, rotation=20)
            ax.set_ylim(0, 1)
            ax.set_ylabel('accuracy')
            ax.set_title(f'Qwen3-Coder-30B in-context, {m} (mean of 5 draws)')
            ax.grid(alpha=0.3)
        axes[0].legend()
        fig.tight_layout()
        fig.savefig(f'{figdir}/run1_forms.png', dpi=130)
        plt.close(fig)
        # delta plot
        fig, ax = plt.subplots(figsize=(7, 4))
        for i, m in enumerate(('greedy', 'pass8')):
            for j, f in enumerate([x for x in s2['forms'] if x != 'tokens']):
                xs, ys, lo, hi = [], [], [], []
                for k, g in enumerate(['all'] + GROUPS):
                    d = s2['delta'].get(f'{f}-tokens/{m}/{g}')
                    if d:
                        xs.append(k + (i * 2 + j) * 0.15 - 0.2)
                        ys.append(d['mean'])
                        lo.append(d['mean'] - d['ci95'][0])
                        hi.append(d['ci95'][1] - d['mean'])
                ax.errorbar(xs, ys, yerr=[lo, hi], fmt='o' if m == 'greedy' else 's', color=C[f], label=f'{f} − tokens ({m})', capsize=3)
        ax.axhline(0, color='k', lw=0.8)
        ax.set_xticks(range(len(GROUPS) + 1))
        ax.set_xticklabels(['all'] + GROUPS, rotation=20)
        ax.set_ylabel('paired accuracy difference')
        ax.set_title('Surface form effect (95 % bootstrap CI over theorems)')
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
        fig.tight_layout()
        fig.savefig(f'{figdir}/run1_delta.png', dpi=130)
        plt.close(fig)
    if s3 and s3.get('models'):
        fig, axes = plt.subplots(1, 2, figsize=(11, 4))
        classes = sorted({t['cls'] for t in theorems})
        ladder = s3['ladder']
        for c, col in zip(classes, ['#4C72B0', '#DD8452', '#55A868', '#8172B2']):
            ys = [s3['rates'].get(f'{m}/{c}', {}).get('any17', float('nan')) for m in ladder]
            axes[0].plot([SCALE_B[m] for m in ladder], ys, 'o-', color=col, label=f'{c} (n={s3["n"][c]})')
        axes[0].set_xscale('log')
        axes[0].set_xlabel('Qwen3 parameters (B)')
        axes[0].set_ylabel('theorems with ≥ 1 Lean proof (greedy + 16 samples)')
        axes[0].set_ylim(0, 1)
        axes[0].grid(alpha=0.3)
        axes[0].legend()
        axes[0].set_title('RL-found classes: solve rate by scale')
        thm = {t['name']: t for t in theorems}
        for c, col in zip(classes, ['#4C72B0', '#DD8452', '#55A868', '#8172B2']):
            names = [n for n, t in thm.items() if t['cls'] == c]
            x = [thm[n]['rl_logp_T08'] for n in names]
            y = [ladder.index(s3['first_scale'][n]) if s3['first_scale'][n] else len(ladder) for n in names]
            axes[1].scatter(x, np.array(y) + np.random.default_rng(1).uniform(-0.15, 0.15, len(y)), s=14, color=col, alpha=0.7, label=c)
        axes[1].set_yticks(range(len(ladder) + 1))
        axes[1].set_yticklabels([m.replace('Qwen3-', '') for m in ladder] + ['none'])
        axes[1].set_xlabel('base log p(RL-found proof) at T = 0.8 (Phase 1)')
        axes[1].set_ylabel('smallest scale with a Lean proof')
        axes[1].grid(alpha=0.3)
        axes[1].legend()
        axes[1].set_title('First-success scale vs base log-prob')
        fig.tight_layout()
        fig.savefig(f'{figdir}/run1_scale.png', dpi=130)
        plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--judged', default=None)
    ap.add_argument('--scale', default=None, help='glob of judged scale files')
    ap.add_argument('--theorems', default='data/r1/scale_theorems.jsonl')
    ap.add_argument('--out', default='artifacts/r1/summary.json')
    ap.add_argument('--fig', default='figures')
    a = ap.parse_args()
    s2 = metric = s3 = None
    theorems = load(a.theorems) if os.path.exists(a.theorems) else []
    if a.judged and os.path.exists(a.judged):
        s2, metric = step2(load(a.judged))
    if a.scale:
        files = sorted(glob.glob(a.scale))
        if files:
            s3 = step3(files, theorems)
    json.dump({'step2': s2, 'step3': s3}, open(a.out, 'w'), indent=1)
    figures(s2, metric, s3, theorems, a.fig)
    if s2:
        print('| form | greedy | pass@1 | pass@8 | greedy lenient | pass@8 lenient |')
        print('|---|---:|---:|---:|---:|---:|')
        for f in s2['forms']:
            print(f"| {f} | {s2['by_form'][f + '/greedy']:.3f} | {s2['by_form'][f + '/pass1']:.3f} | {s2['by_form'][f + '/pass8']:.3f} | {s2['by_form'][f + '/greedy_len']:.3f} | {s2['by_form'][f + '/pass8_len']:.3f} |")
        print('\n| form / metric | ' + ' | '.join(GROUPS) + ' |')
        print('|---|' + '---:|' * len(GROUPS))
        for f in s2['forms']:
            for m in ('greedy', 'pass8'):
                print(f'| {f} {m} | ' + ' | '.join(f"{s2['by_form_group'][f'{f}/{m}/{g}']:.3f}" for g in GROUPS) + ' |')
        print('\n| delta | mean | 95% CI | n |')
        print('|---|---:|---|---:|')
        for k, d in s2['delta'].items():
            print(f"| {k} | {d['mean']:+.3f} | [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}] | {d['n_theorems']} |")
        print('\ngreedy failure reasons:', json.dumps(s2['greedy_failure_reasons'], indent=1))
    if s3:
        print('\n| model | ' + ' | '.join(f'{c} greedy / any17' for c in sorted(s3['n'])) + ' |')
        for m in s3['models']:
            print(f'| {m} | ' + ' | '.join(f"{s3['rates'].get(f'{m}/{c}', {}).get('greedy', float('nan')):.2f} / {s3['rates'].get(f'{m}/{c}', {}).get('any17', float('nan')):.2f}" for c in sorted(s3['n'])) + ' |')
        print(json.dumps(s3['spearman'], indent=1))
        print(json.dumps(s3['first_scale_hist'], indent=1))


if __name__ == '__main__':
    main()
