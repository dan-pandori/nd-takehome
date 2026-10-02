#!/usr/bin/env bash
# trajectory-cap6 (added after the per-stratum truncation table): re-read, at 2x caps (max_action 1024, max_steps 192), the
# theorems whose group the caps could have changed — C at r8 (C -> B) and B at pend (B -> A) — with sample seed 0, k 256,
# T 0.8 (the group-defining draw).  Inputs data/tj6/capdiag_s<S>_<ck>_<pool>.jsonl.  Usage: bash pod/tj6/capdiag.sh <seed>
source pod/tj6/env.sh
S=$1; mkdir -p artifacts/tj6/capdiag
for ck in r8 pend; do
  CK=$([ $ck = r8 ] && echo ckpts/tj6/ladder/la_T1_best6_s${S}_r8.pt || echo ckpts/tj6/stage1_best6_s${S}_b1200.pt)
  [ -s $CK ] || hf buckets cp $BK/trajectory-cap6/$CK $CK >/dev/null 2>&1 || { echo "MISSING $CK"; exit 1; }
  for p in tb72 h250; do
    LF=$([ $p = tb72 ] && echo reference_lines || echo n_lines); O=artifacts/tj6/capdiag/s${S}_${ck}__${p}_x0_2x
    [ -s $O.json ] && continue
    python3 state_eval.py --ckpt $CK --in data/tj6/capdiag_s${S}_${ck}_$p.jsonl --k 256 --temperature 0.8 --seed 0 --batch 1024 \
      --max_action 1024 --max_steps 192 --lenfield $LF --out $O.jsonl --summary $O.json > artifacts/tj6/logs/capdiag_s${S}_${ck}_$p.log 2>&1 \
      || { echo "FAILED $O"; exit 1; }
    echo "=== $O $(grep -m1 -o '"solved": [0-9]*' $O.json)"
  done
done
up artifacts/tj6
