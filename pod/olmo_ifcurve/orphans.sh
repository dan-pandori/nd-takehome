#!/usr/bin/env bash
# orphans.sh: VPS-side guard (written 2026-11-21 after 17 pods leaked during a RunPod REST DNS outage). List the account's
# pods with the GraphQL-based `runpodctl get pod`; delete every pod named ifc-* whose id is not the POD_ID of its
# registry file ~/.config/nd-rl/pods/<name> (`runpodctl remove pod`, GraphQL), and log it with an estimated cost to
# ~/podhours.log (rate unknown here: 5.29 $/h, the secure H200 price, from its first sighting). Prints the pod count.
L=~/runs/olmo-ifcurve/orphans.log; S=~/runs/olmo-ifcurve/orphans_seen.txt; touch $S
out=$(timeout 60 runpodctl get pod 2>/dev/null) || { echo "$(date -u +%FT%TZ) listing failed" >> $L; echo "LIST_FAIL"; exit 1; }
n=0
while read -r id name rest; do
  [ -z "$id" ] || [ "$id" = "ID" ] && continue
  case "$name" in ifc-*) ;; *) continue ;; esac
  n=$((n + 1))
  reg=~/.config/nd-rl/pods/$name
  if [ -f "$reg" ] && grep -q "POD_ID=$id" "$reg"; then continue; fi
  first=$(awk -v i="$id" '$1==i {print $2; exit}' $S); [ -n "$first" ] || first=$(date -u +%FT%TZ)
  r=$(timeout 60 runpodctl remove pod "$id" 2>&1 | tr '\n' ' ')
  echo "$(date -u +%FT%TZ) ORPHAN $name $id (first seen $first) -> $r" >> $L
  h=$(awk -v a="$(date -u +%s)" -v b="$(date -u -d "$first" +%s)" 'BEGIN{printf "%.4f",(a-b)/3600 + 0.05}')
  echo "$(date -u +%FT%TZ) olmo-ifcurve orphan-$id $h $(awk -v h="$h" 'BEGIN{printf "%.2f",h*5.29}') NVIDIA H200" >> ~/podhours.log
done <<< "$(printf '%s\n' "$out" | tr '\t' ' ')"
printf '%s\n' "$out" | tr '\t' ' ' | awk '$2 ~ /^ifc-/ {print $1, strftime("%Y-%m-%dT%H:%M:%SZ", systime(), 1)}' >> $S
echo "$n"
