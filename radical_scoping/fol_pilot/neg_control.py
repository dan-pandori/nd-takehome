"""P1 negative control: Lean must reject broken FOL proofs. Two mutations on the first 300 pool proofs:
 (m1) conclusion constant swap: the first constant in the rendered conclusion is replaced by a different one;
 (m2) eigenvariable violation: every ALLI's parameter is renamed to a constant of a premise (if the proof has ALLI and
      the premises have a constant), so the generalised constant is no longer fresh.
Some m1 mutants stay valid (e.g. the constant was irrelevant); the point is that the rejection rate is far from 0."""
import json, re, sys, subprocess, tempfile, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fol2lean
recs = [json.loads(l) for l in open('pool1k.jsonl')][:300]
LEAN = fol2lean.LEAN
def run(srcs):
    body = 'set_option maxErrors 100000\n' + '\n'.join(s.replace('theorem t ', f'theorem t{k} ', 1) + f'#print axioms t{k}\n' for k, s in srcs)
    fn = os.path.join(tempfile.mkdtemp(), 'n.lean'); open(fn, 'w').write(body)
    out = subprocess.run([LEAN, '-DmaxErrors=100000', fn], capture_output=True, text=True); out = out.stdout + out.stderr
    starts = sorted((body[:m.start()].count('\n') + 1, int(m.group(1))) for m in re.finditer(r'^theorem t(\d+) ', body, re.M))
    bad = set()
    for m in re.finditer(r':(\d+):\d+: error', out):
        ln = int(m.group(1)); bad.add(max(k for s, k in starts if s <= ln))
    bad |= {int(k) for k in re.findall(r"'t(\d+)' depends on axioms: \[[^\]]*sorryAx", out)}
    return bad
m1, m2 = [], []
for k, r in enumerate(recs):
    s = fol2lean.render(r)
    head, body = s.split(' :=\n', 1); pre, concl = re.split(r'\) +: ', head, maxsplit=1)[0], re.split(r'\) +: ', head)[-1]
    cs = re.findall(r'\b([a-e])\b', concl)
    if cs:
        new = 'b' if cs[0] != 'b' else 'c'
        m1.append((k, pre + ') : ' + re.sub(rf'\b{cs[0]}\b', new, concl, count=1) + ' :=\n' + body))
    if 'ALLI' in r['rules']:
        pc = re.findall(r'\(h\d+ : [^\n]*?\b([a-e])\b', pre)
        alli = re.findall(r'\(fun \(([a-e]) : U\)', body)
        if pc and alli and pc[0] not in alli:
            m2.append((k, re.sub(rf'\(fun \({alli[0]} : U\)', f'(fun ({pc[0]} : U)', s, count=1)))
for name, ms in (('m1 conclusion-constant swap', m1), ('m2 ALLI eigenvariable clash', m2)):
    bad = run(ms); print(f'{name}: mutants={len(ms)} rejected={len(bad)} ({100*len(bad)/max(len(ms),1):.0f}%)')
