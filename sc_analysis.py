#!/usr/bin/env python3
"""support-curves analysis: aggregate support.py's per-theorem records into artifacts/sc/summary.json,
then the crux sets, the scatter and the per-stratum pass@k curves.

  python3 sc_analysis.py summary                 # -> artifacts/sc/summary.json  (+ a printed table)
  python3 sc_analysis.py crux --k 10000          # -> data/sc/crux_forward.txt, data/sc/crux_reverse.txt
  python3 sc_analysis.py report                  # counts, pass@k, crossover k  -> artifacts/sc/report.json

A row of summary.json is one (theorem, model, temperature, seed) cell with n and c POOLED over every stage
that used those four labels.  Pooling is valid because support.py draws i.i.d. per theorem, so stage 2 is an
independent continuation of stage 1.  Every row names its source files.

p-hat = c / n.  Wilson 95 % interval throughout; for c = 0 the reported quantity is the 95 % upper bound
3 / n ("rule of three") and the scatter draws it as a downward arrow.

Stopping-rule caveat (pre-registered): a theorem that reached `stop_at` successes stopped at a batch boundary,
so its n is a stopping time and p-hat carries an O(1/c) ~ 2 % bias at stop_at = 50.  Theorems that never
reached it have fixed n and an exactly unbiased p-hat.  `stopped_early` is carried on every row.
"""
import argparse, json, os, glob, math, collections

ART = 'artifacts/sc'


def wilson(c, n, z=1.959963984540054):
    if n == 0:
        return (0.0, 1.0)
    p = c / n
    d = 1 + z * z / n
    ctr = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, ctr - half), min(1.0, ctr + half))


def load_rows(pattern=f'{ART}/*.jsonl'):
    """Every per-theorem record written by support.py, excluding the probe and the gate logs."""
    rows = []
    for fn in sorted(glob.glob(pattern)):
        base = os.path.basename(fn)
        if base.startswith('gate') or 'probe' in fn or base.startswith('summary') or base.startswith('report'):
            continue
        for l in open(fn):
            if not l.strip():
                continue
            r = json.loads(l)
            if 'n_tried' not in r or r.get('stage') == 'probe':
                continue
            r['_src'] = fn
            rows.append(r)
    return rows


def aggregate(rows):
    """(name, model, temperature, seed) -> pooled cell."""
    cells = {}
    for r in rows:
        k = (r['name'], r['model'], float(r['temperature']), int(r['seed']))
        c = cells.get(k)
        if c is None:
            c = cells[k] = {'name': r['name'], 'L_true': r['L_true'], 'schema': r.get('schema'),
                            'source': r.get('source'), 'model': r['model'], 'temperature': float(r['temperature']),
                            'seed': int(r['seed']), 'ckpt': r['ckpt'], 'ckpt_md5': r['ckpt_md5'],
                            'n': 0, 'c': 0, 'stages': {}, 'src': [], 'stopped_early': False,
                            'first_hit_s1': None, 'proofs': {}, 'gen_s': 0.0, 'lean_s': 0.0}
        assert c['ckpt_md5'] == r['ckpt_md5'], f"{k}: two checkpoints under one model label"
        c['n'] += r['n_tried']
        c['c'] += r['n_ok']
        c['stages'][r['stage']] = {'n': r['n_tried'], 'c': r['n_ok'], 'first_hit': r['first_hit'],
                                   'stopped_early': r['stopped_early']}
        c['src'].append(os.path.basename(r['_src']))
        c['stopped_early'] |= bool(r['stopped_early'])
        c['gen_s'] += r.get('gen_s', 0.0); c['lean_s'] += r.get('lean_s', 0.0)
        if r['stage'] == 's1':
            c['first_hit_s1'] = r['first_hit']
        for p in r['proofs']:                      # distinct accepted proofs, pooled; keep the earliest
            q = c['proofs'].get(p['proof'])
            if q is None:
                c['proofs'][p['proof']] = dict(p)
            else:
                q['count'] += p['count']
                q['first'] = min(q['first'], p['first'])
    for c in cells.values():
        lo, hi = wilson(c['c'], c['n'])
        c['p_hat'] = c['c'] / c['n'] if c['n'] else None
        c['wilson_lo'], c['wilson_hi'] = lo, hi
        c['ub95'] = 3.0 / c['n'] if (c['c'] == 0 and c['n']) else None    # rule of three
        c['n_distinct_ok'] = len(c['proofs'])
        c['min_lines'] = min((p['n_lines'] for p in c['proofs'].values()), default=None)
        c['min_term_size'] = min((p['term_size'] for p in c['proofs'].values()), default=None)
        c['proofs'] = sorted(c['proofs'].values(), key=lambda p: p['first'])
    return cells


def cmd_summary(a):
    rows = load_rows()
    cells = aggregate(rows)
    out = sorted(cells.values(), key=lambda c: (c['model'], c['seed'], c['temperature'], c['L_true'], c['name']))
    os.makedirs(ART, exist_ok=True)
    with open(f'{ART}/summary.json', 'w') as f:
        json.dump(out, f)
    print(f'{len(rows)} per-theorem records -> {len(out)} cells -> {ART}/summary.json')
    g = collections.defaultdict(lambda: [0, 0, 0, 0])          # (model,T,seed) -> [cells, solved, n, c]
    for c in out:
        k = (c['model'], c['temperature'], c['seed'])
        g[k][0] += 1; g[k][1] += (c['c'] > 0); g[k][2] += c['n']; g[k][3] += c['c']
    print(f"{'model':6} {'T':>4} {'seed':>4} {'cells':>6} {'solved':>7} {'samples':>12} {'ok':>8}")
    for k in sorted(g):
        v = g[k]
        print(f'{k[0]:6} {k[1]:4} {k[2]:4d} {v[0]:6d} {v[1]:7d} {v[2]:12,d} {v[3]:8,d}')
    return out


