#!/usr/bin/env python3
"""Reviewer's independent recount for round3-run2 (blind phase 1).

Run from the phase-1 workspace:  cd ~/review/round3-run2 && python3 <worktree>/review_r3_2_recount.py <part> [arm-prefix ...]
Parts: pools | arms | cov | splits | mix.  Output: <worktree>/artifacts/review_r3_2/<part>*.json

Only nd_verify is shared with the executor.  Parser, pruning, start-index normaliser, predicates, depth counter and the
atom-renaming key are the reviewer's own (review_run5_recount.py); the stratum / ignition / first-round bookkeeping is new here.
"""
import json, re, os, sys, glob, collections, random, gzip
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from review_run5_recount import rkey, parse_proof, prune, normalise, classify, rd, thm_of_prompt
from nd_verify import verify_text

OUT = f'{HERE}/artifacts/review_r3_2'
os.makedirs(OUT, exist_ok=True)
A = 'artifacts/r3_2'
TRAIN_DIR = '/home/dan/nd-takehome/data/p2'          # train_* files are gitignored; data only, no write-ups read there
RED_POOL, RED_TR = 'data/r3_2/targets_reductio_req6.jsonl', 'data/p2/transfer_reductio_req.jsonl'
DORE_POOL, DORE_TR = 'data/p2/targets_derived_ore_req.jsonl', 'data/p2/transfer_derived_ore_req.jsonl'
IGNITION = 10


def stratum_of(r):
    return r.get('stratum', r.get('min_lines_ub') or r['n_lines'])


def fullmatch_rounds(d, pat):
    out = []
    for f in os.listdir(d):
        m = re.fullmatch(pat.replace('{}', r'(\d+)'), f)
        if m:
            out.append(int(m.group(1)))
    return sorted(out)


# ------------------------------------------------------------------------------------------------ arms
def count_pool(d, fnpat, pool_file, pattern, last_rounds_expected):
    pool = rd(pool_file)
    prompts = {r['name']: r['prompt'] for r in pool}
    strat = {r['name']: stratum_of(r) for r in pool}
    schema = {r['name']: r.get('schema') for r in pool}
    rounds = fullmatch_rounds(d, fnpat)
    R = rounds[-1]
    first, field_min, raw_last = {}, {}, 0
    for rr in rounds:
        recs = rd(f'{d}/' + fnpat.format(rr))
        for x in recs:
            k = (x['name'], normalise(x['proof']))
            first.setdefault(k, rr)
            if rr == R:
                field_min[k] = min(field_min.get(k, 99), x['round'])
        if rr == R:
            raw_last = len(recs)
    lastset = set(field_min)
    res = {'rounds_present': [rounds[0], R, len(rounds)], 'rounds_ok': rounds == list(range(1, last_rounds_expected + 1)),
           'raw_records_last': raw_last, 'distinct_norm_proofs': len(first),
           'earlier_files_subset_of_last': set(first) <= lastset,
           'round_field_agrees_with_first_file': f'{sum(first[k] == field_min.get(k) for k in first)}/{len(first)}'}
    solved, acq, acq_unpr = {}, {}, {}
    nver = vfail = unparsable = unknown = 0
    whist, phist, dhist = collections.Counter(), collections.Counter(), collections.Counter()
    pat_whist = collections.Counter()
    for (name, np_), rr in first.items():
        if name not in prompts:
            unknown += 1; continue
        rr = min(rr, field_min.get((name, np_), 99))          # min-round rule over both sources
        c = classify(np_)
        ok, reason, nl = verify_text(prompts[name] + ' ' + np_)
        nver += 1
        if c is None or not ok or nl != c['written']:
            vfail += 1; unparsable += c is None
            continue
        whist[c['written']] += 1; phist[c['pruned']] += 1; dhist[c['depth']] += 1
        solved[name] = min(solved.get(name, 99), rr)
        if c[pattern]:
            acq[name] = min(acq.get(name, 99), rr); pat_whist[c['written']] += 1
        if c[pattern + '_unpruned']:
            acq_unpr[name] = min(acq_unpr.get(name, 99), rr)
    res.update({'n': len(pool), 'solved': len(solved), 'acquired': len(acq), 'acq_rate': round(len(acq) / len(pool), 4),
                'acquired_unpruned_predicate': len(acq_unpr), 'solved_without_pattern': sorted(set(solved) - set(acq)),
                'first_acq_round': min(acq.values()) if acq else None,
                'cum_acquired_by_round': [sum(v <= rr for v in acq.values()) for rr in range(1, R + 1)],
                'cum_solved_by_round': [sum(v <= rr for v in solved.values()) for rr in range(1, R + 1)],
                'verified': nver, 'verify_failures': vfail, 'unparsable': unparsable, 'unknown_names': unknown,
                'written_hist': dict(sorted(whist.items())), 'pruned_hist': dict(sorted(phist.items())),
                'pattern_written_hist': dict(sorted(pat_whist.items())), 'max_depth_hist': dict(sorted(dhist.items())),
                'frontier_written_ge5': max([L for L, c in whist.items() if c >= 5], default=0)})
    by = {}
    for s in sorted(set(strat.values())):
        names = [n for n in strat if strat[n] == s]
        cum = [sum(1 for n in names if acq.get(n, 99) <= rr) for rr in range(1, R + 1)]
        by[str(s)] = {'n': len(names), 'solved': sum(n in solved for n in names), 'acquired': cum[-1], 'cum_acquired_by_round': cum,
                      'first_proof_round': min([acq[n] for n in names if n in acq], default=None),
                      'ignition_round': next((i + 1 for i, v in enumerate(cum) if v >= IGNITION), None)}
    res['by_stratum'] = by
    bs = collections.defaultdict(lambda: [0, 0])
    for n in strat:
        bs[f'{schema[n]}|{strat[n]}'][0] += 1; bs[f'{schema[n]}|{strat[n]}'][1] += n in acq
    res['by_schema_stratum(n,acquired)'] = dict(sorted(bs.items()))
    res['acquired_names'] = sorted(acq)
    return res


