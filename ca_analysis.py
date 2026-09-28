#!/usr/bin/env python3
"""Run ckpt-avg analysis (VPS, no torch).  Every number is recomputed from the per-theorem half-B files
artifacts/ca/ev/<stem>.jsonl and the half-A losses artifacts/ca/valloss_A.jsonl.

Model for every number: run stage1-dynamics' checkpoints, 3,214,336 params, from scratch, lean_seq,
cap 6, WSD (arm W: data/p2/train_depth3_f0_a1.jsonl, seeds 0-7; arm F: data/sd/train_fresh.jsonl,
seeds 0-3), and uniform weight averages of them.  Judge: Lean alone.

  python3 ca_analysis.py      -> artifacts/ca/summary.json, stdout tables
"""
import collections, glob, gzip, json, math, os, statistics as st, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scipy import stats as sps
from ca_plan import averages, candidates, runs

EV = 'artifacts/ca/ev'
SL = ['len2', 'len3', 'len4', 'len5', 'len6', 'len6nd3', 'depth3', 'all']
CUT = 0.44
ARMS = {'W': [f'w_s{k}' for k in range(8)], 'F': [f'f_s{k}' for k in range(4)]}
VARIANTS = {'W': ['E24', 'A24_K2', 'A24_K4', 'A24_K8', 'T24_3', 'T24_5', 'LS6', 'LSd3',
                  'E12', 'A12_K2', 'A12_K4', 'A12_K8', 'E6', 'A6_K2', 'A6_K4'],
            'F': ['E24', 'A24_K2', 'A24_K4', 'A24_K8', 'T24_3', 'LS6', 'LSd3']}
RULE_CANDS = ['A24_K2', 'A24_K4', 'A24_K8', 'T24_3', 'T24_5', 'LS6', 'LSd3']


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


_cache = {}
def ev(stem):
    """Per-slice rates + term size / lines of solved proofs on half B, from the per-theorem file."""
    if stem in _cache:
        return _cache[stem]
    rows = [json.loads(l) for l in gzip.open(f'{EV}/{stem}.jsonl.gz', 'rt')]
    assert len(rows) == 2500, stem
    s = {}
    groups = {'all': rows, 'depth3': [r for r in rows if r['depth3']],
              'len6nd3': [r for r in rows if r['n_lines'] == 6 and not r['depth3']]}
    for L in range(2, 7):
        groups[f'len{L}'] = [r for r in rows if r['n_lines'] == L]
    for k, g in groups.items():
        ok = [r for r in g if r['lean_ok']]
        s[k] = len(ok) / len(g)
        s[k + '_n'] = len(g)
        if k in ('all', 'depth3', 'len6'):
            s[k + '_term'] = st.mean(r['n_tok'] for r in ok) if ok else None
            s[k + '_have'] = st.mean(r['n_have'] for r in ok) if ok else None
    meta = json.load(open(f'{EV}/{stem}.json'))
    s['hit_max_new'] = meta.get('hit_max_new'); s['peak_alloc_gb'] = (meta.get('sampler_stats') or {}).get('peak_alloc_gb')
    s['_verdicts'] = [r['lean_ok'] for r in rows]
    _cache[stem] = s
    return s


