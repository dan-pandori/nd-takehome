import os, sys, time, statistics
os.environ.update(ND_REGISTRY_DIR='/tmp/rrrev/reg5', ND_REGISTRY_SYNC='0', ND_RUN_ID='rr-review-timing', ND_OFFLINE='1')
sys.path.insert(0, os.path.expanduser('~/review/results-registry'))
import record
record.set_config({'a': 1, 'data': os.path.expanduser('~/review/results-registry/data/p2/heldout.jsonl')})
record.record('warm', 0)
ts = []
for i in range(2000):
    t = time.perf_counter(); record.record('x', i / 7, n=100, split='heldout', L=3); ts.append(time.perf_counter() - t)
print('record() ms/row: median %.3f  p99 %.3f  max %.3f' % (1e3*statistics.median(ts), 1e3*sorted(ts)[1979], 1e3*max(ts)))
