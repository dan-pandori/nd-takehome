#!/usr/bin/env bash
# Priority 2: knockout s1, rounds 25-32, by create-or-elicit's Addendum 6 procedure (a --resume of the same ladder, every
# setting unchanged, replay from K12-), from the r24 files in create-or-elicit's bucket folder (read-only); then the plain
# r32 read on read1054 and the per-round analysis through r32 (new file la_ko_s1_r32.json).  Usage: bash pod/d01/ko_ext.sh
source pod/d01/env.sh
N=ko_s1; L=artifacts/coe/ladder/la_$N; SRC=$BK/create-or-elicit
mkdir -p $L ckpts/coe/ladder artifacts/coe/rounds
echo "=== ko_ext fetch $(date -u +%FT%TZ)"
for f in args.json args_r1-16.json found_24.jsonl found_transfer_24.jsonl $(seq -f "round_%g.json" 1 24) $(seq -f "alloc_%g.json" 1 24); do
  [ -s $L/$f ] || [ -s $L/found_25.jsonl ] || hf buckets cp $SRC/artifacts/coe/ladder/la_$N/$f $L/$f > /dev/null 2>&1 || echo "fetch failed $f"
done
for f in coe/ladder/la_${N}_r24.pt coe/stage1_$N.pt; do
  [ -s ckpts/$f ] || hf buckets cp $SRC/ckpts/$f ckpts/$f > /dev/null 2>&1 || echo "fetch failed $f"
done
md5sum ckpts/coe/ladder/la_${N}_r24.pt ckpts/coe/stage1_$N.pt data/coe/train_k12ko.jsonl
ls -la $L | head -5; ls $L/round_*.json | wc -l; ls $L/alloc_*.json | wc -l
[ -s $L/args_r17-24.json ] || cp $L/args.json $L/args_r17-24.json
last=$(ls $L/round_*.json | sed 's/.*round_//; s/.json//' | sort -n | tail -1)
ls $L/found_$last.jsonl $L/found_transfer_$last.jsonl $L/alloc_$last.json ckpts/coe/ladder/la_${N}_r$last.pt || { echo "KO_EXT FAILED missing resume files"; exit 1; }
if [ "$last" -lt 32 ]; then
  echo "=== ko_ext ladder from r$((last+1)) $(date -u +%FT%TZ)"
  ND_ARM=ko ND_SEED=1 LEAN_GATE_DUMP=artifacts/coe/dump/la_${N}_r25-32.jsonl python3 state_ladder_ei.py --init ckpts/coe/stage1_$N.pt \
    --name la_$N --seed 1 --batch 1024 --train data/coe/train_k12ko.jsonl --heldout data/coe/heldout1000.jsonl \
    --transfer data/coe/transfer_track832.jsonl --outdir artifacts/coe/ladder --ckptdir ckpts/coe/ladder \
    --resume --start_round $((last+1)) --rounds $((32-last)) || { echo "KO_EXT FAILED ladder $(date -u +%FT%TZ)"; exit 1; }
  cp $L/args.json $L/args_r$((last+1))-32.json
fi
touch artifacts/coe/markers/ladder_ko_ext.done
echo "=== ko_ext rounds analysis $(date -u +%FT%TZ)"
nice -n 10 python3 coe/coe_rounds.py --dir $L --out artifacts/coe/rounds/la_${N}_r32.json > artifacts/coe/logs/rounds_la_${N}_r32.log 2>&1 || echo "ROUNDS FAILED"
nice -n 10 python3 coe/d01_heldout_proofs.py --dir $L --out artifacts/coe/rounds/heldout_proofs_la_${N}_r32.jsonl.gz >> artifacts/coe/logs/rounds_la_${N}_r32.log 2>&1 || echo "PROOFS FAILED"
up artifacts/coe/rounds
R=artifacts/coe/eval/r32_${N}_x0
echo "=== read r32_${N}_x0 $(date -u +%FT%TZ)"
[ -s $R.json ] || { python3 state_eval.py --ckpt ckpts/coe/ladder/la_${N}_r32.pt --in data/coe/read1054.jsonl --k 256 --temperature 0.8 \
  --seed 0 --batch 512 --max_action 512 --max_steps 96 --out $R.jsonl --summary $R.json > $R.log 2>&1 && gzip -f $R.jsonl; }
up artifacts/coe/eval
gzip -f artifacts/coe/dump/la_${N}_r25-32.jsonl 2>/dev/null
up $L
hf buckets sync artifacts/coe/dump $BK/coe-dose01/artifacts/coe/dump --include '*.gz' >/dev/null 2>&1 || echo "DUMP UPLOAD FAILED"
up artifacts/coe/logs
touch artifacts/coe/markers/ko_ext.done
echo "=== ko_ext done $(date -u +%FT%TZ)"
