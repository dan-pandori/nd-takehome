"""Every per-round RL cell of the review's rl_<arm>.json vs the executor's artifacts/ps/rl_found.json."""
import json
E = json.load(open('/home/dan/work/proof-strategies/artifacts/ps/rl_found.json'))
bad = cells = 0
for arm, e in E.items():
    r = json.load(open(f'/home/dan/review/proof-strategies/review_ps/out/rl_{arm}.json'))
    for key in ('new_by_round', 'reductio_by_round', 'working_by_round', 'template_only_by_round', 'free_working_by_round', 'neg_goal_working_by_round'):
        for rd in range(1, 17):
            cells += 1; bad += e[key].get(str(rd), 0) != r[key].get(str(rd), 0)
    bad += e['sigma_cov_first_working_round'] != r['sigma_cov_first_working_round']
print('cells', cells, 'mismatches', bad)
