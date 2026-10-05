#!/usr/bin/env bash
# J1 stage 2 (pre-registered in log.md before launch): exact 33-name-base teacher-forced scores of the stage-2 targets
# of seed S (top 20 known proofs per theorem under each of pend / r8 / r16 by stage-1 score, plus every distinct proof
# pend found in J2) under init / pend / r8 / r16.  T 1.0 and T 0.8.  Resumable per checkpoint.
. pod/cd/env.sh
S=$1
printf "s${S}_init $CK/s${S}_init.pt\ns${S}_pend $CK/s${S}_pend.pt\ns${S}_r8 $CK/s${S}_r8.pt\ns${S}_r16 $CK/s${S}_r16.pt\n" > artifacts/cd/j1/ckpts_s${S}.txt
echo "$(date -u +%FT%TZ) start stage2 s$S"
ND_ARM=j1_b33 python3 cd_score.py --targets artifacts/cd/j1/s2targets_s${S}.jsonl --ckpts artifacts/cd/j1/ckpts_s${S}.txt \
  --out artifacts/cd/j1/b33_s${S} --nbases 33
python3 capability_defs/analysis/cd_j1_compact.py artifacts/cd/j1/b33_s${S}
echo "$(date -u +%FT%TZ) end stage2 s$S"
