#!/usr/bin/env bash
# Phase 6 (style-edl): l_V re-fits (written by style_edl/make_lv_queue.py). Restartable.
. pod/sedl/env.sh
J=pod/sedl/job.sh; D=data/style_edl/streams; O=artifacts/style_edl/lv; V=data/style_edl/vset.jsonl
$J lv_s0_S_own python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s0_b1200.pt --stream $D/s0/S_own.stream.jsonl --test $D/s0/S_own.test.jsonl --lrs 1e-05 --orders 0,1 --algo es --arm S_own --lseed 0 --vset $V --out $O/s0/S_own.json
$J lv_s1_S_own python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s1_b1200.pt --stream $D/s1/S_own.stream.jsonl --test $D/s1/S_own.test.jsonl --lrs 1e-05 --orders 0,1 --algo es --arm S_own --lseed 1 --vset $V --out $O/s1/S_own.json
$J lv_s2_S_own python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s2_b1200.pt --stream $D/s2/S_own.stream.jsonl --test $D/s2/S_own.test.jsonl --lrs 1e-05 --orders 0,1 --algo es --arm S_own --lseed 2 --vset $V --out $O/s2/S_own.json
up artifacts/style_edl/lv
$J lv_s0_S_own2 python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s0_b1200.pt --stream $D/s0/S_own2.stream.jsonl --test $D/s0/S_own2.test.jsonl --lrs 1e-05 --orders 0,1 --algo es --arm S_own2 --lseed 0 --vset $V --out $O/s0/S_own2.json
$J lv_s1_S_own2 python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s1_b1200.pt --stream $D/s1/S_own2.stream.jsonl --test $D/s1/S_own2.test.jsonl --lrs 1e-05 --orders 0,1 --algo es --arm S_own2 --lseed 1 --vset $V --out $O/s1/S_own2.json
$J lv_s2_S_own2 python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s2_b1200.pt --stream $D/s2/S_own2.stream.jsonl --test $D/s2/S_own2.test.jsonl --lrs 1e-05 --orders 0,1 --algo es --arm S_own2 --lseed 2 --vset $V --out $O/s2/S_own2.json
up artifacts/style_edl/lv
$J lv_s0_S_seed python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s0_b1200.pt --stream $D/s0/S_seed.stream.jsonl --test $D/s0/S_seed.test.jsonl --lrs 1e-05 --orders 0,1 --algo es --arm S_seed --lseed 0 --vset $V --out $O/s0/S_seed.json
$J lv_s1_S_seed python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s1_b1200.pt --stream $D/s1/S_seed.stream.jsonl --test $D/s1/S_seed.test.jsonl --lrs 1e-05 --orders 0,1 --algo es --arm S_seed --lseed 1 --vset $V --out $O/s1/S_seed.json
$J lv_s2_S_seed python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s2_b1200.pt --stream $D/s2/S_seed.stream.jsonl --test $D/s2/S_seed.test.jsonl --lrs 1e-05 --orders 0,1 --algo es --arm S_seed --lseed 2 --vset $V --out $O/s2/S_seed.json
up artifacts/style_edl/lv
$J lv_s0_S_short python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s0_b1200.pt --stream $D/s0/S_short.stream.jsonl --test $D/s0/S_short.test.jsonl --lrs 0.0001 --orders 0,1 --algo es --arm S_short --lseed 0 --vset $V --out $O/s0/S_short.json
$J lv_s1_S_short python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s1_b1200.pt --stream $D/s1/S_short.stream.jsonl --test $D/s1/S_short.test.jsonl --lrs 0.0001 --orders 0,1 --algo es --arm S_short --lseed 1 --vset $V --out $O/s1/S_short.json
$J lv_s2_S_short python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s2_b1200.pt --stream $D/s2/S_short.stream.jsonl --test $D/s2/S_short.test.jsonl --lrs 0.0001 --orders 0,1 --algo es --arm S_short --lseed 2 --vset $V --out $O/s2/S_short.json
up artifacts/style_edl/lv
$J lv_s0_S_RL python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s0_b1200.pt --stream $D/s0/S_RL.stream.jsonl --test $D/s0/S_RL.test.jsonl --lrs 1e-05 --orders 0,1 --algo es --arm S_RL --lseed 0 --vset $V --out $O/s0/S_RL.json
$J lv_s1_S_RL python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s1_b1200.pt --stream $D/s1/S_RL.stream.jsonl --test $D/s1/S_RL.test.jsonl --lrs 1e-05 --orders 0,1 --algo es --arm S_RL --lseed 1 --vset $V --out $O/s1/S_RL.json
$J lv_s2_S_RL python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s2_b1200.pt --stream $D/s2/S_RL.stream.jsonl --test $D/s2/S_RL.test.jsonl --lrs 1e-05 --orders 0,1 --algo es --arm S_RL --lseed 2 --vset $V --out $O/s2/S_RL.json
up artifacts/style_edl/lv
$J lv_s0_S_Kal python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s0_b1200.pt --stream $D/s0/S_Kal.stream.jsonl --test $D/s0/S_Kal.test.jsonl --lrs 0.0001 --orders 0,1 --algo es --arm S_Kal --lseed 0 --vset $V --out $O/s0/S_Kal.json
up artifacts/style_edl/lv
echo "QUEUE DONE $(date -u +%FT%TZ)"
