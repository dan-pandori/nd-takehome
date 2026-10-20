#!/usr/bin/env bash
# kc-3: B3 focus-given causal test (pre-registration addendum 2): STD vs FOC, size M, seeds 0-2, theorems [0, 8192).
. pod/kc/env.sh
mkdir -p artifacts/kc/b3
B="python3 kalmar_complexity/b3_focus.py"
for arm in STD FOC; do bash pod/kc/job.sh b3prep_$arm python3 -c "
import sys; sys.argv=['x','--arm','$arm','--seed','0','--out','/dev/null']
sys.path.insert(0,'kalmar_complexity'); import b3_focus as B, pickle, os
base = B.B2.load_records('kal', 8192)
recs = [[(B.transform(st, '$arm')[0], act, tg) for st, act, tg in rec] for rec in base]
os.makedirs('data/kc', exist_ok=True); pickle.dump(recs, open('data/kc/b3_${arm}_8192.pkl.tmp', 'wb')); os.replace('data/kc/b3_${arm}_8192.pkl.tmp', 'data/kc/b3_${arm}_8192.pkl')
print('prep', '$arm', len(recs), sum(map(len, recs)))" & done
wait
for s in 0 1 2; do for arm in STD FOC; do
  bash pod/kc/job.sh b3_${arm}_s$s $B --arm $arm --seed $s --size M --n_thm 8192 --out artifacts/kc/b3/${arm}_s$s.json &
  sleep 3; done; done
wait
up artifacts/kc
echo QUEUE3 DONE > artifacts/kc/logs/queue3.done
