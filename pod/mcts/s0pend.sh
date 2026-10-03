#!/usr/bin/env bash
# s0's end-of-pretraining read-outs on their own pod (mc-3), to finish sooner; every arm of (s0, pend) runs here.
source pod/mcts/env.sh
SEEDS=0 bash pod/mcts/setup.sh
hf buckets cp $BK/mcts-a/ckpts/mcts/value_s0_pend.pt ckpts/mcts/value_s0_pend.pt
hf buckets cp $BK/mcts-a/artifacts/mcts/cfg_final.json artifacts/mcts/cfg_final.json
md5sum ckpts/mcts/*.pt; cat artifacts/mcts/cfg_final.json | tail -5
bash pod/mcts/read.sh 0 pend C tb72 h250 rrQ100 long2
echo SEED_DONE $(ts)
