#!/usr/bin/env bash
# finish_b.sh: VPS-side. (1) when T2c_s2300 has started on iffu-b, queue T4b_s0750 behind it (runq waits for the running
# sampler); (2) when T4b_s0750 is done, copy iffu-b's generic logs to logs/iffu-b/ on the pod, pull the files of
# T2c_dpo, T2c_s2300, T4b_s0750 and logs/iffu-b, check row counts, then delete iffu-b (kept if any check fails).
L=~/runs/olmo-iffu/finish_b.log; W=/home/dan/work/olmo-iffu; export POD_LOCAL_ROOT=$W; N=iffu-b
log() { echo "$(date -u +%FT%TZ) $*" >> $L; }
P=/workspace/nd-takehome/artifacts/olmo_iffu
until podrun $N "grep -q JOB_START $P/logs/q_T2c_s2300.log" > /dev/null 2>&1; do sleep 60; done
sleep 120   # the s2300 sampler is then up (model load), so runq's wait sees it
podrun $N "cd /workspace/nd-takehome; setsid nohup bash pod/olmo_iffu/runq.sh T4b_s0750 > artifacts/olmo_iffu/logs/queue5.log 2>&1 < /dev/null & disown; sleep 1; echo queued" >> $L 2>&1
log "T4b queued behind T2c_s2300"
until podrun $N "test -f $P/meta/T4b_s0750.done" > /dev/null 2>&1; do sleep 120; done
log "T4b done"
podrun $N "cd $P/logs; mkdir -p iffu-b; cp queue*.log setup.log cap32.log prefetch_*.log iffu-b/ 2>/dev/null; echo copied" >> $L 2>&1
ok=1
for J in T2c_dpo:2048 T2c_s2300:512 T4b_s0750:16; do
  j=${J%%:*}; R=${J##*:}
  for f in samples/$j.jsonl.gz graded/$j.jsonl meta/$j.json meta/$j.done logs/q_$j.log logs/${j}_smi.log; do
    podpull $N artifacts/olmo_iffu/$f > /dev/null 2>&1 || { log "PULL_FAIL $f"; ok=0; }
  done
  ns=$(python3 -c "import gzip
n=0
try:
    for l in gzip.open('$W/artifacts/olmo_iffu/samples/$j.jsonl.gz','rt'): n+=1
except Exception: pass
print(n)")
  ng=$(wc -l < $W/artifacts/olmo_iffu/graded/$j.jsonl 2>/dev/null || echo 0)
  log "$j samples=$ns graded=$ng expected=$R"; [ "$ns" = "$R" ] && [ "$ng" = "$R" ] || ok=0
done
podpull $N artifacts/olmo_iffu/logs/iffu-b > /dev/null 2>&1 || { log "PULL_FAIL logs/iffu-b"; ok=0; }
podrun $N "ls $P/meta/" 2>/dev/null | grep -E 'pod_env|pip_freeze' | while read f; do podpull $N artifacts/olmo_iffu/meta/$f > /dev/null 2>&1; done
if [ $ok = 1 ]; then log "all checks passed; deleting $N"; podrm $N >> $L 2>&1; log "podrm rc=$?"; else log "CHECK FAILED; $N kept"; fi
