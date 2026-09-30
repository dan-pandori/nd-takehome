#!/usr/bin/env python3
"""lit-measures M3: mode shares round by round (preregistration/lit-measures.md, section M3). Stdlib only.

Input: --root holding bucket paths as in pod/lm/m3_files.txt, i.e. <root>/<run>/artifacts/<dir>/<ladder>/found_<last>.jsonl
(+ found_transfer_<last>.jsonl, args.json). found_<r>.jsonl is cumulative (every row carries the `round` it was first
found in; found_r is a superset of found_{r-1}, checked on noise-floor la_frozen_p3_s0 rounds 1-2), so the last round's
file gives every round: new proofs of round r = rows with round == r; all found proofs by round r = rows with round <= r.

Interpretations (the pre-registration leaves these open; written down here and in report.txt):
 * a "proof" is one row of found_<r>.jsonl (ladder_ei keeps distinct start-index-normalised proofs, up to several per
   theorem); box depth and rules are read from the `proof` field as written (not the pruned proof).
 * every family stores `proof` in the ND text format (`N1 A : PR ; N4 | S : AS ; ...`), including lean-format /
   lean-seed2 (Lean is only the judge) and the state-env families: box depth of a step = number of `|` tokens,
   rule = first token after ` : `. Rule mix = share of each rule over all steps (PR and AS lines included).
 * "the same share at round r" (separation) = share of depth>=3 proofs among all proofs found by round r (cumulative),
   matching the end-mode definition; the share among round-r new proofs is reported as a secondary variant.
 * pairwise agreement: a seed pair is excluded if its final shares tie; a round-r tie with a non-tied final counts 0.5.
 * E3.2 "moves monotonically": the per-round new-proof depth>=3 share is weakly monotone (all non-decreasing or all
   non-increasing, not constant) over rounds 1..last with >= 1 new proof; counted over ladders of headline arms that
   have >= 2 seeds; the cumulative share is reported alongside.
 * arms = (family, ladder name without the seed); `_s1rerun` = seed 1; noise-floor la_*_dsc_a1_s1 / la_*_dsg_g1_s0 are
   the ds-composition / ds-generator ladders of that arm and seed (identical args but init/seed/outdir), so they are
   counted there. Ladders stopped before their family's last round, and ladders with 0 found proofs, are excluded.
"""
import argparse, collections, itertools, json, os, re, sys

HEADLINE = ['ladder-A', 'ds-composition', 'ds-generator', 'lean-format', 'lean-seed2', 'support-curves',
            'state-env', 'state-frontier', 'state-cap12', 'round3-run4b']
DBINS = ['d0', 'd1', 'd2', 'd3p']
SEED_RX = re.compile(r'^(.*?)_s(\d+)(rerun|[ab])?((?:_[A-Za-z0-9]+)?)$')


def classify(run, name):
    """-> (family, arm, seed, role, note) or None. role: headline | extra | frozen | reference-only."""
    fam = run
    m = re.match(r'^la_(T1|frozen)_(dsc|dsg)_(.*)$', name) if run == 'noise-floor' else None
    note = ''
    if m:
        fam = {'dsc': 'ds-composition', 'dsg': 'ds-generator'}[m.group(2)]
        note = f'from noise-floor/{name}'
        name = f'la_{m.group(1)}_{m.group(3)}'
    s = SEED_RX.match(name)
    if not s:
        return None
    arm = s.group(1) + s.group(4)
    seed = int(s.group(2))
    if s.group(3):
        note = (note + '; ' if note else '') + f'seed suffix {s.group(3)!r} treated as s{seed}'
    frozen = name.startswith('la_frozen_') or arm.endswith('_frozen')
    if frozen:
        role = 'frozen'
    elif fam in HEADLINE and (name.startswith('la_T1_') or (fam == 'round3-run4b' and name.startswith('ei_depth3_'))):
        role = 'headline'
    elif fam == 'ladder-A' and re.match(r'la_T[2-6]_', name):
        role = 'extra'
    else:
        role = 'other'
    return fam, arm, seed, role, note


def parse_nd(proof):
    """ND text -> (max box depth, [rules]) or None if unparseable."""
    rules, depth = [], 0
    for st in proof.split(' ; '):
        st = st.strip()
        if not st or st == 'QED':
            continue
        if ' : ' not in st:
            return None
        lhs, rhs = st.rsplit(' : ', 1)
        toks = lhs.split()
        if not toks or not toks[0].startswith('N'):
            return None
        d = 0
        for t in toks[1:]:
            if t == '|':
                d += 1
            else:
                break
        depth = max(depth, d)
        r = rhs.split()
        if not r:
            return None
        rules.append(r[0])
    if not rules:
        return None
    return depth, rules


def dbin(d):
    return DBINS[min(d, 3)]