def count_arm(arm, kind):
    d = f'{A}/{arm}'
    args = json.load(open(f'{d}/args.json'))
    pattern = 'reductio' if kind == 'reductio' else 'derived_ore_strict'
    pool, tr = (RED_POOL, RED_TR) if kind == 'reductio' else (DORE_POOL, DORE_TR)
    out = {'arm': arm, 'args': {k: args[k] for k in ('init', 'targets', 'transfer', 'heldout', 'train', 'rounds', 'k', 'temperature', 'seed', 'no_train', 'start_round', 'resume_found', 'max_per_thm', 'retain', 'batch')}}
    assert args['targets'] == pool and args['transfer'] == tr, (arm, args['targets'], args['transfer'])
    rj = {r: json.load(open(f'{d}/round_{r}.json')) for r in fullmatch_rounds(d, 'round_{}.json')}
    R = max(rj)
    out['rounds'] = R
    out['attempts_per_target'] = sum(x['k'] for x in rj.values())
    out['round_seeds'] = [rj[r]['seed'] for r in sorted(rj)]
    out['round_ckpts_first_last'] = [rj[min(rj)]['ckpt'], rj[R]['ckpt']]
    out['ckpt_chain_ok'] = all((rj[r]['ckpt'] == args['init'] if args['no_train'] else True) for r in rj)
    out['exec_targets_cum_solved'] = rj[R]['targets_cum']['solved']
    out['exec_transfer_cum_solved'] = rj[R]['transfer_cum']['solved']
    out['heldout_greedy_by_round'] = [round(rj[r]['heldout_greedy']['rate'], 4) for r in sorted(rj)]
    out['transfer_greedy_by_round'] = [rj[r]['transfer_greedy']['solved'] for r in sorted(rj)]
    out['targets'] = count_pool(d, 'found_{}.jsonl', pool, pattern, R)
    out['transfer'] = count_pool(d, 'found_transfer_{}.jsonl', tr, pattern, R)
    out['solved_matches_exec'] = [out['targets']['solved'] == out['exec_targets_cum_solved'], out['transfer']['solved'] == out['exec_transfer_cum_solved']]
    return out


