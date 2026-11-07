#!/usr/bin/env bash
# launch_t2c.sh: VPS-side. After test 4 (T4_s0750 done on iffu-b, or launch_t4.sh having declined it), starts test 2c
# (runq T2c_dpo T2c_s2300) on iffu-b only if spend + $5.0 (test 2c) + $1.5 (continuations) <= $55 (pre-registered
# addition, 2026-11-07). Log: ~/runs/olmo-iffu/launch_t2c.log
L=~/runs/olmo-iffu/launch_t2c.log; log() { echo "$(date -u +%FT%TZ) $*" >> $L; }
until grep -q "T4 NOT launched" ~/runs/olmo-iffu/launch_t4.log 2>/dev/null || \
      podrun iffu-b "test -f /workspace/nd-takehome/artifacts/olmo_iffu/meta/T4_s0750.done" > /dev/null 2>&1; do sleep 120; done
podrun iffu-b "pgrep -f 'olmo_iffu/[s]ample.py'" > /dev/null 2>&1 && { log "a sampler still runs on iffu-b; waiting"; \
  while podrun iffu-b "pgrep -f 'olmo_iffu/[s]ample.py'" > /dev/null 2>&1; do sleep 60; done; }
U=$(podbudget 2>/dev/null | awk '$1=="olmo-iffu"{gsub(/\$/,"",$5); print $5}')
log "test 4 finished or declined; spend $U"
if python3 -c "import sys; sys.exit(0 if float('$U') + 6.5 <= 55 else 1)"; then
  podrun iffu-b "cd /workspace/nd-takehome; setsid nohup bash pod/olmo_iffu/runq.sh T2c_dpo T2c_s2300 > artifacts/olmo_iffu/logs/queue4.log 2>&1 < /dev/null & disown; sleep 1; echo launched" >> $L 2>&1
  log "T2c launched"
else log "T2c NOT launched: spend $U + 6.5 > 55"; fi
