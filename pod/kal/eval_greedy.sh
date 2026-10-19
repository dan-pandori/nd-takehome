#!/usr/bin/env bash
# GREEDY read-outs of one model (teacher-forced agreement and greedy free generation; batch 1,024 for every arm) (each step skipped if its .done marker exists, so the script resumes).
# Usage: bash pod/kal/eval_greedy.sh <tag> <ckpt> <kal|ctl> [batch]
. pod/kal/env.sh
T=$1; CK=$2; KIND=$3; B=${4:-1024}
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
run tf_$T python3 kalmar/tf_agree.py --ckpt $CK --in $K/tf1200_kal_sl.jsonl --out $TF/${T}__tf1200.json --batch $B
run fg_$T python3 kalmar/kal_free.py --ckpt $CK --in $K/tf1200_kal_sl.jsonl --k 1 --temperature 0 --out $F/${T}__tf1200_greedy.json $CAPS
run g1sg_$T python3 kalmar/kal_free.py --ckpt $CK --in $K/g1_premises.jsonl --k 1 --temperature 0 --supply_pr --out $F/${T}__g1_supplied_greedy.json $CAPS
for S in holdout250 rr600 ge17 long2 candidate_v0 candidate_v1 batch3 hand_proved_14; do
  run gr_${S}_$T python3 kalmar/kal_free.py --ckpt $CK --in $K/${S}_kal_sl.jsonl --k 1 --temperature 0 --out $F/${T}__${S}_greedy.json $CAPS
done
for S in g1_premises g2_large g3_classical; do
  run gr_${S}_$T python3 kalmar/kal_free.py --ckpt $CK --in $K/$S.jsonl --k 1 --temperature 0 --out $F/${T}__${S}_greedy.json $CAPS
done
up artifacts/kalmar/eval; up artifacts/kalmar/free; up artifacts/kalmar/tf; up artifacts/kalmar/logs
touch $M/greedy_$T.done
echo "GREEDY DONE $T $(date -u +%FT%TZ)" >> $L/eval_$T.log
