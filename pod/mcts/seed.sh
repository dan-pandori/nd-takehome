#!/usr/bin/env bash
# Everything for one seed on one pod, in order: value heads (r8, pend); [s0: tuning]; wait for cfg_final.json; read-outs
# at r8 then pend.  Usage: bash pod/mcts/seed.sh <seed>
source pod/mcts/env.sh
S=$1
bash pod/mcts/value.sh $S pend
[ $S = 0 ] && bash pod/mcts/tune.sh
bash pod/mcts/value.sh $S r8
until [ -s artifacts/mcts/cfg_final.json ]; do
  hf buckets cp $BK/mcts-a/artifacts/mcts/cfg_final.json artifacts/mcts/cfg_final.json >/dev/null 2>&1 || sleep 60
done
bash pod/mcts/read.sh $S r8 C tb72 h250 rrQ100 long2
bash pod/mcts/read.sh $S pend C tb72 h250 rrQ100 long2
echo SEED_DONE $(ts)