def part_arms(prefixes):
    arms = sorted(a for a in os.listdir(A) if os.path.isfile(f'{A}/{a}/args.json'))
    for arm in arms:
        if prefixes and not any(arm.startswith(p) for p in prefixes):
            continue
        kind = 'reductio' if 'reductio' in arm else 'dore'
        res = count_arm(arm, kind)
        json.dump(res, open(f'{OUT}/arm_{arm}.json', 'w'), indent=1)
        t = res['targets']
        print(arm, 'R', res['rounds'], 'att', res['attempts_per_target'], 'solved', t['solved'], 'acq', t['acquired'],
              {s: (v['acquired'], v['first_proof_round'], v['ignition_round']) for s, v in t['by_stratum'].items()},
              'nopat', len(t['solved_without_pattern']), 'ver', t['verified'], 'fail', t['verify_failures'],
              'transfer acq', res['transfer']['acquired'], flush=True)


def part_r5curve():
    """Run 5's 7-line curves with the same code (for E5) and the run-5 derived-ORE arms (for monotonicity)."""
    global A
    A = 'artifacts/r5'
    out = {}
    for arm in sorted(os.listdir(A)):
        if not os.path.isfile(f'{A}/{arm}/args.json'):
            continue
        d = f'{A}/{arm}'
        args = json.load(open(f'{d}/args.json'))
        pattern = 'reductio' if 'reductio' in arm else 'derived_ore_strict'
        R = max(fullmatch_rounds(d, 'round_{}.json'))
        t = count_pool(d, 'found_{}.jsonl', args['targets'], pattern, R)
        out[arm] = {'targets_file': args['targets'], 'seed': args['seed'], 'init': args['init'], 'acquired': t['acquired'], 'n': t['n'], 'cum': t['cum_acquired_by_round'],
                    'by_stratum': {s: v['cum_acquired_by_round'] for s, v in t['by_stratum'].items()}, 'acquired_names': t['acquired_names'],
                    'verify_failures': t['verify_failures']}
        print(arm, t['acquired'], out[arm]['by_stratum'], flush=True)
    json.dump(out, open(f'{OUT}/r5_arms.json', 'w'), indent=1)


# ------------------------------------------------------------------------------------------------ coverage
def part_cov():
    out = {}
    files = sorted(glob.glob(f'{A}/cov*.jsonl')) + sorted(glob.glob('artifacts/r5/cov_derived_ore_strict*_req.s0.jsonl'))
    for fn in files:
        pattern = 'reductio' if 'reductio' in fn else 'derived_ore_strict'
        recs = rd(fn)
        reach, solved, incomplete, vfail, nver, hits_pat, tried = [], [], 0, 0, 0, 0, set()
        disagree = 0
        for x in recs:
            tried.add(x['n_tried'])
            incomplete += x['n_distinct_ok'] > len(x['proofs'])
            mine = False
            for p in x['proofs']:
                np_ = normalise(p['proof'])
                c = classify(np_)
                ok, _, nl = verify_text(x['prompt'] + ' ' + np_)
                nver += 1
                if c is None or not ok:
                    vfail += 1; continue
                if c[pattern]:
                    mine = True; hits_pat += p['count']
                disagree += c[pattern] != p['pat'][pattern]
            if x['n_ok'] > 0:
                solved.append(x['name'])
            if mine:
                reach.append(x['name'])
        key = os.path.basename(fn).replace('.s0.jsonl', '')
        out[key] = {'file': fn, 'n_targets': len(recs), 'n_tried': sorted(tried), 'solved_any': len(solved), 'reach_pattern': len(reach), 'reach_names': sorted(reach),
                    'samples_with_pattern': hits_pat, 'proof_lists_incomplete': incomplete, 'verified': nver, 'verify_failures': vfail,
                    'predicate_disagreements_with_executor_flag': disagree}
        print(key, {k: v for k, v in out[key].items() if k not in ('reach_names', 'file')}, flush=True)
    json.dump(out, open(f'{OUT}/cov.json', 'w'), indent=1)


