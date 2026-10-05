#!/usr/bin/env bash
# One VPS-side orchestrator for the remaining capability-defs pod launches (replaces several waiting chains, so the VPS
# never runs more than a few processes).  Polls each pod; every event fires once (markers in /tmp/cdorch).
# Events: E1 cd-b J3 done -> J10 s0, s1 | E2 cd-i stage B s1 done -> part3 + J9 selection s1 -> J9 s1 even chunks |
# E3 cd-c J3c6 done -> guided re-runs (batch 1,024) + J10 s2 | E4 cd-d J6b done (after E2) -> J9 s1 odd chunks |
# E5 cd-j stage B s2 -> J9 s2 even | E6 cd-a J3 done (after E5) -> J9 s2 odd | E7 cd-k stage B s0 -> J9 s0 even |
# E8 cd-h J8 done (after E7) -> J9 s0 odd.
cd /home/dan/work/capability-defs
M=/tmp/cdorch; mkdir -p $M
W=/workspace/nd-takehome/artifacts/cd
log() { echo "$(date -u +%FT%TZ) $*"; }
has() { timeout 60 podrun $1 "test -e $W/$2.done -o -e $W/$2.fail" > /dev/null 2>&1; }
part3() { timeout 1500 python3 capability_defs/analysis/cd_part3.py > capability_defs/analysis/out/part3.txt 2>&1; log "part3 rc=$?"; }
while true; do
  left=0
  if [ ! -e $M/E1 ]; then left=1; if has cd-b queue_b; then
    log E1; pod/cd/pull.sh cd-b artifacts/cd/j3 > /dev/null; pod/cd/push.sh cd-b > /tmp/push_b.log 2>&1
    pod/cd/bg.sh cd-b j10_s01 "bash pod/cd/j10.sh 0 && bash pod/cd/j10.sh 1"; touch $M/E1; fi; fi
  if [ ! -e $M/E2 ]; then left=1; if has cd-i j2b_s1; then
    log E2; pod/cd/pull.sh cd-i 'artifacts/cd/j2/s1_[dbt]*'; part3; python3 capability_defs/analysis/cd_j9_select.py 1
    pod/cd/push.sh cd-i > /tmp/push_i.log 2>&1; pod/cd/bg.sh cd-i j9_s1a "bash pod/cd/j9.sh 1 0,2,4,6,8"; touch $M/E2; fi; fi
  if [ ! -e $M/E3 ]; then left=1; if has cd-c queue_c; then
    log E3; pod/cd/pull.sh cd-c artifacts/cd/j3 > /dev/null; pod/cd/push.sh cd-c > /tmp/push_c.log 2>&1
    pod/cd/bg.sh cd-c j3fix_j10 "bash pod/cd/j3fix.sh c6_s1_r8,c6_s2_r8,c6_s2_r16; bash pod/cd/setup.sh && bash pod/cd/j10.sh 2"
    touch $M/E3; fi; fi
  if [ ! -e $M/E4 ]; then left=1; if [ -e $M/E2 ] && has cd-d queue_d4; then
    log E4; pod/cd/pull.sh cd-d artifacts/cd/j6b > /dev/null
    python3 capability_defs/analysis/cd_lem.py > capability_defs/analysis/out/lem.txt
    pod/cd/push.sh cd-d > /tmp/push_d.log 2>&1; pod/cd/bg.sh cd-d j9_s1b "bash pod/cd/j9.sh 1 1,3,5,7,9"; touch $M/E4; fi; fi
  if [ ! -e $M/E5 ]; then left=1; if has cd-j j2b_s2; then
    log E5; pod/cd/pull.sh cd-j 'artifacts/cd/j2/s2_[dbt]*'; part3; python3 capability_defs/analysis/cd_j9_select.py 2
    pod/cd/push.sh cd-j > /tmp/push_j.log 2>&1; pod/cd/bg.sh cd-j j9_s2a "bash pod/cd/j9.sh 2 0,2,4,6,8,10"; touch $M/E5; fi; fi
  if [ ! -e $M/E6 ]; then left=1; if [ -e $M/E5 ] && has cd-a queue_a; then
    log E6; pod/cd/pull.sh cd-a artifacts/cd/j3 > /dev/null; pod/cd/push.sh cd-a > /tmp/push_a.log 2>&1
    pod/cd/bg.sh cd-a j9_s2b "bash pod/cd/j9.sh 2 1,3,5,7,9"; touch $M/E6; fi; fi
  if [ ! -e $M/E7 ]; then left=1; if has cd-k j2b_s0; then
    log E7; pod/cd/pull.sh cd-k 'artifacts/cd/j2/s0_[dbt]*'; part3; python3 capability_defs/analysis/cd_j9_select.py 0
    pod/cd/push.sh cd-k > /tmp/push_k2.log 2>&1; pod/cd/bg.sh cd-k j9_s0a "bash pod/cd/j9.sh 0 0,2,4,6,8"; touch $M/E7; fi; fi
  if [ ! -e $M/E8 ]; then left=1; if [ -e $M/E7 ] && has cd-h queue_h; then
    log E8; pod/cd/pull.sh cd-h artifacts/cd/j8 > /dev/null; pod/cd/push.sh cd-h > /tmp/push_h.log 2>&1
    pod/cd/bg.sh cd-h j9_s0b "bash pod/cd/setup.sh && bash pod/cd/j9.sh 0 1,3,5,7"; touch $M/E8; fi; fi
  [ $left = 0 ] && { log "all events fired"; break; }
  sleep 60
done
