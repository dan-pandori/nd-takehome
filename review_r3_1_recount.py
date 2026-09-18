#!/usr/bin/env python3
"""Reviewer's independent recount for round3-run1 (pool composition or pattern class?).

Only nd_verify is shared with the executor. Parser, dependency pruning, start-index normaliser, reductio predicate, depth
counter and renaming key are the reviewer's own (review_run5_recount.py, written for the round2-run5 review).

  ROOT=~/review/round3-run1 python3 review_r3_1_recount.py pools|splits|cov|dcov|arms [prefix]|rounds

Outputs artifacts/review_r3_1/*.json under the directory this script lives in.
"""
import json, os, sys, glob, re, collections, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.expanduser(os.environ.get('ROOT', HERE))
sys.path.insert(0, HERE)
from review_run5_recount import rkey, thm_of_prompt, parse_proof, prune, normalise, p_reductio, max_depth, rd
sys.path.insert(0, ROOT)
from nd_verify import verify_text

OUT = os.path.join(HERE, 'artifacts', 'review_r3_1')
os.makedirs(OUT, exist_ok=True)
A = os.path.join(ROOT, 'artifacts', 'r3_1')
D = os.path.join(ROOT, 'data', 'r3_1')
SEEDS = list(range(20, 28))
THRESH = {'depth3': 20, 'reductio': 12}


def has_pat(proof, pattern):
    """(parsed?, pattern in the dependency-pruned proof, pruned depth, uses DN in pruned proof)."""
    ls = parse_proof(proof)
    if ls is None:
        return None
    pr = prune(ls)
    d = max_depth(pr)
    return {'depth3': d >= 3, 'reductio': p_reductio(pr), 'depth': d, 'dn': any(l['rule'] == 'DN' for l in pr),
            'written': len(ls), 'pruned': len(pr), 'rules': [l['rule'] for l in pr]}


def ok(prompt, proof):
    return bool(verify_text(prompt + ' ' + proof)[0])


def dump(name, obj):
    json.dump(obj, open(os.path.join(OUT, name), 'w'), indent=1, sort_keys=True)


# ---------------------------------------------------------------- pools
def negi_close(proof):
    """Last line is NEGI whose box hypothesis is ( ~ X ) where the conclusion is ( ~ ( ~ X ) )."""
    ls = parse_proof(proof)
    if not ls:
        return False
    last = ls[-1]
    by = {l['idx']: l for l in ls}
    if last['rule'] != 'NEGI' or len(last['refs']) != 2:
        return False
    h = by.get(last['refs'][0])
    return bool(h and h['rule'] == 'AS' and last['f'] == ('~', h['f']) and isinstance(h['f'], tuple) and h['f'][0] == '~')


