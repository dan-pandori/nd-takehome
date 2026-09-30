#!/usr/bin/env bash
# Smoke: (1) the control path is byte-identical to the pre-change driver (_orig_ladder.py, not committed) on 1 small round;
# (2) the supply arm runs 2 small rounds.  Usage: bash pod/fsup/smoke.sh
source pod/fsup/env.sh; export ND_OFFLINE=1
D=artifacts/fsup/smoke; mkdir -p $D data/fsup/smoke
head -300 data/ladder/rl_targets.jsonl > data/fsup/smoke/t300.jsonl; head -20 data/ladder/transfer.jsonl > data/fsup/smoke/tr20.jsonl
C="--init ckpts/sc12/stage1_SN12_s0.pt --seed 0 --batch 2048 --targets data/fsup/smoke/t300.jsonl --transfer data/fsup/smoke/tr20.jsonl
   --ft_steps 20 --retain 2000 --train data/kh/train_k12.jsonl --heldout data/p2/heldout.jsonl --outdir $D --ckptdir ckpts/fsup/smoke"
python3 _orig_ladder.py $C --name O --rounds 1 > $D/O.log 2>&1 || echo "O FAILED"
python3 state_ladder_ei.py $C --name N --rounds 1 > $D/N.log 2>&1 || echo "N FAILED"
for f in found_1.jsonl mix_1.jsonl alloc_1.json; do echo "$f $(md5sum < $D/O/$f | cut -c1-12) $(md5sum < $D/N/$f | cut -c1-12)"; done
python3 state_ladder_ei.py $C --name S --rounds 2 --supply_frac 0.25 --transfer_k 0 > $D/S.log 2>&1 || echo "S FAILED"
grep "supply\|=== round" $D/S.log
python3 -c "import torch; print('peak', torch.cuda.is_available())"
echo SMOKE_DONE
