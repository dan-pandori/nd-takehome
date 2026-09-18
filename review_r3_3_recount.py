#!/usr/bin/env python3
"""Reviewer's independent recount for round3-run3 (base generalisation by pattern class, 72 Stage-1 draws, no RL).

Only nd_verify is shared with the executor. Parser, dependency pruning, predicates (strict reductio, strict derived-ORE,
box depth), first-half predicates on verified proofs and the renaming key are the reviewer's own
(review_run5_recount.py + this file).

  ROOT=~/review/round3-run3 python3 review_r3_3_recount.py pools|splits|train <set>|logs|cov <family>|ign

Outputs artifacts/review_r3_3/*.json under the directory this script lives in.
"""
import json, os, sys, glob, re, collections, io, pickle, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.expanduser(os.environ.get('ROOT', HERE))
TRAINDIR = os.path.expanduser(os.environ.get('TRAINDIR', '~/nd-takehome/data/p2'))
sys.path.insert(0, HERE)
from review_run5_recount import rkey, thm_of_prompt, parse_proof, parse_formula, prune, p_reductio, p_derived_ore_strict, max_depth, rd
sys.path.insert(0, ROOT)
from nd_verify import verify_text

OUT = os.path.join(HERE, 'artifacts', 'review_r3_3')
os.makedirs(OUT, exist_ok=True)
A = os.path.join(ROOT, 'artifacts', 'r3_3')
D = os.path.join(ROOT, 'data', 'r3_3')
SEEDS = list(range(30, 54))
SETS = {'depth3': 'depth3_f0_a1', 'reductio': 'reductio_f0', 'derived_ore_strict': 'derived_ore_f0'}
# family -> (pattern, file glob piece, pool file, k)
FAM = {
    'd3p1': ('depth3', 'cov_depth3_f0_a1_s{s}_p1', f'{D}/targets_depth3_p1.jsonl', 2000),
    'd3p2': ('depth3', 'cov_depth3_f0_a1_s{s}_p2', f'{D}/targets_depth3_p2.jsonl', 2000),
    'red': ('reductio', 'cov_reductio_f0_s{s}_req', f'{ROOT}/data/p2/targets_reductio_req.jsonl', 2000),
    'dos6': ('derived_ore_strict', 'cov_derived_ore_f0_s{s}_dos6', f'{D}/targets_derived_ore_strict_c6.jsonl', 2000),
    'deepred': ('reductio', 'deep_reductio_f0_s{s}', f'{D}/targets_reductio_deep52.jsonl', 20000),
    'deepd3': ('depth3', 'deep_depth3_f0_a1_s{s}', f'{D}/targets_depth3_deep45.jsonl', 20000),
}


def dump(name, obj):
    json.dump(obj, open(os.path.join(OUT, name), 'w'), indent=1, sort_keys=True)


def ok(prompt, proof):
    return bool(verify_text(prompt + ' ' + proof)[0])


def goal_of(prompt):
    toks = prompt.split()
    f, _ = parse_formula(toks, toks.index('SEQ') + 1)
    return f


def pats(proof):
    ls = parse_proof(proof)
    if ls is None:
        return None
    pr = prune(ls)
    return {'depth3': max_depth(pr) >= 3, 'reductio': p_reductio(pr), 'derived_ore_strict': p_derived_ore_strict(pr), 'depth': max_depth(pr),
            'written': len(ls), 'pruned': len(pr), 'lines': ls, 'pruned_lines': pr}


