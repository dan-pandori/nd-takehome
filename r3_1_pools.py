#!/usr/bin/env python3
"""round3-run1 pools (data/r3_1/): depth-3 required@8 targets, depth-3 neighbours, reductio required, reductio neighbours.

  python r3_1_pools.py d3cands            # candidates for the depth-3 required@8 pool -> data/r3_1/depth3_cands.jsonl (VPS)
  # on a pod:  minlen.py --in depth3_cands.jsonl --out depth3_cands_md2b8.jsonl --max_depth 2 --bound 8 --time 20
  python r3_1_pools.py d3select           # known 142 + newly labelled required -> depth3_req_pre.jsonl (for the bound-10 pass)
  # on a pod:  minlen.py --in depth3_req_pre.jsonl --out depth3_req_md2b10.jsonl --max_depth 2 --bound 10 --time 40
  python r3_1_pools.py d3build            # -> depth3_req.jsonl (300), depth3_req_transfer.jsonl (100), depth3_nb.jsonl (300), depth3_mix.jsonl (600)
  python r3_1_pools.py rncands            # reductio-neighbour candidates: pool_long_minlen (167) + generated concl_nn shards
  # on a pod:  minlen.py --bound 8 (unrestricted), minlen.py --forbid DN --bound 10 --time 40, intuit.py
  python r3_1_pools.py rnbuild            # -> reductio_nb.jsonl (300), reductio_req.jsonl (300, copy of p2 with stratum), reductio_mix.jsonl
  python r3_1_pools.py check              # class-disjointness of every pool vs training sets / held-out / val-36; summary json
  python r3_1_pools.py handcheck          # print 10 required@8 depth-3 targets (depth-3 proof + 9-line alternative) and 10 neighbours per pattern

Every record: name, thm, key, prompt, n_lines (= unrestricted min_lines_ub), stratum (required | neighbour), oracle fields.
expert_iter.py ignores `stratum`.
"""
import argparse, json, os, sys, random, collections, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import canon_key
from patterns import classify
from nd_verify import verify_text

D = 'data/r3_1'
P2 = 'data/p2'
TRAIN = {'depth3': f'{P2}/train_depth3_f0_a1.jsonl', 'reductio': f'{P2}/train_reductio_f0.jsonl'}


def read(fn):
    return [json.loads(l) for l in open(fn) if l.strip()]


def write(fn, recs):
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    with open(fn, 'w') as f:
        for r in recs:
            f.write(json.dumps(r) + '\n')
    print(fn, len(recs))


def key_of(r):
    return r.get('key') or canon_key(r['thm'].strip())


def excluded_keys(train_files):
    """Renaming-class keys of the training sets, both held-out sets, validation-36 and every earlier p2 target/transfer pool
    (the earlier pools are excluded from NEW candidates only; the 142 known required targets come from targets_depth3)."""
    ks = set()
    for fn in train_files + [f'{P2}/heldout.jsonl', 'data/heldout.jsonl']:
        for r in read(fn):
            ks.add(key_of(r))
    ks |= {canon_key(json.loads(l)['thm'].strip()) for l in open('targets/validation_36.jsonl')}
    return ks


def d3cands(a):
    rng = random.Random(0)
    md2 = {r['name']: r for r in read(f'{P2}/targets_depth3_maxdepth2.jsonl')}
    d3 = {r['name']: r for r in read(f'{P2}/targets_depth3.jsonl')}
    known = [n for n, r in md2.items() if r['min_lines_ub'] is None and not r['timeout'] and d3[n]['min_lines_ub'] in (7, 8)]
    print('known required@8 in targets_depth3:', len(known))
    excl = excluded_keys([TRAIN['depth3'], TRAIN['reductio']])
    for fn in (f'{P2}/targets_depth3.jsonl', f'{P2}/transfer_depth3.jsonl', f'{P2}/targets_reductio_req.jsonl', f'{P2}/transfer_reductio_req.jsonl'):
        excl |= {key_of(r) for r in read(fn)}
    cands, seen = [], set()
    for r in read(f'{P2}/pool_long_minlen.jsonl'):
        if r['min_lines_ub'] not in (7, 8):
            continue
        k = canon_key(r['thm'].strip())
        if k in seen or k in excl:
            continue
        seen.add(k)
        cl = classify(r['proof'])
        if not (cl and cl['depth3']):
            continue
        cands.append({'name': r['name'], 'thm': r['thm'], 'key': k, 'prompt': r['prompt'], 'n_lines': r['min_lines_ub'],
                      'min_lines_ub': r['min_lines_ub'], 'oracle_proof': r['proof'], 'src': 'pool_long'})
    print('new candidates (depth-3 minlen proof at 7-8 lines, class-disjoint):', len(cands))
    rng.shuffle(cands)
    cands = cands[:a.n]
    write(f'{D}/depth3_cands.jsonl', cands)
    kn = [{'name': n, 'thm': d3[n]['thm'], 'key': d3[n]['key'], 'prompt': d3[n]['prompt'], 'n_lines': d3[n]['min_lines_ub'],
           'min_lines_ub': d3[n]['min_lines_ub'], 'oracle_proof': d3[n]['gen_proof'], 'src': 'targets_depth3',
           'r8_min_lines_ub': None, 'r8_timeout': False} for n in known]
    write(f'{D}/depth3_known_req.jsonl', kn)


