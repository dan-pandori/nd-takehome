#!/usr/bin/env python3
"""long-pool-2: assemble data/ladder/transfer_long2.jsonl (interval labels above 16) and the calibration file.

  python3 lpool2_assemble.py --chunks b1 b2 c1 ... --excl_manifest artifacts/lpool2/excl_manifest.txt \
      --out data/ladder/transfer_long2.jsonl --calib_out data/ladder/transfer_long2_calib.jsonl

Per chunk (pod/lpool2/label.sh): stages A-D as long-pool (bounds 10/12/14/16); a timeout at any of them = unknown,
excluded and counted. No proof at bound 16 and no timeout = lower bound 17. Stage E (bound 17 / 1,800 s):
  proof of 17 lines found -> exact 17 (L_lb = L_ub = 17);  finished without proof -> L_lb 18;  timeout -> L_lb 17.
Upper bound L_ub = min(construction length after pruning, stage-E proof length). Pruning = dependency closure of the
generator's proof (own parser; nd_verify is not used). The pruned construction is written to `ub_proof` for the Lean check
(lean_check.py --check <out> --field ub_proof).
Renaming class = gen.canon_key over the prompt (premise order kept), as long-pool; a second, premise-order-invariant key
(premises sorted after renaming) is checked too and reported.
"""
import argparse, json, os, sys, gzip, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen import canon_key

HOME_REPO = os.path.expanduser('~/nd-takehome')


def pkey(prompt):
    return canon_key(prompt.replace('THM ', '', 1).replace(' PRF', '').strip())


def okey(prompt):
    """premise-order-invariant: canonicalise every premise order and keep the smallest key."""
    body = prompt.replace('THM ', '', 1).replace(' PRF', '').strip()
    prem, concl = body.split(' SEQ ')
    ps = [p.strip() for p in prem.split(' , ')] if prem.strip() else []
    return min(canon_key(' , '.join(sorted(ps, key=lambda p: canon_key(p))) + ' SEQ ' + concl.strip()),
               canon_key(' , '.join(sorted(ps)) + ' SEQ ' + concl.strip()))


def prune(body):
    lines = [l.split() for l in body.split(';') if l.strip() and l.strip() != 'QED']
    by = {t[0]: t[t.index(':') + 2:] for t in lines}
    keep, st = set(), [lines[-1][0]]
    while st:
        i = st.pop()
        if i in keep or i not in by:
            continue
        keep.add(i); st.extend(by[i])
    kept = [' '.join(t) for t in lines if t[0] in keep]
    # renumber N<i> -> N1.. in order so the pruned text is a well-formed proof
    ren = {t[0]: f'N{j + 1}' for j, t in enumerate([t for t in lines if t[0] in keep])}
    out = []
    for s in kept:
        out.append(' '.join(ren.get(w, w) if w.startswith('N') and w[1:].isdigit() else w for w in s.split()))
    return len(keep), ' ; '.join(out) + ' ; QED'


def opener(fn):
    if not os.path.exists(fn) and os.path.exists(os.path.join(HOME_REPO, fn)):
        fn = os.path.join(HOME_REPO, fn)
    return gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)


