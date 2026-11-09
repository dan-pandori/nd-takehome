#!/usr/bin/env bash
# job.sh <job> <name> <repo|-> <rev> <n> <pids|-> <seed> <chunk> <chunk0> [sampler flags ...]: fetch, sample, grade.
# olmo-ifladder: pod/olmo_iffu/job.sh with the run's sampler (olmo_ifladder/sample.py, rung 4's few-shot turns) and
# artifact dir; TP 1 by default (one job per GPU, the worker sets CUDA_VISIBLE_DEVICES); repo "-" = a local model
# directory /workspace/models/<name> (the merged LoRA models), not fetched.
# env: PROBLEMS (required), TP (default 1), GPU (index for the nvidia-smi log, default 0).
J=$1; NAME=$2; R=$3; V=$4; N=$5; P=$6; S=$7; CH=$8; C0=$9; shift 9
cd /workspace/nd-takehome; A=artifacts/olmo_ifladder; TP=${TP:-1}; G=${GPU:-0}; mkdir -p $A/samples $A/graded $A/meta $A/logs
[ -n "$PROBLEMS" ] || { echo "PROBLEMS unset"; exit 1; }
[ "$R" = "-" ] || bash pod/olmo_ifomega/fetch.sh "$R" "$V" "$NAME" || { echo "FETCH_FAIL $(date -u +%FT%TZ)"; exit 1; }
PIDS=""; [ "$P" != "-" ] && PIDS="--pids $P"
( while sleep 30; do echo "$(date -u +%T) $(nvidia-smi -i $G --query-gpu=memory.used,utilization.gpu --format=csv,noheader | tr '\n' ' ')"; done ) > $A/logs/${J}_smi.log 2>&1 &
SMI=$!
echo "JOB_START $J $(date -u +%FT%TZ) tp=$TP gpu=$G cvd=$CUDA_VISIBLE_DEVICES problems=$PROBLEMS extra=[$*]"
VLLM_ATTENTION_BACKEND=FLASH_ATTN python -u olmo_ifladder/sample.py --model /workspace/models/$NAME --tokenizer /workspace/models/tok \
  --name "$NAME" --rev "$V" --problems $PROBLEMS $PIDS --n $N --chunk $CH --chunk0 $C0 --seed $S --job $J --tp $TP \
  --out $A/samples/$J.jsonl.gz --meta $A/meta/$J.json "$@"
rc=$?; kill $SMI 2>/dev/null
python olmo_ifomega/grade.py $A/samples/$J.jsonl.gz $PROBLEMS $A/graded/$J.jsonl
echo "JOB_DONE $J rc=$rc $(date -u +%FT%TZ)"; [ $rc -eq 0 ] && touch $A/meta/$J.done
