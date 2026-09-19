"""Reviewer recount for round3-run4b, phase 1. Own code only (review_run4b_lib) + unmodified nd_verify.
Usage: python3 review_run4b_recount.py > review_run4b_recount.out ; writes review_run4b_recount.json
"""
import json, os, glob, sys, random, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from review_run4b_lib import normalise, is_depth3, max_depth_pruned, n_written, prompt_to_thm
from nd_verify import verify_text

A = 'artifacts/r3_4b'
DRAWS = [f'{sz}_s{s}' for sz in ('25M', '25Mr', '85M', '85Mr') for s in (0, 1, 2)]
OUT = {}
rng = random.Random(20260919)


def rd(fn):
    return [json.loads(l) for l in open(fn) if l.strip()]


def vok(prompt, proof):
    ok, reason, nl = verify_text(prompt + ' ' + proof)
    return ok


req = rd('data/r3_1/depth3_req.jsonl')
mix = rd('data/r3_1/depth3_mix.jsonl')
REQ = {r['name'] for r in req}
assert len(REQ) == 300 and sum(r['stratum'] == 'required' for r in mix) == 300 and {r['name'] for r in mix if r['stratum'] == 'required'} == REQ
PROMPT = {r['name']: r['prompt'] for r in mix}
print('pool: required by n_lines', collections.Counter(r['n_lines'] for r in req),
      '| r10 alternative', collections.Counter(str(r['r10_min_lines_ub']) for r in req))
print('mix neighbours by n_lines', collections.Counter(r['n_lines'] for r in mix if r['stratum'] != 'required'))

# ---------- E5 gate: re-verify every greedy held-out proof ----------
print('\n== E5 held-out greedy (5,000), re-verified with nd_verify ==')
gate = {}
for d in DRAWS:
    rows = rd(f'{A}/heldout_greedy_{d}.jsonl')
    n = len(rows); ok = 0; by = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        good = bool(r['proofs']) and vok(r['prompt'], r['proofs'][0])
        assert good == bool(r['solved']), r['name']
        ok += good; by[r['n_lines']][0] += good; by[r['n_lines']][1] += 1
    gate[d] = {'n': n, 'solved': ok, 'rate': ok / n, 'by_len': {k: v[0] / v[1] for k, v in sorted(by.items())}}
    print(d, n, ok, f'{ok/n:.4f}', {k: round(v, 3) for k, v in gate[d]['by_len'].items()})
for sz, thr in (('25M', .90), ('25Mr', .90), ('85M', .93), ('85Mr', .93)):
    m = statistics.median(gate[f'{sz}_s{s}']['rate'] for s in (0, 1, 2))
    print(f'  median {sz}: {m:.4f} gate {thr} -> {"PASS" if m >= thr else "MISS"}')
OUT['gate'] = gate

# ---------- pre-RL coverage ----------
def cov_stats(fn, names=None, verify_all=True):
    rows = rd(fn)
    tried = sum(r['n_tried'] for r in rows)
    hits = 0; ok_nonpat = 0; tg = set(); tg_nonpat = set(); f256 = set(); distinct = set(); nver = 0
    for r in rows:
        for p in r['proofs']:
            if verify_all:
                assert vok(r['prompt'], p['proof']), (fn, r['name']); nver += 1
            if is_depth3(p['proof']):
                hits += p['count']; tg.add(r['name']); distinct.add((r['name'], normalise(p['proof'])))
                if p['first'] is not None and p['first'] <= 256:   # index convention checked below
                    f256.add(r['name'])
            else:
                ok_nonpat += p['count']; tg_nonpat.add(r['name'])
    return {'targets': len(rows), 'names': sorted(r['name'] for r in rows), 'tried': tried, 'hits': hits, 'rate': hits / tried if tried else None,
            'targets_hit': sorted(tg), 'distinct': len(distinct), 'frozen256': sorted(f256), 'ok_nonpattern': ok_nonpat,
            'targets_nonpattern': sorted(tg_nonpat), 'verified': nver,
            'per_target_tried': collections.Counter(r['n_tried'] for r in rows)}


print('\n== pre-RL required-pool sample (k=2000, 600k) ==')
cov = {}
for d in DRAWS:
    fn = f'{A}/cov_depth3_{d}.merged.jsonl' if os.path.exists(f'{A}/cov_depth3_{d}.merged.jsonl') else f'{A}/cov_depth3_{d}.s0.jsonl'
    c = cov_stats(fn); cov[d] = c
    assert set(c['names']) == REQ, (d, len(c['names']))
    print(d, os.path.basename(fn), 'targets', c['targets'], 'tried', c['tried'], dict(c['per_target_tried']), 'pattern hits', c['hits'],
          'rate', f"{c['rate']:.2e}", 'targets hit', len(c['targets_hit']), 'distinct', c['distinct'], 'frozen@256', len(c['frozen256']),
          'valid non-pattern samples', c['ok_nonpattern'], 'on', len(c['targets_nonpattern']), 'targets')
