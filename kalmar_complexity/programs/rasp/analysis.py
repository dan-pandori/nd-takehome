#!/usr/bin/env python3
"""Measures of the RASP-L Kalmár policy and the calibration programs -> results.json (run kalmar-complexity).

  python3 kalmar_complexity/programs/rasp/analysis.py [--dump states_1000_s20261020.jsonl.gz] \
      [--test test_1000_s20261020.json] [--calib calibration.json] [--out results.json]

- program length (ops by kind, source tokens / lines), attention depth, MLP run, flagged ops: decision, rendering,
  total, at H = 9 (every K12 formula) and as a function of H (formula levels) and Hd (descent levels);
- per case of the decision (the rule that fires): the cone of nodes that decide it (its phase conditions, its own
  rule's inputs, its content values): ops and attention depth;
- per builder step tag: the cases that fired on the test states, the static cone (H = 9) and the *effective*
  attention depth of each state = the cone depth of a program with H = the state's largest formula height and
  Hd = the descent moves it needed + 1 (the smallest program that makes the same decision on that state).
"""
import argparse, collections, json, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rasp as R
import kalmar_policy as KP

PY = os.path.join(HERE, 'kalmar_policy.py')


def build(H, Hd=None):
    outs, info = KP.build_decision(H, Hd)
    nxt = KP.build_render(outs, info['start'])
    return outs, info, nxt


def static(H=9):
    outs, info, nxt = build(H)
    dec = R.metrics(list(outs.values()))
    tot = R.metrics([nxt])
    dec_ids = {n.id for n in R.ancestors(list(outs.values()))}
    ren_nodes = [n for n in R.ancestors([nxt]) if n.id not in dec_ids and n.kind not in R.FREE]
    kinds = collections.Counter(n.kind for n in ren_nodes)
    rflags = collections.Counter(f for n in ren_nodes for f in n.flags)
    # rendering alone: depth of the renderer measured from its inputs (decision outputs and `start` count as given)
    ren = {'ops': len(ren_nodes), 'by_kind': dict(kinds), 'flagged_ops': sum(1 for n in ren_nodes if n.flags),
           'flags': dict(rflags), 'attn_depth_added': tot['attn_depth'] - dec['attn_depth'],
           'attn_depth_alone': _depth_alone(nxt, dec_ids)}
    dsrc = [x + y for x, y in zip(R.source_size(R.region(PY, 'DECISION')),
                                  R.source_size(R.region(PY, 'DECISION_HELPERS')))]
    rsrc = [x + y + z for x, y, z in zip(R.source_size(R.region(PY, 'RENDER')),
                                         R.source_size(R.region(PY, 'RENDER_HELPERS')),
                                         R.source_size(R.region(PY, 'FORMULA_TOKENS')))]
    dec.update(source_tokens=dsrc[0], source_lines=dsrc[1])
    ren.update(source_tokens=rsrc[0], source_lines=rsrc[1])
    tot.update(source_tokens=dsrc[0] + rsrc[0], source_lines=dsrc[1] + rsrc[1])
    return dec, ren, tot, outs, info


def _depth_alone(out, given_ids):
    """attention depth of `out` counting only nodes outside `given_ids` (those are inputs)."""
    A = {}
    for n in R.ancestors([out]):
        if n.id in given_ids:
            A[n.id] = 0
            continue
        a = max((A[x.id] for x in n.args), default=0)
        A[n.id] = a + (1 if n.kind in R.ATTN else 0)
    return A[out.id]


def cone(nodes):
    m = R.metrics(nodes)
    return {'ops': m['ops'], 'attn_depth': m['attn_depth'], 'mlp_run': m['mlp_run'], 'flagged_ops': m['flagged_ops']}


def scaling():
    rows = []
    for H in range(1, 11):
        outs, info = KP.build_decision(H)
        m = R.metrics(list(outs.values()))
        rows.append({'H': H, 'ops': m['ops'], 'attn_depth': m['attn_depth'], 'mlp_run': m['mlp_run'],
                     'flagged_ops': m['flagged_ops']})
    return rows


GROUPS = {'PR': 'premise line', 'EM': 'excluded middle (top level and inside its two boxes)',
          'SPLIT': 'open / close a split', 'BOX': 'fixed steps inside a lemma box',
          'POST': 'leaf after the recursion (ex falso, R line, exact)',
          'REC': "Kalmar's recursion step (box opening, ∧I, ∨I) at the leaf"}