def firsthalf_mine(ls, goal):
    """Reviewer's version of the pre-registered first-half predicates, on the written (unpruned) lines."""
    by = {l['idx']: l for l in ls}
    ng = ('~', goal)
    negis = [l for l in ls if l['rule'] == 'NEGI' and l['refs'] and by.get(l['refs'][0], {}).get('rule') == 'AS' and by[l['refs'][0]]['f'] == ng]
    dn_cites = {l['refs'][0] for l in ls if l['rule'] == 'DN' and l['refs']}
    return {
        'd3_written': any(l['depth'] >= 3 for l in ls),
        'd3_as_as': any(a['rule'] == 'AS' and a['depth'] == 2 and b['rule'] == 'AS' and b['depth'] == 3 for a, b in zip(ls, ls[1:])),
        'd2_two_boxes': sum(1 for l in ls if l['rule'] == 'AS' and l['depth'] == 2) >= 2,
        'neg_goal_hyp': any(l['rule'] == 'AS' and l['f'] == ng for l in ls),
        'negi_neggoal': bool(negis),
        'negi_neggoal_nodn': any(n['idx'] not in dn_cites for n in negis),
        'derived_disj': any(l['rule'] not in ('PR', 'AS', 'ORI1', 'ORI2', 'R') and isinstance(l['f'], tuple) and l['f'][0] == 'v' and l['f'][1] != l['f'][2] for l in ls[:-1]),
        'ore_on_derived': any(l['rule'] == 'ORE' and l['refs'] and by.get(l['refs'][0], {}).get('rule') not in ('PR', 'AS', None) for l in ls),
    }


