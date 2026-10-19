#!/usr/bin/env bash
# SAMPLED read-outs of one model (T 0.8; batch 2,048 for every arm, on a 48 GB card) (each step skipped if its .done marker exists, so the script resumes).
# Usage: bash pod/kal/eval_sampled.sh <tag> <ckpt> <kal|ctl> [batch]
. pod/kal/env.sh
T=$1; CK=$2; KIND=$3; B=${4:-2048}
E=artifacts/kalmar/eval; F=artifacts/kalmar/free; TF=artifacts/kalmar/tf; L=artifacts/kalmar/logs; M=artifacts/kalmar/markers
mkdir -p $E $F $TF $L $M
K=data/kalmar
SETS=data/bs/holdout250.jsonl,data/ladder/transfer_long_rr600.jsonl,data/ladder/transfer_long_ge17.jsonl,data/ladder/transfer_long2.jsonl,data/gt/candidate_v0.jsonl,data/gt/candidate_v1.jsonl,data/gt/batch3.jsonl,data/gt/hand_proved_14.jsonl,data/bs/textbook72.jsonl,$K/g1_premises.jsonl,$K/g2_large.jsonl,$K/g3_classical.jsonl
CAPS="--max_steps 1024 --max_action 512 --batch $B"
run() { local name=$1; shift; [ -f $M/$name.done ] && return 0
  echo "START $name $(date -u +%FT%TZ)" >> $L/eval_$T.log
  "$@" > $L/$name.log 2>&1; local rc=$?
  echo "END $name rc=$rc $(date -u +%FT%TZ)" >> $L/eval_$T.log
  [ $rc = 0 ] && touch $M/$name.done; return $rc; }
run plain32_$T python3 guided_eval.py --ckpt $CK --arm plain --k 32 --seed 1 --sets $SETS --out $E/${T}_plain_k32 $CAPS
run guided32_$T python3 guided_eval.py --ckpt $CK --arm logical --k 32 --seed 1 --sets $SETS --out $E/${T}_logical_k32 $CAPS
run fs_$T python3 kalmar/kal_free.py --ckpt $CK --in $K/tf1200_kal_sl.jsonl --k 8 --temperature 0.8 --seed 1 --out $F/${T}__tf1200_t08k8.json $CAPS
run g1s32_$T python3 kalmar/kal_free.py --ckpt $CK --in $K/g1_premises.jsonl --k 32 --temperature 0.8 --seed 1 --supply_pr --out $F/${T}__g1_supplied_k32.json $CAPS
if [ "$KIND" = kal ] && [ "${EXT:-1}" = 1 ]; then      # pass@256: 224 more attempts on every theorem unsolved at k 32
  X=$(python3 kalmar/unsolved.py $E/${T}_plain_k32.rows.jsonl.gz $K/ext_$T ${SETS//,/ })
  [ -n "$X" ] && run plain224_$T python3 guided_eval.py --ckpt $CK --arm plain --k 224 --seed 2 --sets $X --out $E/${T}_plain_ext224 $CAPS
fi
if [ "$KIND" = ctl ]; then                           # k 256 plain where no stored best-state read exists
  run plain256_$T python3 guided_eval.py --ckpt $CK --arm plain --k 256 --seed 1 --sets data/ladder/transfer_long_ge17.jsonl,data/gt/candidate_v0.jsonl,data/gt/candidate_v1.jsonl,data/gt/batch3.jsonl,data/gt/hand_proved_14.jsonl,$K/g1_premises.jsonl,$K/g2_large.jsonl,$K/g3_classical.jsonl --out $E/${T}_plain_k256 $CAPS
fi
up artifacts/kalmar/eval; up artifacts/kalmar/free; up artifacts/kalmar/tf; up artifacts/kalmar/logs
touch $M/sampled_$T.done
echo "SAMPLED DONE $T $(date -u +%FT%TZ)" >> $L/eval_$T.log
