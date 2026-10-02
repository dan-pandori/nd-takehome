#!/usr/bin/env bash
# wait until both control queues on this pod have finished
cd /workspace/nd-takehome; until [ $(ls artifacts/rfc/CQ*.done artifacts/rfc/CQ*.fail 2>/dev/null | wc -l) -ge 2 ]; do sleep 60; done