# ---------------------------------------------------------------- pools
def part_pools():
    res = {}
    # depth-3: p1 + p2 == campaign pool, order, lengths, required@8 stratum recomputed from the depth<=2 search file
    full = rd(f'{ROOT}/data/p2/targets_depth3.jsonl'); p1 = rd(f'{D}/targets_depth3_p1.jsonl'); p2 = rd(f'{D}/targets_depth3_p2.jsonl')
    md2 = {x['name']: x for x in rd(f'{ROOT}/data/p2/targets_depth3_maxdepth2.jsonl')}
    r = {'n_full': len(full), 'n_p1': len(p1), 'n_p2': len(p2),
         'p1_is_first300': [x['prompt'] for x in p1] == [x['prompt'] for x in full[:300]],
         'p2_is_rest': [x['prompt'] for x in p2] == [x['prompt'] for x in full[300:]],
         'p1_len_hist': dict(collections.Counter(x['min_lines_ub'] for x in p1)), 'p2_len_hist': dict(collections.Counter(str(x['min_lines_ub']) for x in p2)),
         'full_sorted_by_n_lines': [x['n_lines'] for x in full] == sorted(x['n_lines'] for x in full),
         'full_sorted_by_min_lines_ub': [x['min_lines_ub'] or 99 for x in full] == sorted(x['min_lines_ub'] or 99 for x in full),
         'distinct_rkey': len({rkey(thm_of_prompt(x['prompt'])) for x in full})}
    req8 = [x['name'] for x in full if md2[x['name']]['min_lines_ub'] is None and not md2[x['name']]['timeout'] and md2[x['name']]['bound'] == 8
            and x['min_lines_ub'] is not None and x['min_lines_ub'] <= 8]
    r['required8_mine'] = len(req8); r['required8_in_p1'] = len(set(req8) & {x['name'] for x in p1})
    r['stratum_field'] = {'p1': dict(collections.Counter(x.get('stratum') for x in p1)), 'p2': dict(collections.Counter(x.get('stratum') for x in p2))}
    r['stratum_field_matches_mine'] = {x['name'] for x in p1 + p2 if x.get('stratum') == 'required8'} == set(req8)
    # gen_proof verified and depth-3 under my predicate; md2 proof (if any) verified and depth<=2
    c = collections.Counter()
    for x in full:
        h = pats(x['gen_proof']); c['gen_verified'] += ok(x['prompt'], x['gen_proof']); c['gen_depth3'] += h['depth3']
        m = md2[x['name']]
        if m['proof']:
            hm = pats(m['proof']); c['md2_proofs'] += 1; c['md2_verified'] += ok(x['prompt'], m['proof']); c['md2_depth_le2'] += hm['depth'] <= 2
            c[f'md2_len_{m["min_lines_ub"]}'] += 1
        c['md2_timeout'] += bool(m['timeout'])
    r['checks'] = dict(c); res['depth3'] = r
    dump('req8_names.json', req8)
    # reductio required pool
    rq = rd(f'{ROOT}/data/p2/targets_reductio_req.jsonl')
    c = collections.Counter(); sch = collections.defaultdict(collections.Counter)
    for x in rq:
        h = pats(x['oracle_proof']); c['oracle_verified'] += ok(x['prompt'], x['oracle_proof']); c['oracle_strict_reductio'] += h['reductio']
        c['requires'] += bool(x['requires']); sch[x['schema']][x['min_lines_ub']] += 1
        g = goal_of(x['prompt']); fh = firsthalf_mine(h['lines'], g); c['oracle_negi_on_sequent_goal'] += fh['negi_neggoal']
    res['reductio'] = {'n': len(rq), 'distinct_rkey': len({rkey(thm_of_prompt(x['prompt'])) for x in rq}), 'checks': dict(c),
                       'schema_by_len': {k: dict(v) for k, v in sch.items()}}
    d52 = rd(f'{D}/targets_reductio_deep52.jsonl')
    seven = [x['prompt'] for x in rq if x['min_lines_ub'] == 7]
    res['deep52'] = {'n': len(d52), 'is_all_7line_of_req': sorted(x['prompt'] for x in d52) == sorted(seven), 'schema': dict(collections.Counter(x['schema'] for x in d52))}
    # derived-ORE strict: candidates, oracle labels, pool
    cands = rd(f'{D}/derived_ore_strict_cands.jsonl'); nec = rd(f'{D}/derived_ore_strict_nec.jsonl'); pool = rd(f'{D}/targets_derived_ore_strict_c6.jsonl')
    alld = rd(f'{ROOT}/data/p2/targets_derived_ore.jsonl')
    mine_strict = [x['name'] for x in alld if pats(x['gen_proof'])['derived_ore_strict']]
    c = collections.Counter(); bad = []
    for x in nec:
        c['n'] += 1; c['requires'] += bool(x['requires']); c['timeout_u'] += bool(x['timeout']); c['timeout_r'] += bool(x['r_timeout'])
        c['reachable'] += x['min_lines_ub'] is not None; c[f'min_{x["min_lines_ub"]}'] += 1
        c['oracle_ok_false'] += x.get('oracle_ok') is False
        if x['proof']:
            v = ok(x['prompt'], x['proof']); h = pats(x['proof']); c['u_verified'] += v; c['u_len_ok'] += h['written'] == x['min_lines_ub']
            c['u_has_strict'] += h['derived_ore_strict']
            if x['requires'] and not h['derived_ore_strict']:
                bad.append(x['name'])
        if x['r_proof']:
            v = ok(x['prompt'], x['r_proof']); h = pats(x['r_proof']); c['r_proofs'] += 1; c['r_verified'] += v; c['r_has_strict'] += h['derived_ore_strict']
            c['r_len_gt_u'] += x['r_min_lines_ub'] > x['min_lines_ub']; c['r_len_eq_u'] += x['r_min_lines_ub'] == x['min_lines_ub']
        if x['requires']:
            c[f'req_min_{x["min_lines_ub"]}'] += 1
            if not (x['r_min_lines_ub'] is None and not x['r_timeout'] and x['min_lines_ub'] is not None and x['min_lines_ub'] <= 10):
                c['requires_inconsistent'] += 1
    necby = {x['prompt']: x for x in nec}
    pc = collections.Counter()
    for i, x in enumerate(pool):
        n = necby.get(x['prompt']); pc['in_nec'] += n is not None; pc['requires'] += bool(x['requires']); pc['requires_matches_nec'] += bool(n and n['requires'] == x['requires'])
        pc[f'stratum_{x.get("stratum")}'] += 1; pc[f'min_{x["min_lines_ub"]}_{"req" if x["requires"] else "nonreq"}'] += 1
    firstnon = next((i for i, x in enumerate(pool) if not x['requires']), None)
    res['derived_ore_strict'] = {'n_campaign_pool': len(alld), 'strict_by_my_predicate_on_pruned_gen_proof': len(mine_strict), 'n_cands': len(cands),
                                 'cands_equal_mine': sorted(x['name'] for x in cands) == sorted(mine_strict), 'nec': dict(c), 'required_without_my_pattern': bad,
                                 'pool': dict(pc), 'pool_n': len(pool), 'pool_distinct_rkey': len({rkey(thm_of_prompt(x['prompt'])) for x in pool}),
                                 'pool_first_nonrequired_index': firstnon, 'pool_required_all_before_nonrequired': all(x['requires'] for x in pool[:firstnon or len(pool)]) and not any(x['requires'] for x in pool[firstnon or len(pool):])}
    print(json.dumps(res, indent=1))
    dump('pools.json', res)


