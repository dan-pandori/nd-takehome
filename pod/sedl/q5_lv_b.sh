#!/usr/bin/env bash
# Phase 6 (style-edl): l_V re-fits (written by style_edl/make_lv_queue.py). Restartable.
. pod/sedl/env.sh
J=pod/sedl/job.sh; D=data/style_edl/streams; O=artifacts/style_edl/lv; V=data/style_edl/vset.jsonl
up artifacts/style_edl/lv
up artifacts/style_edl/lv
up artifacts/style_edl/lv
up artifacts/style_edl/lv
up artifacts/style_edl/lv
$J lv_s1_S_Kal python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s1_b1200.pt --stream $D/s1/S_Kal.stream.jsonl --test $D/s1/S_Kal.test.jsonl --lrs 0.0001 --orders 0,1 --algo es --arm S_Kal --lseed 1 --vset $V --out $O/s1/S_Kal.json
$J lv_s2_S_Kal python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s2_b1200.pt --stream $D/s2/S_Kal.stream.jsonl --test $D/s2/S_Kal.test.jsonl --lrs 0.0001 --orders 0,1 --algo es --arm S_Kal --lseed 2 --vset $V --out $O/s2/S_Kal.json
up artifacts/style_edl/lv
echo "QUEUE DONE $(date -u +%FT%TZ)"
