#!/usr/bin/env python3
"""support-state analysis: every count in numbers.md § support-state, from the pulled `ss_support.py` records.

  python3 ss_analysis.py            # -> artifacts/ss/summary.json + printed tables (stdout is the table)

Inputs (all on file):
  artifacts/ss/{H,S1,S2*}_<model>_<T>_s<seed>.s0.jsonl    this run's per-theorem records (ss_support.py)
  origin/dan_support-curves:artifacts/sc/summary.json      whole-proof base / EI cells (support-curves; Lean alone)
  origin/dan_support-followups:artifacts/sf/d_steps.jsonl  whole-proof EI survivor proofs + per-step base log p (part D)
Cells pool n and c over every file with the same (model, seed, temperature) -- sampling is i.i.d. per theorem.
p-hat = c / n; a row that hit stop_at has a stopping-time n (O(1/c) bias, stated with the numbers).
"""
import json, glob, os, re, math, subprocess, collections, statistics, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

A = 'artifacts/ss'
SURV = [l.strip() for l in open('data/sc/falsifier_survivors.txt') if l.strip()]
THM = {json.loads(l)['name']: json.loads(l) for l in open('data/sc/theorems.jsonl') if l.strip()}
MODEL = {
    'base': 'SN base = state-env ckpts/se/stage1_SN_s{s}.pt (3,216,384 params, lean_staten, from scratch, '
            'train_depth3_f0_a1 6,000 x 128, cap 6), sampled in Env(canon, assign)',
    'ei': 'SN EI = state-env ckpts/se/ladder/la_T1_SN_s{s}_r8.pt (SN base + 8 x k32 EI at T 0.8 on rl_targets)',
    'wp_base': 'whole-proof base = ckpts/lf/stage1_a1_seq_s0.pt md5 9bde44c0 (3,214,336 params, lean_seq, from scratch)',
    'wp_ei': 'whole-proof EI = la_T1_sc_s0_r8.pt md5 5cebd7ec (support-curves)',
}


def git_json(ref, path, lines=False):
    t = subprocess.run(['git', 'show', f'{ref}:{path}'], capture_output=True, text=True, check=True).stdout
    return [json.loads(l) for l in t.splitlines() if l.strip()] if lines else json.loads(t)


def load():
    """-> {(stage, model, seed, T): {name: rec}} and a pooled {(model, seed, T): {name: [n, c, files, first_hits]}}"""
    by_file, pooled = {}, collections.defaultdict(dict)
    for fn in sorted(glob.glob(f'{A}/*.s0.jsonl')):
        base = os.path.basename(fn)
        m = re.match(r'(\w+?)_(base|ei)_T(\d+)_s(\d)\.s0\.jsonl', base)
        if not m:
            continue
        stage, model, T, seed = m.group(1), m.group(2), int(m.group(3)) / 10, int(m.group(4))
        recs = {}
        for l in open(fn):
            if l.strip():
                r = json.loads(l); recs[r['name']] = r
        by_file[(stage, model, seed, T, base)] = recs
        for nm, r in recs.items():
            assert abs(r['temperature'] - T) < 1e-9 and r['seed'] == seed and r['model'] == model, (fn, nm)
            cell = pooled[(model, seed, T)].setdefault(nm, {'n': 0, 'c': 0, 'files': [], 'recs': []})
            cell['n'] += r['n_tried']; cell['c'] += r['n_ok']; cell['files'].append(base); cell['recs'].append(r)
    return by_file, pooled


def phat(cell):
    return cell['c'] / cell['n'] if cell and cell['n'] else None


def passk(n, c, k):
    if c == 0:
        return 0.0
    if k <= n and n - c >= k:
        return 1.0 - math.exp(math.lgamma(n - c + 1) - math.lgamma(n - c - k + 1) - math.lgamma(n + 1) + math.lgamma(n - k + 1))
    if k <= n:
        return 1.0
    return 1.0 - (1.0 - c / n) ** k


def med(xs):
    return statistics.median(xs) if xs else None


# ---- part 3: support-followups' step segmentation (sf_steps.steps_of), inlined so this file needs no torch -------
RULE = {'.1', '.2', '.elim', 'Or.inl', 'Or.inr', 'Or.elim', 'Classical.byContradiction', '⟨'}


