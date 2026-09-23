#!/usr/bin/env bash
# Stop the current bench queue (kept in a file so the ssh command line cannot self-match the pattern).
pkill -f 'bench_all[.]sh' ; pkill -f 'bench_sampler[.]py' ; pkill -f 'ef/job[.]sh' ; sleep 2
pgrep -af 'bench_sampler[.]py' || echo "no bench processes left"