# ---------------------------------------------------------------- splits
def keys_of(fn):
    out = set()
    for l in open(fn):
        if l.strip():
            out.add(rkey(thm_of_prompt(json.loads(l)['prompt'])))
    return out


def part_splits():
    files = {'train_depth3_f0_a1': f'{TRAINDIR}/train_depth3_f0_a1.jsonl', 'train_reductio_f0': f'{TRAINDIR}/train_reductio_f0.jsonl',
             'train_derived_ore_f0': f'{TRAINDIR}/train_derived_ore_f0.jsonl', 'heldout': f'{ROOT}/data/p2/heldout.jsonl',
             'depth3_p1': f'{D}/targets_depth3_p1.jsonl', 'depth3_p2': f'{D}/targets_depth3_p2.jsonl', 'reductio_req': f'{ROOT}/data/p2/targets_reductio_req.jsonl',
             'dos6': f'{D}/targets_derived_ore_strict_c6.jsonl', 'validation_36': f'{ROOT}/targets/validation_36.jsonl',
             'test_short': f'{ROOT}/targets/test_short_prompts.jsonl', 'test_long': f'{ROOT}/targets/test_long_prompts.jsonl'}
    K = {n: keys_of(fn) for n, fn in files.items() if os.path.exists(fn) or print('MISSING', fn)}
    res = {'sizes': {n: len(k) for n, k in K.items()}, 'overlaps': {}}
    names = list(K)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            res['overlaps'][f'{a} x {b}'] = len(K[a] & K[b])
    print(json.dumps(res, indent=1)); dump('splits.json', res)


# ---------------------------------------------------------------- training files (f = 0 under my predicates, cap 6)
def part_train(which):
    fn = f'{TRAINDIR}/train_{SETS[which]}.jsonl'
    c = collections.Counter(); ex = []
    for i, l in enumerate(open(fn)):
        if not l.strip():
            continue
        x = json.loads(l); c['n'] += 1
        h = pats(x['proof'])
        if h is None:
            c['unparsable'] += 1; continue
        c['cap6_violations'] += h['written'] > 6; c[f'written_{h["written"]}'] += 1
        for p in ('depth3', 'reductio', 'derived_ore_strict'):
            c[f'{p}_pruned'] += h[p]
        ls = h['lines']
        c['depth3_written'] += max_depth(ls) >= 3; c['reductio_written'] += p_reductio(ls); c['derived_ore_strict_written'] += p_derived_ore_strict(ls)
        fh = firsthalf_mine(ls, goal_of(x['prompt']))
        for k, v in fh.items():
            c[f'fh_{k}'] += v
        if i % 100 == 0:
            c['verified_sample'] += 1; c['verify_failures'] += not ok(x['prompt'], x['proof'])
    print(which, json.dumps(dict(c), sort_keys=True)); dump(f'train_{which}.json', dict(c))


# ---------------------------------------------------------------- training logs and checkpoints
def ckpt_extra(fn):
    class Stub:
        def __init__(self, *a, **k): pass
        def __setstate__(self, s): self.s = s
    class U(pickle.Unpickler):
        def find_class(self, mod, name):
            if mod.startswith('torch'):
                return Stub
            try:
                return super().find_class(mod, name)
            except Exception:
                return Stub
        def persistent_load(self, pid):
            return None
    with zipfile.ZipFile(fn) as z:
        name = [n for n in z.namelist() if n.endswith('data.pkl')][0]
        obj = U(io.BytesIO(z.read(name))).load()
    return {'extra': obj.get('extra'), 'tok_mode': obj.get('tok_mode')}


