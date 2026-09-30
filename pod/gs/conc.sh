source pod/gs/env.sh
CK=ckpts/sc12/stage1_SN12_s0.pt
for A in default passk; do
  ND_ARM=conc_$A ND_SEED=1 python3 grpo_state.py --init $CK --name conc_$A --seed 1 --adv $A --lr 3e-5 --max_steps_total 6 --no_eval --steps_log \
    --outdir artifacts/grpo_state --ckptdir ckpts/grpo_state --heldout data/p2/heldout.jsonl > artifacts/grpo_state/logs/conc_$A.log 2>&1 &
done
wait; echo CONC_DONE