def d3select(a):
    kn = read(f'{D}/depth3_known_req.jsonl')
    lab = {r['name']: r for r in read(f'{D}/depth3_cands_md2b8.jsonl')}
    new = []
    for r in read(f'{D}/depth3_cands.jsonl'):
        m = lab.get(r['name'])
        if m is None:
            continue
        r['r8_min_lines_ub'], r['r8_timeout'] = m['min_lines_ub'], m['timeout']
        if m['min_lines_ub'] is None and not m['timeout']:
            new.append(r)
    print('labelled', len(lab), 'required@8 among new candidates:', len(new), 'timeouts:', sum(m['timeout'] for m in lab.values()))
    # the 7-8-line depth-3 proof must verify and have the pattern (oracle consistency)
    pre = []
    for r in kn + new:
        ok, reason, nl = verify_text(r['prompt'] + ' ' + r['oracle_proof'])
        cl = classify(r['oracle_proof'])
        assert ok and cl['depth3'] and nl == r['min_lines_ub'], (r['name'], reason, nl)
        pre.append(r)
    write(f'{D}/depth3_req_pre.jsonl', pre)


def d3build(a):
    rng = random.Random(0)
    pre = read(f'{D}/depth3_req_pre.jsonl')
    lab = {r['name']: r for r in read(f'{D}/depth3_req_md2b10.jsonl')}
    for r in pre:
        m = lab[r['name']]
        r['r10_min_lines_ub'], r['r10_timeout'], r['r10_proof'] = m['min_lines_ub'], m['timeout'], m['proof']
        if m['proof']:
            ok, _, nl = verify_text(r['prompt'] + ' ' + m['proof'])
            cl = classify(m['proof'])
            assert ok and not cl['depth3'] and nl == m['min_lines_ub'], r['name']
    hist = collections.Counter((r['r10_min_lines_ub'], r['r10_timeout']) for r in pre)
    print('bound-10 depth<=2 alternative (len, timeout):', dict(hist))
    rng.shuffle(pre)
    req, tr = pre[:a.n_req], pre[a.n_req:a.n_req + a.n_transfer]
    for i, r in enumerate(req):
        r['stratum'] = 'required'; r['name'] = f'd3req_{i}'
    for i, r in enumerate(tr):
        r['stratum'] = 'required'; r['name'] = f'd3req_transfer_{i}'
    # neighbours: depth-<=2 proof at 7-8 lines (targets_depth3_maxdepth2), disjoint from the required set by key
    md2 = {r['name']: r for r in read(f'{P2}/targets_depth3_maxdepth2.jsonl')}
    d3 = {r['name']: r for r in read(f'{P2}/targets_depth3.jsonl')}
    used = {r['key'] for r in req + tr}
    nb = []
    for n, m in md2.items():
        if m['min_lines_ub'] in (7, 8) and not m['timeout'] and d3[n]['key'] not in used:
            ok, _, nl = verify_text(m['prompt'] + ' ' + m['proof'])
            cl = classify(m['proof'])
            assert ok and not cl['depth3'] and nl == m['min_lines_ub'], n
            nb.append({'name': n, 'thm': m['thm'], 'key': d3[n]['key'], 'prompt': m['prompt'], 'n_lines': d3[n]['min_lines_ub'],
                       'min_lines_ub': d3[n]['min_lines_ub'], 'r8_min_lines_ub': m['min_lines_ub'], 'r8_timeout': m['timeout'],
                       'nb_proof': m['proof'], 'oracle_proof': d3[n]['gen_proof'], 'src': 'targets_depth3', 'stratum': 'neighbour'})
    print('neighbour candidates:', len(nb), collections.Counter((r['n_lines'], r['r8_min_lines_ub']) for r in nb))
    rng.shuffle(nb)
    nb = nb[:a.n_nb]
    for i, r in enumerate(nb):
        r['name'] = f'd3nb_{i}'
    write(f'{D}/depth3_req.jsonl', req)
    write(f'{D}/depth3_req_transfer.jsonl', tr)
    write(f'{D}/depth3_nb.jsonl', nb)
    write(f'{D}/depth3_mix.jsonl', req + nb)


