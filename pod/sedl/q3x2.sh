#!/usr/bin/env bash
# sedl1, after q3x: the seed-2 Kalmar cross-fit moved here from sedl2 (whose queue skips it via a placeholder log).
. pod/sedl/env.sh
until grep -q "QUEUE DONE" artifacts/style_edl/logs/queue_q3x_xfit.log 2>/dev/null; do sleep 60; done
grep -q placeholder artifacts/style_edl/logs/xfit_s2_S_Kal.log 2>/dev/null && rm -f artifacts/style_edl/logs/xfit_s2_S_Kal.log
D=data/style_edl/streams; s=2; S=S_Kal
pod/sedl/job.sh xfit_s${s}_$S python3 style_edl/edl_run.py --ckpt ckpts/bs/stage1_best12_s${s}_b1200.pt --stream $D/s$s/$S.test.jsonl --test $D/s$s/$S.stream.jsonl --lrs 1e-5,1e-4,1e-3 --orders 0,1 --arm $S --lseed $s --algo es --out artifacts/style_edl/edl_x/s$s/$S.json
up artifacts/style_edl/edl_x
echo "QUEUE DONE $(date -u +%FT%TZ)"
