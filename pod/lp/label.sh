#!/usr/bin/env bash
# long-pool: generate + staged minlen labelling.  Usage: label.sh <tag> <workers> <tries_per_worker> <seed> [gen_min] [gen_max] [extra gen flags...]
# Output under data/lp/<tag>*.  Stage A bound 10/5 s, B 12/30 s, C 14/120 s, D 16/600 s; each stage runs on the previous
# stage's None-without-timeout records only.  Restartable: a stage whose output is complete is skipped.
cd /workspace/nd-takehome; export OMP_NUM_THREADS=1
T=$1; W=$2; TR=$3; S=$4; MN=${5:-12}; MX=${6:-40}; shift 6 2>/dev/null; X="$*"
mkdir -p data/lp artifacts/lp; L=artifacts/lp/$T.log
echo "$(date -u +%FT%TZ) START $T W=$W tries=$TR seed=$S len=$MN-$MX extra=$X" >> $L
if [ ! -s data/lp/$T.jsonl ]; then
  python3 make_coverage_sets.py gen --long --min $MN --max $MX --out data/lp/raw_$T --workers $W --tries $TR --cap_np 1000000000 --cap_pat 1000000000 --seed $S $X >> $L 2>&1
  python3 make_coverage_sets.py merge --glob "data/lp/raw_$T.w*.jsonl" --out data/lp/$T.jsonl --prefix $T >> $L 2>&1
  rm -f data/lp/raw_$T.w*.jsonl
fi
echo "$(date -u +%FT%TZ) GEN_DONE $(wc -l < data/lp/$T.jsonl)" >> $L
prev=data/lp/$T.jsonl
for st in "A 10 5" "B 12 30" "C 14 120" "D 16 600"; do
  set -- $st; out=data/lp/${T}_ml$2.jsonl
  if [ ! -s $out ] || [ $(wc -l < $out) -lt $(wc -l < $prev) ]; then
    python3 minlen.py --in $prev --out $out --bound $2 --time $3 --procs $W >> $L 2>&1
  fi
  python3 - $prev $out data/lp/${T}_cand$2.jsonl <<'PY' >> $L
import json, sys
src, lab, out = sys.argv[1:]
none = {json.loads(l)['prompt'] for l in open(lab) if json.loads(l)['min_lines_ub'] is None and not json.loads(l)['timeout'] and not json.loads(l).get('error')}
n = 0
with open(out, 'w') as fo:
    for l in open(src):
        if json.loads(l)['prompt'] in none: fo.write(l); n += 1
print('stage', lab, 'None-without-timeout ->', n)
PY
  echo "$(date -u +%FT%TZ) STAGE_$1_DONE $(wc -l < data/lp/${T}_cand$2.jsonl)" >> $L
  prev=data/lp/${T}_cand$2.jsonl
done
echo "$(date -u +%FT%TZ) LABEL_DONE $T" >> $L
