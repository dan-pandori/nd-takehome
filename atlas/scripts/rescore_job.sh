#!/usr/bin/env bash
# evidence-atlas re-score (pod): whole-proof lean_seq checkpoints on textbook72 (k 256), dev1108 (k 64), holdout250 (k 256),
# T 0.8, sample seed 0, batch 4096, max_new 512 — the settings of best-state's reads (pod/bs/read.sh) and Robbie's
# harness, so the rows land in the same apples group. Lean alone decides (eval_set -> lean_judge).
# Usage: bash atlas/scripts/rescore_job.sh <label>=<bucket path of ckpt> ...   (restartable: done reads are skipped)
export PATH=$HOME/.elan/bin:$PATH OMP_NUM_THREADS=8 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export LEAN_GATE_WORKERS=${LEAN_GATE_WORKERS:-12} ND_SAMPLE_PATH=fast ND_RUN_ID=evidence-atlas MAXNEW=512
cd /workspace/nd-takehome || exit 1
[ -f eval_set.py ] || tar xzf podcode.tgz
mkdir -p ckpts/atlas artifacts/atlas/eval artifacts/atlas/logs
BK=hf://buckets/dan-pandori/nd-rl
for spec in "$@"; do
  L=${spec%%=*}; P=${spec#*=}; CK=ckpts/atlas/$L.pt
  [ -s $CK ] || hf buckets cp $BK/$P $CK >/dev/null || { echo "DOWNLOAD FAILED $L"; continue; }
  for R in tb72 dev h250; do
    O=artifacts/atlas/eval/${L}__$R; [ -s $O.json ] && { echo "skip $L $R"; continue; }
    case $R in
      tb72) IN=data/bs/textbook72.jsonl; K=256; LF=reference_lines ;;
      dev)  IN=data/bs/dev1108.jsonl;    K=64;  LF=n_lines ;;
      h250) IN=data/bs/holdout250.jsonl; K=256; LF=n_lines ;;
    esac
    echo "=== $L $R $(date -u +%FT%TZ)"
    python3 atlas/scripts/rescore.py --ckpt $CK --in $IN --k $K --temperature 0.8 --seed 0 --batch 4096 --lenfield $LF \
      --out $O.jsonl --summary $O.json > artifacts/atlas/logs/${L}__$R.log 2>&1 || echo "READ FAILED $L $R"
    echo "=== done $L $R $(date -u +%FT%TZ) $(grep -m1 -o '"solved"[^,]*' $O.json 2>/dev/null)"
  done
done
