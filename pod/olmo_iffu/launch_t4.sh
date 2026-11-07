#!/usr/bin/env bash
# launch_t4.sh: VPS-side. Waits for T3_dpo's done marker on iffu-b, then applies the brief's test-4 condition by the
# ledger: T4_s0750 starts only if podbudget's spend for olmo-iffu is <= $50.50 (>= $8 left after tests 1-3, keeping
# $1.50 for test-3 continuation jobs) and no other olmo-iffu pod (iffu-a) is still up. Log: ~/runs/olmo-iffu/launch_t4.log
L=~/runs/olmo-iffu/launch_t4.log; log() { echo "$(date -u +%FT%TZ) $*" >> $L; }
until podrun iffu-b "test -f /workspace/nd-takehome/artifacts/olmo_iffu/meta/T3_dpo.done" > /dev/null 2>&1; do sleep 120; done
log "T3_dpo done"
while [ -f ~/.config/nd-rl/pods/iffu-a ]; do sleep 120; done
U=$(podbudget 2>/dev/null | awk '$1=="olmo-iffu"{gsub(/\$/,"",$5); print $5}')
log "spend $U"
if python3 -c "import sys; sys.exit(0 if float('$U') <= 50.5 else 1)"; then
  podrun iffu-b "cd /workspace/nd-takehome; setsid nohup bash pod/olmo_iffu/runq.sh T4_s0750 > artifacts/olmo_iffu/logs/queue3.log 2>&1 < /dev/null & disown; sleep 1; echo launched" >> $L 2>&1
  log "T4 launched"
else log "T4 NOT launched: spend $U > 50.50"; fi
