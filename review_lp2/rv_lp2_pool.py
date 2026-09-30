#!/usr/bin/env python3
"""Reviewer (long-pool-2), phase 1: pool recount from the raw stage files, with my own renaming-class key.

  python3 rv/rv_lp2_pool.py funnel      # stage fates per chunk, duplication across chunks, stage E/F, vs pool files
  python3 rv/rv_lp2_pool.py disjoint    # renaming-class disjointness of the 91 pool theorems vs every data file

Own code: key() renames atoms in first-occurrence order (premises in order, then goal); okey() takes the min over all
premise orders. Neither imports gen / lpool2_assemble.
"""
import json, os, re, sys, glob, gzip, itertools, collections

R = os.path.expanduser('~/review/long-pool-2')
LP2 = f'{R}/rv/lp2'
ATOM = re.compile(r'\b([A-EG-Z])\b')      # single capitals except F (falsum)


def split(prompt):
    body = prompt.strip()
    if body.startswith('THM '):
        body = body[4:]
    if body.endswith(' PRF'):
        body = body[:-4]
    sep = ' SEQ ' if ' SEQ ' in body else ' |- '
    if body.startswith('SEQ ') or body.startswith('|- '):
        return [], body.split(' ', 1)[1].strip()
    prem, goal = body.split(sep, 1)
    ps = [p.strip() for p in prem.split(' , ')] if prem.strip() else []
    return ps, goal.strip()


def rename(parts):
    m = {}
    out = []
    for s in parts:
        out.append(ATOM.sub(lambda x: m.setdefault(x.group(1), 'abcdefghijklmnop'[len(m)]), s))
    return out


def key(prompt):
    ps, g = split(prompt)
    r = rename(ps + [g])
    return ' , '.join(r[:-1]) + ' => ' + r[-1]


def okey(prompt):
    ps, g = split(prompt)
    best = None
    for perm in itertools.permutations(ps):
        r = rename(list(perm) + [g])
        k = ' , '.join(sorted(r[:-1])) + ' => ' + r[-1]    # premise set after this renaming
        if best is None or k < best:
            best = k
    return best


def skel(s):
    return ATOM.sub('A', s)


def rows(fn):
    op = gzip.open if fn.endswith('.gz') else open
    with op(fn, 'rt') as f:
        for l in f:
            if l.strip():
                yield json.loads(l)


