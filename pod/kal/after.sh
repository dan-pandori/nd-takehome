#!/usr/bin/env bash
# Run a command once a marker file exists.  Usage: bash pod/kal/after.sh <marker> <command...>
cd /workspace/nd-takehome
until [ -f "$1" ]; do sleep 60; done
shift
exec "$@"
