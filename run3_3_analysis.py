#!/usr/bin/env python3
"""Round 3, run 3: base generalisation by pattern class, 24 Stage-1 seeds per set, no RL.

  python run3_3_analysis.py --out artifacts/r3_3/summary.json --figs figures [--seeds 30-53]

Per set (depth3 / reductio / derived_ore) and seed: coverage files artifacts/r3_3/cov_<tag>_s<seed>_<pool>.s0.jsonl
(pass@2000, T = 0.8, every distinct verified proof with its hit count and pattern labels; first-half predicate counts over
every decoded sample), training logs artifacts/r3_3/train_<tag>_s<seed>.log (running val + final heldout_breakdown).

Definitions (preregistration/round3-run3.md): a draw GENERALISES iff >= 1 verified sample over the full pool carries the
pattern (patterns.classify on the pruned proof); rate = sum of pattern hits / sum of samples, re-derived from the per-proof
`count` fields (asserted equal to hits_by_pattern); frozen@256 = targets whose first pattern hit index <= 256;
Clopper-Pearson 95 % intervals; Spearman rho of predictors vs the generalisation indicator and vs log10 rate among
generalisers, permutation p (10,000 shuffles, seed 0).  The ignition study's draws (artifacts/ign/summary.json,
300-target samples) are an external stratum, never pooled.
"""
import argparse, json, os, sys, glob, math, re, collections, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ignition_analysis import clopper_pearson

SETS = {
    'depth3': dict(tag='depth3_f0_a1', pattern='depth3', pools=['p1', 'p2'], primary_fh='d3_written',
                   pool_files={'p1': 'data/r3_3/targets_depth3_p1.jsonl', 'p2': 'data/r3_3/targets_depth3_p2.jsonl'}, ign='depth3'),
    'reductio': dict(tag='reductio_f0', pattern='reductio', pools=['req'], primary_fh='negi_neggoal_nodn',
                     pool_files={'req': 'data/p2/targets_reductio_req.jsonl'}, ign='reductio'),
    'derived_ore': dict(tag='derived_ore_f0', pattern='derived_ore_strict', pools=['dos6'], primary_fh='derived_disj',
                        pool_files={'dos6': 'data/r3_3/targets_derived_ore_strict_c6.jsonl'}, ign=None),
}
RULES_OF_INTEREST = ('AS', 'IMPI', 'NEGI', 'DN', 'NEGE', 'ORE', 'IMPE', 'ANDE1', 'ANDE2', 'ORI1', 'ORI2', 'BOTE', 'R')


def load_pool(fn):
    recs = [json.loads(l) for l in open(fn) if l.strip()]
    return {r['name']: r for r in recs}