def _group(c):
    if c == 'PR':
        return 'PR'
    if c.startswith('LB') or c.startswith('LEM') or c == 'EX_LB':
        return 'EM'
    if c in ('SPLIT_ORE', 'EX_SPLIT'):
        return 'SPLIT'
    if c.startswith('BX') or c in ('EX_BOX', 'EXBL'):
        return 'BOX'
    if c.startswith('LF'):
        return 'REC'
    return 'POST'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dump', default=os.path.join(HERE, 'states_1000_s20261020.jsonl.gz'))
    ap.add_argument('--test', default=os.path.join(HERE, 'test_1000_s20261020.json'))
    ap.add_argument('--calib', default=os.path.join(HERE, 'calibration.json'))
    ap.add_argument('--out', default=os.path.join(HERE, 'results.json'))
    a = ap.parse_args()
    dec, ren, tot, outs, info = static(9)
    res = {'H': 9, 'decision': dec, 'rendering': ren, 'total': tot}
    print('decision', dec)
    print('rendering', ren)
    print('total', tot)
    sc = scaling()
    res['scaling_H'] = sc
    # fit ops and depth = a + b H over H >= 4 (shape levels saturate at 4)
    xs = [r['H'] for r in sc if r['H'] >= 4]
    for key in ('ops', 'attn_depth'):
        ys = [r[key] for r in sc if r['H'] >= 4]
        b = (ys[-1] - ys[0]) / (xs[-1] - xs[0])
        res[f'{key}_per_H'] = {'intercept': ys[0] - b * xs[0], 'slope': b}
    print('scaling', sc)
    # per case cones at H = 9
    res['cases'] = {cn: cone(info['deps'][cn]) for cn in KP.CASES}
    # per step tag from the dump
    if os.path.exists(a.dump):
        import gzip
        states = [json.loads(l) for l in (gzip.open(a.dump, 'rt') if a.dump.endswith('.gz') else open(a.dump))]
        need = {(max(s['hmax'], 1), s['moves'] + 1) for s in states}
        eff = {}
        for (H, Hd) in sorted(need):
            o, inf = KP.build_decision(H, Hd)
            eff[(H, Hd)] = {cn: R.metrics(inf['deps'][cn])['attn_depth'] for cn in KP.CASES}
        bytag = collections.defaultdict(list)
        for s in states:
            s['eff'] = eff[(max(s['hmax'], 1), s['moves'] + 1)][s['case']]
            bytag[s['tag']].append(s)
        tags = {}
        for tag, ss in sorted(bytag.items(), key=lambda kv: -len(kv[1])):
            cases = collections.Counter(s['case'] for s in ss)
            st_ops = [res['cases'][s['case']]['ops'] for s in ss]
            st_dep = [res['cases'][s['case']]['attn_depth'] for s in ss]
            ef = [s['eff'] for s in ss]
            mv = [s['moves'] for s in ss]
            tags[tag] = {'n': len(ss), 'cases': dict(cases.most_common()),
                         'static_ops_mean': round(statistics.mean(st_ops), 1), 'static_ops_range': [min(st_ops), max(st_ops)],
                         'static_attn_depth_mean': round(statistics.mean(st_dep), 2),
                         'static_attn_depth_range': [min(st_dep), max(st_dep)],
                         'effective_attn_depth_mean': round(statistics.mean(ef), 2),
                         'effective_attn_depth_median': statistics.median(ef),
                         'effective_attn_depth_range': [min(ef), max(ef)],
                         'descent_moves_mean': round(statistics.mean(mv), 2),
                         'max_formula_height_mean': round(statistics.mean(s['hmax'] for s in ss), 2)}
        res['per_tag'] = tags
        groups = collections.defaultdict(list)
        for s in states:
            groups[_group(s['case'])].append(s)
        res['per_decision_path'] = {
            g: {'n': len(ss), 'tags': dict(collections.Counter(s['tag'] for s in ss).most_common()),
                'cone_ops_range': [min(res['cases'][s['case']]['ops'] for s in ss),
                                   max(res['cases'][s['case']]['ops'] for s in ss)],
                'cone_attn_depth_range': [min(res['cases'][s['case']]['attn_depth'] for s in ss),
                                          max(res['cases'][s['case']]['attn_depth'] for s in ss)],
                'effective_attn_depth_mean': round(statistics.mean(s['eff'] for s in ss), 2),
                'effective_attn_depth_median': statistics.median(s['eff'] for s in ss),
                'effective_attn_depth_range': [min(s['eff'] for s in ss), max(s['eff'] for s in ss)]}
            for g, ss in groups.items()}
        print('per decision path', json.dumps(res['per_decision_path'], indent=None)[:2000])
        res['max_formula_height_in_test_states'] = max(s['hmax'] for s in states)
        res['max_descent_moves'] = max(s['moves'] for s in states)
        for tag, d in tags.items():
            print(f"{tag:18s} n={d['n']:6d} static ops {d['static_ops_mean']:6.1f} depth {d['static_attn_depth_mean']:5.1f}"
                  f"  effective depth {d['effective_attn_depth_mean']:5.1f} [{d['effective_attn_depth_range'][0]},"
                  f"{d['effective_attn_depth_range'][1]}]  moves {d['descent_moves_mean']}  cases {d['cases']}")
    if os.path.exists(a.test):
        res['test'] = json.load(open(a.test))
    fresh = os.path.join(HERE, 'test_1000_s7.json')
    if os.path.exists(fresh):
        res['test_fresh_seed'] = json.load(open(fresh))
    if os.path.exists(a.calib):
        res['calibration'] = json.load(open(a.calib))
    with open(a.out, 'w') as fh:
        json.dump(res, fh, indent=1)
    print('wrote', a.out)


