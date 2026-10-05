#!/usr/bin/env bash
# J8 (pre-registered in log.md before launch): the elicitation share by start.  For seed S, every known proof (all reads
# of all models, incl. rl-from-ckpt ladders, and references) of each theorem that some rl-from-ckpt ladder (start p1600 /
# p5000 / p12000 / p16000) solves at r8 while its start fails it (0 / 512), scored at one name base (stage-1 bound,
# b0 - ln 33) under the four start checkpoints.  Resumable per part / checkpoint.
. pod/cd/env.sh
S=$1
printf "s${S}_p1600 $CK/s${S}_p1600.pt\ns${S}_p5000 $CK/s${S}_p5000.pt\ns${S}_p12000 $CK/s${S}_p12000.pt\ns${S}_p16000 $CK/s${S}_p16000.pt\n" > artifacts/cd/j8/ckpts_s${S}.txt
for T in artifacts/cd/j8/targets_s${S}_p*.jsonl; do
  P=$(basename $T .jsonl); P=${P#targets_}
  echo "$(date -u +%FT%TZ) start $P"
  ND_ARM=j8_b1 python3 cd_score.py --targets $T --ckpts artifacts/cd/j8/ckpts_s${S}.txt --out artifacts/cd/j8/b1_${P} --nbases 1
  python3 capability_defs/analysis/cd_j1_compact.py artifacts/cd/j8/b1_${P} && rm -f artifacts/cd/j8/b1_${P}/s*.jsonl
  echo "$(date -u +%FT%TZ) end $P"
done