def part_logs():
    res = {}
    for pat, st in SETS.items():
        for s in SEEDS:
            fn = f'{A}/train_{st}_s{s}.log'
            txt = open(fn).read()
            steps = re.findall(r'^step (\d+) loss ([\d.]+) .*? val ([\d.]+)', txt, re.M)
            bd = re.search(r'^heldout_breakdown (\{.*\})$', txt, re.M)
            r = {'n_step_lines': len(steps), 'last_step': int(steps[-1][0]) if steps else None, 'final_val': float(steps[-1][2]) if steps else None,
                 'final_train_loss': float(steps[-1][1]) if steps else None, 'first_lines': txt[:600].split('\n')[:4], 'n_saved': txt.count('saved ckpts')}
            if bd:
                b = json.loads(bd.group(1))
                r['by_rule'] = {k: v['mean'] for k, v in b['by_rule'].items()}; r['by_rule_name_pos'] = {k: v['mean'] for k, v in b['by_rule_name_pos'].items()}
                r['by_class'] = {k: v['mean'] for k, v in b['by_class'].items()}
                tot = sum(v['sum'] for v in b['by_class'].values()); n = sum(v['n'] for v in b['by_class'].values()); r['breakdown_total_mean'] = tot / n
            ck = f'{ROOT}/ckpts/r3_3/stage1_{st}_s{s}.pt'
            if os.path.exists(ck):
                try:
                    r['ckpt'] = ckpt_extra(ck)
                except Exception as e:
                    r['ckpt'] = {'error': repr(e)}
                r['ckpt_bytes'] = os.path.getsize(ck)
            else:
                r['ckpt'] = None
            res[f'{st}_s{s}'] = r
            print(st, s, r['last_step'], r['final_val'], r.get('breakdown_total_mean'), (r['ckpt'] or {}).get('extra') if not isinstance((r['ckpt'] or {}).get('extra'), dict) else {k: v for k, v in r['ckpt']['extra'].items() if k in ('seed', 'data', 'steps', 'cap', 'train', 'args')}, flush=True)
    dump('logs.json', res)


# ---------------------------------------------------------------- coverage
def cov_file(fn, pattern, pool, k):
    recs = rd(fn)
    poolby = {x['name']: x for x in pool}
    r = {'n_records': len(recs), 'names_match_pool': sorted(x['name'] for x in recs) == sorted(poolby), 'dup_names': len(recs) - len({x['name'] for x in recs}),
         'prompts_match_pool': all(poolby.get(x['name'], {}).get('prompt') == x['prompt'] for x in recs), 'n_tried': sum(x['n_tried'] for x in recs),
         'n_tried_set': sorted({x['n_tried'] for x in recs}), 'n_parsed': sum(x.get('n_parsed', 0) for x in recs), 'n_ok': 0, 'n_distinct_ok': 0, 'verify_fail': 0,
         'label_diff': 0, 'sum_count_ne_n_ok': 0, 'dup_proofs_after_my_normalise': 0,
         'pattern_hits': 0, 'pattern_distinct': 0, 'pattern_targets': {}, 'pattern_first': {}, 'ok_targets': 0, 'frozen256_pattern_targets': 0, 'frozen256_any_targets': 0,
         'other_pattern_hits': collections.Counter(), 'fh_all': collections.Counter(), 'fh_ok_file': collections.Counter(), 'fh_ok_mine': collections.Counter(),
         'pattern_hits_by_written_len': collections.Counter(), 'examples': []}
    for x in recs:
        r['n_ok'] += x['n_ok']; r['n_distinct_ok'] += len(x['proofs']); r['ok_targets'] += x['n_ok'] > 0
        if sum(p['count'] for p in x['proofs']) != x['n_ok']:
            r['sum_count_ne_n_ok'] += 1
        for kk, v in x.get('fh_by_pred', {}).items():
            r['fh_all'][kk] += v
        for kk, v in x.get('fh_ok_by_pred', {}).items():
            r['fh_ok_file'][kk] += v
        goal = goal_of(x['prompt']); hits = 0; first = None; firstany = None
        for p in x['proofs']:
            if not ok(x['prompt'], p['proof']):
                r['verify_fail'] += 1; continue
            h = pats(p['proof'])
            for q in ('depth3', 'reductio', 'derived_ore_strict'):
                if h[q] != p['pat'][q]:
                    r['label_diff'] += 1
                if q != pattern and h[q]:
                    r['other_pattern_hits'][q] += p['count']
            for kk, v in firsthalf_mine(h['lines'], goal).items():
                if v:
                    r['fh_ok_mine'][kk] += p['count']
            firstany = p['first'] if firstany is None else min(firstany, p['first'])
            if h[pattern]:
                hits += p['count']; r['pattern_distinct'] += 1; first = p['first'] if first is None else min(first, p['first'])
                r['pattern_hits_by_written_len'][h['written']] += p['count']
                if len(r['examples']) < 3:
                    r['examples'].append({'name': x['name'], 'prompt': x['prompt'], 'proof': p['proof'], 'count': p['count']})
        if hits:
            r['pattern_hits'] += hits; r['pattern_targets'][x['name']] = hits; r['pattern_first'][x['name']] = first
            r['frozen256_pattern_targets'] += first <= 256
        r['frozen256_any_targets'] += firstany is not None and firstany <= 256
    for kk in ('other_pattern_hits', 'fh_all', 'fh_ok_file', 'fh_ok_mine', 'pattern_hits_by_written_len'):
        r[kk] = dict(r[kk])
    r['k_expected'] = k
    return r


