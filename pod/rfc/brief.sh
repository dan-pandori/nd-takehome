#!/usr/bin/env bash
# VPS: compact status: per ladder pod "start/seed:last round done", reader progress, new done/fail markers since last call.
cd /home/dan/work/rl-from-ckpt; S=/tmp/rfc/brief_seen; touch $S; line=""; new=""
for f in $(ls ~/.config/nd-rl/pods/ | grep '^rfc-' | sort -V); do
  o=$(TO=25 pod/rfc/sh.sh $f "r=\$(ls artifacts/rfc/la_*/round_*.json 2>/dev/null | grep -v _p0/ | wc -l); e=\$(ls artifacts/rfc/eval/.done_* 2>/dev/null | wc -l); c=\$(ls artifacts/rfc/rc_*/round_*.json 2>/dev/null | wc -l); echo \"\$r \$e \$c\"; ls artifacts/rfc/*.done artifacts/rfc/*.fail 2>/dev/null | xargs -r -n1 basename 2>/dev/null; true" </dev/null 2>/dev/null) || { line="$line ${f#rfc-}:DOWN"; continue; }
  set -- $(echo "$o" | head -n1); line="$line ${f#rfc-}:L$1/E$2/C$3"
  for m in $(echo "$o" | tail -n +2); do grep -qx "$f:$m" $S || { new="$new $f:$m"; echo "$f:$m" >> $S; }; done
done
echo "$(date -u +%H:%M)$line"; [ -n "$new" ] && echo "NEW:$new"; exit 0