def coverage_stats(fn, pattern, pool):
    recs = [json.loads(l) for l in open(fn) if l.strip()]
    st = dict(file=fn, n_targets=len(recs), n_tried=0, n_ok=0, solved_any=0, hits=0, targets_with_pattern=0, distinct_pattern_proofs=0,
              frozen256_pattern_theorems=0, frozen256_solved_any=0, n_parsed=0, fh=collections.Counter(), fh_ok=collections.Counter(),
              written_hist=collections.Counter(), per_target=[], hits_required=0, targets_required_with_pattern=0, hits_by_stratum=collections.Counter(),
              hits_all_patterns=collections.Counter(), solved_by_stratum=collections.Counter())
    for r in recs:
        ps = r['proofs']
        assert sum(p['count'] for p in ps) == r['n_ok'], fn
        hp = sum(p['count'] for p in ps if p['pat'][pattern])
        assert hp == r['hits_by_pattern'][pattern], (fn, r['name'])
        st['n_tried'] += r['n_tried']; st['n_ok'] += r['n_ok']; st['solved_any'] += bool(r['n_ok']); st['hits'] += hp
        st['n_parsed'] += r.get('n_parsed', 0)
        for k, v in r['hits_by_pattern'].items(): st['hits_all_patterns'][k] += v
        for k, v in (r.get('fh_by_pred') or {}).items(): st['fh'][k] += v
        for k, v in (r.get('fh_ok_by_pred') or {}).items(): st['fh_ok'][k] += v
        tgt = pool.get(r['name'], {})
        stratum = tgt.get('stratum') or ('required' if tgt.get('requires') else 'other')
        st['solved_by_stratum'][stratum] += bool(r['n_ok'])
        if hp:
            st['targets_with_pattern'] += 1; st['distinct_pattern_proofs'] += sum(1 for p in ps if p['pat'][pattern])
            first_p = min(p['first'] for p in ps if p['pat'][pattern])
            st['frozen256_pattern_theorems'] += first_p <= 256
            for p in ps:
                if p['pat'][pattern]: st['written_hist'][p['written']] += 1
            st['hits_by_stratum'][stratum] += hp
            if stratum in ('required', 'required8'):
                st['hits_required'] += hp; st['targets_required_with_pattern'] += 1
            st['per_target'].append({'name': r['name'], 'thm': r['thm'], 'hits': hp, 'n_tried': r['n_tried'], 'first': first_p,
                                     'stratum': stratum, 'schema': tgt.get('schema'), 'n_lines': tgt.get('n_lines', r.get('gen_lines'))})
        if r['first_hit'] is not None and r['first_hit'] <= 256:
            st['frozen256_solved_any'] += 1
    st['per_target'].sort(key=lambda x: -x['hits'])
    for k in ('fh', 'fh_ok', 'written_hist', 'hits_by_stratum', 'hits_all_patterns', 'solved_by_stratum'):
        st[k] = dict(sorted(st[k].items(), key=lambda kv: str(kv[0])))
    return st


def parse_train_log(fn):
    if not os.path.exists(fn):
        return None
    out = {'file': fn, 'val': None, 'val_curve': [], 'breakdown': None, 'saved': False}
    for l in open(fn):
        m = re.match(r'step (\d+) loss ([\d.]+) lr \S+ \d+s val ([\d.]+)', l)
        if m:
            out['val_curve'].append((int(m.group(1)), float(m.group(3)))); out['val'] = float(m.group(3))
        if l.startswith('heldout_breakdown '):
            out['breakdown'] = json.loads(l[len('heldout_breakdown '):])
        if l.startswith('saved '):
            out['saved'] = True
    return out


def ranks(v):
    idx = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and v[idx[j + 1]] == v[idx[i]]:
            j += 1
        for k in range(i, j + 1):
            r[idx[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(x, y):
    n = len(x); mx = sum(x) / n; my = sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x)); sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def spearman_perm(x, y, n_perm=10000, seed=0):
    """Spearman rho and a two-sided permutation p (y shuffled)."""
    if len(x) < 4:
        return {'rho': None, 'p': None, 'n': len(x)}
    rx, ry = ranks(x), ranks(y)
    rho = pearson(rx, ry)
    if rho is None:
        return {'rho': None, 'p': None, 'n': len(x)}
    rng = random.Random(seed); ge = 0; ry2 = list(ry)
    for _ in range(n_perm):
        rng.shuffle(ry2); r2 = pearson(rx, ry2)
        if r2 is not None and abs(r2) >= abs(rho) - 1e-12:
            ge += 1
    return {'rho': rho, 'p': (ge + 1) / (n_perm + 1), 'n': len(x)}


