#!/usr/bin/env python3
"""Every number of run lean-only, re-derived from pulled files under artifacts/lo/ and data/lo/.

  python3 lean_only_analysis.py phase1     -> artifacts/lo/phase1_summary.json  (lean_check validation, throughput, relabelling)
  python3 lean_only_analysis.py phase2     -> artifacts/lo/summary.json         (held-out, mechanism, base rates, depth-3 dial, ladder; both units)
"""
import sys, os, re, json, glob, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text


def jl(fn):
    return [json.loads(l) for l in open(fn) if l.strip()]


def phase1():
    out = {}
    st = json.load(open('artifacts/lo/lean_check_selftest.json'))
    out['selftest'] = {'pass': st['pass'], 'n': st['n'], 'lean': st['lean'], 'cases': {r['name']: {'ok': r['ok'], 'size': r['size'], 'pass': r['pass']} for r in st['rows']}}
    # pool proofs: nd_verify vs lean_check, term sizes
    pool = jl('artifacts/lo/pool_check.jsonl')
    c = collections.Counter((r['nd_ok'], r['lean_ok']) for r in pool)
    by_src = collections.Counter(); by_src_ok = collections.Counter()
    for r in pool:
        by_src[r.get('name', '').rsplit('_', 1)[0] if r.get('name') else '?'] += 1
    sizes = [r['size'] for r in pool if r['size'] is not None]
    lines = [r['nd_lines'] for r in pool if r['size'] is not None]
    by_lines = collections.defaultdict(list)
    for r in pool:
        if r['size'] is not None: by_lines[r['nd_lines']].append(r['size'])
    out['pool'] = {'n': len(pool), 'distinct_prompt_proof': len({(r['prompt'], r['proof']) for r in pool}),
                   'both_accept': c[(True, True)], 'nd_ok_lean_rej': c[(True, False)], 'nd_rej_lean_ok': c[(False, True)], 'both_reject': c[(False, False)],
                   'term_size': {'min': min(sizes), 'median': sorted(sizes)[len(sizes) // 2], 'mean': sum(sizes) / len(sizes), 'max': max(sizes)},
                   'term_size_by_lines': {str(L): {'n': len(v), 'median': sorted(v)[len(v) // 2], 'mean': round(sum(v) / len(v), 2), 'max': max(v)} for L, v in sorted(by_lines.items())},
                   'sources': dict(collections.Counter(r['name'].rsplit('_', 1)[0] for r in pool if r.get('name')).most_common())}
    neg = jl('artifacts/lo/negatives_check.jsonl')
    cn = collections.Counter((r['nd_ok'], r['lean_ok']) for r in neg)
    out['negatives'] = {'n': len(neg), 'lean_accepted': cn[(False, True)] + cn[(True, True)], 'nd_accepted': cn[(True, True)] + cn[(True, False)], 'both_reject': cn[(False, False)],
                        'lean_reject_kinds': dict(collections.Counter(r['lean_reason'].split(':')[0].split(' |')[0][:24] for r in neg if not r['lean_ok']).most_common(6))}
    # the 460 in-loop "Lean yes / nd_verify no" texts of lean-format under lean_check
    d = jl('artifacts/lo/disagree460_check.jsonl')
    kinds = collections.Counter()
    for r in d:
        if re.search(r'n\d+\.elim', r['lean_text']): k = 'elim (old BOTE rendering -> Not.elim)'
        else:
            reason = verify_text(r['prompt'] + ' ' + r['nd'])[1]
            k = 'unrestated premise' if 'premise block' in reason else 'not-A = A -> False unfolding'
        kinds[(k, r['lean_ok'])] += 1
    out['disagree460'] = {'n': len(d), 'lean_check_accepts': sum(r['lean_ok'] for r in d), 'lean_check_rejects': sum(not r['lean_ok'] for r in d),
                          'by_kind': {f'{k} | lean_check {"accepts" if ok else "rejects"}': n for (k, ok), n in kinds.most_common()},
                          'nd_verify_accepts': sum(bool(r.get('nd_ok')) for r in d)}
    # throughput from the phase-1 log
    log = open('artifacts/lo/logs/phase1b_checks.log' if os.path.exists('artifacts/lo/logs/phase1b_checks.log') else 'artifacts/lo/logs/phase1_checks.log').read()
    m = re.search(r'(\d+) records: translate (\d+)s, lean (\d+)s wall / (\d+)s proc \((\d+) per wall-s, (\d+) per proc-s, (\d+) workers', log)
    out['throughput'] = {'records': int(m.group(1)), 'lean_wall_s': int(m.group(3)), 'lean_proc_s': int(m.group(4)), 'per_wall_s': int(m.group(5)), 'per_proc_s': int(m.group(6)), 'workers': int(m.group(7)),
                         'lean_format_gate_per_proc_s_on_file': 85.5, 'nd_verify_per_s_on_file': 14497}
    out['relabel'] = json.load(open('artifacts/lo/relabel_summary.json'))
    json.dump(out, open('artifacts/lo/phase1_summary.json', 'w'), indent=1)
    for k, v in out.items():
        if k != 'relabel':
            print(k, json.dumps(v)[:600])
    for k, v in out['relabel'].items():
        print(k, {kk: vv for kk, vv in v.items() if kk not in ('label_mismatch', 'ts_by_L_true', 'ts_hist')})


# ---------------------------------------------------------------- phase 2
FMTS = ('seq', 'free'); SEEDS = (0, 1)


def lstar(solved, pool, key, need=5):
    """max L with >= need pool theorems solved at pool[key] >= L"""
    vals = sorted({t[key] for t in pool if t.get(key) is not None})
    best = 0; ge = {}
    for L in vals:
        n = sum(1 for t in pool if t.get(key) is not None and t[key] >= L and t['name'] in solved)
        ge[str(L)] = n
        if n >= need: best = L
    return best, ge


def found_map(fn):
    """found file -> name -> list of records"""
    m = collections.defaultdict(list)
    if os.path.exists(fn):
        for x in jl(fn): m[x['name']].append(x)
    return m


def classify_nd(proof):
    from patterns import classify
    try:
        return classify(proof)
    except Exception:
        return None


def nd_of(x):
    """the ND proof of a counted record: as stored when it is ND, else re-denoted from the Lean text with the current converter
    (the in-loop converter did not accept `P`/`Q`/`R`/`S` as binder names; verdicts were lean_check's and are unchanged)"""
    p = x['proof']
    if p.startswith('N') and p.rstrip().endswith('QED'):
        return p
    from lean_free import denote
    nd = denote(x['prompt'], x.get('text') or p)
    return nd if nd and verify_text(x['prompt'] + ' ' + nd)[0] else None


def text_tokens(rec):
    t = rec.get('text')
    return len(t.split()) if t else None


def arm_dir(arm):
    for d in (f'artifacts/lo/{arm}', f'artifacts/lo/lo/{arm}'):
        if os.path.isdir(d): return d
    return None


def gate_totals(prefix):
    tot = collections.Counter(); kinds = collections.Counter(); secs = collections.Counter()
    for fn in glob.glob(f'artifacts/lo/gate_{prefix}*.jsonl'):
        if fn.endswith('.disagree.jsonl'): continue
        for r in jl(fn):
            for k in ('samples', 'no_eos', 'distinct_checked', 'both_ok', 'nd_ok_lean_rej', 'nd_rej_lean_ok', 'both_rej'): tot[k] += r.get(k, 0)
            for k, v in r.get('disagreement_kinds', {}).items(): kinds[k] += v
            secs['lean_wall_s'] += r.get('lean_wall_s', 0); secs['lean_proc_s'] += r.get('lean_proc_s', 0); secs['nd_s'] += r.get('denote_nd_verify_s', 0)
    return {**tot, 'disagreement_kinds': dict(kinds.most_common(12)), **secs}


def phase2():
    out = {}
    la_pool = jl('data/lo/la_transfer.jsonl'); la_targets = jl('data/lo/la_rl_targets.jsonl')
    d3_pool = jl('data/lo/targets_depth3.jsonl'); d3_transfer = jl('data/lo/transfer_depth3.jsonl')
    # 1. Stage-1: held-out greedy, transfer pass@16, tokens per accepted proof
    st = {}
    for fmt in FMTS:
        for s in SEEDS:
            tag = f'stage1_full_{fmt}_s{s}'; row = {}
            for k, suf in (('heldout', '_heldout_greedy'), ('transfer_k16', '_transfer2_k16')):
                fn = f'artifacts/lo/{tag}{suf}.json'
                if os.path.exists(fn):
                    j = json.load(open(fn))
                    row[k] = {'rate': j['rate'], 'ci': j['ci'], 'solved': j['solved'], 'n': j['n'], 'written_hist': j.get('written_hist'), 'ts_hist': j.get('ts_hist'),
                              'frontier_written': j.get('frontier_written'), 'frontier_ts': j.get('frontier_ts'), 'no_nd_denotation': j.get('no_nd_denotation'), 'by_len': {L: v['rate'] for L, v in j['by_len'].items()}}
                    rows = jl(f'artifacts/lo/{tag}{suf}.jsonl')
                    toks = [len(t.split()) for r in rows for t in r.get('lean_texts', []) if t]
                    row[k]['tokens_per_accepted_proof'] = (sum(toks) / len(toks)) if toks else None
                    row[k]['distinct_proofs'] = sum(len(r['proofs']) for r in rows)
            st[tag] = row
    out['stage1'] = st
    # 2. base rates at pass@2000 on the depth-3 targets (a1 models)
    br = {}
    for fmt in FMTS:
        for s in SEEDS:
            fn = f'artifacts/lo/base_d3_{fmt}_s{s}_k2000.jsonl'
            if not os.path.exists(fn): continue
            rows = jl(fn); n = len(rows)
            solved = sum(r['solved'] for r in rows); d3_nd = 0; d3_lam = 0; red_nd = 0; red_any = 0; nd_none = 0; n_proofs = 0
            for r in rows:
                has_d3 = has_red = has_lam = False
                for p, ld, lt in zip(r['proofs'], r.get('lam_depths', [None] * len(r['proofs'])), r.get('lean_texts', [None] * len(r['proofs']))):
                    n_proofs += 1
                    nd = nd_of({'proof': p, 'prompt': r['prompt'], 'text': lt})
                    cl = classify_nd(nd) if nd else None
                    if cl is None: nd_none += 1
                    else:
                        has_d3 |= cl['depth3']; has_red |= cl['reductio']
                    if ld is not None and ld >= 3: has_lam = True
                d3_nd += has_d3; red_nd += has_red; d3_lam += has_lam
            summ = json.load(open(fn.replace('.jsonl', '.json')))
            br[f'{fmt}_s{s}'] = {'n': n, 'k': summ['k'], 'solved': solved, 'depth3_nd_rate': d3_nd / n, 'depth3_lambda_rate': d3_lam / n, 'reductio_nd_rate': red_nd / n,
                                 'distinct_proofs': n_proofs, 'proofs_without_nd_denotation': nd_none, 'ts_hist': summ.get('ts_hist'), 'written_hist': summ.get('written_hist')}
    out['base_rates_k2000'] = br
    # 3. depth-3 dial
    from phase2_metrics import arm_metrics
    d3 = {}
    for fmt in FMTS:
        for kind in ('ei', 'frozen'):
            for s in SEEDS:
                arm = f'{kind}_d3_{fmt}_s{s}'; d = arm_dir(arm)
                if not d or not glob.glob(f'{d}/round_*.json'): continue
                m = arm_metrics(d, 'depth3')
                last = m[-1]
                rounds = {str(r['round']): round(r['acq_targets'], 3) for r in m}
                fd = found_map(f'{d}/found_{last["round"]}.jsonl')
                lam3 = sum(1 for name, xs in fd.items() if any((x.get('ld') or 0) >= 3 for x in xs))
                thm_d3 = set(); n_re = 0
                for name, xs in fd.items():
                    for x in xs:
                        nd = nd_of(x); n_re += (nd is not None and not x['proof'].startswith('N'))
                        cl = classify_nd(nd) if nd else None
                        if cl and cl['depth3']: thm_d3.add(name)
                secs = [json.load(open(f'{d}/round_{r["round"]}.json')).get('secs') for r in m]
                d3[arm] = {'rounds': last['round'], 'targets_solved': last['targets_solved'], 'acq_targets': last['acq_targets'], 'acq_targets_theorems': last['acq_targets_theorems'],
                           'n_pattern_proofs': last['n_pattern_proofs_targets'], 'first_round_pattern': last['first_round_pattern_targets'], 'acq_by_round': rounds,
                           'transfer_solved': last['transfer_solved'], 'acq_transfer': last['acq_transfer'], 'heldout_greedy_final': last['heldout_greedy'],
                           'acq_targets_redenoted': len(thm_d3) / last['targets_n'], 'text_proofs_redenoted': n_re, 'lambda_depth3_theorems': lam3, 'proofs_without_nd_denotation': sum(1 for xs in fd.values() for x in xs if not x['proof'].startswith('N')),
                           'ts_hist': dict(sorted(collections.Counter(x['ts'] for xs in fd.values() for x in xs if x.get('ts') is not None).items())),
                           'round_secs': secs, 'tokens_per_proof': (lambda v: sum(v) / len(v) if v else None)([text_tokens(x) for xs in fd.values() for x in xs if text_tokens(x)])}
    out['depth3_dial'] = d3
    # 4. ladder T1 + frozen: L* in lines and term size
    la = {}
    for fmt in FMTS:
        for kind in ('T1', 'frozen'):
            for s in SEEDS:
                arm = f'la_{kind}_{fmt}_s{s}'; d = arm_dir(arm)
                if not d or not glob.glob(f'{d}/round_*.json'): continue
                R = max(int(f.split('_')[-1][:-5]) for f in glob.glob(f'{d}/round_*.json'))
                ft = found_map(f'{d}/found_transfer_{R}.jsonl'); fg = found_map(f'{d}/found_{R}.jsonl')
                lsL, geL = lstar(set(ft), la_pool, 'L_true'); lsT, geT = lstar(set(ft), la_pool, 'ts_minlen')
                lsLt, _ = lstar(set(fg), la_targets, 'L_true'); lsTt, _ = lstar(set(fg), la_targets, 'ts_minlen')
                by_round = {}
                for r in range(1, R + 1):
                    j = json.load(open(f'{d}/round_{r}.json')); by_round[str(r)] = {'secs': int(j.get('secs', 0)), 'transfer_solved': j['transfer_cum']['solved'], 'lstar': j['transfer_cum']['lstar'], 'heldout': round(j['heldout_greedy']['rate'], 4)}
                def wlen(x):
                    if x['written']: return x['written']
                    nd = nd_of(x); return verify_text(x['prompt'] + ' ' + nd)[2] if nd else 0
                wl = [wlen(x) for xs in ft.values() for x in xs]; tsz = [x['ts'] for xs in ft.values() for x in xs if x.get('ts') is not None]
                shortest = {}
                for name, xs in ft.items():
                    L = next(t['L_true'] for t in la_pool if t['name'] == name)
                    w = min((wlen(x) for x in xs if wlen(x)), default=None)
                    if w is not None and w < L: shortest[name] = (L, w)
                la[arm] = {'rounds': R, 'transfer_solved': len(ft), 'transfer_n': len(la_pool), 'lstar_lines': lsL, 'ge_lines': geL, 'lstar_ts': lsT, 'ge_ts': geT,
                           'targets_solved': len(fg), 'lstar_lines_targets': lsLt, 'lstar_ts_targets': lsTt,
                           'transfer_solved_at_L_true_ge_11': sum(1 for t in la_pool if t['L_true'] >= 11 and t['name'] in ft),
                           'by_L_true': {str(L): sum(1 for t in la_pool if t['L_true'] == L and t['name'] in ft) for L in range(7, 15)},
                           'written_hist_transfer': dict(sorted(collections.Counter(wl).items())), 'ts_hist_transfer': dict(sorted(collections.Counter(tsz).items())),
                           'max_written': max(wl, default=0), 'max_ts': max(tsz, default=0), 'frontier_ts': max([t for t, c in collections.Counter(tsz).items() if c >= 5], default=0),
                           'proofs_without_nd_denotation': sum(1 for xs in ft.values() for x in xs if not x['proof'].startswith('N')), 'still_without_after_redenote': sum(1 for xs in ft.values() for x in xs if not x['proof'].startswith('N') and nd_of(x) is None),
                           'labels_contradicted': shortest, 'by_round': by_round, 'heldout_final': by_round[str(R)]['heldout'],
                           'tokens_per_proof': (lambda v: sum(v) / len(v) if v else None)([text_tokens(x) for xs in ft.values() for x in xs if text_tokens(x)])}
    out['ladder'] = la
    # 5. checker of record, gate totals, timing
    out['record'] = {os.path.basename(f)[7:-5]: json.load(open(f)) for f in sorted(glob.glob('artifacts/lo/record_*.json'))}
    out['gate'] = {p: gate_totals(p) for p in ('la_T1_seq', 'la_T1_free', 'la_frozen_seq', 'la_frozen_free', 'ei_d3_seq', 'ei_d3_free', 'frozen_d3_seq', 'frozen_d3_free', 'base_d3_seq', 'base_d3_free', 'mech_full_seq', 'mech_full_free')}
    tm = {}
    for fmt in FMTS:
        d = arm_dir(f'timing_d3_{fmt}')
        if d and os.path.exists(f'{d}/round_1.json'): tm[fmt] = json.load(open(f'{d}/round_1.json')).get('secs')
    out['timing_solo_d3_round_secs'] = tm
    json.dump(out, open('artifacts/lo/summary.json', 'w'), indent=1)
    for k in ('stage1', 'base_rates_k2000', 'depth3_dial', 'ladder', 'timing_solo_d3_round_secs'):
        print('==', k)
        for a, v in (out[k].items() if isinstance(out[k], dict) else []):
            print(' ', a, json.dumps({kk: vv for kk, vv in v.items() if kk not in ('by_round', 'ge_lines', 'ge_ts', 'written_hist_transfer', 'ts_hist_transfer', 'ts_hist', 'written_hist', 'labels_contradicted', 'acq_by_round', 'round_secs')} if isinstance(v, dict) else v)[:400])


def e10_patterns():
    """E10: per EI arm, fraction of depth-3 targets with >= 1 counted proof containing each pattern (patterns.py + patterns2.py, on the
    dependency-pruned ND proof) — free-form and fragment arms of this run, proposal 8's lean_seq arms and the token arms on file."""
    from patterns import classify, PATTERNS
    from patterns2 import classify2, PATTERNS2
    arms = {'free_s0': 'artifacts/lo/ei_d3_free_s0', 'free_s1': 'artifacts/lo/ei_d3_free_s1', 'seq_s0': 'artifacts/lo/ei_d3_seq_s0', 'seq_s1': 'artifacts/lo/ei_d3_seq_s1',
            'lf_seq_s0 (on file)': 'artifacts/lf/ei_d3_seq_s0', 'lf_seq_s1 (on file)': 'artifacts/lf/ei_d3_seq_s1', 'token_s0 (on file)': 'artifacts/p2/ei_depth3_f0_a1_s0', 'token_s1 (on file)': 'artifacts/p2/ei_depth3_f0_a1_s1',
            'free_frozen_s0': 'artifacts/lo/frozen_d3_free_s0', 'free_frozen_s1': 'artifacts/lo/frozen_d3_free_s1', 'seq_frozen_s0': 'artifacts/lo/frozen_d3_seq_s0', 'seq_frozen_s1': 'artifacts/lo/frozen_d3_seq_s1'}
    out = {}
    for arm, d in arms.items():
        fn = f'{d}/found_8.jsonl'
        if not os.path.exists(fn): continue
        thm = collections.defaultdict(set); n_thm = set(); n_none = 0
        for x in jl(fn):
            n_thm.add(x['name'])
            nd = nd_of(x) if 'prompt' in x else x['proof']
            if not nd: n_none += 1; continue
            c1 = classify(nd); c2 = classify2(nd)
            if c1 is None: n_none += 1; continue
            for p in PATTERNS:
                if c1.get(p): thm[p].add(x['name'])
            for p in PATTERNS2:
                if c2 and c2.get(p): thm[p].add(x['name'])
        out[arm] = {'solved': len(n_thm), 'proofs_unclassified': n_none, **{p: round(len(thm[p]) / 1000, 3) for p in PATTERNS + PATTERNS2}}
    json.dump(out, open('artifacts/lo/e10_patterns.json', 'w'), indent=1)
    for a, v in out.items(): print(a, v)
    return out


if __name__ == '__main__':
    globals()[sys.argv[1]]()
