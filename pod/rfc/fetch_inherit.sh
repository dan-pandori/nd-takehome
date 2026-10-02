#!/usr/bin/env bash
# Fetch trajectory's records this run reuses into inherit/tj (VPS; gitignored): reference/eventual scores under the start
# checkpoints and r8, per-theorem reads of the starts and the end arm's r2/r4/r8, the reference targets.
B=hf://buckets/dan-pandori/nd-rl/trajectory; cd /home/dan/work/rl-from-ckpt; mkdir -p inherit/tj
hf buckets sync $B/artifacts/tj/score inherit/tj/score --include '*/targets.jsonl' --include '*_p0.jsonl' --include '*_p1600.jsonl' \
  --include '*_p5000.jsonl' --include '*_p12000.jsonl' --include '*_p16000.jsonl' --include '*_pend.jsonl' --include '*_r[248].jsonl'
hf buckets sync $B/artifacts/tj/eval inherit/tj/eval --include '*_p0__*.jsonl' --include '*_p1600__*.jsonl' --include '*_p5000__*.jsonl' \
  --include '*_p12000__*.jsonl' --include '*_p16000__*.jsonl' --include '*_pend__*.jsonl' --include '*_r[248]__*.jsonl'
hf buckets sync $B/data/tj inherit/tj/data --include 'ref_*.jsonl'