def part_pools():
    res = {}
    for pool in ['depth3_req', 'depth3_req_transfer', 'depth3_nb', 'reductio_req', 'reductio_req_transfer', 'reductio_nb', 'depth3_mix', 'reductio_mix']:
        recs = rd(f'{D}/{pool}.jsonl')
        r = collections.Counter()
        r['n'] = len(recs)
        r['distinct_names'] = len({x['name'] for x in recs})
        r['distinct_rkey'] = len({rkey(thm_of_prompt(x['prompt'])) for x in recs})
        bad = []
        for x in recs:
            r['stratum_' + str(x.get('stratum'))] += 1
            r['min_lines_ub_' + str(x.get('min_lines_ub'))] += 1
            if thm_of_prompt(x['prompt']).split() != x['thm'].split():
                r['thm_prompt_mismatch'] += 1
            for fld in ['oracle_proof', 'r10_proof', 'nb_proof', 'u_proof', 'nodn_proof', 'gen_proof']:
                p = x.get(fld)
                if not p:
                    continue
                v = ok(x['prompt'], p)
                h = has_pat(p, 'depth3')
                r[f'{fld}_n'] += 1
                r[f'{fld}_verified'] += v
                if not v:
                    bad.append((x['name'], fld))
                r[f'{fld}_written_{h["written"]}'] += 1
                r[f'{fld}_depth_{h["depth"]}'] += 1
                r[f'{fld}_usesDN'] += h['dn']
                r[f'{fld}_strict_reductio'] += h['reductio']
                if fld == 'nodn_proof':
                    r['nodn_negi_close'] += negi_close(p)
                    r['nodn_has_BOTE'] += 'BOTE' in h['rules']
            if 'r8_min_lines_ub' in x:
                r['r8_' + str(x['r8_min_lines_ub'])] += 1
                r['r8_timeout_' + str(x.get('r8_timeout'))] += 1
            if 'r10_min_lines_ub' in x:
                r['r10_' + str(x['r10_min_lines_ub'])] += 1
                r['r10_timeout_' + str(x.get('r10_timeout'))] += 1
            if 'nodn_min_lines_ub' in x:
                r['nodn_' + str(x['nodn_min_lines_ub'])] += 1
                r['nodn_timeout_' + str(x.get('nodn_timeout'))] += 1
                r['intuit_' + str(x.get('intuit_provable'))] += 1
                concl = thm_of_prompt(x['prompt']).split('|-')[1].split()
                r['concl_notnot'] += concl[:4] == ['(', '~', '(', '~']
            if 'requires' in x:
                r['requires_' + str(x['requires'])] += 1
                r['r_min_' + str(x.get('r_min_lines_ub'))] += 1
                r['schema_' + str(x.get('schema'))] += 1
        res[pool] = dict(r); res[pool]['unverified'] = bad
        print(pool, json.dumps(res[pool], sort_keys=True))
    # mix == req + nb ?
    for pat in ['depth3', 'reductio']:
        mix = [x['name'] for x in rd(f'{D}/{pat}_mix.jsonl')]
        rn = [x['name'] for x in rd(f'{D}/{pat}_req.jsonl')] + [x['name'] for x in rd(f'{D}/{pat}_nb.jsonl')]
        res[f'{pat}_mix_is_req_plus_nb'] = sorted(mix) == sorted(rn)
        mixp = {x['name']: x['prompt'] for x in rd(f'{D}/{pat}_mix.jsonl')}
        srcp = {x['name']: x['prompt'] for f in ('req', 'nb') for x in rd(f'{D}/{pat}_{f}.jsonl')}
        res[f'{pat}_mix_prompts_equal'] = mixp == srcp
    # reductio_req identical to data/p2/targets_reductio_req.jsonl ?
    a = {x['prompt'] for x in rd(f'{D}/reductio_req.jsonl')}
    b = {x['prompt'] for x in rd(f'{ROOT}/data/p2/targets_reductio_req.jsonl')}
    res['reductio_req_same_prompts_as_p2'] = a == b
    a = {x['prompt'] for x in rd(f'{D}/reductio_req_transfer.jsonl')}
    b = {x['prompt'] for x in rd(f'{ROOT}/data/p2/transfer_reductio_req.jsonl')}
    res['reductio_req_transfer_same_prompts_as_p2'] = a == b
    # depth3_req provenance: how many of the 142 known
    known = {rkey(thm_of_prompt(x['prompt'])) for x in rd(f'{D}/depth3_known_req.jsonl')}
    req = {rkey(thm_of_prompt(x['prompt'])) for x in rd(f'{D}/depth3_req.jsonl')}
    tr = {rkey(thm_of_prompt(x['prompt'])) for x in rd(f'{D}/depth3_req_transfer.jsonl')}
    res['depth3_known142_in_req'] = len(known & req); res['depth3_known142_in_transfer'] = len(known & tr)
    res['depth3_req_src'] = dict(collections.Counter(x.get('src') for x in rd(f'{D}/depth3_req.jsonl')))
    res['depth3_nb_src'] = dict(collections.Counter(x.get('src') for x in rd(f'{D}/depth3_nb.jsonl')))
    res['reductio_nb_src'] = dict(collections.Counter(x.get('src') for x in rd(f'{D}/reductio_nb.jsonl')))
    # candidates for the tightened neighbour rule
    c = rd(f'{D}/reductio_nb_cands_all.jsonl')
    cc = collections.Counter()
    for x in c:
        cc['n'] += 1
        p = x.get('nodn_proof')
        good = bool(p) and x.get('intuit_provable') is True and x.get('min_lines_ub') in (7, 8)
        cc['eligible_v1'] += good
        if good:
            cc['eligible_negi_close'] += negi_close(p)
            h = has_pat(p, 'reductio')
            cc['eligible_with_BOTE'] += 'BOTE' in h['rules']
    res['reductio_nb_cands_all'] = dict(cc)
    print(json.dumps({k: v for k, v in res.items() if not isinstance(v, dict) or k.endswith('src') or k.endswith('all')}, indent=1))
    dump('pools.json', res)


