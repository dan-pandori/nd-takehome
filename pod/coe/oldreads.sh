#!/usr/bin/env bash
# Reads of the OLD full seeds (trajectory pend / r8, rl-continue r16; s0-s2) on the 732 tracked transfer theorems that are not
# in holdout250 (their R322 reads exist: trajectory / rl-continue plain x0, x1 at batch 2048; capability-defs J3 guided).
# Same settings as the new seeds' reads (pod/coe/read.sh: k 256, T 0.8, 96 steps, 512 tokens/action, batch 512).
# Usage: bash pod/coe/oldreads.sh <seed>        (run up to 3 seeds concurrently on one A40)
source pod/coe/env.sh
S=$1; mkdir -p ckpts/coe/old
get() { [ -s ckpts/coe/old/$2 ] || hf buckets cp $BK/$1/$2 ckpts/coe/old/$2 >/dev/null 2>&1; }
get trajectory/ckpts/tj stage1_best12_s${S}_b1200.pt
mkdir -p ckpts/coe/old/ladder
[ -s ckpts/coe/old/ladder/la_T1_best12_s${S}_r8.pt ] || hf buckets cp $BK/trajectory/ckpts/tj/ladder/la_T1_best12_s${S}_r8.pt ckpts/coe/old/ladder/la_T1_best12_s${S}_r8.pt >/dev/null 2>&1
[ -s ckpts/coe/old/ladder/la_T1_best12_s${S}_r16.pt ] || hf buckets cp $BK/rl-continue/ckpts/rc/ladder/la_T1_best12_s${S}_r16.pt ckpts/coe/old/ladder/la_T1_best12_s${S}_r16.pt >/dev/null 2>&1
md5sum ckpts/coe/old/stage1_best12_s${S}_b1200.pt ckpts/coe/old/ladder/la_T1_best12_s${S}_r8.pt ckpts/coe/old/ladder/la_T1_best12_s${S}_r16.pt
one() {   # <ckpt> <tag> <plain|guided> <seed>
  local O=artifacts/coe/eval/$2
  [ -s $O.json ] && return 0
  echo "=== read $2 $(date -u +%FT%TZ)"
  if [ "$3" = plain ]; then
    python3 state_eval.py --ckpt $1 --in data/coe/fam_extra.jsonl --k 256 --temperature 0.8 --seed $4 --batch 512 \
      --max_action 512 --max_steps 96 --out $O.jsonl --summary $O.json && gzip -f $O.jsonl
  else
    python3 guided_eval.py --ckpt $1 --arm logical --sets data/coe/fam_extra.jsonl --k 256 --seed $4 --batch 512 \
      --max_action 512 --max_steps 96 --max_rej 10 --out $O
  fi
  up artifacts/coe/eval
}
P=ckpts/coe/old/stage1_best12_s${S}_b1200.pt; R8=ckpts/coe/old/ladder/la_T1_best12_s${S}_r8.pt; R16=ckpts/coe/old/ladder/la_T1_best12_s${S}_r16.pt
one $P pend_full_s${S}_x0e plain 0
one $R16 r16_full_s${S}_x0e plain 0
one $R8 r8_full_s${S}_x0e plain 0
one $P pend_full_s${S}_x1e plain 1
one $R16 r16_full_s${S}_x1e plain 1
one $R16 r16_full_s${S}_g0e guided 0
one $P pend_full_s${S}_g0e guided 0
echo "=== oldreads s$S done $(date -u +%FT%TZ)"