OUT['cov'] = {d: {k: v for k, v in c.items() if k not in ('names', 'per_target_tried')} for d, c in cov.items()}

# merged files: check they are the disjoint union of the two half files
print('\n-- merged-file check (85Mr pre-RL halves)')
for d in ('85Mr_s0', '85Mr_s1', '85Mr_s2'):
    a = rd(f'{A}/cov_depth3_{d}.s0.jsonl'); b = rd(f'{A}/cov_depth3_{d}.s0r.jsonl'); m = rd(f'{A}/cov_depth3_{d}.merged.jsonl')
    na, nb = [r['name'] for r in a], [r['name'] for r in b]
    print(d, 'fwd', len(a), 'rev', len(b), 'overlap', len(set(na) & set(nb)), 'merged', len(m),
          'merged hits==max/sum?', sum(r['n_ok'] for r in m), sum(r['n_ok'] for r in a), sum(r['n_ok'] for r in b),
          'overlap names', sorted(set(na) & set(nb))[:5])

print('\n== pre-RL optional-pool sample (A1) ==')
opt = {}
optpool = rd('data/p2/targets_depth3.jsonl')[:300]
for d in DRAWS:
    c = cov_stats(f'{A}/optcov_depth3_{d}.s0.jsonl'); opt[d] = c
    assert c['names'] == sorted(r['name'] for r in optpool)
    print(d, 'targets', c['targets'], 'tried', c['tried'], 'pattern hits', c['hits'], 'rate', f"{c['rate']:.2e}", 'targets hit', len(c['targets_hit']),
          '| valid non-pattern samples', c['ok_nonpattern'], 'on', len(c['targets_nonpattern']), 'targets')
OUT['optcov'] = {d: {k: v for k, v in c.items() if k not in ('names', 'per_target_tried')} for d, c in opt.items()}

# ---------- EI arms ----------
def arm_stats(path, nver=150):
    if not os.path.isdir(path) or not glob.glob(f'{path}/found_[0-9]*.jsonl'):
        return None   # absent, or a directory holding only args.json (arm started and stopped before round 1)
    rounds = sorted(int(os.path.basename(f)[6:-5]) for f in glob.glob(f'{path}/round_*.json'))
    founds = sorted(int(os.path.basename(f)[6:-6]) for f in glob.glob(f'{path}/found_[0-9]*.jsonl'))
    last = max(founds)
    rows = rd(f'{path}/found_{last}.jsonl')
    # cumulative-file check: every earlier file is a subset of the last
    allset = collections.Counter((r['name'], r['proof']) for r in rows)
    for k in founds[:-1]:
        for r in rd(f'{path}/found_{k}.jsonl'):
            assert (r['name'], r['proof']) in allset, (path, k)
    first = {}; first_any = {}; distinct = collections.defaultdict(set); nonpat_solved = set()
    for r in rows:
        first_any[r['name']] = min(first_any.get(r['name'], 99), r['round'])
        if is_depth3(r['proof']):
            first[r['name']] = min(first.get(r['name'], 99), r['round'])
            distinct[r['name']].add(normalise(r['proof']))
    req_first = {n: v for n, v in first.items() if n in REQ}
    cum = [sum(v <= k for v in req_first.values()) for k in range(1, 9)]
    req_any = {n for n in first_any if n in REQ}
    nonpat_only = sorted(n for n in req_any if n not in req_first)
    nb_any = [sum(1 for n, v in first_any.items() if n not in REQ and v <= k) for k in range(1, 9)]
    ign20 = next((k for k, c in enumerate(cum, 1) if c >= 20), None)
    ign6 = next((k for k, c in enumerate(cum, 1) if c >= 6), None)
    trained = {}
    for k in rounds:
        j = json.load(open(f'{path}/round_{k}.json')); trained[k] = j.get('mix_rl_records', 0)
    # re-verify a sample of counted proofs (all if fewer than nver)
    counted = [r for r in rows if r['name'] in REQ and is_depth3(r['proof'])]
    samp = counted if len(counted) <= nver else rng.sample(counted, nver)
    bad = sum(not vok(PROMPT.get(r['name'], r['prompt']), r['proof']) for r in samp)
    # transfer
    tl = max(int(os.path.basename(f)[15:-6]) for f in glob.glob(f'{path}/found_transfer_*.jsonl'))
    trows = rd(f'{path}/found_transfer_{tl}.jsonl')
    t_pat = {r['name'] for r in trows if is_depth3(r['proof'])}
    return {'rounds': rounds, 'found_files': founds, 'req_cum': cum, 'acq': cum[-1] if len(cum) else 0, 'ign20': ign20, 'ign6': ign6,
            'req_nonpattern_only': nonpat_only, 'req_solved_any': len(req_any), 'nb_cum': nb_any, 'rl_records': trained,
            'rounds_trained': sum(v > 0 for v in trained.values()), 'proofs_counted': len(counted),
            'distinct_norm': sum(len(v) for n, v in distinct.items() if n in REQ), 'reverified': len(samp), 'reverify_bad': bad,
            'transfer_pattern_targets': len(t_pat), 'transfer_last': tl, 'acquired': sorted(req_first)}


