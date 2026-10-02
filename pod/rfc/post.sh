#!/usr/bin/env bash
# On a ladder pod, after its ladder: r8 reads (sample seeds 1, 0), then teacher-forced scoring (tj_score.py) of the 315
# references + this ladder's eventual proofs under r0 (the start), r2, r4, r8 and the matching control's r8.
# Usage: bash pod/rfc/post.sh <seed> <start>
source pod/rfc/env.sh; source pod/rfc/ckpt.sh
S=$1; P=$2; L=s${S}_$P; N=la_T1_best12_$L; C=rc_best12_$L
until [ -f artifacts/rfc/L_$L.done ]; do [ -f artifacts/rfc/L_$L.fail ] && { echo "ladder failed"; exit 1; }; sleep 120; done
for SS in 1 0; do
  bash pod/rfc/read.sh ckpts/rfc/ladder/${N}_r8.pt ${L}_r8 $SS tb72 h250
  [ -s artifacts/rfc/eval/${L}_r8__tb72_x$SS.json ] && [ -s artifacts/rfc/eval/${L}_r8__h250_x$SS.json ] && touch artifacts/rfc/eval/.done_${L}_r8_x$SS
done
fetch rl-from-ckpt/ckpts/rfc/control/${C}_r8.pt ckpts/rfc/control/${C}_r8.pt     # waits for the control
mkdir -p artifacts/rfc/score data/rfc; K=artifacts/rfc/score/ckpts_$L.txt
{ echo "${L}_r0 $(startck $S $P)"; for r in 2 4 8; do echo "${L}_r$r ckpts/rfc/ladder/${N}_r$r.pt"; done; echo "${L}_c8 ckpts/rfc/control/${C}_r8.pt"; } > $K
for f in $(cut -d' ' -f2 $K); do [ -s $f ] || { echo "MISSING $f"; exit 1; }; done
md5sum $(cut -d' ' -f2 $K) > artifacts/rfc/score/ckpts_$L.md5
grep "^${L}_r8 " $K > artifacts/rfc/score/ckpt_r8_$L.txt
python3 tj_targets.py cands --label $L --root artifacts/rfc --data data/rfc || exit 1
python3 tj_score.py --targets data/rfc/cand_$L.jsonl --ckpts artifacts/rfc/score/ckpt_r8_$L.txt --out artifacts/rfc/score/cand_$L || exit 1
python3 tj_targets.py select --label $L --root artifacts/rfc --data data/rfc --refs data/rfc/ref_targets.jsonl || exit 1
python3 tj_score.py --targets data/rfc/targets_$L.jsonl --ckpts $K --out artifacts/rfc/score/$L --lean || exit 1
mkdir -p artifacts/rfc/targets; cp data/rfc/cand_$L.jsonl data/rfc/eventual_$L.jsonl data/rfc/targets_$L.jsonl artifacts/rfc/targets/
up artifacts/rfc
echo "=== post $L done $(date -u +%FT%TZ)"
