#!/usr/bin/env bash
# One create-or-elicit seed: Stage 1 (state_env_october recipe, 1,200 s on this A40) -> held-out greedy (p2/heldout 5,000)
# -> 16-round T1 ladder (k 32, T 0.8, 600 ft steps, 20,000 replay records from the arm's own pretraining set).
# Usage: bash pod/coe/seed.sh <full|ko> <seed>        env LB = ladder sampling batch (default 1024)
source pod/coe/env.sh
ARM=$1; S=$2; LB=${LB:-1024}
case $ARM in full) D=data/kh/train_k12.jsonl;; ko) D=data/coe/train_k12ko.jsonl;; *) echo "arm?"; exit 1;; esac
N=${ARM}_s${S}; CK=ckpts/coe/stage1_$N.pt
echo "=== seed $N start $(date -u +%FT%TZ) host $(hostname) data $D $(md5sum $D | cut -c1-12)"
if [ ! -s $CK ]; then
  echo "=== stage1 $N $(date -u +%FT%TZ)"
  ND_ARM=$ARM ND_SEED=$S python3 state_train.py --recipe best --data $D --heldout data/p2/heldout.jsonl --mode lean_staten \
    --cap 12 --seed $S --budget_secs 1200 --out $CK || exit 1
fi
touch artifacts/coe/markers/stage1_$N.done
if [ ! -s artifacts/coe/eval/heldout_$N.json ]; then
  echo "=== heldout greedy $N $(date -u +%FT%TZ)"
  ND_ARM=$ARM ND_SEED=$S python3 state_eval.py --ckpt $CK --in data/p2/heldout.jsonl --k 1 --temperature 0 --batch 1024 \
    --out artifacts/coe/eval/heldout_$N.jsonl --summary artifacts/coe/eval/heldout_$N.json || exit 1
fi
touch artifacts/coe/markers/heldout_$N.done
up artifacts/coe/eval
if [ ! -s artifacts/coe/ladder/la_$N/round_16.json ]; then
  echo "=== ladder $N $(date -u +%FT%TZ)"
  R=""; last=$(ls artifacts/coe/ladder/la_$N/round_*.json 2>/dev/null | sed 's/.*round_//; s/.json//' | sort -n | tail -1)
  if [ -n "$last" ]; then R="--resume --start_round $((last+1)) --rounds $((16-last))"; else R="--rounds 16"; fi
  ND_ARM=$ARM ND_SEED=$S LEAN_GATE_DUMP=artifacts/coe/dump/la_$N.jsonl python3 state_ladder_ei.py --init $CK --name la_$N --seed $S \
    --batch $LB --train $D --heldout data/coe/heldout1000.jsonl --transfer data/coe/transfer_track832.jsonl \
    --outdir artifacts/coe/ladder --ckptdir ckpts/coe/ladder $R || { echo "LADDER FAILED $N $(date -u +%FT%TZ)"; exit 1; }
fi
touch artifacts/coe/markers/ladder_$N.done
gzip -f artifacts/coe/dump/la_$N.jsonl 2>/dev/null
up artifacts/coe/ladder/la_$N
hf buckets sync artifacts/coe/dump $BK/create-or-elicit/artifacts/coe/dump --include '*.gz' >/dev/null 2>&1 || echo "DUMP UPLOAD FAILED"
echo "=== seed $N done $(date -u +%FT%TZ)"
