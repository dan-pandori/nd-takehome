#!/usr/bin/env bash
# rm.sh <pod>: delete a registered pod with podrm2.sh (RunPod REST v2, verified); podrm (REST v1) no longer works.
bash /home/dan/work/olmo-ifcurve/pod/olmo_ifcurve/podrm2.sh "$1"