def rncands(a):
    """Reductio-neighbour candidates: conclusion ( ~ ( ~ X ) ). From pool_long_minlen (unrestricted min 7-8 already known)
    and from generated concl_nn shards (data/r3_1/raw_nn.w*.jsonl, unrestricted min length still to be labelled)."""
    excl = excluded_keys([TRAIN['depth3'], TRAIN['reductio']])
    for fn in (f'{P2}/targets_depth3.jsonl', f'{P2}/transfer_depth3.jsonl', f'{P2}/targets_reductio_req.jsonl', f'{P2}/transfer_reductio_req.jsonl'):
        excl |= {key_of(r) for r in read(fn)}
    seen, out = set(), []
    for r in read(f'{P2}/pool_long_minlen.jsonl'):
        if r['min_lines_ub'] not in (7, 8) or not r['thm'].split('|-')[1].strip().startswith('( ~ ( ~'):
            continue
        k = canon_key(r['thm'].strip())
        if k in seen or k in excl:
            continue
        seen.add(k)
        out.append({'name': f'rn_pl_{len(out)}', 'thm': r['thm'], 'key': k, 'prompt': r['prompt'], 'n_lines': r['min_lines_ub'],
                    'min_lines_ub': r['min_lines_ub'], 'u_proof': r['proof'], 'src': 'pool_long'})
    n_pl = len(out)
    gen = []
    for fn in sorted(glob.glob(f'{D}/raw_nn.w*.jsonl')):
        for r in read(fn):
            k = r['key']
            if k in seen or k in excl:
                continue
            seen.add(k)
            gen.append({'name': f'rn_gen_{len(gen)}', 'thm': r['thm'], 'key': k, 'prompt': r['prompt'], 'gen_lines': r['n_lines'],
                        'gen_proof': r['proof'], 'src': 'gen_nn'})
    print('pool_long candidates (min 7-8):', n_pl, '; generated candidates (unlabelled):', len(gen))
    write(f'{D}/reductio_nb_cands_pl.jsonl', out)
    write(f'{D}/reductio_nb_cands_gen.jsonl', gen)


def rnbuild(a):
    rng = random.Random(0)
    pl = read(f'{D}/reductio_nb_cands_pl.jsonl')
    gen = read(f'{D}/reductio_nb_cands_gen.jsonl')
    ulab = {r['name']: r for r in read(f'{D}/reductio_nb_gen_u8.jsonl')} if os.path.exists(f'{D}/reductio_nb_gen_u8.jsonl') else {}
    for r in gen:
        m = ulab.get(r['name'])
        if m and m['min_lines_ub'] in (7, 8):
            r['min_lines_ub'] = m['min_lines_ub']; r['n_lines'] = m['min_lines_ub']; r['u_proof'] = m['proof']
    cands = pl + [r for r in gen if r.get('min_lines_ub') in (7, 8)]
    print('candidates with unrestricted min 7-8:', len(cands), '(pool_long', len(pl), ')')
    flab = {r['name']: r for r in read(f'{D}/reductio_nb_cands_nodn.jsonl')}
    ilab = {r['name']: r for r in read(f'{D}/reductio_nb_cands_intuit.jsonl')}
    keep = []
    for r in cands:
        f, it = flab.get(r['name']), ilab.get(r['name'])
        if f is None or it is None:
            continue
        r['nodn_min_lines_ub'], r['nodn_timeout'], r['nodn_proof'], r['intuit_provable'] = f['min_lines_ub'], f['timeout'], f['proof'], it['intuit_provable']
        if f['min_lines_ub'] is None or not it['intuit_provable']:
            continue
        ok, _, nl = verify_text(r['prompt'] + ' ' + f['proof'])
        cl = classify(f['proof'])
        assert ok and not cl['reductio'] and 'DN' not in f['proof'].split() and nl == f['min_lines_ub'], r['name']
        r['stratum'] = 'neighbour'
        keep.append(r)
    print('neighbours (no-DN proof <= 10 found, intuitionistically provable):', len(keep),
          collections.Counter((r['min_lines_ub'], r['nodn_min_lines_ub']) for r in keep))
    rng.shuffle(keep)
    keep = keep[:a.n_nb]
    for i, r in enumerate(keep):
        r['name'] = f'rnb_{i}'
    req = read(f'{P2}/targets_reductio_req.jsonl')
    tr = read(f'{P2}/transfer_reductio_req.jsonl')
    for r in req + tr:
        r['stratum'] = 'required'
    write(f'{D}/reductio_req.jsonl', req)
    write(f'{D}/reductio_req_transfer.jsonl', tr)
    write(f'{D}/reductio_nb.jsonl', keep)
    write(f'{D}/reductio_mix.jsonl', req + keep)