if __name__ == '__main__':
    main()


def tables(path=os.path.join(HERE, 'results.json')):
    """markdown tables for the README, from results.json."""
    r = json.load(open(path))
    L = []
    L.append('| program | ops (sel / agg / map) | source tokens / lines | attention depth | MLP run | flagged ops | test |')
    L.append('|---|---|---|---|---|---|---|')
    t = r.get('test', {})
    tst = f"{t.get('decision_exact_python_render', '?'):,} / {t.get('n_states', '?'):,}" if t else ''
    for name, d in (('Kalmár decision (H=9)', r['decision']), ('Kalmár rendering', r['rendering']),
                    ('Kalmár total', r['total'])):
        bk = d['by_kind']
        sel = bk.get('select', 0)
        agg = bk.get('aggregate', 0) + bk.get('sel_width', 0)
        mp = bk.get('tok_map', 0) + bk.get('seq_map', 0)
        dep = d.get('attn_depth', d.get('attn_depth_added'))
        dep = f"+{d['attn_depth_added']} ({d['attn_depth_alone']} alone)" if 'attn_depth_added' in d else dep
        L.append(f"| {name} | {d['ops']} ({sel} / {agg} / {mp}) | {d['source_tokens']:,} / {d['source_lines']} | {dep} | "
                 f"{d.get('mlp_run', '')} | {d['flagged_ops']} | {tst if 'total' in name else ''} |")
    for row in r.get('calibration', {}).get('rows', []):
        bk = row['by_kind']
        sel = bk.get('select', 0)
        agg = bk.get('aggregate', 0) + bk.get('sel_width', 0)
        mp = bk.get('tok_map', 0) + bk.get('seq_map', 0)
        L.append(f"| {row['task']} | {row['ops']} ({sel} / {agg} / {mp}) | {row['source_tokens']} / {row['source_lines']} | "
                 f"{row['attn_depth']} | {row['mlp_run']} | {row['flagged_ops']} | {row['exact']} / {row['cases']} |")
    L.append('')
    L.append('| step tag | states | cases fired | cone ops (H=9) | cone attn depth (H=9) | effective depth mean [min, max] |')
    L.append('|---|---|---|---|---|---|')
    for tag, d in r.get('per_tag', {}).items():
        cs = ', '.join(f'{k} {v}' for k, v in d['cases'].items())
        L.append(f"| {tag} | {d['n']:,} | {cs} | {d['static_ops_mean']:.0f} | {d['static_attn_depth_mean']:.1f} | "
                 f"{d['effective_attn_depth_mean']:.1f} [{d['effective_attn_depth_range'][0]}, "
                 f"{d['effective_attn_depth_range'][1]}] |")
    print('\n'.join(L))
