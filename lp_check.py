"""lean-prefilter C2/C3: Lean verdict + pre-filter verdict for stored (prompt, lean_text) records.
    python3 lp_check.py IN.jsonl OUT.jsonl        (IN: json lines with 'prompt' (ND prompt) and 'lean_text')
OUT: one line per distinct (prompt, lean_text) that parses in the strict grammar:
    {prompt, lean_text, src, lean, filter}  -- lean = Lean 4 core's verdict via lean_gate.check_sources."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lean_tok import LeanTokenizer, inverse, ParseFail
from lean_gate import check_sources
from lean_prefilter import reject_reason
from lean_prefilter import _split

tok = LeanTokenizer('lean_seq')
inp, outp = sys.argv[1], sys.argv[2]
seen = {}; unparsed = 0
for l in open(inp):
    d = json.loads(l)
    k = (d['prompt'], d['lean_text'])
    if k in seen:
        continue
    try:
        inverse(_split(d['lean_text']))
    except (ParseFail, Exception):
        unparsed += 1; continue
    seen[k] = d.get('src', os.path.basename(inp))
keys = list(seen)
stmt = {p: tok.statement(p) for p in {p for p, _ in keys}}
ok, wall, proc = check_sources([f'{stmt[p]} {tx}' for p, tx in keys])
with open(outp, 'w') as f:
    for (p, tx), v in zip(keys, ok):
        f.write(json.dumps({'prompt': p, 'lean_text': tx, 'src': seen[(p, tx)], 'lean': bool(v),
                            'filter': reject_reason(stmt[p], tx)}, ensure_ascii=False) + '\n')
print(json.dumps({'in': inp, 'distinct_parsed': len(keys), 'unparsed_skipped': unparsed, 'lean_ok': sum(ok),
                  'lean_wall_s': wall, 'lean_proc_s': proc}), flush=True)
