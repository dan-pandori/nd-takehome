#!/usr/bin/env bash
for p in "$@"; do timeout 60 podrun $p "bash pod/r3_4a/status_remote.sh" 2>&1; done
