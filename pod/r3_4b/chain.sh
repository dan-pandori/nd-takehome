#!/usr/bin/env bash
# round3-run4b: once the retry checkpoint of <size> s<seed> has its gate result, run it through the pipeline, then the optional-pool samples
# (post.sh's guard keeps one pre-RL sampler per GPU). On the pod: bash pod/r3_4b/chain.sh <25M|85M> <seed>
cd /workspace/nd-takehome; SIZE=$1; S=$2; Q=artifacts/r3_4b/q
pkill -f 'pod/r3_4b/pos[t].sh'
until [ -f $Q/gate_${SIZE}r_s$S.done ]; do sleep 30; done
bash pod/r3_4b/launch.sh ${SIZE}r $S; sleep 90
bash pod/r3_4b/launch_post.sh ${SIZE}r $S
bash pod/r3_4b/launch_post.sh $SIZE $S
