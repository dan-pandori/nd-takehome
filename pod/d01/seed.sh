#!/usr/bin/env bash
# One 0.1 % dose seed = pod/coe/seed2.sh with ARM=dose01 (Stage 1 best recipe, 1,200 s on this A40 -> held-out greedy
# (p2/heldout 5,000) -> 16-round T1 ladder: k 32, T 0.8, 600 ft steps, 20,000 replay records per round from K12^0.1 %),
# then the per-round analysis (coe/coe_rounds.py, needs the last found files, which stay on the pod) and uploads to the
# coe-dose01 bucket folder.  Reads run beside it (pod/d01/reader.sh).  Usage: bash pod/d01/seed.sh <seed>
source pod/d01/env.sh
ARM=dose01; S=$1; LB=${LB:-1024}
D=data/coe/train_k12dose01.jsonl
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
echo "=== rounds analysis $N $(date -u +%FT%TZ)"
nice -n 10 python3 coe/coe_rounds.py --dir artifacts/coe/ladder/la_$N --out artifacts/coe/rounds/la_$N.json > artifacts/coe/logs/rounds_la_$N.log 2>&1 || echo "ROUNDS FAILED $N"
nice -n 10 python3 coe/d01_heldout_proofs.py --dir artifacts/coe/ladder/la_$N --out artifacts/coe/rounds/heldout_proofs_la_$N.jsonl.gz >> artifacts/coe/logs/rounds_la_$N.log 2>&1 || echo "PROOFS FAILED $N"
up artifacts/coe/rounds
gzip -f artifacts/coe/dump/la_$N.jsonl 2>/dev/null
up artifacts/coe/ladder/la_$N
hf buckets sync artifacts/coe/dump $BK/coe-dose01/artifacts/coe/dump --include '*.gz' >/dev/null 2>&1 || echo "DUMP UPLOAD FAILED"
up artifacts/coe/logs
touch artifacts/coe/markers/seed_$N.done
echo "=== seed $N done $(date -u +%FT%TZ)"
