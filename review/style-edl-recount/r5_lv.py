#!/usr/bin/env python3
"""R5 (reviewer, phase 1): the style-blind score l_V.
  (1) rebuild V(x) from the raw sources the pre-registration names (all 18 stream files, the selection k 32 and the
      S_own2 k 4 reads, the plain capability reads of the 3 learners and the 18 theta*), with my parsers, and compare
      with data/style_edl/vset.jsonl theorem by theorem;
  (2) every stream proof is in V(x); l_V <= the single-string code of the stream proof under the same model;
  (3) Lean re-check of every V(x) proof (my renderer);
  (4) EDL_V and EDL_V,c recomputed from the lv runs' per-theorem l_V; the lv fits' single-string bits vs the primary
      edl runs (the 'fits re-run deterministically' claim); the share of the EDL_c excess over S_own2 that l_V removes.
  python3 r5_lv.py -> out/r5_lv.json
"""
import collections, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C

A = f'{C.WS}/artifacts/style_edl'
SEEDS = (0, 1, 2)
STREAMS = ('S_own', 'S_own2', 'S_seed', 'S_short', 'S_RL', 'S_Kal')
LOG3 = math.log2(3)


def key(L):
    return tuple(L)


def main():
    allp = {r['name']: r['prompt'] for r in C.jl(f'{C.WS}/data/style_edl/sets/all256.jsonl')}
    mine = collections.defaultdict(dict)       # name -> key -> source set
    stream_keys = collections.defaultdict(set)

    def add(nm, L, src):
        mine[nm].setdefault(key(L), set()).add(src)

    for s in SEEDS:
        for S in STREAMS:
            for part in ('stream', 'test'):
                for r in C.jl(f'{C.WS}/data/style_edl/streams/s{s}/{S}.{part}.jsonl'):
                    L = C.parse_nd(r['nd'])
                    add(r['name'], L, f'stream:{S}')
                    stream_keys[r['name']].add(key(L))
    parse_fail = collections.Counter()

    def add_reads(fn, src):
        for r in C.jl(fn):
            nm = r['name']
            if nm not in allp:
                continue
            for t in r['accepted']:
                try:
                    add(nm, C.ls_to_nd(allp[nm], t), src)
                except C.Bad as e:
                    parse_fail[src] += 1

    for s in SEEDS:
        add_reads(f'{A}/reads/base_s{s}__tf1200_plain_k32_seed1.rows.jsonl.gz', 'sel_k32')
        add_reads(f'{A}/reads/base_s{s}__tf1200_plain_k4_seed3.rows.jsonl.gz', 'own2_k4')
        add_reads(f'{A}/cap/base_s{s}__plain_k32_seed2.rows.jsonl.gz', 'cap_learner')
        for S in STREAMS:
            add_reads(f'{A}/cap/s{s}_{S}__plain_k32_seed2.rows.jsonl.gz', f'cap_theta:{S}')
    vs = C.jl(f'{C.WS}/data/style_edl/vset.jsonl')
    theirs = collections.defaultdict(set)
    dup = 0
    for r in vs:
        k = key(C.parse_nd(r['nd']))
        if k in theirs[r['name']]:
            dup += 1
        theirs[r['name']].add(k)
    cmpv = {'their_records': len(vs), 'their_duplicates': dup, 'names_theirs': len(theirs), 'names_mine': len(mine),
            'theorems_equal': 0, 'theorems_mine_extra': 0, 'theorems_theirs_extra': 0, 'mine_total': 0, 'theirs_total': 0,
            'stream_proof_not_in_theirs': 0, 'my_parse_fail': dict(parse_fail)}
    extra_src = collections.Counter()
    for nm in allp:
        a, b = set(mine[nm]), theirs[nm]
        cmpv['mine_total'] += len(a); cmpv['theirs_total'] += len(b)
        cmpv['theorems_equal'] += a == b
        cmpv['theorems_mine_extra'] += bool(a - b)
        cmpv['theorems_theirs_extra'] += bool(b - a)
        for k in a - b:
            for sname in mine[nm][k]:
                extra_src[sname] += 1
        cmpv['stream_proof_not_in_theirs'] += len(stream_keys[nm] - b)
    cmpv['mine_extra_by_source'] = dict(extra_src)
    sizes = [len(theirs[nm]) for nm in allp]
    cmpv['size_mean'] = sum(sizes) / len(sizes); cmpv['size_max'] = max(sizes); cmpv['size_min'] = min(sizes)
    # only-from-stream proofs: proofs in V(x) found by no sampler (e.g. Kalmar, minlen)
    src_only = collections.Counter()
    for nm in allp:
        for k, ss in mine[nm].items():
            if all(x.startswith('stream:') for x in ss):
                src_only[tuple(sorted(ss))] += 1
    cmpv['proofs_only_in_streams_by_stream_set'] = {'|'.join(k): v for k, v in src_only.most_common(12)}
    # Lean re-check of V(x) as stored
    srcs = [C.nd_to_lean(r['prompt'], C.parse_nd(r['nd']), f'v{i}') for i, r in enumerate(vs)]
    lr = C.lean_check(srcs, tag='vset')
    cmpv['lean_checked'] = len(srcs); cmpv['lean_accepted'] = sum(ok for ok, _ in lr)
    # (4) EDL_V
    cells = {}
    r3 = json.load(open(os.path.join(C.HERE, 'out', 'r3_edl.json')))['cells']
    for s in SEEDS:
        for S in STREAMS:
            d = json.load(open(f'{A}/lv/s{s}/{S}.json'))
            e = json.load(open(f'{A}/edl/s{s}/{S}.json'))
            lr_star = r3[f's{s}/{S}']['lr_star']
            n, nt = d['n_stream'], d['n_test']
            lvs, lvt = d['base']['lv_stream'], d['base']['lv_test']
            sn, tn = d['stream_names'], d['test_names']
            b0s, b0t = d['base']['stream']['bits'], d['base']['test']['bits']
            viol = sum(lvs[nm] > b + 1e-6 for nm, b in zip(sn, b0s)) + sum(lvt[nm] > b + 1e-6 for nm, b in zip(tn, b0t))
            MV = sum(lvs[nm] for nm in sn) - n * sum(lvt[nm] for nm in tn) / nt
            per_o = {}
            maxdiff = 0.0
            for r in d['runs']:
                assert abs(r['lr'] - lr_star) < 1e-12, (s, S, r['lr'], lr_star)
                pre = sum(sum(b['lv_block'].values()) for b in r['blocks'])
                Lt = sum(r['theta']['lv_test'].values()) / nt
                pre_ss = sum(sum(b['block']['bits']) for b in r['blocks'])
                Lt_ss = sum(r['theta']['test']['bits']) / nt
                # same fit as the primary run?
                er = [x for x in e['runs'] if abs(x['lr'] - lr_star) < 1e-12 and x['order'] == r['order']][0]
                for b1, b2 in zip(r['blocks'], er['blocks']):
                    for x1, x2 in zip(b1['block']['bits'], b2['block']['bits']):
                        maxdiff = max(maxdiff, abs(x1 - x2))
                for x1, x2 in zip(r['theta']['test']['bits'], er['theta']['test']['bits']):
                    maxdiff = max(maxdiff, abs(x1 - x2))
                # l_V <= single-string bits per block proof and per theta* test proof
                for b in r['blocks']:
                    names = [r_ for r_ in b['lv_block']]
                    for nm, x in zip(names, b['block']['bits']):
                        viol += b['lv_block'][nm] > x + 1e-6
                per_o[r['order']] = {'EDL_V': pre - n * Lt + LOG3, 'EDL_ss_lvrun': pre_ss - n * Lt_ss + LOG3,
                                     'p_blocks': [b['fit'].get('passes') for b in r['blocks']],
                                     'p_theta': r['theta']['fit'].get('passes')}
            EV = sum(v['EDL_V'] for v in per_o.values()) / len(per_o)
            ESS = sum(v['EDL_ss_lvrun'] for v in per_o.values()) / len(per_o)
            cells[f's{s}/{S}'] = {'EDL_V_per_proof': EV / n, 'EDL_V_c_per_proof': (EV - MV) / n, 'M_V_per_proof': MV / n,
                                  'EDL_ss_from_lv_runs_per_proof': ESS / n,
                                  'EDL_ss_primary_per_proof': r3[f's{s}/{S}']['EDL_per_proof'],
                                  'EDL_c_primary_per_proof': r3[f's{s}/{S}']['EDL_c_per_proof'],
                                  'max_abs_bits_diff_vs_primary_fit': maxdiff, 'lv_gt_single_string_violations': viol,
                                  'learner_lv_mean_all256': (sum(lvs.values()) + sum(lvt.values())) / (n + nt),
                                  'p': {o: (v['p_blocks'], v['p_theta']) for o, v in per_o.items()}}
    rem = {}
    for S in STREAMS:
        if S == 'S_own2':
            continue
        ex = [cells[f's{s}/{S}']['EDL_c_primary_per_proof'] - cells[f's{s}/S_own2']['EDL_c_primary_per_proof'] for s in SEEDS]
        exv = [cells[f's{s}/{S}']['EDL_V_c_per_proof'] - cells[f's{s}/S_own2']['EDL_V_c_per_proof'] for s in SEEDS]
        ex_u = [cells[f's{s}/{S}']['EDL_ss_primary_per_proof'] - cells[f's{s}/S_own2']['EDL_ss_primary_per_proof'] for s in SEEDS]
        exv_u = [cells[f's{s}/{S}']['EDL_V_per_proof'] - cells[f's{s}/S_own2']['EDL_V_per_proof'] for s in SEEDS]
        m, mv = sum(ex) / 3, sum(exv) / 3
        rem[S] = {'excess_EDL_c': ex, 'excess_EDL_V_c': exv, 'mean_excess_c': m, 'mean_excess_V_c': mv,
                  'share_removed_c': (1 - mv / m) if abs(m) > 1e-9 else None,
                  'excess_EDL': ex_u, 'excess_EDL_V': exv_u,
                  'share_removed_uncorrected': (1 - (sum(exv_u) / 3) / (sum(ex_u) / 3)) if abs(sum(ex_u)) > 1e-9 else None}
    kal = {s: cells[f's{s}/S_Kal']['EDL_V_c_per_proof'] / cells[f's{s}/S_Kal']['EDL_c_primary_per_proof'] for s in SEEDS}
    out = {'vset_rebuild': cmpv, 'cells': cells, 'removed': rem, 'S_Kal_EDL_V_c_over_EDL_c': kal}
    json.dump(out, open(os.path.join(C.HERE, 'out', 'r5_lv.json'), 'w'), indent=1)
    print(json.dumps(cmpv, indent=1))
    for k, v in cells.items():
        print(k, {a: (round(b, 4) if isinstance(b, float) else b) for a, b in v.items() if a != 'p'})
    for S, v in rem.items():
        print(S, {a: ([round(x, 3) for x in b] if isinstance(b, list) else (round(b, 3) if isinstance(b, float) else b)) for a, b in v.items()})
    print('S_Kal EDL_V,c / EDL_c', kal)


if __name__ == '__main__':
    main()
