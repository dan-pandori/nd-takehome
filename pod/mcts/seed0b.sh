#!/usr/bin/env bash
# s0 after addendum 1: finish the (extended) tuning, take the s0 r8 value head from the bucket (trained on mc-2), read-outs.
source pod/mcts/env.sh
bash pod/mcts/tune.sh
until [ -s ckpts/mcts/value_s0_r8.pt ]; do
  hf buckets cp $BK/mcts-a/ckpts/mcts/value_s0_r8.pt ckpts/mcts/value_s0_r8.pt >/dev/null 2>&1 || sleep 60
done
hf buckets cp $BK/mcts-a/artifacts/mcts/value/value_s0_r8.json artifacts/mcts/value/value_s0_r8.json >/dev/null 2>&1
hf buckets cp $BK/mcts-a/artifacts/mcts/vdata/vdata_s0_r8.json artifacts/mcts/vdata/vdata_s0_r8.json >/dev/null 2>&1
bash pod/mcts/read.sh 0 r8 C tb72 h250 rrQ100 long2
bash pod/mcts/read.sh 0 pend C tb72 h250 rrQ100 long2
echo SEED_DONE $(ts)