def analyse_set(name, cfg, seeds, root):
    pat = cfg['pattern']; tag = cfg['tag']
    pools = {p: load_pool(os.path.join(root, cfg['pool_files'][p])) for p in cfg['pools']}
    draws = {}
    for s in seeds:
        d = {'seed': s, 'pools': {}, 'complete': True}
        for p in cfg['pools']:
            fn = os.path.join(root, f'artifacts/r3_3/cov_{tag}_s{s}_{p}.s0.jsonl')
            if not os.path.exists(fn):
                d['pools'][p] = None; d['complete'] = False; continue
            st = coverage_stats(fn, pat, pools[p])
            if st['n_targets'] != len(pools[p]):
                st['partial'] = True; d['complete'] = False
            d['pools'][p] = st
        have = [st for st in d['pools'].values() if st]
        d['n_tried'] = sum(st['n_tried'] for st in have); d['hits'] = sum(st['hits'] for st in have)
        d['rate'] = d['hits'] / d['n_tried'] if d['n_tried'] else None
        d['generalises'] = d['hits'] > 0 if have else None
        d['targets_with_pattern'] = sum(st['targets_with_pattern'] for st in have)
        d['frozen256_pattern_theorems'] = sum(st['frozen256_pattern_theorems'] for st in have)
        d['hits_required'] = sum(st['hits_required'] for st in have)
        d['n_parsed'] = sum(st['n_parsed'] for st in have)
        d['n_ok'] = sum(st['n_ok'] for st in have); d['solved_any'] = sum(st['solved_any'] for st in have)
        hap = collections.Counter(); sbs = collections.Counter()
        for st in have:
            hap.update(st['hits_all_patterns']); sbs.update(st['solved_by_stratum'])
        d['hits_all_patterns'] = dict(hap); d['solved_by_stratum'] = dict(sbs)
        fh = collections.Counter()
        for st in have:
            fh.update(st['fh'])
        d['fh_rate'] = {k: v / d['n_parsed'] for k, v in fh.items()} if d['n_parsed'] else {}
        d['primary_fh_rate'] = d['fh_rate'].get(cfg['primary_fh'])
        d['hit_targets'] = [t for st in have for t in st['per_target']]
        d['train'] = parse_train_log(os.path.join(root, f'artifacts/r3_3/train_{tag}_s{s}.log'))
        draws[s] = d
    done = [d for d in draws.values() if d['generalises'] is not None]
    full = [d for d in done if d['complete']]
    k = sum(d['generalises'] for d in done); n = len(done)
    out = {'pattern': pat, 'tag': tag, 'pools': {p: len(pools[p]) for p in cfg['pools']}, 'seeds': seeds,
           'n_draws_sampled': n, 'n_draws_complete': len(full), 'n_with_pattern': k, 'fraction': k / n if n else None,
           'ci95': list(clopper_pearson(k, n)) if n else None,
           'rates': {d['seed']: d['rate'] for d in done}, 'rates_when_present': {d['seed']: d['rate'] for d in done if d['generalises']},
           'frozen256_pattern_theorems': {d['seed']: d['frozen256_pattern_theorems'] for d in done},
           'targets_with_pattern': {d['seed']: d['targets_with_pattern'] for d in done},
           'hits_required_stratum': {d['seed']: d['hits_required'] for d in done},
           'val': {d['seed']: (d['train'] or {}).get('val') for d in draws.values()},
           'primary_fh': cfg['primary_fh'], 'primary_fh_rate': {d['seed']: d['primary_fh_rate'] for d in done},
           'fh_rates': {d['seed']: d['fh_rate'] for d in done}, 'draws': {}}
    out['n_ok'] = {d['seed']: d['n_ok'] for d in done}; out['solved_any'] = {d['seed']: d['solved_any'] for d in done}
    out['hits_all_patterns'] = {d['seed']: d['hits_all_patterns'] for d in done}
    out['solved_by_stratum'] = {d['seed']: d['solved_by_stratum'] for d in done}
    pos = sorted(d['rate'] for d in done if d['rate'])
    out['rate_span'] = {'min': pos[0], 'max': pos[-1], 'orders_of_magnitude': math.log10(pos[-1] / pos[0])} if pos else None
    ratios = [d['primary_fh_rate'] / d['rate'] for d in done if d['rate'] and d['primary_fh_rate'] is not None]
    out['attempt_over_success_summary'] = {'n': len(ratios), 'min': min(ratios), 'median': sorted(ratios)[len(ratios) // 2], 'n_below_10x': sum(1 for x in ratios if x < 10)} if ratios else None
    zero = [d['primary_fh_rate'] for d in done if d['rate'] == 0 and d['primary_fh_rate'] is not None]
    out['primary_fh_rate_in_zero_hit_draws'] = {'n': len(zero), 'min': min(zero), 'max': max(zero), 'n_below_1e-4': sum(1 for x in zero if x < 1e-4)} if zero else None
    # POST-HOC (not pre-registered): fraction of draws with rate above fixed thresholds, robust to the detection floor of
    # '>= 1 hit' (1 / n_tried, which differs between pools: 1.7e-6 at 600k samples, 5e-7 at 2M)
    out['fraction_above'] = {}
    for thr in (1e-5, 1e-4):
        ka = sum(1 for d in done if d['rate'] and d['rate'] >= thr)
        out['fraction_above'][str(thr)] = {'k': ka, 'n': n, 'ci95': list(clopper_pearson(ka, n)) if n else None}
    out['detection_floor'] = {d['seed']: 1.0 / d['n_tried'] for d in done if d['n_tried']}
    out['hits'] = {d['seed']: d['hits'] for d in done}
    # rate histogram (log10 bins) with zero-hit draws separate
    hist = collections.Counter()
    for d in done:
        hist['0'] += d['rate'] == 0
        if d['rate']:
            hist[f'1e{math.floor(math.log10(d["rate"]))}'] += 1
    out['rate_hist'] = dict(sorted(hist.items()))
    # per-target concentration over all draws
    tc = collections.Counter(); tinfo = {}
    for d in done:
        for t in d['hit_targets']:
            tc[t['name']] += t['hits']; tinfo[t['name']] = t
    out['top_targets'] = [{**tinfo[nm], 'hits_all_draws': h, 'draws_hitting': sum(1 for d in done if any(t['name'] == nm for t in d['hit_targets']))}
                          for nm, h in tc.most_common(15)]
    out['n_targets_ever_hit'] = len(tc)
    # E3 for reductio: schema / length of every hit target
    if name == 'reductio':
        out['hit_schemata'] = dict(collections.Counter(f"{t['schema']}:{t['n_lines']}" for d in done for t in d['hit_targets']))
        out['hits_on_8plus_line_schema'] = sum(t['hits'] for d in done for t in d['hit_targets'] if (t['n_lines'] or 0) >= 8)
    # E5 for depth3: part 1 vs part 2
    if name == 'depth3':
        p1d = [d for d in draws.values() if d['pools'].get('p1') and not d['pools']['p1'].get('partial')]
        k1 = sum(1 for d in p1d if d['pools']['p1']['hits'] > 0)
        out['p1_only'] = {'n_draws': len(p1d), 'n_with_pattern': k1, 'ci95': list(clopper_pearson(k1, len(p1d))) if p1d else None,
                          'rates': {d['seed']: d['pools']['p1']['hits'] / d['pools']['p1']['n_tried'] for d in p1d},
                          'frozen256_pattern_theorems': {d['seed']: d['pools']['p1']['frozen256_pattern_theorems'] for d in p1d}}
        both = [d for d in full]
        out['p1_vs_p2'] = {'draws_with_both_parts': len(both),
                           'hits_p1': sum(d['pools']['p1']['hits'] for d in both), 'hits_p2': sum(d['pools']['p2']['hits'] for d in both),
                           'zero_p1_positive_p2': [d['seed'] for d in both if d['pools']['p1']['hits'] == 0 and d['pools']['p2']['hits'] > 0],
                           'generalise_p1_only': sum(1 for d in both if d['pools']['p1']['hits'] > 0),
                           'generalise_full': sum(1 for d in both if d['hits'] > 0),
                           'required8_hits': sum(d['hits_required'] for d in both),
                           'required8_draws_with_hit': sum(1 for d in both if d['hits_required'] > 0)}
    if name == 'derived_ore':
        out['required_stratum'] = {'hits': sum(d['hits_required'] for d in done), 'draws_with_hit': sum(1 for d in done if d['hits_required'] > 0)}
    # predictors
    preds = {}
    def add_pred(key, getter):
        xs, ys, ls = [], [], []
        for d in done:
            v = getter(d)
            if v is None: continue
            xs.append(v); ys.append(1.0 if d['generalises'] else 0.0)
            if d['generalises']: ls.append((v, math.log10(d['rate'])))
        if len(xs) >= 4:
            preds[key] = {'vs_generalises': spearman_perm(xs, ys), 'vs_log_rate_among_generalisers': spearman_perm([a for a, _ in ls], [b for _, b in ls]),
                          'values': {d['seed']: getter(d) for d in done if getter(d) is not None}}
    add_pred('heldout_val', lambda d: (d['train'] or {}).get('val'))
    for fh_key in sorted({k for d in done for k in d['fh_rate']}):
        add_pred(f'fh_{fh_key}', lambda d, k=fh_key: d['fh_rate'].get(k))
    def bd(d, grp, key):
        b = (d['train'] or {}).get('breakdown')
        return b[grp][key]['mean'] if b and key in b[grp] else None
    for r in RULES_OF_INTEREST:
        add_pred(f'rule_{r}', lambda d, r=r: bd(d, 'by_rule', r))
        add_pred(f'rulename_{r}', lambda d, r=r: bd(d, 'by_rule_name_pos', r))
    for c in ('bar', 'idx', 'formula', 'rule', 'ref', 'sep'):
        add_pred(f'class_{c}', lambda d, c=c: bd(d, 'by_class', c))
    out['predictors'] = preds
    # E7 attempt vs success
    out['attempt_over_success'] = {d['seed']: (d['primary_fh_rate'] / d['rate'] if d['rate'] and d['primary_fh_rate'] is not None else None) for d in done}
    out['draws'] = {d['seed']: {k: v for k, v in d.items() if k not in ('hit_targets',)} | {'hit_targets': d['hit_targets'][:10]} for d in draws.values()}
    return out



def deep_pass(name, cfg, seeds, root, main):
    """ADDENDUM (pre-registered 2026-09-18 09:45): deep second-seed pass, k = 20,000, sampling seed 1, on an a-priori pool.
    Compares, per draw, main-pass hits (whole pool, and restricted to the deep-pool targets) with deep-pass hits."""
    pat = cfg['pattern']; tag = cfg['tag']
    pool_fn = {'depth3': 'data/r3_3/targets_depth3_deep45.jsonl', 'reductio': 'data/r3_3/targets_reductio_deep52.jsonl'}.get(name)
    if not pool_fn:
        return None
    names = set(load_pool(os.path.join(root, pool_fn)))
    out = {'pool': pool_fn, 'n_targets': len(names), 'draws': {}}
    for s in seeds:
        fn = os.path.join(root, f'artifacts/r3_3/deep_{tag}_s{s}.s0.jsonl')
        if not os.path.exists(fn):
            continue
        recs = [json.loads(l) for l in open(fn) if l.strip()]
        if len(recs) != len(names):
            out['draws'][s] = {'partial': len(recs)}; continue
        hits = 0; n = 0; tw = 0
        for r in recs:
            assert sum(p['count'] for p in r['proofs']) == r['n_ok']
            hp = sum(p['count'] for p in r['proofs'] if p['pat'][pat]); assert hp == r['hits_by_pattern'][pat]
            hits += hp; n += r['n_tried']; tw += bool(hp)
        # main-pass hits restricted to the deep-pool targets
        mh = 0; mn = 0
        for p in cfg['pools']:
            for l in open(os.path.join(root, f'artifacts/r3_3/cov_{tag}_s{s}_{p}.s0.jsonl')):
                r = json.loads(l)
                if r['name'] in names:
                    mh += r['hits_by_pattern'][pat]; mn += r['n_tried']
        out['draws'][s] = {'deep_hits': hits, 'deep_n': n, 'deep_targets_with_pattern': tw, 'deep_rate': hits / n,
                           'main_hits_all': main['hits'][s], 'main_hits_on_deep_pool': mh, 'main_n_on_deep_pool': mn,
                           'main_rate_on_deep_pool': mh / mn if mn else None}
    D = {s: d for s, d in out['draws'].items() if 'deep_hits' in d}
    out['n_draws'] = len(D)
    zero_main = [s for s, d in D.items() if d['main_hits_all'] == 0]
    out['main_zero_draws'] = zero_main
    out['main_zero_with_deep_hit'] = [s for s in zero_main if D[s]['deep_hits'] > 0]
    out['main_ge2_confirmed'] = [sum(1 for s, d in D.items() if d['main_hits_all'] >= 2 and d['deep_hits'] > 0), sum(1 for d in D.values() if d['main_hits_all'] >= 2)]
    out['main_eq1_confirmed'] = [sum(1 for s, d in D.items() if d['main_hits_all'] == 1 and d['deep_hits'] > 0), sum(1 for d in D.values() if d['main_hits_all'] == 1)]
    either = sum(1 for d in D.values() if d['main_hits_all'] > 0 or d['deep_hits'] > 0); both0 = len(D) - either
    out['either_pass'] = {'k': either, 'n': len(D), 'ci95': list(clopper_pearson(either, len(D))) if D else None}
    out['zero_in_both'] = {'k': both0, 'n': len(D), 'ci95': list(clopper_pearson(both0, len(D))) if D else None}
    out['rate_ratio_deep_over_main'] = {s: d['deep_rate'] / d['main_rate_on_deep_pool'] for s, d in D.items() if d['main_hits_on_deep_pool'] >= 20}
    out['deep_rates'] = {s: d['deep_rate'] for s, d in D.items()}
    return out


def selfcheck(seeds, root):
    """Re-verify every stored pattern proof (main + deep files) with nd_verify and recompute its pattern label."""
    from nd_verify import verify_text
    from patterns import classify
    out = {}
    for name, cfg in SETS.items():
        n = 0; bad = 0
        files = [f'artifacts/r3_3/cov_{cfg["tag"]}_s{s}_{p}.s0.jsonl' for s in seeds for p in cfg['pools']] + [f'artifacts/r3_3/deep_{cfg["tag"]}_s{s}.s0.jsonl' for s in seeds]
        for fn in files:
            fn = os.path.join(root, fn)
            if not os.path.exists(fn): continue
            for l in open(fn):
                r = json.loads(l)
                for p in r['proofs']:
                    if p['pat'][cfg['pattern']]:
                        n += 1
                        ok, _, nl = verify_text(r['prompt'] + ' ' + p['proof'])
                        cl = classify(p['proof'])
                        bad += (not ok) or (not cl[cfg['pattern']]) or nl != p['written']
        out[name] = {'pattern_proofs_checked': n, 'failures': bad}
    return out

def external_stratum(root):
    fn = os.path.join(root, 'artifacts/ign/summary.json')
    if not os.path.exists(fn):
        return None
    s = json.load(open(fn)); out = {}
    for k in ('depth3', 'reductio'):
        bg = s[k]['base_generalisation']
        out[k] = {'n_draws': bg['n_draws'], 'n_with_pattern': bg['n_with_pattern'], 'fraction': bg['fraction'], 'ci95': bg['ci95'],
                  'rates_when_present': bg['rates_when_present'], 'sample': '300 targets x 2000 (reductio s0: 300 x 10000)'}
    return out


def table(summary):
    L = ['| set | pattern | pool | draws sampled (complete) | generalise | fraction | 95 % CI | rate hist | frozen@256 > 0 | ignition stratum |', '|---|---|---|---|---|---|---|---|---|---|']
    for name, o in summary['sets'].items():
        ext = (summary['external'] or {}).get(o.get('ign_key') or '', None) if summary.get('external') else None
        ext_s = f"{ext['n_with_pattern']}/{ext['n_draws']} ({ext['ci95'][0]:.2f}-{ext['ci95'][1]:.2f})" if ext else '-'
        ci = f"{o['ci95'][0]:.2f}-{o['ci95'][1]:.2f}" if o['ci95'] else '-'
        fz = sum(1 for v in o['frozen256_pattern_theorems'].values() if v > 0)
        L.append(f"| {name} | {o['pattern']} | {'+'.join(f'{p}:{n}' for p, n in o['pools'].items())} | {o['n_draws_sampled']} ({o['n_draws_complete']}) | {o['n_with_pattern']} | "
                 f"{(o['fraction'] or 0):.3f} | {ci} | {o['rate_hist']} | {fz} | {ext_s} |")
    L.append(''); L.append('| set | predictor | rho vs generalises | perm p | rho vs log rate (generalisers) | perm p | n |'); L.append('|---|---|---|---|---|---|---|')
    for name, o in summary['sets'].items():
        for key, p in o['predictors'].items():
            a, b = p['vs_generalises'], p['vs_log_rate_among_generalisers']
            f = lambda z: '-' if z is None else f'{z:.3f}'
            L.append(f"| {name} | {key} | {f(a['rho'])} | {f(a['p'])} | {f(b['rho'])} | {f(b['p'])} | {a['n']}/{b['n']} |")
    return '\n'.join(L)


def figures(summary, figdir):
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    os.makedirs(figdir, exist_ok=True)
    sets = summary['sets']; ext = summary.get('external') or {}
    # 1. generalisation fraction with CI, new vs ignition stratum
    fig, ax = plt.subplots(figsize=(6, 3.6)); xs = []; labels = []
    for i, (name, o) in enumerate(sets.items()):
        if o['ci95']:
            ax.errorbar([i], [o['fraction']], yerr=[[o['fraction'] - o['ci95'][0]], [o['ci95'][1] - o['fraction']]], fmt='o', color='C0', capsize=4,
                        label='this run (24 seeds, full pool)' if i == 0 else None)
        e = ext.get(o.get('ign_key') or '')
        if e:
            ax.errorbar([i + 0.2], [e['fraction']], yerr=[[e['fraction'] - e['ci95'][0]], [e['ci95'][1] - e['fraction']]], fmt='s', color='C1', capsize=4,
                        label='ignition study (300 targets)' if i == 0 else None)
        xs.append(i); labels.append(f"{name}\n{o['n_with_pattern']}/{o['n_draws_sampled']}")
    ax.set_xticks(xs); ax.set_xticklabels(labels); ax.set_ylim(0, 1); ax.set_ylabel('fraction of Stage-1 draws with >= 1 pattern sample'); ax.legend(fontsize=8)
    ax.set_title('Base generalisation per pattern class (Clopper-Pearson 95 %)', fontsize=10); fig.tight_layout(); fig.savefig(os.path.join(figdir, 'r3_3_generalisation.png'), dpi=130); plt.close(fig)
    # 2. rate histograms
    fig, axs = plt.subplots(1, len(sets), figsize=(3.4 * len(sets), 3.2), sharey=True)
    for ax, (name, o) in zip(axs, sets.items()):
        vals = [v for v in o['rates'].values() if v]; zeros = sum(1 for v in o['rates'].values() if v == 0)
        bins = list(range(-7, -1))
        ax.hist([math.log10(v) for v in vals], bins=[b - 0.5 for b in bins] + [bins[-1] + 0.5], color='C0', alpha=0.8)
        ax.bar([-8], [zeros], color='grey', width=0.9); ax.set_xticks([-8] + bins); ax.set_xticklabels(['0'] + [f'1e{b}' for b in bins], fontsize=7)
        ax.set_title(f"{name}: {o['n_with_pattern']}/{o['n_draws_sampled']} generalise", fontsize=9); ax.set_xlabel('per-sample pattern rate')
    axs[0].set_ylabel('draws'); fig.tight_layout(); fig.savefig(os.path.join(figdir, 'r3_3_rate_hist.png'), dpi=130); plt.close(fig)
    # 3. predictor scatter: primary first-half rate vs pattern rate; held-out val vs pattern rate
    fig, axs = plt.subplots(2, len(sets), figsize=(3.4 * len(sets), 6))
    for j, (name, o) in enumerate(sets.items()):
        floor = 1e-7
        for row, (key, xl) in enumerate(((f"fh_{o['primary_fh']}", f"first-half rate ({o['primary_fh']})"), ('heldout_val', 'held-out loss (final)'))):
            ax = axs[row, j]; p = o['predictors'].get(key)
            if not p: ax.set_visible(False); continue
            for s, x in p['values'].items():
                r = o['rates'][int(s)] if isinstance(s, str) else o['rates'][s]
                ax.scatter([x], [max(r, floor)], color='C0' if r else 'grey', s=22)
            ax.set_yscale('log'); ax.set_xlabel(xl, fontsize=8); ax.set_ylabel('pattern rate (0 at floor)', fontsize=8)
            if row == 0 and p['values'] and min(p['values'].values()) > 0: ax.set_xscale('log')
            a = p['vs_generalises']; ax.set_title(f"{name}: rho vs generalises {a['rho']:.2f} (p {a['p']:.3f})" if a['rho'] is not None else name, fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(figdir, 'r3_3_predictors.png'), dpi=130); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='artifacts/r3_3/summary.json'); ap.add_argument('--figs', default=None)
    ap.add_argument('--selfcheck', action='store_true'); ap.add_argument('--seeds', default='30-53'); ap.add_argument('--root', default=os.path.dirname(os.path.abspath(__file__)))
    a = ap.parse_args()
    lo, hi = map(int, a.seeds.split('-')); seeds = list(range(lo, hi + 1))
    summary = {'sets': {}, 'external': external_stratum(a.root)}
    for name, cfg in SETS.items():
        o = analyse_set(name, cfg, seeds, a.root); o['ign_key'] = cfg['ign']; o['deep'] = deep_pass(name, cfg, seeds, a.root, o); summary['sets'][name] = o
        if o['deep'] and o['deep']['n_draws']:
            dp = o['deep']; print(f"  deep pass: {dp['n_draws']} draws; main-zero {len(dp['main_zero_draws'])}, of which deep hit {len(dp['main_zero_with_deep_hit'])}; either pass {dp['either_pass']}; zero in both {dp['zero_in_both']}", flush=True)
        print(f"{name}: {o['n_with_pattern']}/{o['n_draws_sampled']} generalise (complete {o['n_draws_complete']}), CI {o['ci95']}, rate hist {o['rate_hist']}", flush=True)
    # E2
    d3, rd = summary['sets']['depth3'], summary['sets']['reductio']
    if d3['ci95'] and rd['ci95']:
        summary['E2_intervals_separate'] = d3['ci95'][0] > rd['ci95'][1]
        print('E2 separate:', summary['E2_intervals_separate'], d3['ci95'], rd['ci95'])
    if a.selfcheck:
        summary['selfcheck'] = selfcheck(seeds, a.root); print('selfcheck', summary['selfcheck'], flush=True)
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(summary, open(a.out, 'w'), indent=1, default=str)
    open(a.out.replace('.json', '_table.md'), 'w').write(table(summary) + '\n')
    print(table(summary))
    if a.figs:
        figures(summary, a.figs)


if __name__ == '__main__':
    main()