def read_stage(fn):
    return {json.loads(l)['name']: json.loads(l) for l in open(fn)} if os.path.exists(fn) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--chunks', nargs='+', required=True); ap.add_argument('--dir', default='data/lp2')
    ap.add_argument('--excl_manifest', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--calib_in', default='data/ladder/transfer_long_ge17.jsonl')
    ap.add_argument('--calib_out', required=True)
    a = ap.parse_args()
    import record as ndrec; ndrec.save_config(vars(a), a.out)
    st = collections.Counter(); cands = {}
    for c in a.chunks:
        src = [json.loads(l) for l in open(f'{a.dir}/{c}.jsonl')]
        st[f'{c}:generated'] = len(src); st['generated'] += len(src)
        stages = {b: read_stage(f'{a.dir}/{c}_ml{b}.jsonl') for b in (10, 12, 14, 16, 17)}
        if stages[17] is None:
            st[f'{c}:stage_E_missing'] += 1; print(f'{c}: stage E not run, skipped', file=sys.stderr); continue
        for r in src:
            n = r['name']; fate = None
            for b in (10, 12, 14, 16):
                x = (stages[b] or {}).get(n)
                if x is None:
                    fate = 'not_reached'; break
                if x.get('timeout') or x.get('error'):
                    fate = f'timeout_{b}'; break
                if x['min_lines_ub'] is not None:
                    fate = f'le{b}'; break
            if fate is None:
                fate = 'lb17'
            st[fate] += 1
            if fate == 'lb17':
                cands[n] = (c, r, stages[16][n], stages[17].get(n))
    print(json.dumps(st), file=sys.stderr)

    def label(c, r, x16, x17):
        nub, ubp = prune(r['gen_proof'])
        rec = {'name': f'lp2_{r["name"]}' if c != 'calib' else r['name'], 'thm': r['thm'], 'key': pkey(r['prompt']),
               'prompt': r['prompt'], 'source': 'gen', 'schema': None, 'chunk': c, 'gen_lines': r['gen_lines'],
               'n_prem': r.get('n_prem'), 'rules': r.get('rules'), 'gen_proof': r['gen_proof'],
               'construction_pruned': nub, 'ub_proof': ubp, 'minlen16_secs': x16.get('secs') if x16 else None}
        if x17 is None:
            e, lb, ub, p = 'missing', 17, nub, None
        elif x17.get('timeout') or x17.get('error'):
            e, lb, ub, p = 'timeout', 17, nub, None
        elif x17['min_lines_ub'] is not None:
            e, lb, ub, p = 'exact17', 17, x17['min_lines_ub'], x17['proof']
            assert x17['min_lines_ub'] == 17, x17
        else:
            e, lb, ub, p = 'ge18', 18, nub, None
        if p:
            rec['ub_proof'] = p
        rec.update({'L_lb': lb, 'L_ub': ub, 'L_true': lb if lb == ub else None, 'L_true_lb': lb, 'n_lines': None,
                    'stageE': e, 'stageE_secs': x17.get('secs') if x17 else None,
                    'ub_source': 'minlen17' if p else 'construction',
                    'ub_bin': ('17-18' if ub <= 18 else '19-20' if ub <= 20 else '21-22' if ub <= 22 else '23-24' if ub <= 24 else '25+'),
                    'ub_qbin': ('<=28' if ub <= 28 else '29-32' if ub <= 32 else '33-36' if ub <= 36 else '37+')})
        return rec

    # calibration: long-pool's >= 17 file + stage E on it
    cal17 = read_stage(f'{a.dir}/calib_ml17.jsonl') or {}
    calib = [label('calib', r, {'secs': r.get('minlen_secs')}, cal17.get(r['name'])) for r in map(json.loads, open(a.calib_in))]
    for r in calib:
        r['chunk'] = 'lp_' + r['name'].split('_')[1]
    calib_keys = {r['key'] for r in calib}

    # disjointness
    keys = {}
    for n, v in cands.items():
        keys.setdefault(pkey(v[1]['prompt']), n)
    okeys = {okey(v[1]['prompt']) for v in cands.values()}
    files = [l.strip() for l in open(a.excl_manifest) if l.strip() and not l.startswith('#')]
    hit, ohit, nrec = collections.defaultdict(set), collections.defaultdict(set), {}
    for fn in files:
        n = 0
        with opener(fn) as f:
            for l in f:
                i = l.find('"prompt": "')
                if i < 0:
                    i = l.find('"thm": "')
                    if i < 0:
                        continue
                    j = l.find('"', i + 8); p = 'THM ' + l[i + 8:j].replace('|-', 'SEQ') + ' PRF'
                else:
                    j = l.find('"', i + 11); p = l[i + 11:j]
                n += 1; k = pkey(p)
                if k in keys:
                    hit[fn].add(k)
                try:
                    ok = okey(p)
                except Exception:
                    continue
                if ok in okeys:
                    ohit[fn].add(ok)
        nrec[fn] = n
        print(f'{fn}: {n} records, {len(hit[fn])} / {len(ohit[fn])} hits (ordered / order-invariant)', file=sys.stderr)
    excl = set().union(*hit.values()) if hit else set()
    oexcl = set().union(*ohit.values()) if ohit else set()
    pool, seen, dup = [], set(), 0
    for n in sorted(cands):
        c, r, x16, x17 = cands[n]
        k = pkey(r['prompt'])
        if k in seen:
            dup += 1; continue
        seen.add(k)
        if k in excl or okey(r['prompt']) in oexcl or k in calib_keys:
            st['excluded'] += 1; continue
        pool.append(label(c, r, x16, x17))
    assert not ({r['key'] for r in pool} & (excl | calib_keys))
    with open(a.out, 'w') as f:
        for r in pool:
            f.write(json.dumps(r) + '\n')
    with open(a.calib_out, 'w') as f:
        for r in calib:
            f.write(json.dumps(r) + '\n')
    C = lambda rs, f: dict(sorted(collections.Counter(r[f] for r in rs).items()))
    summ = {'n': len(pool), 'n_calib': len(calib), 'stats': dict(st), 'duplicates_across_chunks': dup,
            'ub_bin': C(pool, 'ub_bin'), 'ub_qbin': C(pool, 'ub_qbin'), 'stageE': C(pool, 'stageE'),
            'calib_ub_qbin': C(calib, 'ub_qbin'), 'calib_stageE': C(calib, 'stageE'),
            'excl_files': len(files), 'excl_records': sum(nrec.values()),
            'excluded_ordered_key': len(excl), 'excluded_order_invariant_key': len(oexcl),
            'hits_by_file': {fn: [len(hit[fn]), len(ohit[fn])] for fn in files if hit[fn] or ohit[fn]}}
    json.dump(summ, open(a.out.replace('.jsonl', '_summary.json'), 'w'), indent=1)
    print(json.dumps({k: summ[k] for k in ('n', 'n_calib', 'ub_bin', 'ub_qbin', 'stageE', 'calib_stageE')}, indent=1))


if __name__ == '__main__':
    main()
