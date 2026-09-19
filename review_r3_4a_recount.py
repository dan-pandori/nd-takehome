#!/usr/bin/env python3
"""Reviewer's independent recount for round3-run4a (phase 1). Reads only raw artefacts under <root>/artifacts/r3_4a and
data files; uses review_r3_4a_lib (own parser / normaliser / pruner / predicate) and the unmodified nd_verify.
usage: python3 review_r3_4a_recount.py <root> <out.json>"""
import json, sys, os, glob, re, collections, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from review_r3_4a_lib import classify, normalise, canon, thm_of_prompt
from nd_verify import verify_text

ROOT, OUT = sys.argv[1], sys.argv[2]
A = f'{ROOT}/artifacts/r3_4a'
rd = lambda fn: [json.loads(l) for l in open(fn) if l.strip()]
T = rd(f'{ROOT}/data/p2/targets_reductio_req.jsonl')
STRAT = {t['name']: t['min_lines_ub'] for t in T}
SCHEMA = {t['name']: t['schema'] for t in T}
PROMPT = {t['name']: t['prompt'] for t in T}
rng = random.Random(12345)
res = {}


def verify(prompt, proof):
    return verify_text(prompt + ' ' + proof)[0]


def stage1(tag):
    o = {}
    fn = f'{A}/train_{tag}.log'
    if os.path.exists(fn):
        txt = open(fn).read()
        m = re.search(r'params (\d+)', txt); o['params'] = int(m.group(1)) if m else None
        m = re.search(r'train records (\d+)', txt); o['train_records'] = int(m.group(1)) if m else None
        st = re.findall(r'step (\d+) loss ([\d.]+) lr (\S+) \S+ val ([\d.]+)', txt)
        if st:
            o['last_step'], o['peak_lr'], o['final_val'] = int(st[-1][0]), max(float(s[2]) for s in st), float(st[-1][3])
        o['saved'] = 'saved ' in txt
    fn = f'{A}/heldout_greedy_{tag}.jsonl'
    if os.path.exists(fn):
        rows = rd(fn)
        # re-verify every greedy output myself rather than trusting the 'solved' flag
        ok = sum(1 for r in rows if r['proofs'] and verify(r['prompt'], r['proofs'][0]))
        flag = sum(1 for r in rows if r['solved'])
        o['heldout_n'], o['heldout_ok_reverified'], o['heldout_flagged'] = len(rows), ok, flag
        o['heldout_greedy'] = ok / len(rows)
    return o


def cov(fn, full=True):
    """coverage file -> hits (verified samples), strict-reductio hits (my predicate on stored distinct proofs x count)."""
    rows = rd(fn)
    o = {'targets': len(rows), 'samples': sum(r['n_tried'] for r in rows), 'n_ok': 0, 'strict_hits': 0, 'patfree_hits': 0,
         'count_mismatch': 0, 'targets_hit': 0, 'targets_hit_strict': 0, 'distinct_ok': 0, 'not_normalised': 0,
         'hits_by_stratum': collections.Counter(), 'hits_by_schema': collections.Counter(), 'targets_hit_by_stratum': collections.Counter(),
         'first_hit_le256': 0, 'patfree_targets': []}
    pool = []
    for r in rows:
        s = sum(p['count'] for p in r['proofs'])
        o['count_mismatch'] += (s != r['n_ok'])
        o['n_ok'] += s
        o['distinct_ok'] += len(r['proofs'])
        if len({normalise(p['proof']) for p in r['proofs']}) != len(r['proofs']):
            o['not_normalised'] += 1
        sh = 0
        for p in r['proofs']:
            c = classify(p['proof'])
            if c and c['reductio']:
                sh += p['count']
            else:
                o['patfree_hits'] += p['count']
            pool.append((r['prompt'], p['proof']))
        if s:
            o['targets_hit'] += 1
            o['targets_hit_by_stratum'][STRAT[r['name']]] += 1
        if sh:
            o['targets_hit_strict'] += 1
        if s and not sh:
            o['patfree_targets'].append(r['name'])
        o['strict_hits'] += sh
        o['hits_by_stratum'][STRAT[r['name']]] += sh
        o['hits_by_schema'][SCHEMA[r['name']]] += sh
        if r['first_hit'] is not None and r['first_hit'] <= 256:
            o['first_hit_le256'] += 1
    o['rate_strict'] = o['strict_hits'] / o['samples'] if o['samples'] else None
    samp = pool if len(pool) <= 300 else rng.sample(pool, 300)
    o['reverified'] = len(samp); o['reverify_fail'] = sum(1 for pr, p in samp if not verify(pr, p))
    o['names_hit'] = sorted(r['name'] for r in rows if r['n_ok'] > 0)
    o['names'] = sorted(r['name'] for r in rows)
    for k in ('hits_by_stratum', 'hits_by_schema', 'targets_hit_by_stratum'):
        o[k] = dict(sorted(o[k].items(), key=lambda x: str(x[0])))
    return o