def main():
    loss = {}
    for l in open('artifacts/ca/valloss_A.jsonl'):
        r = json.loads(l)
        loss[os.path.basename(r['ckpt'])[:-3]] = r['loss']
    avg = averages()
    out = {'model': 'stage1-dynamics checkpoints: 3,214,336 params, from scratch, lean_seq, cap 6, WSD; '
                    'arm W = data/p2/train_depth3_f0_a1.jsonl seeds 0-7, arm F = data/sd/train_fresh.jsonl seeds 0-3',
           'judge': 'Lean alone (sd_eval.py)', 'eval_set': 'data/ca/heldout_B.jsonl (2,500; 250 depth-3)',
           'selection_set': 'data/ca/heldout_A.jsonl', 'cut': CUT, 'arms': {}}

    # per-run: variant -> checkpoint stem(s)
    def stem_of(run, v):
        ends = dict((s, e) for s, _, e in runs())[run]
        if v in ends:
            return ends[v]
        if v.startswith('LS'):
            key = 'len6' if v == 'LS6' else 'depth3'
            c = candidates(run)
            return min(c, key=lambda x: loss[x][key])
        return f'{run}.{v}'

    for arm, rs in ARMS.items():
        A = out['arms'][arm] = {'seeds': rs, 'variants': {}}
        base = {sl: [ev(stem_of(r, 'E24'))[sl] for r in rs] for sl in SL}
        for v in VARIANTS[arm]:
            stems = [stem_of(r, v) for r in rs]
            if not all(os.path.exists(f'{EV}/{s}.jsonl.gz') for s in stems):
                continue
            vals = {sl: [ev(s)[sl] for s in stems] for sl in SL}
            d = {'ckpts': stems, 'per_seed': vals, 'mean': {}, 'sd': {}}
            for sl in SL:
                d['mean'][sl] = st.mean(vals[sl]); d['sd'][sl] = st.stdev(vals[sl])
            hi = sum(x >= CUT for x in vals['depth3'])
            d['high_mode'] = {'k': hi, 'n': len(rs), 'ci': wilson(hi, len(rs))}
            for k in ('all_term', 'depth3_term', 'len6_term', 'all_have'):
                xs = [ev(s)[k] for s in stems if ev(s)[k] is not None]
                d['mean'][k] = st.mean(xs) if xs else None
            if v != 'E24':
                n = len(rs)
                d['vs_E24'] = {}
                for sl in SL:
                    diff = [a - b for a, b in zip(vals[sl], base[sl])]
                    se = st.stdev(diff) / math.sqrt(n) if n > 1 else float('nan')
                    t = sps.t.ppf(0.975, n - 1)
                    d['vs_E24'][sl] = {'mean_diff': st.mean(diff), 'ci': (st.mean(diff) - t * se, st.mean(diff) + t * se)}
                for sl in ('depth3', 'len6'):
                    ratio = st.stdev(base[sl]) / max(d['sd'][sl], 1e-9)
                    # F-test CI on the sd ratio (independent-sample approximation; ignores the pairing)
                    lo = ratio / math.sqrt(sps.f.ppf(0.975, n - 1, n - 1)); hi_ = ratio * math.sqrt(sps.f.ppf(0.975, n - 1, n - 1))
                    d.setdefault('sd_ratio', {})[sl] = {'ratio': ratio, 'ci': (lo, hi_)}
            if v.startswith('LS'):
                d['selected_step'] = [s.split('.step')[1] if '.step' in s else s for s in stems]
            # averages vs their constituents
            if stems[0] in avg:
                pos = collections.Counter(); above_mean = 0; rows = []
                for s in stems:
                    cs = [ev(m)['depth3'] for m in avg[s]]
                    x = ev(s)['depth3']
                    p = 'above' if x > max(cs) else 'below' if x < min(cs) else 'between'
                    pos[p] += 1; above_mean += x > st.mean(cs)
                    easy = {sl: ev(s)[sl] - st.mean(ev(m)[sl] for m in avg[s]) for sl in ('len2', 'len3', 'len4', 'len5', 'all')}
                    worst = {sl: ev(s)[sl] - min(ev(m)[sl] for m in avg[s]) for sl in ('len2', 'len3', 'len4', 'len5')}
                    rows.append({'avg': x, 'constituents': cs, 'pos': p, 'minus_const_mean': easy, 'minus_const_worst': worst})
                d['vs_constituents'] = {'depth3_position': dict(pos), 'depth3_above_const_mean': above_mean, 'rows': rows}
            A['variants'][v] = d
        # adoption rule (arm W only)
        if arm == 'W':
            E = A['variants']['E24']
            res = {}
            for v in RULE_CANDS:
                if v not in A['variants']:
                    continue
                d = A['variants'][v]
                c1 = d['sd']['depth3'] <= 0.5 * E['sd']['depth3']
                c2 = d['sd']['len6'] < E['sd']['len6']
                c3 = all(d['mean'][sl] >= E['mean'][sl] - 0.02 for sl in ['len2', 'len3', 'len4', 'len5', 'len6', 'depth3'])
                res[v] = {'sd_depth3_halved': c1, 'sd_len6_lower': c2, 'no_bin_down_2pp': c3, 'adopt': c1 and c2 and c3}
            out['rule'] = res
        # the rule's candidates also scored on the trajectory's own oscillation: readout-mean reference
        tm = []
        for r in rs:
            steps = [c for c in candidates(r) if '.step' in c]
            tm.append(st.mean(ev(c)['depth3'] for c in steps))
        A['trajectory_mean_readout_depth3'] = {'per_seed': tm, 'mean': st.mean(tm), 'sd': st.stdev(tm)}

    # control: self-average reproduces its constituent exactly
    c = 'w_s0.CTRL_self19000'
    if os.path.exists(f'{EV}/{c}.jsonl.gz'):
        out['control_self_average_identical'] = ev(c)['_verdicts'] == ev('w_s0.step19000')['_verdicts']
    # truncation and memory
    js = [json.load(open(f)) for f in glob.glob(f'{EV}/*.json')]
    out['n_evals'] = len(js)
    out['hit_max_new_total'] = sum(j.get('hit_max_new', 0) for j in js)
    out['hit_max_new_max_per_eval'] = max(j.get('hit_max_new', 0) for j in js)
    out['peak_alloc_gb_max'] = max((j.get('sampler_stats') or {}).get('peak_alloc_gb', 0) for j in js)
    out['sampler'] = js[0]['sampler']
    # loss vs accuracy on half A/B across every W trajectory checkpoint (Spearman)
    xs, ys = [], []
    for r in ARMS['W']:
        for cnd in candidates(r):
            xs.append(loss[cnd]['depth3']); ys.append(ev(cnd)['depth3'])
    out['spearman_W_lossA_d3_vs_accB_d3'] = sps.spearmanr(xs, ys).statistic
    out['spearman_n'] = len(xs)
    for s in _cache.values():
        s.pop('_verdicts', None)
    json.dump(out, open('artifacts/ca/summary.json', 'w'), indent=1, default=float)
    # ---- tables
    for arm, A in out['arms'].items():
        print(f'\n## arm {arm} (n={len(A["seeds"])}), half B; mean (sd); d3 high = seeds >= {CUT}')
        print(f'{"variant":9s} ' + ' '.join(f'{sl:>13s}' for sl in SL) + '  high  sdratio_d3 [95%]   d(d3) vs E24')
        for v, d in A['variants'].items():
            sr = d.get('sd_ratio', {}).get('depth3')
            dd = d.get('vs_E24', {}).get('depth3')
            print(f'{v:9s} ' + ' '.join(f'{d["mean"][sl]:.3f}({d["sd"][sl]:.3f})' for sl in SL)
                  + f'  {d["high_mode"]["k"]}/{d["high_mode"]["n"]}'
                  + (f'  {sr["ratio"]:.2f} [{sr["ci"][0]:.2f},{sr["ci"][1]:.2f}]' if sr else '')
                  + (f'  {dd["mean_diff"]:+.3f} [{dd["ci"][0]:+.3f},{dd["ci"][1]:+.3f}]' if dd else ''))
        print('depth-3 per seed:')
        for v, d in A['variants'].items():
            print(f'  {v:9s} ' + ' '.join(f'{x:.2f}' for x in d['per_seed']['depth3'])
                  + (f'   pos {d["vs_constituents"]["depth3_position"]} >mean {d["vs_constituents"]["depth3_above_const_mean"]}' if 'vs_constituents' in d else '')
                  + (f'   sel {d["selected_step"]}' if 'selected_step' in d else ''))
        print('trajectory-mean readout d3:', {k: A['trajectory_mean_readout_depth3'][k] for k in ('mean', 'sd')})
    print('\nrule:', json.dumps(out.get('rule'), indent=0))
    print({k: out[k] for k in out if k.startswith(('control', 'hit', 'peak', 'n_evals', 'spearman'))})


if __name__ == '__main__':
    main()
