import json, glob, os, ast, collections, rvlib
A = '../artifacts/r4/'
TH = 20
out = {}
for d in sorted(glob.glob(A + '*/')):
    arm = os.path.basename(d.rstrip('/'))
    rounds = sorted(int(f.split('_')[-1][:-5]) for f in glob.glob(d + 'round_*.json'))
    founds = sorted(int(f.split('_')[-1][:-6]) for f in glob.glob(d + 'found_[0-9]*.jsonl'))
    best = rvlib.load_found(d)
    R = max(rounds) if rounds else 0
    d3_first = {}; solv_first = {}; nd3 = 0; dmax = collections.Counter()
    for (name, p), r in best.items():
        solv_first[name] = min(r, solv_first.get(name, 99))
        if rvlib.is_d3(p):
            nd3 += 1
            d3_first[name] = min(r, d3_first.get(name, 99))
    d3_by = [sum(1 for v in d3_first.values() if v <= r) for r in range(1, R + 1)]
    sol_by = [sum(1 for v in solv_first.values() if v <= r) for r in range(1, R + 1)]
    ign = next((r + 1 for r, n in enumerate(d3_by) if n >= TH), None)
    ho = []; ck = []
    for r in rounds:
        j = json.load(open(d + 'round_%d.json' % r))
        h = j.get('heldout_greedy'); h = ast.literal_eval(h) if isinstance(h, str) else h
        ho.append(round(h['rate'], 4) if h else None); ck.append(j.get('ckpt'))
    upd = {}
    uf = d + 'updates.jsonl'
    if os.path.exists(uf):
        U = [json.loads(l) for l in open(uf)]
        upd = dict(n_updates=len(U),
                   first_pattern_update=next((u['update'] for u in U if u['pattern_samples'] > 0), None),
                   ign_update=next((u['update'] for u in U if u['cum_pattern_targets'] >= TH), None),
                   var_frac_u1=U[0]['var_frac'], samples_per_update=U[0]['groups'] * U[0]['group_size'],
                   exec_cum_pattern_last=U[-1]['cum_pattern_targets'],
                   max_frac_unterminated=max(u['frac_unterminated'] for u in U))
    out[arm] = dict(rounds=R, round_files=rounds, found_files=founds, distinct_proofs=len(best),
                    n_d3_proofs=nd3, d3_thms_by_round=d3_by, solved_by_round=sol_by, ignition_round=ign,
                    acq=(d3_by[-1] / 1000 if d3_by else None), first_d3_round=min(d3_first.values(), default=None),
                    heldout_by_round=ho, ckpts=sorted(set(ck)), **upd)
    print(arm, R, d3_by, 'ign', ign, 'ho', ho[:1], ho[-1:], {k: upd[k] for k in ('first_pattern_update', 'ign_update', 'var_frac_u1')} if upd else '')
json.dump(out, open('arms.json', 'w'), indent=1)
