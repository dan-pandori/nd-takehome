#!/usr/bin/env bash
# E2's second estimate: teacher-forced log p (coe/cd_score.py = capability-defs cd_score, one name base = a valid lower
# bound, b0 - ln 33) of the full arm's known proofs of the strict sigma-covered members, under the six knockout bases and
# trajectory's full pend s0 (reference).  Runs after Phase 2 on coe-r1.
source pod/coe/env.sh
until grep -q PHASE2_DONE artifacts/coe/logs/phase2.log 2>/dev/null; do sleep 60; done
mkdir -p artifacts/coe/score ckpts/coe/old
for S in 0 1 2 3 4 5; do
  [ -s ckpts/coe/stage1_ko_s$S.pt ] || hf buckets cp $BK/create-or-elicit/ckpts/coe/stage1_ko_s$S.pt ckpts/coe/stage1_ko_s$S.pt >/dev/null 2>&1
done
[ -s ckpts/coe/old/stage1_best12_s0_b1200.pt ] || hf buckets cp $BK/trajectory/ckpts/tj/stage1_best12_s0_b1200.pt ckpts/coe/old/stage1_best12_s0_b1200.pt >/dev/null 2>&1
md5sum ckpts/coe/stage1_ko_s*.pt ckpts/coe/old/stage1_best12_s0_b1200.pt
{ for S in 0 1 2 3 4 5; do echo "ko_s$S ckpts/coe/stage1_ko_s$S.pt"; done; echo "full_s0 ckpts/coe/old/stage1_best12_s0_b1200.pt"; } > artifacts/coe/score/ckpts.txt
gunzip -kf data/coe/known_targets.jsonl.gz
python3 coe/cd_score.py --targets data/coe/known_targets.jsonl --ckpts artifacts/coe/score/ckpts.txt --out artifacts/coe/score/known_b1 --nbases 1 \
  > artifacts/coe/logs/score_known.log 2>&1
gzip -f artifacts/coe/score/known_b1/*.jsonl
up artifacts/coe/score
echo SCORE_DONE
