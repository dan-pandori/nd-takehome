#!/usr/bin/env bash
# For ~9 min: every 60 s, finish (pull + upload) and delete any pod whose listed jobs all have .done/.fail markers.
cd /home/dan/work/frontier-supply; . ~/.config/nd-rl/env
declare -A JOBS=([fsup6]="la_S_s0 la_S_s1" [fsup8]="la_S_s4 la_C_s4 rrfixed2" [fsup9]="la_S_s5 la_C_s5" [fsup10]="la_R_s0 la_R_s1")
end=$((SECONDS + ${1:-520}))
while [ $SECONDS -lt $end ]; do
  for N in "${!JOBS[@]}"; do F=~/.config/nd-rl/pods/$N; [ -f "$F" ] || continue; . "$F"
    m=$(timeout 60 ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o BatchMode=yes -o LogLevel=ERROR -p $POD_PORT root@$POD_IP "ls /workspace/nd-takehome/artifacts/fsup/" 2>/dev/null)
    ok=1; for j in ${JOBS[$N]}; do echo "$m" | grep -qx "$j.\(done\|fail\)" || ok=0; done
    if [ $ok = 1 ]; then echo "$(date -u +%H:%M) $N complete: $(echo "$m" | grep 'fail' | tr '\n' ' ')"; if timeout 900 pod/fsup/finish.sh $N > /tmp/fsup_finish_$N.log 2>&1; then tail -1 /tmp/fsup_finish_$N.log
      podrm $N 2>&1 | tail -1; else echo "FINISH FAILED $N"; fi; fi
  done
  sleep 60
done
date -u +%H:%M; ls ~/.config/nd-rl/pods/ | grep fsup | tr '\n' ' '
