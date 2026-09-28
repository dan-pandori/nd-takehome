#!/usr/bin/env bash
# long-pool: fetch the re-read checkpoints from the bucket into ckpts/lp/<run>__<file>.pt
cd /workspace/nd-takehome; mkdir -p ckpts/lp; B=hf://buckets/dan-pandori/nd-rl
for p in state-env/ckpts/se/ladder/la_T1_S_s0_r8.pt state-env/ckpts/se/ladder/la_T1_S_s1_r8.pt state-env/ckpts/se/ladder/la_T1_SN_s0_r8.pt \
  state-env/ckpts/se/ladder/la_T1_SN_s1_r8.pt state-env/ckpts/se/stage1_S_s0.pt state-env/ckpts/se/stage1_S_s1.pt state-env/ckpts/se/stage1_SN_s0.pt \
  state-env/ckpts/se/stage1_SN_s1.pt ds-generator/ckpts/ladder/la_T1_c0_s0_r8.pt ds-generator/ckpts/ladder/la_T1_c0_s1_r8.pt \
  lean-format/ckpts/lf/stage1_a1_seq_s0.pt lean-format/ckpts/lf/stage1_a1_seq_s1.pt cap-horizon/ckpts/kh/stage1_k12_s0.pt cap-horizon/ckpts/kh/stage1_k14_s0.pt; do
  f=ckpts/lp/$(echo $p | cut -d/ -f1)__$(basename $p); [ -s $f ] || hf buckets cp $B/$p $f > /dev/null
done
sha256sum ckpts/lp/*.pt | cut -c1-16
