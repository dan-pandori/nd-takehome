#!/usr/bin/env bash
# J1 (pre-registered, preregistration/capability-defs.md): teacher-forced log p of every known proof of each seed's hard
# + calibration theorems under init / pend / r8 / r16, at NB name bases (stage 1: NB = 1).  Resumable per part/ckpt.
. pod/cd/env.sh
S=$1; NB=${2:-1}
printf "s${S}_init $CK/s${S}_init.pt\ns${S}_pend $CK/s${S}_pend.pt\ns${S}_r8 $CK/s${S}_r8.pt\ns${S}_r16 $CK/s${S}_r16.pt\n" > artifacts/cd/j1/ckpts_s${S}.txt
for T in artifacts/cd/j1/targets_s${S}_p*.jsonl; do
  P=$(basename $T .jsonl); P=${P#targets_}
  echo "$(date -u +%FT%TZ) start $P nb $NB"
  ND_ARM=j1_b${NB} python3 cd_score.py --targets $T --ckpts artifacts/cd/j1/ckpts_s${S}.txt --out artifacts/cd/j1/b${NB}_${P} --nbases $NB
  echo "$(date -u +%FT%TZ) end $P rc=$?"
done
