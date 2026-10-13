#!/usr/bin/env bash
# Reviewer: download each ladder found file from the bucket (one at a time), classify it (found.py), delete it.
BK=hf://buckets/dan-pandori/nd-rl
cd ~/review/create-or-elicit/review_coe
T=~/review/coe_big/tmp_found.jsonl
run() {   # bucket-path label kind
  [ -s found/$2.json ] && { echo "skip $2"; return; }
  hf buckets cp "$BK/$1" $T >/dev/null 2>&1 || { echo "DOWNLOAD FAILED $1"; return; }
  python3 found.py $T $2 $3 > found/$2.log 2>&1 || echo "FAILED $2"
  head -1 found/$2.log; rm -f $T
}
mkdir -p found
for S in 0 2 3 4 5; do run create-or-elicit/artifacts/coe/ladder/la_ko_s$S/found_16.jsonl ko_s${S}_targets targets; done
run create-or-elicit/artifacts/coe/ladder/la_ko_s1/found_24.jsonl ko_s1_targets24 targets
for S in 0 1 2; do run create-or-elicit/artifacts/coe/ladder/la_dose1_s$S/found_16.jsonl dose1_s${S}_targets targets; done
for S in 3 4 5; do run create-or-elicit/artifacts/coe/ladder/la_full_s$S/found_16.jsonl full_s${S}_targets targets; done
for S in 0 1 2; do run rl-continue/artifacts/rc/la_T1_best12_s$S/found_16.jsonl full_s${S}_targets targets; done
for S in 1 2 3 4 5; do run create-or-elicit/artifacts/coe/ladder/la_ko_s$S/found_transfer_16.jsonl ko_s${S}_transfer transfer; done
run create-or-elicit/artifacts/coe/ladder/la_ko_s1/found_transfer_24.jsonl ko_s1_transfer24 transfer
for S in 0 1 2; do run create-or-elicit/artifacts/coe/ladder/la_dose1_s$S/found_transfer_16.jsonl dose1_s${S}_transfer transfer; done
for S in 3 4 5; do run create-or-elicit/artifacts/coe/ladder/la_full_s$S/found_transfer_16.jsonl full_s${S}_transfer transfer; done
for S in 0 1 2; do run rl-continue/artifacts/rc/la_T1_best12_s$S/found_transfer_16.jsonl full_s${S}_transfer transfer; done
echo ALL DONE
