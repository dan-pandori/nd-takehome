#!/usr/bin/env bash
# Block (<= 580 s) until the set of .done/.fail markers on the pods changes; print the new ones.
snap() { for i in 1 2 3 4; do timeout 30 podrun sf-$i "ls artifacts/sf2/ | grep -E '\.(done|fail)$'" 2>/dev/null | sed "s/^/sf-$i:/"; done | grep -v podrun | sort; }
A=$(snap); T=$(date +%s)
while [ $(( $(date +%s) - T )) -lt 480 ]; do sleep 60; B=$(snap); [ "$A" != "$B" ] && { comm -13 <(echo "$A") <(echo "$B"); exit 0; }; done
echo "no change $(date -u +%T)"
