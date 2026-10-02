"""C1/C2 Lean spot-check (own driver, own statement builder). One lean process per theorem; a text counts as accepted
only if lean exits 0 AND prints nothing containing 'error' / 'sorry' / 'warning: declaration uses'.
usage: c12_lean.py IN.jsonl OUT.tsv   (IN rows: {id, prompt, lean_text, expect})"""
import json, subprocess, sys, tempfile, os, re
LEAN = os.path.expanduser('~/.elan/bin/lean')
SYM = {'~': '¬', '&': '∧', 'v': '∨', '>': '→', 'F': 'False'}
BANNED = re.compile(r'\b(sorry|admit|axiom|native_decide|decide|unsafe|implemented_by|extern|macro|syntax|elab|set_option|import|open|#)\b')
def lean_formula(nd):
    return ' '.join(SYM.get(t, t) for t in nd.split())
def source(prompt, text):
    s = prompt.strip()[3:].rsplit('PRF', 1)[0]
    lhs, rhs = s.split(' SEQ ')
    prem = [p.strip() for p in lhs.split(' , ')] if lhs.strip() else []
    hyps = ' '.join(f'(h{i+1} : {lean_formula(p)})' for i, p in enumerate(prem))
    return f'theorem t (P Q R S : Prop) {hyps} : {lean_formula(rhs.strip())} := by\n  {text}\n'
def check(prompt, text):
    if BANNED.search(text): return False, 'banned'
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, 'T.lean'); open(f, 'w').write(source(prompt, text))
        p = subprocess.run([LEAN, '-DmaxErrors=1000', f], capture_output=True, text=True, timeout=120)
        out = p.stdout + p.stderr
        ok = p.returncode == 0 and not re.search(r'error|sorry|declaration uses', out)
        return ok, out.strip().splitlines()[0][:100] if out.strip() else ''
if __name__ == '__main__':
    rows = [json.loads(l) for l in open(sys.argv[1])]
    res = []; 
    with open(sys.argv[2], 'w') as fo:
        for r in rows:
            ok, msg = check(r['prompt'], r['lean_text'])
            res.append((r['expect'], ok)); fo.write(f"{r['id']}\t{r['expect']}\t{ok}\t{msg}\n")
    for e in ('accept', 'reject'):
        sub = [ok for ex, ok in res if ex == e]
        print(f'{e}: n={len(sub)} lean_accepted={sum(sub)}')