def steps_of(toks):
    sid, kinds, cur = [], [], -1
    for t, x in enumerate(toks):
        prev = toks[t - 1] if t else None
        new = None
        if x == 'have':
            new = 'have'
        elif x == 'exact':
            new = 'exact'
        elif x == '(' and toks[t + 1:t + 3] == ['fun', '('] and prev == ')':
            new = 'box2'
        if new or cur < 0:
            kinds.append(new or 'other'); cur += 1
        sid.append(cur)
    return sid, kinds


def step_sigs(toks):
    """per step: (formula, rule) with every name replaced by N.  formula = tokens between the defining ':' and ':='
    of a `have` (None for exact / box openings); rule = the first token after ':=' (or after `exact`)."""
    sid, kinds = steps_of(toks)
    out = []
    for k in range(len(kinds)):
        ts = [toks[t] for t, s in enumerate(sid) if s == k]
        ts = ['N' if re.fullmatch(r'[nh]\d+', x) else x for x in ts]
        form, rule = None, None
        if ts and ts[0] == 'have' and ':=' in ts:
            j = ts.index(':=')
            form = ' '.join(ts[3:j]) if len(ts) > 3 and ts[2] == ':' else None
            rule = ts[j + 1] if j + 1 < len(ts) else None
            if rule == '(':
                rule = 'fun' if ts[j + 2:j + 3] == ['fun'] else '('
            elif rule == 'N':
                rule = 'N ' + (ts[j + 2] if j + 2 < len(ts) and ts[j + 2] != ';' else '')
        elif ts and ts[0] in ('exact', '('):
            rule = ' '.join(x for x in ts if x not in (';', '<eos>'))   # the whole step, names abstracted
        out.append((kinds[k], form, rule))
    return out