# ---------------------------------------------------------------- splits
def keys_of(fn):
    out = set()
    for x in rd(fn):
        if 'prompt' in x:
            out.add(rkey(thm_of_prompt(x['prompt'])))
        elif 'thm' in x:
            out.add(rkey(' '.join(x['thm'].split())))
    return out


def part_splits():
    train = {'train_depth3_f0_a1': f'{ROOT}/data/p2/train_depth3_f0_a1.jsonl', 'train_reductio_f0': f'{ROOT}/data/p2/train_reductio_f0.jsonl'}
    evalp = {p: f'{D}/{p}.jsonl' for p in ['depth3_req', 'depth3_req_transfer', 'depth3_nb', 'reductio_req', 'reductio_req_transfer', 'reductio_nb']}
    other = {'heldout': f'{ROOT}/data/p2/heldout.jsonl', 'heldout_c8': f'{ROOT}/data/p2/heldout_c8.jsonl', 'validation_36': f'{ROOT}/targets/validation_36.jsonl',
             'test_short': f'{ROOT}/targets/test_short_prompts.jsonl', 'test_long': f'{ROOT}/targets/test_long_prompts.jsonl'}
    K = {}
    for n, fn in {**train, **evalp, **other}.items():
        if os.path.exists(fn):
            K[n] = keys_of(fn)
        else:
            print('MISSING', fn)
    res = {'sizes': {n: len(k) for n, k in K.items()}, 'overlaps': {}}
    names = list(K)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            res['overlaps'][f'{a} x {b}'] = len(K[a] & K[b])
    print(json.dumps(res, indent=1))
    dump('splits.json', res)


# ---------------------------------------------------------------- pre-RL coverage and drift coverage
def cov_file(fn, pattern, reqnames):
    recs = rd(fn)
    r = {'n_targets': len(recs), 'names_match_req': sorted(x['name'] for x in recs) == sorted(reqnames), 'n_tried': sum(x['n_tried'] for x in recs),
         'n_tried_set': sorted({x['n_tried'] for x in recs}), 'n_ok': 0, 'pattern_hits': 0, 'pattern_targets': 0, 'nonpattern_hits': 0, 'nonpattern_targets': 0,
         'pattern_distinct': 0, 'frozen256_pattern_targets': 0, 'frozen256_any_targets': 0, 'verify_fail': 0, 'mine_vs_file_label_diff': 0, 'sum_count_ne_n_ok': 0,
         'pattern_target_names': [], 'nonpattern_examples': []}
    for x in recs:
        pt = npt = False; f256 = f256any = False
        r['n_ok'] += x['n_ok']
        if sum(p['count'] for p in x['proofs']) != x['n_ok']:
            r['sum_count_ne_n_ok'] += 1
        for p in x['proofs']:
            if not ok(x['prompt'], p['proof']):
                r['verify_fail'] += 1
                continue
            h = has_pat(p['proof'], pattern)
            if h[pattern] != p['pat'][pattern]:
                r['mine_vs_file_label_diff'] += 1
            if h[pattern]:
                r['pattern_hits'] += p['count']; r['pattern_distinct'] += 1; pt = True
                f256 |= p['first'] <= 256
            else:
                r['nonpattern_hits'] += p['count']; npt = True
                if len(r['nonpattern_examples']) < 5:
                    r['nonpattern_examples'].append({'name': x['name'], 'prompt': x['prompt'], 'proof': p['proof'], 'count': p['count'], 'h': h})
            f256any |= p['first'] <= 256
        r['pattern_targets'] += pt; r['nonpattern_targets'] += npt
        r['frozen256_pattern_targets'] += f256; r['frozen256_any_targets'] += f256any
        if pt:
            r['pattern_target_names'].append(x['name'])
    return r


