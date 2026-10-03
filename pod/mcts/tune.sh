#!/usr/bin/env bash
# Pre-registered tuning (s0, end-of-pretraining checkpoint, 184 held-out rl_targets theorems with L_true >= 9 -- no
# evaluation pool): eight configs per arm (four pre-registered + four of addendum 1) at the sampling read's wall clock; per arm the most solved wins (ties: the
# earlier config).  Writes artifacts/mcts/cfg_final.json and uploads it.
source pod/mcts/env.sh
python3 - <<'PY'
import json
grid = [dict(K=8, temp=1.0), dict(K=16, temp=1.0), dict(K=8, temp=1.5), dict(K=16, temp=1.5),
        dict(K=2, temp=1.0), dict(K=4, temp=1.0), dict(K=2, temp=0.8), dict(K=4, temp=0.8)]   # t4-t7: addendum 1
for i, g in enumerate(grid):
    json.dump({'prior': g, 'value': g}, open(f'artifacts/mcts/cfg_tune{i}.json', 'w'))
PY
for i in 0 1 2 3 4 5 6 7; do CFG=artifacts/mcts/cfg_tune$i.json TAGSUF=_t$i bash pod/mcts/read.sh 0 pend tune200; done
python3 - <<'PY'
import json
res = {}
for arm in ('prior', 'value'):
    best = None
    for i in range(8):
        s = json.load(open(f'artifacts/mcts/eval/s0_pend__tune200__{arm}_t{i}.json'))
        res[f'{arm}_t{i}'] = s['solved']
        if best is None or s['solved'] > best[0]:
            best = (s['solved'], i)
    res[arm] = json.load(open(f'artifacts/mcts/cfg_tune{best[1]}.json'))[arm]
res['sample'] = json.load(open('artifacts/mcts/eval/s0_pend__tune200__sample.json'))['solved']
json.dump(res, open('artifacts/mcts/cfg_final.json', 'w'), indent=1)
print(json.dumps(res))
PY
up artifacts/mcts
