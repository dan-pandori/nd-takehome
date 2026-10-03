#!/usr/bin/env bash
# Seeds 1 / 2 after addendum 1.  Waits for this seed's r8 value head, replaces the original seed.sh chain, [mc-2: trains
# the s0 r8 value head], runs the sampling arm of every read-out while s0's tuning finishes, then the search arms.
# Usage: bash pod/mcts/seedB.sh <seed> [s0r8]
source pod/mcts/env.sh
S=$1
until [ -s ckpts/mcts/value_s${S}_r8.pt ]; do sleep 30; done
sleep 60                                    # value.sh's uploads
pkill -f "[s]eed.sh $S"
if [ "$2" = s0r8 ]; then
  [ -s ckpts/mcts/la_T1_best12_s0_r8.pt ] || hf buckets cp $BK/trajectory/ckpts/tj/ladder/la_T1_best12_s0_r8.pt ckpts/mcts/
  md5sum ckpts/mcts/la_T1_best12_s0_r8.pt
  bash pod/mcts/value.sh 0 r8
  rm -f artifacts/mcts/vdata/vdata_s0_r8.pt     # in the bucket; keeps this pod's later syncs small
fi
ARMS=" " bash pod/mcts/read.sh $S r8 C tb72 h250 rrQ100 long2
ARMS=" " bash pod/mcts/read.sh $S pend C tb72 h250 rrQ100 long2
until [ -s artifacts/mcts/cfg_final.json ]; do
  hf buckets cp $BK/mcts-a/artifacts/mcts/cfg_final.json artifacts/mcts/cfg_final.json >/dev/null 2>&1 || sleep 60
done
bash pod/mcts/read.sh $S r8 C tb72 h250 rrQ100 long2
bash pod/mcts/read.sh $S pend C tb72 h250 rrQ100 long2
echo SEED_DONE $(ts)