def funnel():
    chunks = sorted({os.path.basename(f).split('_')[0] for f in glob.glob(f'{LP2}/[bcde][0-9]_ml10.jsonl')})
    tot = collections.Counter()
    first = {}                 # key -> first (chunk, name)
    occ = collections.Counter()
    lb17 = collections.defaultdict(list)   # key -> [(chunk, name, rowE)]
    per = {}
    for c in chunks:
        st = {b: {r['name']: r for r in rows(f'{LP2}/{c}_ml{b}.jsonl')} if os.path.exists(f'{LP2}/{c}_ml{b}.jsonl') else {}
              for b in (10, 12, 14, 16, 17)}
        cnt = collections.Counter()
        for n, r in st[10].items():
            k = key(r['prompt']); occ[k] += 1
            first.setdefault(k, (c, n))
            fate = None
            for b in (10, 12, 14, 16):
                x = st[b].get(n)
                if x is None:
                    fate = f'missing_{b}'; break
                if x.get('timeout') or x.get('error'):
                    fate = f'timeout_{b}'; break
                if x['min_lines_ub'] is not None:
                    fate = f'le{b}'; break
                    # min_lines_ub under bound b: some proof of <= b lines
            fate = fate or 'lb17'
            cnt[fate] += 1
            if fate == 'lb17':
                lb17[k].append((c, n, st[17].get(n), st[16].get(n)))
        per[c] = dict(cnt, generated=len(st[10]))
        tot.update(cnt); tot['generated'] += len(st[10])
    print('chunks', len(chunks), chunks)
    print('total fates', dict(sorted(tot.items())))
    uniq = len(occ)
    print(f'distinct renaming classes among generated: {uniq} / {tot["generated"]} = {uniq / tot["generated"]:.3f}')
    by_fam = collections.defaultdict(lambda: [0, set()])
    for c in chunks:
        pass
    # duplication per family (b/c/d/e) and across families
    fam_keys = collections.defaultdict(set); fam_n = collections.Counter()
    for c in chunks:
        for r in rows(f'{LP2}/{c}_ml10.jsonl'):
            fam_keys[c[0]].add(key(r['prompt'])); fam_n[c[0]] += 1
    for f in sorted(fam_keys):
        print(f'  family {f}: {fam_n[f]} generated, {len(fam_keys[f])} distinct ({len(fam_keys[f]) / fam_n[f]:.3f})')
    inter = [(a, b, len(fam_keys[a] & fam_keys[b])) for a, b in itertools.combinations(sorted(fam_keys), 2)]
    print('  cross-family shared classes', inter)
    nlb = sum(len(v) for v in lb17.values())
    print(f'lb17 records {nlb}, distinct classes {len(lb17)}')
    # consistency of stage E across duplicate copies
    E = collections.Counter(); incons = 0
    for k, v in lb17.items():
        outs = set()
        for c, n, e, d in v:
            o = 'missing' if e is None else 'timeout' if (e.get('timeout') or e.get('error')) else \
                ('exact17' if e['min_lines_ub'] == 17 else f'le{e["min_lines_ub"]}') if e['min_lines_ub'] is not None else 'ge18'
            outs.add(o)
        if len(outs - {'timeout', 'missing'}) > 1:
            incons += 1
        # first copy by sorted chunk-name (as a pool builder would keep one)
        E[tuple(sorted(outs))] += 1
    print('stage-E outcomes over duplicate copies (distinct lb17 classes):', dict(E), 'inconsistent', incons)
    # compare with the pool file
    pool = list(rows(f'{R}/data/ladder/transfer_long2.jsonl'))
    cal = list(rows(f'{R}/data/ladder/transfer_long2_calib.jsonl'))
    pk = {key(r['prompt']): r for r in pool}
    print('pool rows', len(pool), 'distinct keys', len(pk), 'pool keys subset of my lb17 classes:', set(pk) <= set(lb17),
          'lb17 classes not in pool:', len(set(lb17) - set(pk)))
    ge17 = list(rows(f'{R}/data/ladder/transfer_long_ge17.jsonl'))
    print('calib == transfer_long_ge17 by key:', {key(r['prompt']) for r in cal} == {key(r['prompt']) for r in ge17},
          'calib ∩ pool:', len({key(r['prompt']) for r in cal} & set(pk)))
    # stage E / F labels vs raw
    F = {}
    for fn in sorted(glob.glob(f'{LP2}/F*_ml18.jsonl')):
        for x in rows(fn):
            F.setdefault(x['name'], x)
    calE = {x['name']: x for x in rows(f'{LP2}/calib_ml17.jsonl')}
    mism = []
    strat = collections.Counter(); cstrat = collections.Counter()
    for r in pool + cal:
        raw = r['name'][4:] if r['name'].startswith('lp2_') else r['name']
        if r in pool:
            copies = lb17[key(r['prompt'])]
            e = next((e for c, n, e, d in copies if n == raw), None)
        else:
            e = calE.get(raw)
        eo = 'missing' if e is None else 'timeout' if (e.get('timeout') or e.get('error')) else \
            ('exact17' if e['min_lines_ub'] == 17 else 'ERR') if e['min_lines_ub'] is not None else 'ge18'
        f = F.get(raw)
        fo = None
        if eo == 'ge18':
            fo = 'not_run' if f is None else 'timeout' if (f.get('timeout') or f.get('error')) else \
                ('exact18' if f['min_lines_ub'] == 18 else 'ERR') if f['min_lines_ub'] is not None else 'ge19'
        s = {'exact17': '17', 'timeout': '>=17', 'missing': '>=17'}.get(eo) or {'exact18': '18', 'ge19': '>=19'}.get(fo, '>=18')
        (strat if r in pool else cstrat)[s] += 1
        if s != r['stratum'] or eo != r['stageE']:
            mism.append((r['name'], eo, fo, s, r['stageE'], r['stratum']))
        if r in pool and eo == 'exact17' and not r['ub_proof'] == e['proof']:
            mism.append((r['name'], 'ub_proof differs'))
    print('my strata new', dict(strat), 'calib', dict(cstrat), 'mismatches', mism)
    # upper bound: my own pruning (dependency closure) of the generator proof
    def prune_len(p):
        ls = [t.split() for t in p.split(' ; ') if t.strip() and t.strip() != 'QED']
        cites = {t[0]: [w for w in t[t.index(':') + 1:] if re.fullmatch(r'N\d+', w)] for t in ls}
        seen, st = set(), [ls[-1][0]]
        while st:
            i = st.pop()
            if i not in seen:
                seen.add(i); st += cites.get(i, [])
        return len(seen), len(ls)
    ubm = []
    for r in pool + cal:
        pl, gl = prune_len(r['gen_proof'])
        ub = min(pl, 17 if r['stageE'] == 'exact17' else 18 if r.get('stageF') == 'exact18' else 999)
        if ub != r['L_ub'] or pl != r['construction_pruned']:
            ubm.append((r['name'], pl, gl, r['construction_pruned'], r['L_ub']))
    print('upper-bound mismatches', ubm)
    cons = sorted(prune_len(r['gen_proof'])[0] for r in pool)
    print('new-pool construction lengths', cons)
    ccons = sorted(prune_len(r['gen_proof'])[0] for r in cal)
    print('calib construction lengths', ccons)
    # timings for the compute record: stage secs
    secs = collections.Counter()
    for c in chunks:
        for b in (10, 12, 14, 16, 17):
            fn = f'{LP2}/{c}_ml{b}.jsonl'
            if os.path.exists(fn):
                for x in rows(fn):
                    secs[b] += x.get('secs') or 0
    print('minlen seconds by bound (sum over chunk records):', {b: round(v) for b, v in secs.items()})
    wasted = collections.Counter()
    for c in chunks:
        pass
    json.dump({'lb17_classes': {k: [(c, n) for c, n, e, d in v] for k, v in lb17.items()}}, open(f'{R}/rv/lb17_classes.json', 'w'), indent=0)


