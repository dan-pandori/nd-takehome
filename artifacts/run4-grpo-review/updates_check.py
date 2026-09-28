import json, glob, os
A = '../artifacts/r4/'; arms = json.load(open('arms.json'))
rows = {}; mism = []
for f in sorted(glob.glob(A + 'grpo_*/updates.jsonl')):
    arm = f.split('/')[-2]; U = [json.loads(l) for l in open(f)]
    a = arms[arm]; upr = 100 if 'sprint' in arm else 40
    for r in range(1, a['rounds'] + 1):
        u = [x for x in U if x['update'] == upr * r]
        if u and u[0]['cum_pattern_targets'] != a['d3_thms_by_round'][r - 1]:
            mism.append((arm, r, u[0]['cum_pattern_targets'], a['d3_thms_by_round'][r - 1]))
    vf = [x['var_frac'] for x in U]
    ig = a.get('ign_update')
    rows[arm] = dict(n_upd=len(U), spu=U[0]['groups'] * U[0]['group_size'], var_u1=vf[0], var_max_first40=max(vf[:40]),
                     var_at_ign=(U[ig - 1]['var_frac'] if ig else None), first_pat=a.get('first_pattern_update'), ign_update=ig,
                     ign_samples=(ig * U[0]['groups'] * U[0]['group_size'] if ig else None),
                     unterm_max=max(x['frac_unterminated'] for x in U))
    print(arm, rows[arm])
print('round-boundary mismatches (arm, round, updates.jsonl, reviewer):', mism)
json.dump(dict(rows=rows, mismatches=mism), open('updates_check.json', 'w'), indent=1)
