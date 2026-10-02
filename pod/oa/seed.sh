#!/usr/bin/env bash
# organism-analysis Q3 forward passes for one seed: c12 (14 ckpts), c6 (11), rfc (4 starts x 3).  Usage: seed.sh <S> [batch]
. pod/oa/env.sh
S=$1; B=${2:-2048}
for L in c12 c6 rfc_p1600 rfc_p5000 rfc_p12000 rfc_p16000; do
  case $L in rfc_*) X=${L#rfc_}; CK=data/oa/ck_rfc_s${S}_${X}.txt; TG=data/oa/targets_rfc_s${S}_${X}.jsonl;;
             *) CK=data/oa/ck_${L}_s${S}.txt; TG=data/oa/targets_${L}_s${S}.jsonl;; esac
  LOC=artifacts/oa/logs/ck_${L}_s${S}.local.txt; : > $LOC
  while read lab p; do fetch "$p"; echo "$lab ckpts/$p" >> $LOC; md5sum "ckpts/$p" | cut -c1-12 | sed "s#^#$lab #" >> artifacts/oa/logs/ck_md5_s${S}.txt; done < $CK
  python3 oa/oa_entropy.py --ckpts $LOC --targets $TG --out artifacts/oa/entropy/${L}_s${S} --batch $B
  up artifacts/oa
done
echo "SEED_DONE $S $(date -u +%FT%TZ)"; touch artifacts/oa/seed${S}.done; up artifacts/oa
