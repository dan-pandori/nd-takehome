#!/usr/bin/env bash
# Wait up to $1 seconds (<= 580), checking every 120 s for trouble on the coe pods (a FAILED line in any log, a Traceback in
# a seed log, CUDA OOM, disk >= 85 %).  Prints the trouble and exits early, or prints "quiet" at the end.
END=$(( $(date +%s) + ${1:-420} ))
IB=~/runs/create-or-elicit/executor.inbox
while [ $(date +%s) -lt $END ]; do
  if [ -f $IB ] && [ "$(stat -c %Y $IB)" != "$(cat /tmp/coe_inbox_mtime 2>/dev/null)" ]; then echo "INBOX changed: $(tail -c 600 $IB)"; stat -c %Y $IB > /tmp/coe_inbox_mtime; exit 0; fi
  for f in ~/runs/create-or-elicit/BRIEF_AMENDMENT.md; do [ -f $f ] && [ ! -f /tmp/coe_amend_seen ] && { echo "AMENDMENT: $(head -c 600 $f)"; touch /tmp/coe_amend_seen; exit 0; }; done
  for P in $(ls ~/.config/nd-rl/pods/ | grep '^coe-'); do
    out=$(timeout 25 podrun $P 'cd /workspace/nd-takehome 2>/dev/null || exit 0; grep -l "FAILED\|out of memory\|OutOfMemory" artifacts/coe/logs/*.log 2>/dev/null | head -3; grep -l "Traceback" artifacts/coe/logs/seed_*.log 2>/dev/null | head -2; df -h / | tail -1 | awk "{gsub(\"%\",\"\",\$5); if (\$5+0 >= 85) print \"DISK \" \$5}"' 2>/dev/null)
    [ -n "$out" ] && { echo "TROUBLE $P: $out"; exit 0; }
  done
  sleep 120
done
echo "quiet $(date -u +%H:%M)"
