#!/usr/bin/env bash
# Addendum 4: C4 (knockout s1 base on its 18 strict converse-contraposition members + la_transfer_916, s3 base on 916;
# 18,432 attempts each, no early stopping) and C5 (Lean over every pre-filter rejection in knockout s1's ladder dump).
source pod/coep/env.sh
mkdir -p artifacts/coe_paper/c4 artifacts/coe_paper/c5
export LEAN_BIN=$HOME/.elan/toolchains/leanprover--lean4---v4.34.1/bin/lean
for S in 1 3; do [ -s ckpts/coe_paper/stage1_ko_s$S.pt ] || hf buckets cp $BK/create-or-elicit/ckpts/coe/stage1_ko_s$S.pt ckpts/coe_paper/stage1_ko_s$S.pt; done
md5sum ckpts/coe_paper/stage1_ko_s1.pt ckpts/coe_paper/stage1_ko_s3.pt
for S in 1 3; do
  [ -s artifacts/coe_paper/c4/ko_s$S.json ] || python3 coe/coe_bigk.py --ckpt ckpts/coe_paper/stage1_ko_s$S.pt \
    --in data/coe_paper/c4_ko_s$S.jsonl --n 18432 --chunk 1024 --seed0 9500 --batch 1024 --stop_successes 0 \
    --out artifacts/coe_paper/c4/ko_s$S > artifacts/coe_paper/logs/c4_ko_s$S.log 2>&1 || echo "C4 FAILED s$S"
done
up artifacts/coe_paper/c4
echo "=== C4 done $(date -u +%FT%TZ)"
[ -s data/coe_paper/dump_ko_s1.jsonl.gz ] || hf buckets cp $BK/create-or-elicit/artifacts/coe/dump/la_ko_s1.jsonl.gz data/coe_paper/dump_ko_s1.jsonl.gz
ls -la data/coe_paper/dump_ko_s1.jsonl.gz; $LEAN_BIN --version
python3 paper/scripts/c5_prefilter_lean.py data/coe_paper/dump_ko_s1.jsonl.gz artifacts/coe_paper/c5/prefilter_ko_s1.json 4 > artifacts/coe_paper/logs/c5.log 2>&1 || echo "C5 FAILED"
up artifacts/coe_paper/c5
echo "=== C5 done $(date -u +%FT%TZ)"; touch artifacts/coe_paper/LANE_E_DONE