print('\n== EI arms (required stratum, pattern = my depth-3 predicate on the dependency cone, min-round) ==')
arms = {}
for d in DRAWS:
    for arm in ('req', 'frozen', 'mix'):
        s = arm_stats(f'{A}/ei_depth3_{d}_{arm}')
        arms[f'{d}_{arm}'] = s
        if s is None:
            print(d, arm, 'ABSENT'); continue
        print(d, arm, 'rounds', s['rounds'][-1], 'req cum', s['req_cum'], 'ign>=20', s['ign20'], 'ign>=6', s['ign6'], '| neighbours cum', s['nb_cum'] if arm == 'mix' else '-',
              '| rounds trained', s['rounds_trained'], '| counted proofs', s['proofs_counted'], 'distinct', s['distinct_norm'],
              f"| reverified {s['reverified']} bad {s['reverify_bad']}", '| req solved w/o pattern', len(s['req_nonpattern_only']), '| transfer pattern targets', s['transfer_pattern_targets'])
OUT['arms'] = arms

# oom partial dirs: are their proofs included anywhere? (should not be counted)
for p in sorted(glob.glob(f'{A}/ei_depth3_*oom*')):
    rows = [r for f in glob.glob(f'{p}/found_[0-9]*.jsonl') for r in rd(f)]
    print('partial', os.path.basename(p), 'rows', len(rows), 'req pattern targets', len({r['name'] for r in rows if r['name'] in REQ and is_depth3(r['proof'])}))

# ---------- pass@1e4 ----------
print('\n== pass@1e4 from the Stage-1 checkpoint (required pool) ==')
p1e4 = {}
for d in ('25Mr_s0', '25Mr_s1', '85Mr_s2'):
    shards = sorted(f for f in glob.glob(f'{A}/cov1e4_depth3_{d}.s*.jsonl'))
    for f in shards:
        rows = rd(f); print('  shard', os.path.basename(f), 'targets', len(rows), 'tried', sum(r['n_tried'] for r in rows), collections.Counter(r['n_tried'] for r in rows).most_common(3))
    names = collections.Counter(r['name'] for f in shards for r in rd(f))
    print('  shard union targets', len(names), 'targets in >1 shard', sum(v > 1 for v in names.values()))
    c = cov_stats(f'{A}/cov1e4_depth3_{d}.merged.jsonl'); p1e4[d] = c
    sh_hits = sum(cov_stats(f, verify_all=False)['hits'] for f in shards)
    acq = set(arms[f'{d}_mix']['acquired'])
    reach = set(c['targets_hit'])
    reach600 = set(cov[d]['targets_hit'])
    eionly = acq - reach
    print(d, 'merged targets', c['targets'], 'tried', c['tried'], dict(c['per_target_tried']), 'pattern hits', c['hits'], '(shards sum', sh_hits, ')', 'rate', f"{c['rate']:.2e}",
          'base-reachable targets', len(reach), sorted(reach), '| acquired by mix', len(acq), 'EI-only', len(eionly), f'{len(eionly)/len(acq):.4f}',
          '| also excluding 600k-sample reach:', len(acq - reach - reach600), '| reachable but not acquired', sorted(reach - acq))
    p1e4[d]['ei_only'] = len(eionly); p1e4[d]['acquired'] = len(acq)
OUT['pass1e4'] = {d: {k: v for k, v in c.items() if k not in ('names', 'per_target_tried')} for d, c in p1e4.items()}

# ---------- 3.2M reference row (run 1's files) ----------
print('\n== 3.2M reference row from artifacts/r3_1 ==')
A1 = 'artifacts/r3_1'
ref = {}
for s in range(20, 28):
    c = cov_stats(f'{A1}/cov_depth3_s{s}.s0.jsonl')
    r_ = arm_stats(f'{A1}/ei_depth3_s{s}_req'); m_ = arm_stats(f'{A1}/ei_depth3_s{s}_mix')
    ref[s] = {'cov': {k: v for k, v in c.items() if k not in ('names', 'per_target_tried')}, 'req': r_, 'mix': m_}
    acq = set(m_['acquired']) if m_ else set()
    print(f's{s}', 'tried', c['tried'], 'hits', c['hits'], 'rate', f"{c['rate']:.2e}", 'targets hit', len(c['targets_hit']),
          '| req cum', r_['req_cum'] if r_ else None, 'trained rounds', r_['rounds_trained'] if r_ else None,
          '| mix req cum', m_['req_cum'] if m_ else None, 'ign20', m_['ign20'] if m_ else None,
          '| mix acquired not in 600k sample', len(acq - set(c['targets_hit'])), 'of', len(acq))
OUT['ref3.2M'] = ref

json.dump(OUT, open('review_run4b_recount.json', 'w'), indent=1, default=list)
