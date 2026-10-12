#!/usr/bin/env bash
# Old full seeds s0-s2 on the 100 tracked transfer theorems inside holdout250 (data/coe/track_in_h250.jsonl), same settings as
# every read of this run (k 256, T 0.8, 96 steps, 512 tokens/action, batch 512), so the 106 strict held-out members are read
# identically for all 12 seeds.  Runs after r0_queue.sh.
source pod/coe/env.sh
until [ -e artifacts/coe/markers/r0_queue.done ]; do sleep 60; done
for S in 0 1 2; do
  P=ckpts/coe/old/stage1_best12_s${S}_b1200.pt; R8=ckpts/coe/old/ladder/la_T1_best12_s${S}_r8.pt; R16=ckpts/coe/old/ladder/la_T1_best12_s${S}_r16.pt
  for spec in "$P pend x0 plain 0" "$P pend x1 plain 1" "$P pend g0 guided 0" "$R8 r8 x0 plain 0" "$R16 r16 x0 plain 0" "$R16 r16 x1 plain 1" "$R16 r16 g0 guided 0"; do
    set -- $spec; O=artifacts/coe/eval/${2}_full_s${S}_${3}h
    [ -s $O.json ] && continue
    if [ "$4" = plain ]; then
      python3 state_eval.py --ckpt $1 --in data/coe/track_in_h250.jsonl --k 256 --temperature 0.8 --seed $5 --batch 512 \
        --max_action 512 --max_steps 96 --out $O.jsonl --summary $O.json && gzip -f $O.jsonl
    else
      python3 guided_eval.py --ckpt $1 --arm logical --sets data/coe/track_in_h250.jsonl --k 256 --seed $5 --batch 512 \
        --max_action 512 --max_steps 96 --max_rej 10 --out $O
    fi
  done
done
up artifacts/coe/eval
touch artifacts/coe/markers/oldreads_h100.done
echo OLDREADS_H100_DONE