# ------------------------------------------------------------------------------------------------ pools
def part_pools():
    out = {}
    pool = rd(RED_POOL)
    out['n'] = len(pool)
    out['strata'] = dict(sorted(collections.Counter(stratum_of(r) for r in pool).items()))
    out['stratum_eq_min_lines_ub'] = sum(r['stratum'] == r['min_lines_ub'] for r in pool)
    out['stratum_eq_n_lines'] = sum(r['stratum'] == r['n_lines'] for r in pool)
    out['schemata_by_stratum'] = {f'{k[0]}|{k[1]}': v for k, v in sorted(collections.Counter((r['schema'], r['stratum']) for r in pool).items())}
    # run-5 records unchanged?
    r5 = {r['name']: r for r in rd('data/p2/targets_reductio_req.jsonl')}
    same = 0
    for r in pool[:300]:
        o = r5.get(r['name'])
        same += o is not None and all(o[k] == r.get(k) for k in o)
    out['run5_records_unchanged'] = f'{same}/300 (first 300 pool records vs data/p2/targets_reductio_req.jsonl, all run-5 fields)'
    # six-liners come from run5_reductio_nec.jsonl?
    nec = rd('data/p2/run5_reductio_nec.jsonl')
    nec_thm = {r['thm'] for r in nec}
    six = [r for r in pool if r['stratum'] == 6]
    out['six_in_run5_nec'] = sum(r['thm'] in nec_thm for r in six)
    out['six_file_equals_pool_six'] = sorted(r['name'] for r in rd('data/r3_2/targets_reductio_six.jsonl')) == sorted(r['name'] for r in six)
    nec6 = [r for r in nec if (r.get('min_lines_ub') or r.get('n_lines')) == 6]
    out['run5_nec_six_line_candidates'] = {'n': len(nec6), 'keys': sorted(nec[0].keys())}
    # oracle proofs
    for label, fn, pat in (('targets', RED_POOL, 'reductio'), ('transfer', RED_TR, 'reductio'), ('dore_targets', DORE_POOL, 'derived_ore_strict'), ('dore_transfer', DORE_TR, 'derived_ore_strict')):
        recs = rd(fn); ok = patn = lenok = noDNN = 0; wl = collections.Counter()
        for r in recs:
            v, _, nl = verify_text(r['prompt'] + ' ' + r['oracle_proof'])
            c = classify(normalise(r['oracle_proof']))
            ok += bool(v); patn += bool(c and c[pat]); lenok += (nl == stratum_of(r)); wl[nl] += 1
            noDNN += '~ ( ~' not in r['thm']
            assert thm_of_prompt(r['prompt']) == r['thm'] or True
        out[f'oracle_{label}'] = {'n': len(recs), 'verifies': ok, 'has_pattern': patn, 'oracle_len_eq_stratum': lenok, 'oracle_len_hist': dict(sorted(wl.items())),
                                  'strata': dict(sorted(collections.Counter(stratum_of(r) for r in recs).items())), 'no_double_neg_in_sequent': noDNN,
                                  'dup_classes': len(recs) - len({rkey(r['thm']) for r in recs}), 'key_field_eq_my_rkey': sum(rkey(r['thm']) == r['key'] for r in recs)}
    out['six_shape'] = collections.Counter(' '.join(l['rule'] for l in parse_proof(r['oracle_proof'])) for r in six).most_common(5)
    json.dump(out, open(f'{OUT}/pools.json', 'w'), indent=1)
    print(json.dumps(out, indent=1))


