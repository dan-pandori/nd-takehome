"""lean-prefilter test (b): the gate with LEAN_PREFILTER=off and =on over the same stored sample must return the same
verdicts.  python3 lp_b.py DUMP N OUT.json   (DUMP: a C1 gate dump; the first N records, in file order, as one generate()
call's output: ND strings and literal texts as the gate saw them)."""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lean_gate
from lean_tok import LeanTokenizer
fn, n, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
recs = []
for l in open(fn):
    d = json.loads(l); recs.append(d)
    if len(recs) >= n: break
tok = LeanTokenizer('lean_seq')
P = [d['prompt'] for d in recs]; N = [d['nd'] for d in recs]; T = [d['lean_text'] for d in recs]
res = {}
for mode in ('off', 'on'):
    lean_gate.PREFILTER = mode
    os.environ['LEAN_GATE_LOG'] = out.replace('.json', f'.gate_{mode}.jsonl')
    t0 = time.time()
    g = lean_gate.Gate(tok, pipeline=True)
    for i in range(0, len(recs), 4096):
        g.submit(P[i:i + 4096], N[i:i + 4096], T[i:i + 4096])
    o = g.finish(P, N, T)
    res[mode] = {'acc': [not x.startswith('LEANREJ') for x in o], 'secs': time.time() - t0}
diff = [i for i, (a, b) in enumerate(zip(res['off']['acc'], res['on']['acc'])) if a != b]
r = {'dump': fn, 'n': len(recs), 'accepted_off': sum(res['off']['acc']), 'accepted_on': sum(res['on']['acc']),
     'differ': len(diff), 'secs_off': res['off']['secs'], 'secs_on': res['on']['secs'], 'workers': lean_gate.WORKERS,
     'first_diffs': [{'prompt': P[i], 'lean_text': T[i]} for i in diff[:20]]}
json.dump(r, open(out, 'w'), indent=1)
print(json.dumps({k: v for k, v in r.items() if k != 'first_diffs'}))