def arm(d, rounds=range(1, 9)):
    """EI / frozen arm directory -> per-round cumulative acquisition (strict reductio on my normalised+pruned form)."""
    o = {'rounds_present': sorted(int(re.search(r'found_(\d+)', f).group(1)) for f in glob.glob(f'{d}/found_[0-9]*.jsonl'))}
    if not o['rounds_present']:
        return o
    last = max(o['rounds_present'])
    rows = rd(f'{d}/found_{last}.jsonl')
    first_round, first_any = {}, {}
    distinct = collections.defaultdict(set)
    allp = []
    unknown = 0
    for x in rows:
        if x['name'] not in STRAT:
            unknown += 1; continue
        c = classify(x['proof'])
        n = normalise(x['proof'])
        first_any[x['name']] = min(first_any.get(x['name'], 99), x['round'])
        if c and c['reductio']:
            first_round[x['name']] = min(first_round.get(x['name'], 99), x['round'])
        distinct[x['name']].add(n)
        allp.append((x['prompt'], x['proof'], x['name']))
    o['unknown_names'] = unknown
    o['raw_records'] = len(rows)
    o['distinct_norm_proofs'] = sum(len(v) for v in distinct.values())
    o['acquired_by_round'] = {r: sum(1 for v in first_round.values() if v <= r) for r in range(min(o['rounds_present']), last + 1)}
    o['solved_any_by_round'] = {r: sum(1 for v in first_any.values() if v <= r) for r in range(min(o['rounds_present']), last + 1)}
    o['acquired'] = len(first_round)
    o['solved_any'] = len(first_any)
    o['patfree_only_targets'] = sorted(set(first_any) - set(first_round))
    o['acquired_by_stratum'] = {s: sum(1 for n in first_round if STRAT[n] == s) for s in (7, 8, 9, 10)}
    o['ignition_round'] = next((r for r, v in sorted(o['acquired_by_round'].items()) if v >= 6), None)
    o['acquired_names'] = sorted(first_round)
    # consistency: found_r is a prefix-closed cumulative file (found_r subset of found_last, rounds tagged <= r)
    bad = 0
    for r in o['rounds_present']:
        rr = rd(f'{d}/found_{r}.jsonl')
        bad += sum(1 for x in rr if x['round'] > r)
        if len(rr) != sum(1 for x in rows if x['round'] <= r):
            bad += 1
    o['cumulative_inconsistencies'] = bad
    # prompts in found match the target file
    o['prompt_mismatch'] = sum(1 for pr, p, n in allp if PROMPT[n] != pr)
    samp = allp if len(allp) <= 400 else rng.sample(allp, 400)
    o['reverified'] = len(samp); o['reverify_fail'] = sum(1 for pr, p, n in samp if not verify(pr, p))
    # did the arm ever train? (mix files / round json)
    rj = [json.load(open(f)) for f in sorted(glob.glob(f'{d}/round_*.json'), key=lambda f: int(re.search(r'round_(\d+)', f).group(1)))]
    o['mix_rl_records'] = [x.get('mix_rl_records') for x in rj]
    o['ckpts'] = [x.get('ckpt') for x in rj]
    o['args'] = json.load(open(f'{d}/args.json'))
    o['heldout_greedy_r_last'] = rj[-1]['heldout_greedy'].get('rate') if rj and isinstance(rj[-1].get('heldout_greedy'), dict) else None
    # transfer pool: acquisition on the 150 transfer theorems (cumulative)
    ft = f'{d}/found_transfer_{last}.jsonl'
    if os.path.exists(ft):
        tr = rd(ft)
        o['transfer_solved_any'] = len({x['name'] for x in tr})
        o['transfer_strict'] = len({x['name'] for x in tr if (classify(x['proof']) or {}).get('reductio')})
    return o


tags = sorted({re.search(r'stage1_(.+)\.done', f).group(1) for f in glob.glob(f'{A}/stage1_*.done')})
for tag in tags:
    print(tag, flush=True)
    o = {'stage1': stage1(tag)}
    if os.path.exists(f'{A}/cov_{tag}_pre.s0.jsonl'):
        o['pre'] = cov(f'{A}/cov_{tag}_pre.s0.jsonl')
    for kind in ('ei', 'frozen'):
        if os.path.isdir(f'{A}/{kind}_{tag}'):
            o[kind] = arm(f'{A}/{kind}_{tag}')
    fn = f'{A}/cov_{tag}_b10k.s0.jsonl'
    if os.path.exists(fn):
        o['b10k'] = cov(fn)
    if 'ei' in o and o['ei'].get('acquired') is not None:
        acq = set(o['ei']['acquired_names'])
        acqf = f'{ROOT}/data/r3_4a/acq_{tag}.jsonl'
        o['acq_file_matches'] = (sorted(x['name'] for x in rd(acqf)) == sorted(acq)) if os.path.exists(acqf) else None
        if acq:
            if 'b10k' in o:
                covered = set(o['b10k']['names'])
                reach = set(o['b10k']['names_hit'])
                pre_reach = set(o['pre']['names_hit'])
                o['ei_only'] = {'acquired': len(acq), 'b10k_covers_acquired': acq <= covered, 'missing_from_b10k': len(acq - covered),
                                'base_reach_1e4': len(acq & reach), 'ei_only_1e4': len(acq - reach),
                                'frac_1e4': len(acq - reach) / len(acq),
                                'ei_only_1e4_or_pre2000': len(acq - reach - pre_reach),
                                'frac_12k': len(acq - reach - pre_reach) / len(acq),
                                'ei_only_by_stratum': {s: [sum(1 for n in acq - reach if STRAT[n] == s), sum(1 for n in acq if STRAT[n] == s)] for s in (7, 8, 9, 10)}}
            else:
                o['ei_only'] = {'acquired': len(acq), 'b10k': 'MISSING'}
    res[tag] = o

for x in sorted(glob.glob(f'{A}/x_ei_*')):
    if os.path.isdir(x):
        print(x, flush=True)
        res[os.path.basename(x)] = {'ei': arm(x)}

for o in res.values():          # names lists are bulky; keep acquired names only
    for k in ('pre', 'b10k'):
        if k in o:
            o[k].pop('names', None)
json.dump(res, open(OUT, 'w'), indent=1, default=str)
print('wrote', OUT)