def load_ladder(path):
    """-> {round: {'n','d0'..'d3p','rules':Counter,'steps'}}, n_rows, n_bad"""
    per = collections.defaultdict(lambda: {'n': 0, 'd0': 0, 'd1': 0, 'd2': 0, 'd3p': 0,
                                           'rules': collections.Counter(), 'steps': 0})
    rows = bad = 0
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            x = json.loads(line)
            rows += 1
            p = parse_nd(x.get('proof') or '')
            if p is None:
                bad += 1
                continue
            d, rl = p
            b = per[int(x['round'])]
            b['n'] += 1; b[dbin(d)] += 1
            b['rules'].update(rl); b['steps'] += len(rl)
    return per, rows, bad


def discover(root):
    out = []  # (run, relpath_dir, name, {'found': (r, path), 'found_transfer': ...})
    for dp, dn, fn in os.walk(root):
        fs = {}
        for f in fn:
            m = re.match(r'^(found|found_transfer)_(\d+)\.jsonl$', f)
            if m:
                r = int(m.group(2))
                if m.group(1) not in fs or r > fs[m.group(1)][0]:
                    fs[m.group(1)] = (r, os.path.join(dp, f))
        if 'found' in fs:
            rel = os.path.relpath(dp, root)
            out.append((rel.split(os.sep)[0], rel, os.path.basename(dp), fs))
    return sorted(out)


def sign(x):
    return (x > 1e-12) - (x < -1e-12)


