#!/usr/bin/env python3
"""R1 (reviewer, phase 1): rebuild the theorem pool, the split and all six streams of every learner seed from the raw
reads, with my own parsers (rv_core), and compare with the stored stream files.  No run code is imported.

  python3 r1_rebuild.py   -> out/r1_rebuild.json, out/r1_lean_items.jsonl (the distinct proofs to Lean-check)
"""
import collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C

WS = C.WS
R = f'{WS}/artifacts/style_edl/reads'
SEEDS = (0, 1, 2)
STREAMS = ('S_own', 'S_own2', 'S_seed', 'S_short', 'S_RL', 'S_Kal')


def rows(fn):
    return {r['name']: r for r in C.jl(fn)}


def main():
    tf = {r['name']: r for r in C.jl(f'{WS}/data/kalmar/tf1200_kal_sl.jsonl')}
    g = {s: rows(f'{R}/base_s{s}__tf1200_greedy.rows.jsonl.gz') for s in SEEDS}
    r8 = {s: rows(f'{R}/r8_s{s}__tf1200_greedy.rows.jsonl.gz') for s in SEEDS}
    k32 = {s: rows(f'{R}/base_s{s}__tf1200_plain_k32_seed1.rows.jsonl.gz') for s in SEEDS}
    k4 = {s: rows(f'{R}/base_s{s}__tf1200_plain_k4_seed3.rows.jsonl.gz') for s in SEEDS}
    short = {r['name']: r for r in C.jl(f'{WS}/data/style_edl/short/tf1200_minlen14.jsonl')}
    out = {'n_tf1200': len(tf)}
    # ---- read-level facts
    for s in SEEDS:
        assert set(g[s]) == set(tf) == set(r8[s]) == set(k32[s]) == set(k4[s]), s
        out[f'reads_s{s}'] = {
            'greedy_valid': sum(r['valid'] for r in g[s].values()),
            'r8_greedy_valid': sum(r['valid'] for r in r8[s].values()),
            'sel_k32_ge29': sum(r['n_ok'] >= 29 for r in k32[s].values()),
            'sel_k32_k': sorted({r['k'] for r in k32[s].values()}),
            'k4_any': sum(bool(r['accepted']) for r in k4[s].values()),
            'k4_k': sorted({r['k'] for r in k4[s].values()}),
            'greedy_end': dict(collections.Counter(r['end'] for r in g[s].values())),
            'r8_end': dict(collections.Counter(r['end'] for r in r8[s].values())),
        }
    out['minlen'] = {'records': len(short), 'found': sum(r['nd'] is not None for r in short.values()),
                     'timeouts': sum(bool(r.get('timeout')) for r in short.values()),
                     'n_lines_max': max(r['n_lines'] for r in short.values() if r['nd'] is not None)}
    # ---- eligibility (flags), then my own parse of every candidate proof
    why = collections.Counter()
    cand = {}
    for nm, t in tf.items():
        fail = []
        for s in SEEDS:
            if k32[s][nm]['n_ok'] < 29: fail.append(f'sel_s{s}')
            if not g[s][nm]['valid']: fail.append(f'greedy_s{s}')
            if not r8[s][nm]['valid']: fail.append(f'r8_s{s}')
            if not k4[s][nm]['accepted']: fail.append(f'own2_s{s}')
        if short.get(nm, {}).get('nd') is None: fail.append('short_none')
        for f in fail:
            why[f] += 1
        if fail:
            why['excluded_flags'] += 1
            continue
        pr = t['prompt']
        try:
            p = {'kal': C.parse_nd(t['proof']), 'short': C.parse_nd(short[nm]['nd'])}
            for s in SEEDS:
                p[f'own{s}'] = C.ls_to_nd(pr, g[s][nm]['text'])
                p[f'rl{s}'] = C.ls_to_nd(pr, r8[s][nm]['text'])
                p[f'own2_{s}'] = C.ls_to_nd(pr, next(iter(k4[s][nm]['accepted'])))
        except C.Bad as e:
            why['my_parse_fail'] += 1
            why[f'my_parse_fail:{str(e)[:40]}'] += 1
            continue
        cand[nm] = p
    out['eligible_by_flags_and_my_parse'] = len(cand)
    out['exclusions'] = dict(why)
    # ---- the stored sets and streams
    all256 = C.jl(f'{WS}/data/style_edl/sets/all256.jsonl')
    test128 = C.jl(f'{WS}/data/style_edl/sets/test128.jsonl')
    names256 = [r['name'] for r in all256]
    tnames = {r['name'] for r in test128}
    out['sets'] = {'all256': len(all256), 'all256_distinct': len(set(names256)), 'test128': len(test128),
                   'test_subset_of_all': tnames <= set(names256),
                   'all256_subset_of_my_eligible': sum(n in cand for n in names256),
                   'prompt_matches_tf1200': sum(r['prompt'] == tf[r['name']]['prompt'] for r in all256)}
    src = {'S_own': lambda s: f'own{s}', 'S_own2': lambda s: f'own2_{s}', 'S_seed': lambda s: f'own{(s + 1) % 3}',
           'S_short': lambda s: 'short', 'S_RL': lambda s: f'rl{s}', 'S_Kal': lambda s: 'kal'}
    cmp = {}
    files_names = {}
    items = {}                  # (prompt, nd text) -> sources, for the Lean check
    stats = {}
    for s in SEEDS:
        for S in STREAMS:
            part_names = {}
            res = {'match': 0, 'mismatch': 0, 'missing_in_my_pool': 0, 'prompt_mismatch': 0, 'nd_string_equal': 0}
            same = 0
            acts, lines_, tsz, asl = [], [], [], []
            for part in ('stream', 'test'):
                recs = C.jl(f'{WS}/data/style_edl/streams/s{s}/{S}.{part}.jsonl')
                part_names[part] = [r['name'] for r in recs]
                for r in recs:
                    nm = r['name']
                    if r['prompt'] != tf[nm]['prompt']:
                        res['prompt_mismatch'] += 1
                    L = C.parse_nd(r['nd'])
                    items.setdefault((r['prompt'], r['nd']), set()).add(f's{s}/{S}')
                    if nm not in cand:
                        res['missing_in_my_pool'] += 1
                        continue
                    mine = cand[nm][src[S](s)]
                    if mine == L:
                        res['match'] += 1
                    else:
                        res['mismatch'] += 1
                        res.setdefault('mismatch_names', []).append(nm)
                    if C.nd_text_of(mine) == r['nd']:
                        res['nd_string_equal'] += 1
                    same += (L == cand[nm][f'own{s}'])
                    acts.append(len(L) + 1)
                    lines_.append(len(L))
                    tsz.append(C.term_size(L))
                    asl.append(sum(x[2] == 'AS' for x in L))
            files_names[f's{s}/{S}'] = part_names
            cmp[f's{s}/{S}'] = res
            n = len(acts)
            stats[f's{s}/{S}'] = {'n': n, 'identical_to_own_greedy': same / n, 'mean_actions': sum(acts) / n,
                                  'mean_nd_lines': sum(lines_) / n, 'mean_term_size': sum(tsz) / n,
                                  'max_actions': max(acts)}
    out['rebuild_vs_stored'] = cmp
    out['stream_stats'] = stats
    # same theorem lists in every stream / seed, and the split = the sets
    ref = files_names['s0/S_own']
    out['same_names_everywhere'] = all(v == ref for v in files_names.values())
    out['test_part_equals_test128'] = set(ref['test']) == tnames
    out['stream_part_plus_test_equals_all256'] = set(ref['stream']) | set(ref['test']) == set(names256)
    st, te = ref['stream'], ref['test']
    cls_st = {C.rclass(tf[n]['prompt']) for n in st}
    cls_te = {C.rclass(tf[n]['prompt']) for n in te}
    out['split'] = {'stream': len(st), 'test': len(te), 'name_overlap': len(set(st) & set(te)),
                    'class_overlap': len(cls_st & cls_te), 'stream_classes': len(cls_st), 'test_classes': len(cls_te),
                    'atoms_stream': dict(sorted(collections.Counter(C.n_atoms(tf[n]['prompt']) for n in st).items())),
                    'atoms_test': dict(sorted(collections.Counter(C.n_atoms(tf[n]['prompt']) for n in te).items())),
                    'atoms_my_eligible': dict(sorted(collections.Counter(C.n_atoms(tf[n]['prompt']) for n in cand).items())),
                    'n_atoms_field_agrees': sum(C.n_atoms(tf[n]['prompt']) == tf[n]['n_atoms'] for n in tf)}
    # renaming classes inside the eligible pool (could two pool theorems share a class?)
    pc = collections.Counter(C.rclass(tf[n]['prompt']) for n in cand)
    out['split']['eligible_classes'] = len(pc)
    out['split']['eligible_classes_with_2plus'] = sum(v > 1 for v in pc.values())
    # S_short minimality against every other valid proof we hold (lines; pruned lines)
    worse = collections.Counter()
    for nm in names256:
        p = cand[nm]
        sl = len(p['short'])
        for k, L in p.items():
            if k != 'short' and len(L) < sl:
                worse[k] += 1
    out['short_longer_than_other_proof'] = dict(worse)
    out['short_lines_hist'] = dict(sorted(collections.Counter(len(cand[n]['short']) for n in names256).items()))
    # Kalmar caps: actions <= 1024; longest action tokens (my lean_seq token count of the longest have line) <= 512
    json.dump(out, open(os.path.join(C.HERE, 'out', 'r1_rebuild.json'), 'w'), indent=1, default=list)
    with open(os.path.join(C.HERE, 'out', 'r1_lean_items.jsonl'), 'w') as f:
        for (pr, nd), srcs in sorted(items.items()):
            f.write(json.dumps({'prompt': pr, 'nd': nd, 'src': sorted(srcs)}) + '\n')
    print(json.dumps({k: out[k] for k in ('eligible_by_flags_and_my_parse', 'exclusions', 'sets', 'split',
                                          'same_names_everywhere', 'test_part_equals_test128',
                                          'short_longer_than_other_proof')}, indent=1, default=list))
    for k, v in cmp.items():
        print(k, {a: b for a, b in v.items() if a != 'mismatch_names'}, json.dumps(stats[k]))
    print('distinct stream proofs:', len(items))


if __name__ == '__main__':
    main()