def main():
    by_file, pooled = load()
    S = {'models': MODEL, 'files': sorted(k[4] for k in by_file)}
    md5s = collections.defaultdict(set)
    for (stage, model, seed, T, base), recs in by_file.items():
        for r in recs.values():
            md5s[f'{model} s{seed}'].add(r['ckpt_md5'])
    S['ckpt_md5'] = {k: sorted(v) for k, v in md5s.items()}
    sc = git_json('origin/dan_support-curves', 'artifacts/sc/summary.json')
    wp = {(r['model'], r['seed'], r['temperature'], r['name']): r for r in sc}

    # ---------------- H: the 29 survivors ----------------
    H = {}
    print('\n== H: the 29 support-curves survivors (whole-proof base s0: 0 in 400,000) ==')
    print(f'{"theorem":<18}{"L":>3} {"wpEI p":>8} | ' + ' | '.join(f'SN base s{s}: T0.8 c/n  first   T1.0 c/n' for s in (0, 1)))
    for s in (0, 1):
        h08 = by_file.get(('H', 'base', s, 0.8, f'H_base_T08_s{s}.s0.jsonl'), {})
        h10 = by_file.get(('H', 'base', s, 1.0, f'H_base_T10_s{s}.s0.jsonl'), {})
        rows = []
        for nm in SURV:
            a, b = h08.get(nm), h10.get(nm)
            wb08, wb10 = wp.get(('base', 0, 0.8, nm)), wp.get(('base', 0, 1.0, nm))
            wei = wp.get(('ei', 0, 0.8, nm))
            rows.append({'name': nm, 'L_true': THM[nm]['L_true'],
                         'T08': (a['n_tried'], a['n_ok']) if a else None, 'first_hit_T08': a['first_hit'] if a else None,
                         'T10': (b['n_tried'], b['n_ok']) if b else None,
                         'reached': bool((a and a['n_ok']) or (b and b['n_ok'])),
                         'done': bool(a and (a['n_ok'] >= 5 or (b is not None))),
                         'p_T08': (a['n_ok'] / a['n_tried']) if a else None,
                         'wp_base_n': (wb08['n'] if wb08 else 0) + (wb10['n'] if wb10 else 0),
                         'wp_base_c': (wb08['c'] if wb08 else 0) + (wb10['c'] if wb10 else 0),
                         'wp_ei_p_T08': wei['p_hat'] if wei else None,
                         'proofs': (a['proofs'] if a else []) + (b['proofs'] if b else [])})
        H[s] = rows
    for i, nm in enumerate(SURV):
        r0 = H[0][i]
        line = f'{nm:<18}{r0["L_true"]:>3} {r0["wp_ei_p_T08"] or 0:>8.4f} | '
        for s in (0, 1):
            r = H[s][i]
            t8 = f'{r["T08"][1]}/{r["T08"][0]}' if r['T08'] else '-'
            t1 = f'{r["T10"][1]}/{r["T10"][0]}' if r['T10'] else '-'
            line += f'{t8:>16} {str(r["first_hit_T08"]):>7} {t1:>12} | '
        print(line)
    Hs = {}
    for s in (0, 1):
        rows = H[s]
        complete = sum(1 for r in rows if r['T08'] is not None and (r['T08'][1] >= 5 or r['T10'] is not None))
        reached = sum(r['reached'] for r in rows)
        ps = [r['p_T08'] for r in rows if r['p_T08'] is not None]
        Hs[s] = {'model': MODEL['base'].format(s=s), 'md5': S['ckpt_md5'].get(f'base s{s}'),
                 'complete_rows': complete, 'reached': reached,
                 'reached_T08_first10k': sum(1 for r in rows if r['first_hit_T08'] is not None and r['first_hit_T08'] <= 10000),
                 'unreached': [r['name'] for r in rows if r['T08'] and not r['reached']],
                 'median_p_T08': med(ps), 'min_p_T08_reached': min([p for p in ps if p > 0], default=None),
                 'attempts': sum((r['T08'][0] if r['T08'] else 0) + (r['T10'][0] if r['T10'] else 0) for r in rows),
                 'wp_base_attempts_min': min(r['wp_base_n'] for r in rows), 'wp_base_successes': sum(r['wp_base_c'] for r in rows)}
        pr = [n for n in SURV if any((pooled[('base', s, T)].get(n) or {}).get('c', 0) > 0 for T in (0.8, 1.0))]
        Hs[s]['reached_pooled_all_draws'] = len(pr)
        Hs[s]['pooled_attempts_unreached'] = {n: sum((pooled[('base', s, T)].get(n) or {}).get('n', 0) for T in (0.8, 1.0))
                                              for n in SURV if n not in pr}
        print(f'SN base s{s}: reached pooled over every draw of this run (H + S1 + S2): {len(pr)}; '
              f'unreached {Hs[s]["pooled_attempts_unreached"]}')
        print(f'SN base s{s}: rows complete {complete}/29, reached {reached}, reached at T0.8 within first 10,000: '
              f'{Hs[s]["reached_T08_first10k"]}, median p(T0.8) {Hs[s]["median_p_T08"]}, attempts {Hs[s]["attempts"]:,}, '
              f'unreached {Hs[s]["unreached"]}')
    S['H'] = {'summary': Hs, 'rows': {s: [{k: v for k, v in r.items() if k != 'proofs'} for r in H[s]] for s in H}}

    # ---------------- S1: 383 theorems, SN base vs SN EI, k 10,000 T 0.8 ----------------
    s1 = {m: by_file.get(('S1', m, 0, 0.8, f'S1_{m}_T08_s0.s0.jsonl'), {}) for m in ('base', 'ei')}
    if s1['base'] and s1['ei']:
        names = [n for n in THM if n in s1['base'] and n in s1['ei']]
        solved = {m: {n for n in names if s1[m][n]['n_ok'] > 0} for m in s1}
        fwd = sorted(n for n in names if s1['base'][n]['n_ok'] == 0 and s1['ei'][n]['n_ok'] > 0)
        rev = sorted(n for n in names if s1['ei'][n]['n_ok'] == 0 and s1['base'][n]['n_ok'] > 0)
        wps = {m: {n for n in names if (wp.get((m, 0, 0.8, n)) or {}).get('stages', {}).get('s1', {}).get('c', 0) > 0}
               for m in ('base', 'ei')}
        print(f'\n== S1: {len(names)} theorems, k 10,000 T 0.8, seed 0 ==')
        print(f'SN base solves {len(solved["base"])}, SN EI {len(solved["ei"])}; whole-proof base {len(wps["base"])}, '
              f'whole-proof EI {len(wps["ei"])} (support-curves stage 1)')
        print(f'SN forward crux {len(fwd)}, reverse crux {len(rev)}')
        bystr = {}
        for L in sorted({THM[n]['L_true'] for n in names}):
            ns = [n for n in names if THM[n]['L_true'] == L]
            row = {'n': len(ns)}
            for m in ('base', 'ei'):
                row[f'SN_{m}'] = {k: round(sum(passk(s1[m][n]['n_tried'], s1[m][n]['n_ok'], k) for n in ns) / len(ns), 4)
                                  for k in (1, 32, 100, 1000, 10000)}
            for m in ('base', 'ei'):
                row[f'WP_{m}_k10000'] = round(sum(n in wps[m] for n in ns) / len(ns), 4)
            bystr[L] = row
            print(f'L{L:>3} n={len(ns):>3}  SN base pass@32/1e4 {row["SN_base"][32]:.3f}/{row["SN_base"][10000]:.3f}  '
                  f'SN EI {row["SN_ei"][32]:.3f}/{row["SN_ei"][10000]:.3f}  | WP base {row["WP_base_k10000"]:.3f} WP EI {row["WP_ei_k10000"]:.3f}')
        S['S1'] = {'n_theorems': len(names), 'SN_base_solved': len(solved['base']), 'SN_ei_solved': len(solved['ei']),
                   'WP_base_solved': len(wps['base']), 'WP_ei_solved': len(wps['ei']),
                   'SN_forward_crux': fwd, 'SN_reverse_crux': rev, 'by_L_true': bystr,
                   'survivors_in_SN_forward_crux': sorted(set(fwd) & set(SURV)),
                   'WP_forward_crux_solved_by_SN_base_k1e4': len(set(l.strip() for l in open('data/sc/crux_forward.txt') if l.strip()) & solved['base'])}
        print(f'whole-proof forward crux (82) solved by SN base at k 10,000: {S["S1"]["WP_forward_crux_solved_by_SN_base_k1e4"]}')
        os.makedirs('data/ss', exist_ok=True)
        open('data/ss/sn_crux_forward.txt', 'w').write(''.join(n + '\n' for n in fwd))
        open('data/ss/sn_crux_reverse.txt', 'w').write(''.join(n + '\n' for n in rev))

        # S2: the SN forward crux, deepened; E8
        e8 = []
        for n in fwd:
            b08, b10 = pooled[('base', 0, 0.8)].get(n), pooled[('base', 0, 1.0)].get(n)
            ei_p = phat(pooled[('ei', 0, 0.8)].get(n))
            e8.append({'name': n, 'L_true': THM[n]['L_true'], 'base_T08': (b08['n'], b08['c']) if b08 else None,
                       'base_T10': (b10['n'], b10['c']) if b10 else None, 'ei_p_T08': ei_p})
        surv = [r for r in e8 if r['base_T08'] and r['base_T10'] and r['base_T08'][0] >= 40000 and r['base_T10'][0] >= 40000
                and r['base_T08'][1] == 0 and r['base_T10'][1] == 0]
        # E8 as pre-registered: 0 in the FIRST 40,000 at each T (S1 + the fwd08k30 continuation; fwd10k40), EI p >= 0.01
        f08 = by_file.get(('S2fwd08k30', 'base', 0, 0.8, 'S2fwd08k30_base_T08_s0.s0.jsonl'), {})
        f10 = by_file.get(('S2fwd10k40', 'base', 0, 1.0, 'S2fwd10k40_base_T10_s0.s0.jsonl'), {})
        strict = [n for n in fwd if n in f08 and n in f10 and s1['base'][n]['n_tried'] + f08[n]['n_tried'] >= 40000
                  and f10[n]['n_tried'] >= 40000 and f08[n]['n_ok'] == 0 and f10[n]['n_ok'] == 0]
        strict_e8 = [n for n in strict if (phat(pooled[('ei', 0, 0.8)].get(n)) or 0) >= 0.01]
        print(f'E8 (pre-registered, first 40,000 per T): {len(strict_e8)} of {len(strict)} zero-at-40k crux theorems have '
              f'SN EI p >= 0.01; SN forward-crux theorems reached within 40,000/T: {len(fwd) - len(strict)}')
        S['S2'] = {'rows': e8, 'E8_strict_40k': strict_e8, 'zero_first_40k_both_T': strict,
                   'at_40k_both_T_zero': [r['name'] for r in surv],
                   'E8_count': sum(1 for r in surv if (r['ei_p_T08'] or 0) >= 0.01),
                   'deepest': {r['name']: (r['base_T08'], r['base_T10']) for r in surv}}
        for d in (40000, 100000, 200000):
            S['S2'][f'zero_at_{d}_both_T_ei_p01'] = sum(1 for r in e8 if r['base_T08'] and r['base_T10'] and
                                                       r['base_T08'][0] >= d and r['base_T10'][0] >= d and
                                                       r['base_T08'][1] == 0 and r['base_T10'][1] == 0 and (r['ei_p_T08'] or 0) >= 0.01)
        print(f'S2: SN forward-crux theorems deepened to >= 40,000 at both T: '
              f'{sum(1 for r in e8 if r["base_T08"] and r["base_T10"] and r["base_T08"][0] >= 40000 and r["base_T10"][0] >= 40000)}; '
              f'zero at both with EI p >= 0.01 (E8): {S["S2"]["E8_count"]}; at 100k/200k: '
              f'{S["S2"]["zero_at_100000_both_T_ei_p01"]}/{S["S2"]["zero_at_200000_both_T_ei_p01"]}')
        rv = []
        for n in rev:
            e = pooled[('ei', 0, 0.8)].get(n)
            rv.append({'name': n, 'ei': (e['n'], e['c']), 'base_p_T08': phat(pooled[('base', 0, 0.8)].get(n))})
        S['S2']['reverse'] = rv
        S['S2']['reverse_survive'] = [r['name'] for r in rv if r['ei'][1] == 0]
        print(f'reverse crux after EI continuation: {len(S["S2"]["reverse_survive"])} of {len(rv)} still 0 for SN EI')

    # ---------------- truncation (policy line 0.1 %) ----------------
    tr = []
    for (stage, model, seed, T, base), recs in sorted(by_file.items()):
        for L in sorted({r['L_true'] for r in recs.values()}):
            rs = [r for r in recs.values() if r['L_true'] == L]
            n = sum(r['n_tried'] for r in rs); t = sum(r['n_trunc_action'] + r['n_step_cap'] for r in rs)
            tr.append({'file': base, 'L_true': L, 'n': n, 'capped': t, 'rate': t / n if n else 0})
    S['truncation'] = {'max_rate': max((x['rate'] for x in tr), default=0), 'over_0.1pct': [x for x in tr if x['rate'] > 0.001],
                       'total_capped': sum(x['capped'] for x in tr), 'total_attempts': sum(x['n'] for x in tr)}
    zero = collections.defaultdict(lambda: [0, 0, 0])     # (model, seed, name) -> [n, c, capped], pooled over T
    for (stage, model, seed, T, base), recs in by_file.items():
        for r in recs.values():
            z = zero[(model, seed, r['name'])]
            z[0] += r['n_tried']; z[1] += r['n_ok']; z[2] += r['n_trunc_action'] + r['n_step_cap']
    zc = {f'{m} s{sd} {n}': round(z[2] / z[0], 5) for (m, sd, n), z in zero.items() if z[1] == 0 and z[0] >= 40000}
    S['truncation']['zero_claims_max_capped_share'] = max(zc.values(), default=0)
    S['truncation']['zero_claims_capped_share'] = zc
    print(f'\nlength caps: {S["truncation"]["total_capped"]} of {S["truncation"]["total_attempts"]:,} attempts; max stratum rate '
          f'{S["truncation"]["max_rate"]:.5f}; strata over 0.1 %: {len(S["truncation"]["over_0.1pct"])}; '
          f'max capped share on a zero-success row (>= 40,000 attempts): {S["truncation"]["zero_claims_max_capped_share"]}')

    # ---------------- proof length: lines and term size (distinct accepted proofs, by model) ----------------
    pl = {}
    for (model, seed, T), cells in pooled.items():
        ls, ts = [], []
        for n, c in cells.items():
            for r in c['recs']:
                for p in r['proofs']:
                    ls.append(p['n_lines']); ts.append(p['term_size'])
        pl[f'{model} s{seed} T{T}'] = {'distinct_proofs': len(ls), 'lines_med': med(ls), 'term_med': med(ts)}
    hp = {s: [p for r in H[s] for p in r['proofs']] for s in H}
    for s in H:
        pl[f'H survivors, SN base s{s}'] = {'distinct_proofs': len(hp[s]), 'lines_med': med([p['n_lines'] for p in hp[s]]),
                                            'term_med': med([p['term_size'] for p in hp[s]])}
    S['proof_length'] = pl
    print('\nproof length (distinct accepted, median lines / term size):')
    for k, v in pl.items():
        print(f'  {k:<30} {v}')

    # ---------------- part 3: does SN base's survivor proof take whole-proof EI's improbable step? ----------------
    D = [r for r in git_json('origin/dan_support-followups', 'artifacts/sf/d_steps.jsonl', lines=True) if r['set'] == 'S']
    best = {}
    for r in D:           # the most base-probable EI proof per survivor (part D's primary unit), at T 1.0
        tot = r['base']['T1']['total']
        if r['name'] not in best or tot > best[r['name']]['base']['T1']['total']:
            best[r['name']] = r
    p3 = []
    for nm in SURV:
        r = best.get(nm)
        if r is None:
            continue
        steps = r['base']['T1']['steps']
        wi = min(range(len(steps)), key=lambda i: steps[i]['lp'])
        ei_sigs = step_sigs(r['tokens'])
        w = ei_sigs[wi] if wi < len(ei_sigs) else None
        sn = [p for rr in H[0] if rr['name'] == nm for p in rr['proofs']]
        form_hit = rule_hit = 0
        for p in sn:
            sg = step_sigs(p['lean_text'].split() + ['<eos>'])
            if w and w[1] and any(x[1] == w[1] for x in sg):
                form_hit += 1
            if w and any(x[1] == w[1] and x[2] == w[2] for x in sg):
                rule_hit += 1
        comparable = bool(w and w[1] is not None)   # an `exact` worst step ("close the box here") has no content to match
        p3.append({'name': nm, 'worst_step': wi, 'worst_kind': steps[wi]['kind'], 'worst_lp': steps[wi]['lp'],
                   'worst_sig': w, 'comparable': comparable, 'sn_proofs': len(sn), 'sn_with_formula': form_hit, 'sn_with_formula_and_rule': rule_hit})
    reached3 = [x for x in p3 if x['sn_proofs'] and x['comparable']]
    S['part3'] = {'rows': p3, 'reached_comparable': len(reached3),
                  'reached_exact_worst': sum(1 for x in p3 if x['sn_proofs'] and not x['comparable']),
                  'share_any_proof_formula_and_rule': (sum(1 for x in reached3 if x['sn_with_formula_and_rule']) / len(reached3)) if reached3 else None,
                  'share_any_proof_formula': (sum(1 for x in reached3 if x['sn_with_formula']) / len(reached3)) if reached3 else None,
                  'worst_kinds': dict(collections.Counter(x['worst_kind'] for x in p3)),
                  'unit': "most base-probable EI s0 proof per survivor at T 1.0 (support-followups D's primary); worst step = "
                          "min per-step base log p; match = some SN base s0 distinct accepted proof has a step with the same "
                          "(formula, rule head) with names abstracted"}
    print(f'\npart 3: {len(reached3)} reached survivors with a `have` worst step ({S["part3"]["reached_exact_worst"]} more with an `exact` one); share where some SN proof has EI\'s worst step '
          f'(formula+rule / formula only): {S["part3"]["share_any_proof_formula_and_rule"]} / {S["part3"]["share_any_proof_formula"]}')

    json.dump(S, open(f'{A}/summary.json', 'w'), indent=1, default=list)
    print(f'-> {A}/summary.json')


if __name__ == '__main__':
    main()
