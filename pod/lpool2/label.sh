#!/usr/bin/env bash
# long-pool-2: generate + staged minlen labelling, long-pool's stages A-D plus stage E (bound 17 / 1,800 s).
# Usage: label.sh <tag> <workers> <tries_per_worker> <seed> [gen_min] [gen_max]      Output data/lp2/<tag>*.
# Time limits are CPU seconds per theorem (pod/lpool2/minlen_cpu.py; from 21:55 UTC, chunks started before used wall seconds).
# Each stage runs on the previous stage's None-without-timeout records.  Restartable (a complete stage is skipped).
# calib mode: label.sh calib <workers>  -> stage E only, on data/ladder/transfer_long_ge17.jsonl.
cd /workspace/nd-takehome; export OMP_NUM_THREADS=1
T=$1; W=$2; TR=$3; S=$4; MN=${5:-32}; MX=${6:-90}
mkdir -p data/lp2 artifacts/lpool2; L=artifacts/lpool2/$T.log
echo "$(date -u +%FT%TZ) START $T W=$W tries=$TR seed=$S len=$MN-$MX" >> $L
if [ "$T" = calib ]; then
  cp data/ladder/transfer_long_ge17.jsonl data/lp2/calib_cand16.jsonl; STAGES="E 17 1800"; prev=data/lp2/calib_cand16.jsonl
else
  if [ ! -s data/lp2/$T.jsonl ]; then
    python3 make_coverage_sets.py gen --long --min $MN --max $MX --out data/lp2/raw_$T --workers $W --tries $TR --cap_np 1000000000 --cap_pat 1000000000 --seed $S >> $L 2>&1
    python3 make_coverage_sets.py merge --glob "data/lp2/raw_$T.w*.jsonl" --out data/lp2/$T.jsonl --prefix $T >> $L 2>&1
    rm -f data/lp2/raw_$T.w*.jsonl
  fi
  echo "$(date -u +%FT%TZ) GEN_DONE $(wc -l < data/lp2/$T.jsonl)" >> $L
  STAGES="A 10 5|B 12 30|C 14 120|D 16 600|E 17 1800"; prev=data/lp2/$T.jsonl
fi
IFS='|'; for st in $STAGES; do IFS=' '
  set -- $st; out=data/lp2/${T}_ml$2.jsonl
  if [ ! -s $out ] || [ $(wc -l < $out) -lt $(wc -l < $prev) ]; then
    P=$W; [ $1 = E ] && P=$(( W < ${EW:-3} ? W : ${EW:-3} ))   # bound-17 searches take 5-8 GB each
    [ -s $prev ] && python3 pod/lpool2/minlen_cpu.py --in $prev --out $out --bound $2 --time $3 --procs $P >> $L 2>&1 || touch $out
  fi
  [ $1 = E ] && break
  python3 - $prev $out data/lp2/${T}_cand$2.jsonl <<'PY' >> $L
import json, sys
src, lab, out = sys.argv[1:]
none = {json.loads(l)['prompt'] for l in open(lab) if json.loads(l)['min_lines_ub'] is None and not json.loads(l)['timeout'] and not json.loads(l).get('error')}
n = 0
with open(out, 'w') as fo:
    for l in open(src):
        if json.loads(l)['prompt'] in none: fo.write(l); n += 1
print('stage', lab, 'None-without-timeout ->', n)
PY
  echo "$(date -u +%FT%TZ) STAGE_$1_DONE $(wc -l < data/lp2/${T}_cand$2.jsonl)" >> $L
  prev=data/lp2/${T}_cand$2.jsonl; IFS='|'
done
echo "$(date -u +%FT%TZ) LABEL_DONE $T" >> $L
