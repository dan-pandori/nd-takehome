#!/usr/bin/env bash
# job.sh <job> <name> <repo> <rev> <n> <pids|-> <seed> <chunk> <chunk0> [sampler flags ...]: fetch, sample, grade.
# env: PROBLEMS (default olmo_rlzero_if/problems.jsonl); TP (default: all GPUs of the pod); TOK (tokenizer dir, default
#      /workspace/models/tok = the RL-Zero-IF tokenizer; the base-tokenizer diagnostic sets /workspace/models/base).
J=$1; NAME=$2; R=$3; V=$4; N=$5; P=$6; S=$7; CH=$8; C0=$9; shift 9
cd /workspace/nd-takehome; A=artifacts/olmo_rlzero_if; PROBLEMS=${PROBLEMS:-olmo_rlzero_if/problems.jsonl}; TP=${TP:-$(nvidia-smi -L | wc -l)}
bash pod/olmo_rlzero_if/fetch.sh "$R" "$V" "$NAME" || { echo "FETCH_FAIL $(date -u +%FT%TZ)"; exit 1; }
PIDS=""; [ "$P" != "-" ] && PIDS="--pids $P"
( while sleep 30; do echo "$(date -u +%T) $(nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader | tr '\n' ' ')"; done ) > $A/logs/${J}_smi.log 2>&1 &
SMI=$!
echo "JOB_START $J $(date -u +%FT%TZ) tp=$TP extra=[$*]"
VLLM_ATTENTION_BACKEND=FLASH_ATTN python -u olmo_rlzero_if/sample.py --model /workspace/models/$NAME --tokenizer ${TOK:-/workspace/models/tok} \
  --name "$NAME" --rev "$V" --problems $PROBLEMS $PIDS --n $N --chunk $CH --chunk0 $C0 --seed $S --job $J --tp $TP \
  --out $A/samples/$J.jsonl.gz --meta $A/meta/$J.json "$@"
rc=$?; kill $SMI 2>/dev/null
python olmo_rlzero_if/grade.py $A/samples/$J.jsonl.gz $PROBLEMS $A/graded/$J.jsonl
echo "JOB_DONE $J rc=$rc $(date -u +%FT%TZ)"; [ $rc -eq 0 ] && touch $A/meta/$J.done