def agreement(seeds_series, last, key):
    """seeds_series: {seed: {round: value}} -> {round: [agree, n_pairs, n_round_ties]}, n_final_ties"""
    res = {}; ftie = 0
    pairs = list(itertools.combinations(sorted(seeds_series), 2))
    for a, b in pairs:
        if sign(seeds_series[a][last] - seeds_series[b][last]) == 0:
            ftie += 1
    for r in range(1, last + 1):
        ag = n = t = 0
        for a, b in pairs:
            fs = sign(seeds_series[a][last] - seeds_series[b][last])
            if fs == 0:
                continue
            va, vb = seeds_series[a].get(r), seeds_series[b].get(r)
            if va is None or vb is None:
                continue
            rs = sign(va - vb); n += 1
            if rs == 0:
                ag += 0.5; t += 1
            elif rs == fs:
                ag += 1
        res[r] = [ag, n, t]
    return res, ftie


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    lad = []
    excluded = []
    for run, rel, name, fs in discover(a.root):
        c = classify(run, name)
        if c is None:
            excluded.append((rel, 'name has no _s<seed>')); continue
        fam, arm, seed, role, note = c
        if role == 'other':
            why = ('family not in the pre-registered M3 run list' if fam not in HEADLINE + ['noise-floor'] else
                   'not in the pre-registered arm set (la_T1_* / ei_depth3_* / la_frozen_*)')
            excluded.append((rel, why)); continue
        lad.append(dict(run=run, rel=rel, name=name, fam=fam, arm=arm, seed=seed, role=role, note=note, fs=fs))
    # truncation: last round below the family's max
    famlast = collections.defaultdict(int)
    for L in lad:
        famlast[L['fam']] = max(famlast[L['fam']], L['fs']['found'][0])
    keep = []
    for L in lad:
        if L['fs']['found'][0] < famlast[L['fam']]:
            excluded.append((L['rel'], f"stopped at round {L['fs']['found'][0]} < family last round {famlast[L['fam']]}"))
        else:
            keep.append(L)
    rules_all = collections.Counter()
    rows_tsv = []
    series = {'found': collections.defaultdict(dict), 'found_transfer': collections.defaultdict(dict)}  # (fam,arm,role)->seed->L
    bad_total = collections.Counter()
    ladders_out = []
    for L in keep:
        for pool in ('found', 'found_transfer'):
            if pool not in L['fs']:
                continue
            last, path = L['fs'][pool]
            per, nrows, bad = load_ladder(path)
            bad_total[(L['fam'], pool)] += bad
            if nrows - bad == 0:
                if pool == 'found':
                    excluded.append((L['rel'], f'0 parseable found proofs ({nrows} rows)'))
                continue
            rounds_seen = sorted(per)
            if pool == 'found' and rounds_seen and rounds_seen[-1] > last:
                excluded.append((L['rel'], f'rows with round > file round {last}')); continue
            cum = {'n': 0, 'd3p': 0}
            new_d3, cum_d3 = {}, {}
            for r in range(1, last + 1):
                b = per.get(r, {'n': 0, 'd0': 0, 'd1': 0, 'd2': 0, 'd3p': 0, 'rules': collections.Counter(), 'steps': 0})
                cum['n'] += b['n']; cum['d3p'] += b['d3p']
                rules_all.update(b['rules'])
                sh = {k: (b[k] / b['n'] if b['n'] else None) for k in DBINS}
                new_d3[r] = sh['d3p']
                cum_d3[r] = cum['d3p'] / cum['n'] if cum['n'] else None
                rows_tsv.append(dict(pool=pool, family=L['fam'], arm=L['arm'], role=L['role'], seed=L['seed'],
                                     ladder=L['rel'], round=r, n_new=b['n'], **{f'new_{k}': sh[k] for k in DBINS},
                                     cum_n=cum['n'], cum_d3p=cum_d3[r], steps=b['steps'],
                                     rules={k: v / b['steps'] for k, v in b['rules'].items()} if b['steps'] else {}))
            rec = dict(ladder=L['rel'], family=L['fam'], arm=L['arm'], seed=L['seed'], role=L['role'], note=L['note'],
                       pool=pool, last=last, rows=nrows, unparsed=bad, end_mode=cum_d3[last],
                       new_d3p=new_d3, cum_d3p=cum_d3)
            ladders_out.append(rec)
            series[pool][(L['fam'], L['arm'], L['role'])][L['seed']] = rec
    # arms with >= 2 seeds
    summary = {'interpretations': __doc__.split('Interpretations')[1].strip(), 'arms': [], 'excluded': excluded,
               'unparsed': {f'{k[0]}|{k[1]}': v for k, v in bad_total.items() if v}}
    arm_res = []
    for pool in ('found', 'found_transfer'):
        for (fam, arm, role), sd in sorted(series[pool].items()):
            if len(sd) < 2:
                if pool == 'found':
                    summary['excluded'].append((f'{fam}/{arm}', f'{role} arm with {len(sd)} usable seed(s) (need >= 2)'))
                continue
            last = min(v['last'] for v in sd.values())
            res = {}
            for key in ('cum_d3p', 'new_d3p'):
                ss = {s: {r: v[key][r] for r in range(1, last + 1) if v[key].get(r) is not None} for s, v in sd.items()}
                ss = {s: v for s, v in ss.items() if last in v}
                res[key] = agreement(ss, last, key)
            ranking = sorted(sd, key=lambda s: -sd[s]['end_mode'])
            arm_res.append(dict(pool=pool, family=fam, arm=arm, role=role, seeds=sorted(sd), last=last,
                                end_mode={s: sd[s]['end_mode'] for s in sorted(sd)}, ranking=ranking,
                                agree=res['cum_d3p'][0], final_ties=res['cum_d3p'][1],
                                agree_new=res['new_d3p'][0], final_ties_new=res['new_d3p'][1]))
    summary['arms'] = arm_res

    def pooled(pool, roles, fam=None, key='agree'):
        tot = collections.defaultdict(lambda: [0.0, 0, 0])
        for x in arm_res:
            if x['pool'] != pool or x['role'] not in roles or (fam and x['family'] != fam):
                continue
            for r, (ag, n, t) in x[key].items():
                tot[r][0] += ag; tot[r][1] += n; tot[r][2] += t
        return {r: dict(agree=v[0], pairs=v[1], round_ties=v[2], frac=(v[0] / v[1] if v[1] else None))
                for r, v in sorted(tot.items())}
    e31 = {}
    for pool in ('found', 'found_transfer'):
        e31[pool] = {'headline_pooled': pooled(pool, ('headline',)),
                     'headline_pooled_new_share': pooled(pool, ('headline',), key='agree_new'),
                     'per_family': {f: pooled(pool, ('headline',), f) for f in HEADLINE},
                     'frozen_reference': pooled(pool, ('frozen',)),
                     'extra_ladderA_T2_T6': pooled(pool, ('extra',))}
    r2 = e31['found']['headline_pooled'].get(2, {})
    fr = r2.get('frac')
    verdict = ('no pairs' if fr is None else 'supported (>= 75 %)' if fr >= 0.75 else
               'falsified (<= 60 %)' if fr <= 0.60 else 'neither (60-75 %)')
    summary['E3_1'] = e31
    summary['E3_1_verdict'] = dict(round=2, frac=fr, pairs=r2.get('pairs'), verdict=verdict)

    def mono(v):
        xs = [v[r] for r in sorted(v) if v[r] is not None]
        if len(xs) < 2:
            return None
        up = all(b >= a for a, b in zip(xs, xs[1:])); dn = all(b <= a for a, b in zip(xs, xs[1:]))
        return 'up' if up and not dn else 'down' if dn and not up else 'flat' if up and dn else None
    e32 = {}
    for role in ('headline', 'frozen', 'extra'):
        ls = [l for l in ladders_out if l['pool'] == 'found' and l['role'] == role and
              any(len(x['seeds']) >= 2 and x['family'] == l['family'] and x['arm'] == l['arm'] and x['pool'] == 'found'
                  for x in arm_res)]
        mn = [(l['ladder'], mono(l['new_d3p']), mono(l['cum_d3p'])) for l in ls]
        # 'flat' (share constant, e.g. always 0) does not "move" and is not counted as monotone
        e32[role] = dict(n_ladders=len(ls), monotone_new=sum(1 for _, m, _ in mn if m in ('up', 'down')),
                         monotone_new_dirs=dict(collections.Counter(m for _, m, _ in mn if m)),
                         monotone_cum=sum(1 for _, _, m in mn if m in ('up', 'down')), ladders=mn)
    summary['E3_2'] = e32
    summary['ladders'] = [{k: v for k, v in l.items()} for l in ladders_out]

    # per_round.tsv
    rl = [r for r, _ in rules_all.most_common()]
    base = ['pool', 'family', 'arm', 'role', 'seed', 'ladder', 'round', 'n_new'] + [f'new_{k}' for k in DBINS] + \
           ['cum_n', 'cum_d3p', 'steps']
    cols = base + [f'rule_{r}' for r in rl]
    fmt = lambda v: '' if v is None else (f'{v:.4f}' if isinstance(v, float) else str(v))
    with open(os.path.join(a.out, 'per_round.tsv'), 'w') as f:
        f.write('\t'.join(cols) + '\n')
        for row in rows_tsv:
            f.write('\t'.join([fmt(row[c]) for c in base] +
                              [fmt(row['rules'].get(r, 0.0)) for r in rl]) + '\n')
    summary['rules'] = dict(rules_all)
    with open(os.path.join(a.out, 'summary.json'), 'w') as f:
        json.dump(summary, f, indent=1, default=str)

    # report.txt
    L = []
    inc = collections.defaultdict(list)
    for x in arm_res:
        if x['pool'] == 'found':
            inc[x['role']].append(f"{x['family']}/{x['arm']} seeds {x['seeds']} (last round {x['last']})")
    L.append('M3 mode shares (lit-measures). Included arms (>= 2 usable seeds):')
    for role in ('headline', 'frozen', 'extra'):
        L.append(f'  [{role}] ' + ('; '.join(inc[role]) or 'none'))
    notes = sorted({(l['ladder'], l['note']) for l in ladders_out if l['note']})
    for lad_, n in notes:
        L.append(f'  note: {lad_}: {n}')
    L.append('Excluded:')
    for e, why in summary['excluded']:
        L.append(f'  {e}: {why}')
    if summary['unparsed']:
        L.append(f"Unparsed proof rows (family|pool: n): {summary['unparsed']}")
    L.append('')
    L.append(f"E3.1 (headline, cumulative depth>=3 share, pairwise agreement with the final ordering) round 2: "
             f"{fmt(fr)} over {r2.get('pairs')} pairs -> {verdict}")
    for pool in ('found', 'found_transfer'):
        L.append(f'E3.1 by round [{pool}] (agree/pairs, frac; ties count 0.5):')
        blocks = [('headline pooled', e31[pool]['headline_pooled']),
                  ('headline pooled, new-proof share', e31[pool]['headline_pooled_new_share'])] + \
                 [(f'  {f}', e31[pool]['per_family'][f]) for f in HEADLINE if e31[pool]['per_family'][f]] + \
                 [('frozen reference', e31[pool]['frozen_reference']), ('extra ladder-A T2-T6', e31[pool]['extra_ladderA_T2_T6'])]
        for lab, d in blocks:
            if not d:
                continue
            L.append(f'  {lab:36s} ' + ' '.join(f"r{r}:{v['agree']:g}/{v['pairs']}" + (f"({v['frac']:.2f})" if v['frac'] is not None else '')
                                                 for r, v in d.items()))
    L.append('')
    for role, v in e32.items():
        L.append(f"E3.2 [{role}] ladders with weakly monotone new-proof depth>=3 share: {v['monotone_new']}/{v['n_ladders']} "
                 f"{v['monotone_new_dirs']}; cumulative share monotone: {v['monotone_cum']}/{v['n_ladders']}")
    L.append('')
    L.append('End mode per seed (cumulative depth>=3 share at last round) and ranking:')
    for x in arm_res:
        if x['pool'] == 'found':
            L.append(f"  [{x['role']}] {x['family']}/{x['arm']}: " +
                     ', '.join(f"s{s}={x['end_mode'][s]:.4f}" for s in x['seeds']) + f"  rank {x['ranking']}" +
                     (f"  [{x['final_ties']} of {len(x['seeds']) * (len(x['seeds']) - 1) // 2} pairs tie at the end: no pairs]"
                      if x['final_ties'] else ''))
    L.append('')
    L.append('Rules seen (steps): ' + ', '.join(f'{r}={n}' for r, n in rules_all.most_common()))
    with open(os.path.join(a.out, 'report.txt'), 'w') as f:
        f.write('\n'.join(L) + '\n')
    print('\n'.join(L[:60]))


if __name__ == '__main__':
    main()