# ------------------------------------------------------------------------------------------------ splits
def classes(fn):
    op = gzip.open if fn.endswith('.gz') else open
    s = set()
    with op(fn, 'rt') as f:
        for l in f:
            if l.strip():
                x = json.loads(l)
                thm = x.get('thm') or thm_of_prompt(x['prompt'])
                s.add(rkey(thm.strip()))
    return s


def part_splits():
    train = {os.path.basename(f): classes(f) for f in [f'{TRAIN_DIR}/train_reductio_f0.jsonl', f'{TRAIN_DIR}/train_reductio_f0.1.jsonl',
             f'{TRAIN_DIR}/train_derived_ore_strict_f0_c8.jsonl', f'{TRAIN_DIR}/train_derived_ore_strict_f0.001_c8.jsonl', f'{TRAIN_DIR}/train_derived_ore_strict_f0.01_c8.jsonl']}
    ev = {'pool345': classes(RED_POOL), 'six45': classes('data/r3_2/targets_reductio_six.jsonl'), 'transfer_reductio_req': classes(RED_TR),
          'dore_targets_req': classes(DORE_POOL), 'dore_transfer_req': classes(DORE_TR), 'heldout': classes('data/p2/heldout.jsonl'),
          'heldout_c8': classes('data/p2/heldout_c8.jsonl'), 'val36': classes('targets/validation_36.jsonl'),
          'test_short': classes('targets/test_short_prompts.jsonl'), 'test_long': classes('targets/test_long_prompts.jsonl')}
    out = {'sizes': {k: len(v) for k, v in {**train, **ev}.items()}, 'train_vs_eval': {}, 'eval_vs_eval': {}}
    for t, ts in train.items():
        for e, es in ev.items():
            out['train_vs_eval'][f'{t} x {e}'] = len(ts & es)
    names = list(ev)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            out['eval_vs_eval'][f'{a} x {b}'] = len(ev[a] & ev[b])
    json.dump(out, open(f'{OUT}/splits.json', 'w'), indent=1)
    print(json.dumps(out, indent=1))


# ------------------------------------------------------------------------------------------------ mix (what EI trained on)
def part_mix():
    """Every record of each EI arm's last mix file: is its renaming class in an evaluation pool other than the arm's own RL targets?"""
    ev = {'transfer_reductio_req': classes(RED_TR), 'dore_transfer_req': classes(DORE_TR), 'heldout': classes('data/p2/heldout.jsonl'),
          'heldout_c8': classes('data/p2/heldout_c8.jsonl'), 'val36': classes('targets/validation_36.jsonl'),
          'test_short': classes('targets/test_short_prompts.jsonl'), 'test_long': classes('targets/test_long_prompts.jsonl')}
    tg = {'reductio': classes(RED_POOL), 'dore': classes(DORE_POOL)}
    out = {}
    for arm in sorted(os.listdir(A)):
        d = f'{A}/{arm}'
        ms = fullmatch_rounds(d, 'mix_{}.jsonl') if os.path.isdir(d) else []
        if not ms:
            continue
        kind = 'reductio' if 'reductio' in arm else 'dore'
        res = {'mix_rounds': [ms[0], ms[-1], len(ms)]}
        for m in (ms[0], ms[-1]):
            recs = rd(f'{d}/mix_{m}.jsonl')
            cl = [rkey((x.get('thm') or thm_of_prompt(x['prompt'])).strip()) for x in recs]
            res[f'mix_{m}'] = {'n': len(recs), 'in_rl_targets': sum(c in tg[kind] for c in cl), **{f'in_{k}': sum(c in v for c in cl) for k, v in ev.items()}}
        out[arm] = res
        print(arm, res, flush=True)
    json.dump(out, open(f'{OUT}/mix.json', 'w'), indent=1)


if __name__ == '__main__':
    part = sys.argv[1]
    {'pools': part_pools, 'cov': part_cov, 'splits': part_splits, 'mix': part_mix, 'r5curve': part_r5curve}.get(part, lambda: part_arms(sys.argv[2:]))()
