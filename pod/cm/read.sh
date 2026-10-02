#!/usr/bin/env bash
# Read-outs of one checkpoint.  Usage: bash pod/cm/read.sh <ckpt> <label> <reads...>
#   reads: tb72 dev h250 rr600 long2 held     (restartable: a read whose summary exists is skipped)
# Settings: T 0.8, seed 0, max_action 512, max_steps 96 for every sampled read; held-out greedy k 1 T 0.
# LEAN_GATE_DUMP keeps the literal text of every sample (gzipped; bucket only).
source pod/cm/env.sh
CK=$1; L=$2; shift 2; B=${B:-2048}; MA=${MA:-512}; MS=${MS:-96}; X=${X:-}; mkdir -p artifacts/cm/eval artifacts/cm/logs/read   # MA/MS/X: cap diagnostics
for R in "$@"; do
  O=artifacts/cm/eval/${L}__$R$X; [ -s $O.json ] && { echo "skip $L $R"; continue; }
  echo "=== $L $R $(date -u +%FT%TZ)"; export LEAN_GATE_DUMP=artifacts/cm/dump/${L}__$R$X.jsonl
  case $R in
    tb72)  python3 state_eval.py --ckpt $CK --in data/bs/textbook72.jsonl --k 256 --temperature 0.8 --seed 0 --batch $B \
             --max_action $MA --max_steps $MS --lenfield reference_lines --out $O.jsonl.tmp --summary $O.json.tmp ;;
    dev)   python3 state_eval.py --ckpt $CK --in data/bs/dev1108.jsonl --k 64 --temperature 0.8 --seed 0 --batch $B \
             --max_action $MA --max_steps $MS --lenfield n_lines --out $O.jsonl.tmp --summary $O.json.tmp ;;
    h250)  python3 state_eval.py --ckpt $CK --in data/bs/holdout250.jsonl --k 256 --temperature 0.8 --seed 0 --batch $B \
             --max_action $MA --max_steps $MS --lenfield n_lines --out $O.jsonl.tmp --summary $O.json.tmp ;;
    held)  python3 state_eval.py --ckpt $CK --in data/p2/heldout.jsonl --k 1 --temperature 0 --batch $B \
             --out $O.jsonl.tmp --summary $O.json.tmp ;;
    rr600) python3 lpool_reread.py --ckpt $CK --in data/ladder/transfer_long_rr600.jsonl --k 256 --temperature 0.8 --seed 0 \
             --batch $B --max_action $MA --max_steps $MS --lenfield L_true_lb --out $O.jsonl.tmp --summary $O.json.tmp ;;
    long2) python3 lpool_reread.py --ckpt $CK --in data/ladder/transfer_long2.jsonl --k 256 --temperature 0.8 --seed 0 \
             --batch $B --max_action $MA --max_steps $MS --lenfield L_true_lb --out $O.jsonl.tmp --summary $O.json.tmp ;;
  esac > artifacts/cm/logs/read/${L}__$R$X.log 2>&1 || { echo "READ FAILED $L $R"; continue; }
  mv $O.jsonl.tmp $O.jsonl; mv $O.json.tmp $O.json
  [ -s $LEAN_GATE_DUMP ] && gzip -f $LEAN_GATE_DUMP
  echo "=== done $L $R $(date -u +%FT%TZ) $(grep -m1 -o 'solved[^,]*' $O.json | head -1)"
done
up artifacts/cm
hf buckets sync artifacts/cm/dump $BK/best-state/artifacts/cm/dump --include '*.gz' >/dev/null 2>&1 || echo "DUMP UPLOAD FAILED"
