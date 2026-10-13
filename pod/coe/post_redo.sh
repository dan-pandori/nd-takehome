#!/usr/bin/env bash
# Redo of post.sh's timing / budget / large-k steps for a seed whose post job ran before artifacts/coe/timing existed
# (coe-k0, 2026-10-13 00:13).  Same commands as post.sh.  Usage: bash pod/coe/post_redo.sh <arm> <seed> [wait-marker]
source pod/coe/env.sh
ARM=$1; S=$2; WAIT=$3; N=${ARM}_s${S}; CK=ckpts/coe/stage1_$N.pt
mkdir -p artifacts/coe/timing artifacts/coe/budget artifacts/coe/large
[ -n "$WAIT" ] && until [ -e artifacts/coe/markers/$WAIT ]; do sleep 60; done
while pgrep -f 'state_ladder_ei.p[y]|state_eval.p[y]|guided_eval.p[y]|state_train.p[y]|coe_bigk.p[y]' > /dev/null; do sleep 30; done
T=artifacts/coe/timing/A40_pend_${N}_b1024
[ -s $T.json ] || python3 state_eval.py --ckpt $CK --in data/coe/r322.jsonl --k 256 --temperature 0.8 --seed 0 --batch 1024 \
  --max_action 512 --max_steps 96 --summary $T.json > $T.log 2>&1
up artifacts/coe/timing
read K NSIG NA < <(python3 coe/coe_kpod.py --arm $ARM --seed $S)
NAMES=artifacts/coe/large/stdA_names_$N.txt
echo "=== post_redo $N: K_train(16) $K, n per sigma member $NSIG, standard-A n $NA on $(wc -l < $NAMES) theorems $(date -u +%FT%TZ)"
up artifacts/coe/budget
if [ "$ARM" = ko ] && [ "$NSIG" -gt 0 ]; then
  python3 coe/coe_bigk.py --ckpt $CK --in data/coe/read1054.jsonl --names @data/coe/sigma_heldout178.txt --n $NSIG --chunk 1024 \
    --batch 1024 --stop_successes 1 --seed0 9000 --out artifacts/coe/large/sig178_$N > artifacts/coe/logs/bigk_sig_$N.log 2>&1
  up artifacts/coe/large
fi
if [ -s "$NAMES" ] && [ "$NA" -gt 0 ]; then
  python3 coe/coe_bigk.py --ckpt $CK --in data/coe/read1054.jsonl --names @$NAMES --n $NA --chunk 2048 \
    --batch 1024 --stop_successes 10 --seed0 9100 --out artifacts/coe/large/stdA_$N > artifacts/coe/logs/bigk_stdA_$N.log 2>&1
  up artifacts/coe/large
fi
touch artifacts/coe/markers/post_redo_$N.done
echo "=== post_redo done $N $(date -u +%FT%TZ)"
