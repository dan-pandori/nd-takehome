#!/usr/bin/env bash
# Phase 1 (style-edl): the reads that build the theorem pool and the sampled streams. Restartable (job.sh skips done jobs).
. pod/sedl/env.sh
J=pod/sedl/job.sh; TF=data/kalmar/tf1200_kal_sl.jsonl; O=artifacts/style_edl/reads
C="--max_steps 1024 --max_action 512 --batch 1024"
export LEAN_GATE_LOG=artifacts/style_edl/logs/lean_gate_reads.jsonl
for s in 0 1 2; do
  $J g_base_s$s python3 kalmar/kal_free.py --ckpt ckpts/bs/stage1_best12_s${s}_b1200.pt --in $TF --k 1 --temperature 0 --seed 0 $C --out $O/base_s${s}__tf1200_greedy.json
  $J g_r8_s$s python3 kalmar/kal_free.py --ckpt ckpts/bs/ladder/la_T1_best12_s${s}_r8.pt --in $TF --k 1 --temperature 0 --seed 0 $C --out $O/r8_s${s}__tf1200_greedy.json
done
for s in 0 1 2; do
  $J k32_base_s$s python3 guided_eval.py --ckpt ckpts/bs/stage1_best12_s${s}_b1200.pt --arm plain --k 32 --seed 1 --temperature 0.8 --sets $TF $C --out $O/base_s${s}__tf1200_plain_k32_seed1
  $J k4_base_s$s python3 guided_eval.py --ckpt ckpts/bs/stage1_best12_s${s}_b1200.pt --arm plain --k 4 --seed 3 --temperature 0.8 --sets $TF $C --out $O/base_s${s}__tf1200_plain_k4_seed3
done
up artifacts/style_edl/reads
echo "QUEUE DONE $(date -u +%FT%TZ)"
