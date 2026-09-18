#!/usr/bin/env bash
# round3-run4b, 85M pods: after `req`. If the req arm never trained (0 proofs in 8 rounds) the frozen arm would be a bit-identical copy of it
# (verified on the three 25M draws: all 24 round files equal), so it is skipped (marker q/frozen_<T>.skipped) and the `mix` arm runs instead.
# If req did train, draw.sh's frozen stage is left alone and mix waits for it. On the pod: bash pod/r3_4b/post2.sh 85M <seed>
cd /workspace/nd-takehome
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
SIZE=$1; S=$2; FTLR=3e-5; EB=768
T=${SIZE}_s${S}; Q=artifacts/r3_4b/q; CK=ckpts/r3_4b/stage1_depth3_f0_a1_$T.pt
until [ -f $Q/req_$T.done ]; do sleep 20; done
TR=$(python3 -c "import json,glob; print(sum(json.load(open(f)).get('mix_rl_records',0)>0 for f in glob.glob('artifacts/r3_4b/ei_depth3_${T}_req/round_*.json')))")
if [ "$TR" = 0 ]; then
  pkill -f 'pod/r3_4b/dra[w].sh'; sleep 2; pkill -f "ei_depth3_${T}_froze[n]"; sleep 5
  echo "$(date -u +%FT%TZ) req arm never trained: frozen arm skipped (identical to req by construction)" > $Q/frozen_$T.skipped
else until [ -f $Q/frozen_$T.done ]; do sleep 30; done; fi
echo "$(date -u +%FT%TZ) start mix $T"
python3 expert_iter.py --init $CK --name r3_4b/ei_depth3_${T}_mix --targets data/r3_1/depth3_mix.jsonl --transfer data/r3_1/depth3_req_transfer.jsonl --heldout data/p2/heldout.jsonl --train data/p2/train_depth3_f0_a1.jsonl --rounds 8 --k 32 --temperature 0.8 --retain 20000 --ft_steps 600 --ft_lr $FTLR --seed $S --batch $EB > $Q/mix_$T.log 2>&1 && touch $Q/mix_$T.done
echo "$(date -u +%FT%TZ) POST2 DONE $T"