def part_cov(prefix='cov'):
    res = {}
    for pat in ['depth3', 'reductio']:
        reqnames = [x['name'] for x in rd(f'{D}/{pat}_req.jsonl')]
        for fn in sorted(glob.glob(f'{A}/{prefix}_{pat}_s*.jsonl')):
            key = os.path.basename(fn).replace('.s0.jsonl', '')
            res[key] = cov_file(fn, pat, reqnames)
            r = res[key]
            print(key, {k: r[k] for k in ['n_targets', 'names_match_req', 'n_tried', 'n_ok', 'pattern_hits', 'pattern_targets', 'nonpattern_hits', 'nonpattern_targets',
                                          'frozen256_pattern_targets', 'verify_fail', 'mine_vs_file_label_diff']}, flush=True)
    dump(f'{prefix}.json', res)


# ---------------------------------------------------------------- arms
def fullmatch_found(arm):
    out = {}
    for fn in glob.glob(f'{A}/{arm}/found_*.jsonl'):
        m = re.fullmatch(r'found_(\d+)\.jsonl', os.path.basename(fn))
        if m:
            out[int(m.group(1))] = fn
    return out


def count_arm(arm, pattern, pool):
    """pool: name -> record (prompt, stratum).  Everything from the last found file; round = min over raw records of a normalised proof."""
    ff = fullmatch_found(arm)
    last = max(ff)
    raw = rd(ff[last])
    res = {'arm': arm, 'found_files': sorted(ff), 'raw_records': len(raw), 'verify_fail': 0, 'unparsed': 0, 'unknown_name': 0, 'prompt_mismatch': 0}
    # cumulativity: raw records with round <= r in the last file vs lines of found_r
    res['cum_check'] = {}
    rc = collections.Counter(x['round'] for x in raw)
    for r in sorted(ff):
        n_r = sum(1 for _ in open(ff[r]))
        res['cum_check'][r] = [n_r, sum(v for k, v in rc.items() if k <= r)]
    first = {}  # (name, normproof) -> min round
    for x in raw:
        t = pool.get(x['name'])
        if t is None:
            res['unknown_name'] += 1; continue
        if x['prompt'] != t['prompt']:
            res['prompt_mismatch'] += 1; continue
        if not ok(t['prompt'], x['proof']):
            res['verify_fail'] += 1; continue
        k = (x['name'], normalise(x['proof']))
        if k not in first or x['round'] < first[k]:
            first[k] = x['round']
    res['verified_raw'] = len(raw) - res['verify_fail'] - res['unknown_name'] - res['prompt_mismatch']
    res['distinct_norm_proofs'] = len(first)
    # per target: first round solved, first round with pattern proof
    solved, patr = {}, {}
    npat_proofs = 0
    depth_hist = collections.Counter()
    for (name, proof), r in first.items():
        h = has_pat(proof, pattern)
        if h is None:
            res['unparsed'] += 1; continue
        solved[name] = min(solved.get(name, 99), r)
        depth_hist[(pool[name]['stratum'], h['depth'])] += 1
        if h[pattern]:
            npat_proofs += 1
            patr[name] = min(patr.get(name, 99), r)
    res['pattern_distinct_proofs'] = npat_proofs
    res['depth_hist_distinct'] = {f'{s}_d{d}': v for (s, d), v in sorted(depth_hist.items())}
    rounds = list(range(1, last + 1))
    for s in ['required', 'neighbour']:
        names = [n for n, t in pool.items() if t['stratum'] == s]
        if not names:
            continue
        res[f'{s}_n'] = len(names)
        res[f'{s}_solved_cum'] = [sum(1 for n in names if solved.get(n, 99) <= r) for r in rounds]
        res[f'{s}_pattern_cum'] = [sum(1 for n in names if patr.get(n, 99) <= r) for r in rounds]
        res[f'{s}_solved_without_pattern'] = sum(1 for n in names if n in solved and n not in patr)
        res[f'{s}_solved_only_nonpattern_names'] = [n for n in names if n in solved and n not in patr][:20]
    if 'required_pattern_cum' in res:
        th = THRESH[pattern]
        res['ignition_round'] = next((r for r, v in zip(rounds, res['required_pattern_cum']) if v >= th), None)
        # rounds with neighbour-only successes before first required pattern proof
        fr = next((r for r, v in zip(rounds, res['required_pattern_cum']) if v >= 1), None)
        res['first_required_pattern_round'] = fr
        if 'neighbour_solved_cum' in res:
            res['neighbour_solved_before_first_pattern'] = res['neighbour_solved_cum'][fr - 2] if fr and fr >= 2 else (0 if fr else res['neighbour_solved_cum'][-1])
    # round json
    rj = {}
    for fn in glob.glob(f'{A}/{arm}/round_*.json'):
        j = json.load(open(fn))
        rj[j['round']] = j
    res['heldout_greedy'] = [rj[r]['heldout_greedy']['solved'] if r in rj and rj[r].get('heldout_greedy') else None for r in rounds]
    res['heldout_n'] = rj[last]['heldout_greedy']['n'] if last in rj and rj[last].get('heldout_greedy') else None
    res['targets_cum_solved_json'] = [rj[r]['targets_cum']['solved'] if r in rj else None for r in rounds]
    res['mix_rl_records'] = [rj[r].get('mix_rl_records') if r in rj else None for r in rounds]
    res['excluded_pattern_proofs_json'] = [rj[r].get('excluded_pattern_proofs') if r in rj else None for r in rounds]
    res['transfer_cum_solved_json'] = [rj[r]['transfer_cum']['solved'] if r in rj else None for r in rounds]
    res['init'] = json.load(open(f'{A}/{arm}/args.json'))
    return res


