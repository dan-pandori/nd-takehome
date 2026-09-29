#!/usr/bin/env python3
"""minlen.py with its time limit measured in the worker's CPU seconds instead of wall seconds (long-pool-2).
Same search, same arguments; only `minlen.time.time` is replaced by `time.process_time`, so the deadline and the
recorded `secs` are CPU seconds.  Needed on hosts where a worker gets a fraction of a core (lp2-a: ~15 %)."""
import os, sys, time, types
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import minlen
minlen.time = types.SimpleNamespace(time=time.process_time, process_time=time.process_time, sleep=time.sleep)
if __name__ == '__main__':
    minlen.main()