def cmd_crux(a):
    cells = aggregate(load_rows())
    base = {c['name']: c for c in cells.values() if c['model'] == 'base' and c['seed'] == 0 and c['temperature'] == 0.8}
    ei = {c['name']: c for c in cells.values() if c['model'] == 'ei' and c['seed'] == 0 and c['temperature'] == 0.8}
    names = sorted(set(base) & set(ei))

    def solved_within(c, k):
        """c >= 1 within the first k attempts of the STAGE-1 file -- exactly the pre-registered prefix count."""
        fh = c['stages'].get('s1', {}).get('first_hit')
        return fh is not None and fh <= k

    for k in (4000, a.k):
        fwd = [n for n in names if solved_within(ei[n], k) and not solved_within(base[n], k)]
        rev = [n for n in names if solved_within(base[n], k) and not solved_within(ei[n], k)]
        print(f'k={k:>6}: base solved {sum(solved_within(base[n],k) for n in names):3d}/{len(names)}  '
              f'ei solved {sum(solved_within(ei[n],k) for n in names):3d}/{len(names)}  '
              f'forward crux {len(fwd):3d}  reverse crux {len(rev):3d}')
        if k == a.k:
            os.makedirs('data/sc', exist_ok=True)
            open('data/sc/crux_forward.txt', 'w').write('\n'.join(fwd) + '\n')
            open('data/sc/crux_reverse.txt', 'w').write('\n'.join(rev) + '\n')
            hi = [n for n in fwd if ei[n]['p_hat'] and ei[n]['p_hat'] >= 0.01]
            open('data/sc/crux_forward_phi.txt', 'w').write('\n'.join(hi) + '\n')
            print(f'  wrote data/sc/crux_forward.txt ({len(fwd)}), crux_reverse.txt ({len(rev)}), '
                  f'crux_forward_phi.txt ({len(hi)}: the falsifier-eligible p_EI >= 0.01 subset)')
            by = collections.Counter(base[n]['L_true'] for n in fwd)
            print('  forward crux by L_true:', ' '.join(f'{l}:{c}' for l, c in sorted(by.items())))


def pass_at_k(n, c, k):
    """Unbiased pass@k = 1 - C(n-c, k)/C(n, k), for k <= n.  None beyond n (never extrapolate silently)."""
    if k > n:
        return None
    if c == 0:
        return 0.0
    if n - c < k:
        return 1.0
    lp = 0.0
    for i in range(k):
        lp += math.log(n - c - i) - math.log(n - i)
    return 1.0 - math.exp(lp)


def cmd_report(a):
    cells = aggregate(load_rows())
    rep = {'generated': __import__('time').strftime('%FT%TZ', __import__('time').gmtime()), 'strata': {}}
    for seed in sorted({c['seed'] for c in cells.values()}):
        for T in sorted({c['temperature'] for c in cells.values()}):
            base = {c['name']: c for c in cells.values() if c['model'] == 'base' and c['seed'] == seed and c['temperature'] == T}
            ei = {c['name']: c for c in cells.values() if c['model'] == 'ei' and c['seed'] == seed and c['temperature'] == T}
            names = sorted(set(base) & set(ei))
            if not names:
                continue
            by_L = collections.defaultdict(list)
            for n_ in names:
                by_L[base[n_]['L_true']].append(n_)
            for L, ns in sorted(by_L.items()):
                key = f'seed{seed}_T{T}_L{L}'
                curve = {}
                for k in (1, 10, 32, 100, 256, 1000, 2000, 4000, 10000, 20000, 50000, 100000):
                    b = [pass_at_k(base[x]['n'], base[x]['c'], k) for x in ns]
                    e = [pass_at_k(ei[x]['n'], ei[x]['c'], k) for x in ns]
                    b = [v for v in b if v is not None]; e = [v for v in e if v is not None]
                    if len(b) < len(ns) or len(e) < len(ns):     # k exceeds some theorem's n: not comparable
                        continue
                    curve[k] = {'base': sum(b) / len(b), 'ei': sum(e) / len(e), 'n_theorems': len(ns)}
                cross = next((k for k in sorted(curve) if curve[k]['base'] >= curve[k]['ei']), None)
                rep['strata'][key] = {'L_true': L, 'seed': seed, 'temperature': T, 'n_theorems': len(ns),
                                      'curve': curve, 'crossover_k': cross,
                                      'max_k_measured': max(curve) if curve else None}
                print(f'{key}: {len(ns):3d} thms  crossover_k={cross}  '
                      + ' '.join(f'{k}:{v["base"]:.3f}/{v["ei"]:.3f}' for k, v in sorted(curve.items()) if k in (256, 4000, 10000)))
    os.makedirs(ART, exist_ok=True)
    json.dump(rep, open(f'{ART}/report.json', 'w'), indent=1)
    print(f'-> {ART}/report.json')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('summary'); s.set_defaults(fn=cmd_summary)
    s = sub.add_parser('crux'); s.add_argument('--k', type=int, default=10000); s.set_defaults(fn=cmd_crux)
    s = sub.add_parser('report'); s.set_defaults(fn=cmd_report)
    a = ap.parse_args()
    a.fn(a)