def part_arms(prefix=''):
    pools = {}
    for pat in ['depth3', 'reductio']:
        for c, f in [('req', 'req'), ('mix', 'mix'), ('drift', 'nb')]:
            pools[(pat, c)] = {x['name']: x for x in rd(f'{D}/{pat}_{f}.jsonl')}
    for d in sorted(glob.glob(f'{A}/ei_*')):
        arm = os.path.basename(d)
        if not arm.startswith(prefix or 'ei_'):
            continue
        m = re.fullmatch(r'ei_(depth3|reductio)_s(\d+)_(req|mix|drift)', arm)
        if not m:
            print('SKIP', arm); continue
        pat, seed, cond = m.group(1), int(m.group(2)), m.group(3)
        if not fullmatch_found(arm):
            res = {'arm': arm, 'missing': True, 'files': os.listdir(d)}
        else:
            res = count_arm(arm, pat, pools[(pat, cond)])
            a = res['init']
            res['args_ok'] = (a['targets'].endswith(f'{pat}_{"nb" if cond == "drift" else cond}.jsonl') and a['seed'] == seed and a['rounds'] == 8 and a['k'] == 32 and a['temperature'] == 0.8
                              and a['retain'] == 20000 and (a.get('exclude_pattern') == (pat if cond == 'drift' else None)) and f's{seed}' in a['init'] and pat in a['init'])
        dump(f'arm_{arm}.json', res)
        print(arm, {k: res.get(k) for k in ['raw_records', 'verify_fail', 'distinct_norm_proofs', 'pattern_distinct_proofs', 'required_pattern_cum', 'required_solved_without_pattern',
                                            'neighbour_solved_cum', 'neighbour_pattern_cum', 'ignition_round', 'args_ok', 'missing']}, flush=True)


if __name__ == '__main__':
    part = sys.argv[1]
    if part == 'pools':
        part_pools()
    elif part == 'splits':
        part_splits()
    elif part == 'cov':
        part_cov('cov')
    elif part == 'dcov':
        part_cov('dcov')
    elif part == 'arms':
        part_arms(sys.argv[2] if len(sys.argv) > 2 else '')
