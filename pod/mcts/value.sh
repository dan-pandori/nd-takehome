#!/usr/bin/env bash
# Value data (frozen-policy rollouts on rl_targets + 1,500 K12 generator theorems, k 16, T 1.0) and the value head, for
# one checkpoint.  Usage: bash pod/mcts/value.sh <seed> <pend|r8>.  Restartable: finished files are skipped.
source pod/mcts/env.sh
S=$1; C=$2
case $C in pend) CK=ckpts/mcts/stage1_best12_s${S}_b1200.pt ;; r8) CK=ckpts/mcts/la_T1_best12_s${S}_r8.pt ;; esac
D=artifacts/mcts/vdata/vdata_s${S}_$C.pt
echo "=== value data s$S $C $(ts)"
[ -s $D ] || python3 mcts_value_data.py --ckpt $CK --targets data/ladder/rl_targets.jsonl --gen data/kh/train_k12.jsonl \
  --n_gen 1500 --k 16 --temp 1.0 --seed $S --out $D || exit 1
echo "=== value head s$S $C $(ts)"
[ -s ckpts/mcts/value_s${S}_$C.pt ] || python3 mcts_value_train.py --data $D --out ckpts/mcts/value_s${S}_$C.pt \
  --report artifacts/mcts/value/value_s${S}_$C.json --seed $S || exit 1
echo "=== done s$S $C $(ts)"
up artifacts/mcts; up ckpts/mcts/value_s${S}_$C.pt 2>/dev/null; hf buckets cp ckpts/mcts/value_s${S}_$C.pt $BK/mcts-a/ckpts/mcts/value_s${S}_$C.pt >/dev/null 2>&1 || echo "UPLOAD FAILED value"
