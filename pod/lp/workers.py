"""lean-prefilter item 2: Lean gate throughput vs worker count on this pod.  python3 pod/lp/workers.py DUMP N W1,W2,..
Checks the first N distinct texts of a gate dump through lean_gate.check_sources at each worker count; one json line
each with wall seconds, summed process seconds, texts/s, and the accepted count (must not change)."""
import json, os, sys, time, importlib
sys.path.insert(0, os.getcwd())
from lean_tok import LeanTokenizer
tok = LeanTokenizer('lean_seq')
fn, n, ws = sys.argv[1], int(sys.argv[2]), [int(x) for x in sys.argv[3].split(',')]
srcs = []
for l in open(fn):
    d = json.loads(l); srcs.append(f"{tok.statement(d['prompt'])} {d['lean_text']}")
    if len(srcs) >= n: break
import lean_gate
print(json.dumps({'cpu_quota': lean_gate.cpu_quota(), 'nproc': os.cpu_count(), 'texts': len(srcs), 'chunk': lean_gate.CHUNK}), flush=True)
for w in ws:
    lean_gate.WORKERS = w
    ok, wall, proc = lean_gate.check_sources(srcs)
    print(json.dumps({'workers': w, 'wall_s': wall, 'proc_s': proc, 'texts_per_s': len(srcs) / wall, 'accepted': sum(ok)}), flush=True)
