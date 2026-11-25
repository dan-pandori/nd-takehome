#!/usr/bin/env bash
# p32_sft with 32B/sft5e-5/8000 (= SFT main) re-staged into the reference shard layout first (its 14 files use another
# tensor-to-file layout than the other 23 members; restage.py checks bytes), then the engine with --prestaged.
cd /workspace/nd-takehome; A=artifacts/olmo_weights; mkdir -p $A/logs $A/stats $A/restage
export HF_XET_HIGH_PERFORMANCE=1 HF_XET_CHUNK_CACHE_SIZE_BYTES=0
P=/root/prestaged/32B_sft5e-5_8000
if [ ! -f $P/restage.json ]; then
  python olmo_weights/restage.py --label 32B/sft5e-5/8000 --ref-index olmo_weights/manifest/index/allenai__Olmo-3-1125-32B__stage1.json --out $P >> $A/logs/restage.log 2>&1
fi
cp $P/restage.json $A/restage/32B_sft5e-5_8000.json
grep -q '"tensors_byte_identical": 707' $P/restage.json || { echo "RESTAGE FAILED" >> $A/logs/restage.log; exit 1; }
J=p32_sft
for try in 1 2 3; do
  date -u +"%FT%TZ start $J try $try" >> $A/logs/$J.log
  python olmo_weights/engine.py --job $J --work /root/dl --device cuda --inflight 8 --disk-cap-gb 190 --prestaged 32B/sft5e-5/8000=$P >> $A/logs/$J.log 2>&1
  rc=$?
  date -u +"%FT%TZ end $J try $try rc $rc" >> $A/logs/$J.log
  [ $rc = 0 ] && { date -u +%FT%TZ > $A/stats/$J/JOB_DONE; break; }
  sleep 60
done
date -u +%FT%TZ > $A/logs/queue_$(hostname).done