def check(a):
    pools = ['depth3_req', 'depth3_req_transfer', 'depth3_nb', 'reductio_req', 'reductio_req_transfer', 'reductio_nb']
    excl = {}
    for tag, fn in [('train_depth3_f0_a1', TRAIN['depth3']), ('train_reductio_f0', TRAIN['reductio']), ('heldout_p2', f'{P2}/heldout.jsonl'),
                    ('heldout', 'data/heldout.jsonl')]:
        excl[tag] = {key_of(r) for r in read(fn)}
    excl['val36'] = {canon_key(json.loads(l)['thm'].strip()) for l in open('targets/validation_36.jsonl')}
    summ = {}
    keys = {}
    for p in pools:
        fn = f'{D}/{p}.jsonl'
        if not os.path.exists(fn):
            print('missing', fn); continue
        rs = read(fn)
        ks = {r['key'] for r in rs}
        assert len(ks) == len(rs), f'{p}: duplicate classes'
        for r in rs:
            assert r['key'] == canon_key(r['thm'].strip())
        keys[p] = ks
        summ[p] = {'n': len(rs), 'overlap': {t: len(ks & e) for t, e in excl.items()},
                   'by_len': dict(sorted(collections.Counter(r['n_lines'] for r in rs).items())),
                   'stratum': dict(collections.Counter(r['stratum'] for r in rs))}
        if p.startswith('depth3_req'):
            summ[p]['r10_alt'] = dict(sorted(collections.Counter(str(r.get('r10_min_lines_ub')) for r in rs).items()))
        if p == 'reductio_nb':
            summ[p]['nodn_len'] = dict(sorted(collections.Counter(r['nodn_min_lines_ub'] for r in rs).items()))
        print(p, json.dumps(summ[p]))
    for i, p in enumerate(pools):
        for q in pools[i + 1:]:
            if p in keys and q in keys:
                o = len(keys[p] & keys[q])
                summ.setdefault('pool_overlap', {})[f'{p}|{q}'] = o
                assert o == 0, (p, q, o)
    os.makedirs('artifacts/r3_1', exist_ok=True)
    json.dump(summ, open('artifacts/r3_1/pools_summary.json', 'w'), indent=1)
    print('pools OK; artifacts/r3_1/pools_summary.json')


def handcheck(a):
    rng = random.Random(1)
    for p, fields in [('depth3_req', ('oracle_proof', 'r10_proof')), ('depth3_nb', ('nb_proof', 'oracle_proof')), ('reductio_nb', ('nodn_proof', 'u_proof'))]:
        rs = read(f'{D}/{p}.jsonl')
        for r in rng.sample(rs, 10):
            print(f'\n## {p} {r["name"]}  min {r["min_lines_ub"]}  ' + '  '.join(f'{k}={r.get(k)}' for k in ('r8_min_lines_ub', 'r10_min_lines_ub', 'nodn_min_lines_ub', 'intuit_provable') if k in r))
            print('   ', r['thm'])
            for f in fields:
                print(f'   [{f}] ', r.get(f))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd')
    ap.add_argument('--n', type=int, default=1200)
    ap.add_argument('--n_req', type=int, default=300)
    ap.add_argument('--n_transfer', type=int, default=100)
    ap.add_argument('--n_nb', type=int, default=300)
    a = ap.parse_args()
    globals()[a.cmd](a)
