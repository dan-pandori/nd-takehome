#!/usr/bin/env bash
# orphans.sh: VPS-side guard (written 2026-11-21 after 17 pods leaked while RunPod's retired REST v1 broke podnew's undo).
# List the account's pods with REST v2 (rp2.py list); delete every pod named ifc-* whose id is not the POD_ID of its
# registry file ~/.config/nd-rl/pods/<name> (rp2.py delete), and log it with its cost from first sighting to
# ~/podhours.log. Run only when no create is in flight (a pod being created is not registered yet). Prints the ifc count.
L=~/runs/olmo-lowrank/orphans.log; S=~/runs/olmo-lowrank/orphans_seen.txt; touch $S
RP="python3 /home/dan/work/olmo-lowrank/pod/olmo_lowrank/rp2.py"
out=$(timeout 90 $RP list 2>&1) || { echo "$(date -u +%FT%TZ) listing failed: ${out:0:200}" >> $L; echo "LIST_FAIL"; exit 1; }
n=0
while read -r id name status cost; do
  [ -z "$id" ] && continue
  case "$name" in ifc-*) ;; *) continue ;; esac
  n=$((n + 1))
  [ -f ~/runs/olmo-lowrank/creating_$name ] && continue   # podnew2.sh is creating it
  reg=~/.config/nd-rl/pods/$name
  if [ -f "$reg" ] && grep -q "POD_ID=$id" "$reg"; then continue; fi
  first=$(awk -v i="$id" '$1==i {print $2; exit}' $S); [ -n "$first" ] || first=$(date -u +%FT%TZ)
  r=$($RP delete "$id" 2>&1 | tr '\n' ' ')
  echo "$(date -u +%FT%TZ) ORPHAN $name $id $status (first seen $first) -> $r" >> $L
  h=$(awk -v a="$(date -u +%s)" -v b="$(date -u -d "$first" +%s)" 'BEGIN{printf "%.4f",(a-b)/3600 + 0.05}')
  c=${cost:-5.29}; [ "$c" = "None" ] && c=5.29
  echo "$(date -u +%FT%TZ) olmo-lowrank orphan-$id $h $(awk -v h="$h" -v r="$c" 'BEGIN{printf "%.2f",h*r}') NVIDIA H200" >> ~/podhours.log
done <<< "$out"
printf '%s\n' "$out" | awk -v t="$(date -u +%FT%TZ)" '$2 ~ /^ifc-/ {print $1, t}' >> $S
echo "$n"