def part_cov(fam):
    pattern, stem, poolfn, k = FAM[fam]
    pool = rd(poolfn); res = {}
    for s in SEEDS:
        fn = f'{A}/{stem.format(s=s)}.s0.jsonl'
        if not os.path.exists(fn):
            res[str(s)] = None; print(fam, s, 'MISSING', flush=True); continue
        r = cov_file(fn, pattern, pool, k); res[str(s)] = r
        logfn = f'{A}/{stem.format(s=s)}.log'
        if os.path.exists(logfn):
            t = open(logfn).read(); r['log_done'] = t.rstrip().endswith('DONE'); r['log_shard_lines'] = re.findall(r'^shard .*$', t, re.M)
        print(fam, s, {kk: r[kk] for kk in ['n_records', 'names_match_pool', 'n_tried', 'n_tried_set', 'n_ok', 'ok_targets', 'pattern_hits', 'pattern_distinct', 'frozen256_pattern_targets',
                                           'verify_fail', 'label_diff', 'sum_count_ne_n_ok']}, 'targets', len(r['pattern_targets']), flush=True)
    dump(f'cov_{fam}.json', res)


# ---------------------------------------------------------------- external stratum: the ignition study's draws (300-target samples)
def part_ign():
    I = os.path.join(ROOT, 'artifacts', 'ign'); res = {}
    for fn in sorted(glob.glob(f'{I}/cov_*.s0.jsonl')):
        key = os.path.basename(fn).replace('.s0.jsonl', '')
        pattern = 'reductio' if 'reductio' in key else 'depth3'
        recs = rd(fn); pool = [{'name': x['name'], 'prompt': x['prompt']} for x in recs]
        r = cov_file(fn, pattern, pool, None)
        res[key] = {kk: r[kk] for kk in ['n_records', 'n_tried', 'n_tried_set', 'n_ok', 'pattern_hits', 'pattern_distinct', 'pattern_targets', 'frozen256_pattern_targets', 'verify_fail', 'label_diff']}
        print(key, {kk: v for kk, v in res[key].items() if kk != 'pattern_targets'}, len(r['pattern_targets']), flush=True)
    hit = set()
    for key, r in res.items():
        if 'depth3' in key:
            hit |= set(r['pattern_targets'])
    d45 = {x['name'] for x in rd(f'{D}/targets_depth3_deep45.jsonl')}
    res['_deep45'] = {'n_ign_depth3_hit_targets': len(hit), 'deep45_equals_ign_hit_targets': hit == d45, 'only_in_deep45': sorted(d45 - hit), 'only_in_ign': sorted(hit - d45)}
    print(res['_deep45']); dump('ign.json', res)


if __name__ == '__main__':
    part = sys.argv[1]
    if part == 'pools': part_pools()
    elif part == 'splits': part_splits()
    elif part == 'train': part_train(sys.argv[2])
    elif part == 'logs': part_logs()
    elif part == 'cov': part_cov(sys.argv[2])
    elif part == 'ign': part_ign()
    else: raise SystemExit('unknown part')
