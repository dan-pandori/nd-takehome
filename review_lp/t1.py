import json, gzip, collections, os
os.chdir(os.path.expanduser('~/review/lean-prefilter/artifacts/lp/t1'))
acc = {}; alld = {}
for arm in 'ABCD':
    r = json.load(open(f't1_{arm}/round_1.json'))
    g = [json.loads(l) for l in open(f'gate_{arm}.jsonl')]
    exp = sum(x['lean_wall_s'] for x in g)
    rows = [json.loads(l) for l in gzip.open(f'dump_{arm}.jsonl.gz', 'rt')]
    ok = {(d['prompt'], d['lean_text']) for d in rows if d['lean_ok']}
    acc[arm] = ok; alld[arm] = {(d['prompt'], d['lean_text']): d for d in rows}
    fr = sum(1 for d in rows if d['filter'] is not None)
    fr_bad = sum(1 for d in rows if d['filter'] is not None and d.get('lean'))
    samples = sum(x['samples'] for x in g); trunc = sum(x['trunc'] for x in g)
    distinct = sum(x['distinct_checked'] for x in g); lrej = sum(x['lean_rej'] for x in g); frej = sum(x['filter_rej'] for x in g)
    print(arm, 'secs', round(r['secs'], 1), 'phase_s', {k: round(v, 1) for k, v in r['phase_s'].items()}, 'gate exposed', round(exp, 1),
          f'share {100*exp/r["secs"]:.1f}%', 'workers', g[0]['workers'], 'pipeline', g[0]['pipeline'], 'prefilter', g[0]['prefilter'],
          '| samples', samples, 'trunc', trunc, f'{100*trunc/samples:.3f}%', 'distinct', distinct, 'rej', lrej, 'filter_rej', frej,
          f'filter share {100*frej/max(1,lrej):.1f}%', 'lean_proc_s', round(sum(x['lean_proc_s'] for x in g), 1), 'lean_texts', sum(x['lean_texts'] for x in g),
          '| dump rows', len(rows), 'accepted', len(ok), 'dump filter-rej', fr, 'filter-rej with lean true', fr_bad)
    print('   solved targets', r['targets_round'].get('solved') if isinstance(r['targets_round'], dict) else r['targets_round'], 'new', r['new_proofs_this_round'])
for a, b in [('A', 'B'), ('C', 'D'), ('A', 'C')]:
    common = alld[a].keys() & alld[b].keys()
    print(a, b, 'accepted identical:', acc[a] == acc[b], len(acc[a] ^ acc[b]), '| common texts', len(common),
          'verdict disagreements on common', sum(1 for k in common if alld[a][k]['lean_ok'] != alld[b][k]['lean_ok']))