def disjoint():
    pool = list(rows(f'{R}/data/ladder/transfer_long2.jsonl')) + list(rows(f'{R}/data/ladder/transfer_long2_calib.jsonl'))
    tk = {key(r['prompt']): r['name'] for r in pool}
    tok = {okey(r['prompt']): r['name'] for r in pool}
    tsk = {skel(split(r['prompt'])[1]) for r in pool}
    files = sorted(set(glob.glob(os.path.expanduser('~/nd-takehome/data/**/*.jsonl'), recursive=True) +
                       glob.glob(os.path.expanduser('~/nd-takehome/data/**/*.jsonl.gz'), recursive=True) +
                       glob.glob('/tmp/longpool/excl/*') + ['/tmp/longpool/pool_long.jsonl'] +
                       glob.glob(f'{R}/data/**/*.jsonl', recursive=True) + glob.glob(f'{R}/data/**/*.jsonl.gz', recursive=True)))
    if len(sys.argv) > 2:
        files = [f for f in files if f.startswith(sys.argv[2])]
    own = {os.path.realpath(f'{R}/data/ladder/transfer_long2.jsonl'), os.path.realpath(f'{R}/data/ladder/transfer_long2_calib.jsonl')}
    pr = re.compile(r'"(prompt|thm)": "([^"]*)"')
    tot = 0; hits = {}
    for fn in files:
        if os.path.realpath(fn) in own or fn.endswith('args.json'):
            continue
        op = gzip.open if fn.endswith('.gz') else open
        n = 0; h = set(); ho = set()
        with op(fn, 'rt') as f:
            for l in f:
                m = pr.search(l)
                if not m:
                    continue
                n += 1
                p = m.group(2)
                try:
                    ps, g = split(p)
                except ValueError:
                    continue
                if skel(g) not in tsk:
                    continue
                k = key(p)
                if k in tk:
                    h.add(tk[k])
                if len(ps) <= 6:
                    ok = okey(p)
                    if ok in tok:
                        ho.add(tok[ok])
        tot += n
        if h or ho:
            hits[fn] = (sorted(h), sorted(ho))
        print(f'{n:>9} {len(h):>3} {len(ho):>3} {fn}', flush=True)
    print('files', len(files), 'records', tot)
    print('HITS', json.dumps(hits, indent=1))


if __name__ == '__main__':
    {'funnel': funnel, 'disjoint': disjoint}[sys.argv[1]]()
