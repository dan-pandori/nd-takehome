#!/usr/bin/env bash
# One acceptance test. Usage: t.sh <T1|T2|T3|T4|T5>. Writes ~/runs/podjob/tests/<T>.{out,txt}
export PATH="$HOME/.local/bin:$HOME/bin:$PATH"; . ~/.config/nd-rl/env
T=$1; D=~/runs/podjob/tests; export POD_LOCAL_ROOT=$D/local POD_EXTRA="${POD_EXTRA:---public-ip}"
PJ=~/work/podjob-nd-rl/code/tools/orchestration/podjob; G=${GPU:-NVIDIA RTX A4000}; C=${CLOUD:-COMMUNITY}
O=artifacts/pjtest/$T; W='echo host=$(hostname) pod=${RUNPOD_POD_ID:-?} start=$(date +%s)'
case $T in
  T1) args=(-- "mkdir -p $O && $W > $O/out.txt && sleep 30 && echo end=\$(date +%s) >> $O/out.txt");;
  T2) args=(-- "mkdir -p $O && $W > $O/out.txt && exit 3");;
  T3) args=(-- "mkdir -p $O && $W > $O/out.txt && sleep 600");;
  T4) args=(--pack 3 -- "mkdir -p $O && $W > $O/a.txt && sleep 60 && echo end=\$(date +%s) >> $O/a.txt" ';'
            "mkdir -p $O && $W > $O/b.txt && sleep 60 && echo end=\$(date +%s) >> $O/b.txt" ';'
            "mkdir -p $O && $W > $O/c.txt && sleep 60 && echo end=\$(date +%s) >> $O/c.txt");;
  T5) args=(-- "true");;
esac
NAME=pj-podjob-$T-$(date +%H%M%S)
echo "test $T name $NAME t0=$(date -u +%s)" > $D/$T.txt
$PJ podjob --gpu "$G" --cloud $C --name $NAME --out $O "${args[@]}" > $D/$T.out 2>&1 & P=$!
if [ $T = T3 ]; then until grep -q "job 0 started" $D/$T.out || ! kill -0 $P 2>/dev/null; do sleep 5; done; N2=$NAME; for v in old new; do [ $v = old ] && B=$(git -C ~/work/podjob-nd-rl show origin/dan:code/tools/orchestration/podbg > /tmp/podbg_old && echo /tmp/podbg_old) || B=~/work/podjob-nd-rl/code/tools/orchestration/podbg
    s=$SECONDS; bash $B $N2 bg$v "sleep 40; echo done-$v" > /dev/null 2>&1; echo "podbg $v rc=$? took $((SECONDS-s)) s" >> $D/$T.txt; done
  sleep 20; echo "kill TERM at $(date -u +%s)" >> $D/$T.txt; kill -TERM $P; fi
if [ $T = T5 ]; then sleep 20; echo "kill TERM (during creation) at $(date -u +%s)" >> $D/$T.txt; kill -TERM $P; fi
wait $P; echo "podjob exit $? at $(date -u +%s)" >> $D/$T.txt
until ! runpodctl pod list 2>/dev/null | jq -e --arg n $NAME 'map(select(.name==$n))|length>0' >/dev/null; do sleep 5; done
echo "absent from account listing at $(date -u +%s)" >> $D/$T.txt
runpodctl pod list 2>/dev/null | jq -c 'map({id,name})' > $D/$T.listing.json
hf buckets ls hf://buckets/dan-pandori/nd-rl/podjob/$O 2>&1 | head -20 > $D/$T.bucket.txt || true
echo done >> $D/$T.txt
