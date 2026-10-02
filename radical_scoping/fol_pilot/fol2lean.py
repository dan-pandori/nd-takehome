"""P1: render June-sprint FOL Fitch proofs into Lean 4 core terms and check them with Lean (no Mathlib).
Free variables in the sprint's formulas are declared as parameters (x y z w : U). Every line becomes `(show T from e)`; boxes become `fun`; ALLI is `fun (p : U) => ..`, ALLE application to the
instantiating constant, EXI `⟨t, e⟩`, EXE `Exists.elim`, DN `Classical.byContradiction`.
  python3 fol2lean.py --in pool1k.jsonl --n 200 --out lean_report.jsonl
A proof counts iff Lean elaborates it and `#print axioms` shows no sorryAx. Stdout is a summary table."""
import argparse, json, os, re, subprocess, sys, collections, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fol.verify import parse_proof_tokens, parse_formula
from fol.core import match_instance

LEAN = os.environ.get('LEAN', os.path.expanduser('~/.elan/bin/lean'))

def tm(t): return t[1]
def fm(f):
    k = f[0]
    if k == 'bot': return 'False'
    if k == 'atom': return '(' + ' '.join([f[1]] + [tm(t) for t in f[2]]) + ')'
    if k == 'not': return f'(¬ {fm(f[1])})'
    if k == 'and': return f'({fm(f[1])} ∧ {fm(f[2])})'
    if k == 'or': return f'({fm(f[1])} ∨ {fm(f[2])})'
    if k == 'imp': return f'({fm(f[1])} → {fm(f[2])})'
    if k == 'all': return f'(∀ {f[1]} : U, {fm(f[2])})'
    if k == 'ex': return f'(∃ {f[1]} : U, {fm(f[2])})'
    raise ValueError(k)

def render(rec):
    toks = rec['text'].split(); i = 1; prem = []
    if toks[i] != 'SEQ':
        while True:
            f, i = parse_formula(toks, i); prem.append(f)
            if toks[i] == ',': i += 1; continue
            break
    i += 1; concl, i = parse_formula(toks, i)
    lines = {l['idx']: l for l in parse_proof_tokens(toks[toks.index('PRF') + 1:])}
    def T(k):
        l = lines[k]; F = l['formula']; r = l['rule']; R = l['refs']
        if r in ('PR', 'AS'): return f'h{k}'
        if r == 'R': e = T(R[0])
        elif r == 'ANDI': e = f'⟨{T(R[0])}, {T(R[1])}⟩'
        elif r == 'ANDE1': e = f'({T(R[0])}).1'
        elif r == 'ANDE2': e = f'({T(R[0])}).2'
        elif r == 'ORI1': e = f'(Or.inl {T(R[0])})'
        elif r == 'ORI2': e = f'(Or.inr {T(R[0])})'
        elif r == 'IMPE':
            a, b = R; e = f'({T(a)} {T(b)})' if lines[a]['formula'][0] == 'imp' and lines[a]['formula'][2] == F else f'({T(b)} {T(a)})'
        elif r == 'NEGE':
            a, b = R; e = f'({T(b)} {T(a)})' if lines[b]['formula'] == ('not', lines[a]['formula']) else f'({T(a)} {T(b)})'
        elif r in ('IMPI', 'NEGI'):
            s, t = R; e = f'(fun (h{s} : {fm(lines[s]["formula"])}) => {T(t)})'
        elif r == 'BOTE': e = f'(False.elim {T(R[0])})'
        elif r == 'DN': e = f'(Classical.byContradiction {T(R[0])})'
        elif r == 'ORE':
            d, s1, e1, s2, e2 = R
            e = f'(Or.elim {T(d)} (fun (h{s1} : {fm(lines[s1]["formula"])}) => {T(e1)}) (fun (h{s2} : {fm(lines[s2]["formula"])}) => {T(e2)}))'
        elif r == 'ALLE':
            A = lines[R[0]]['formula']; t = match_instance(A[2], A[1], F)
            e = f'({T(R[0])} {tm(t)})'
        elif r == 'EXI':
            t = match_instance(F[2], F[1], lines[R[0]]['formula'])
            e = f'⟨{tm(t)}, {T(R[0])}⟩'
        elif r == 'ALLI':
            t = match_instance(F[2], F[1], lines[R[0]]['formula']); p = '_p' if t == ('v', F[1]) else tm(t)
            e = f'(fun ({p} : U) => {T(R[0])})'
        elif r == 'EXE':
            j, s, t2 = R; Ex = lines[j]['formula']; p = match_instance(Ex[2], Ex[1], lines[s]['formula'])
            e = f'(Exists.elim {T(j)} (fun ({tm(p)} : U) (h{s} : {fm(lines[s]["formula"])}) => {T(t2)}))'
        else: raise ValueError(r)
        return f'(show {fm(F)} from {e})'
    last = max(lines)
    hyps = ' '.join(f'(h{k} : {fm(lines[k]["formula"])})' for k in sorted(lines) if lines[k]['rule'] == 'PR')
    return f'theorem t (U : Type) (P Q : U → Prop) (R S : U → U → Prop) (a b c d e : U) (x y z w : U) {hyps} : {fm(concl)} :=\n  {T(last)}\n'

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--in', dest='inp'); ap.add_argument('--n', type=int, default=200)
    ap.add_argument('--out'); a = ap.parse_args()
    recs = [json.loads(l) for l in open(a.inp)][:a.n]
    srcs = []; bad = 0
    for k, r in enumerate(recs):
        try: srcs.append(render(r).replace('theorem t ', f'theorem t{k} ', 1))
        except Exception as ex: srcs.append(None); bad += 1
    body = 'set_option maxRecDepth 4000\nset_option maxErrors 100000\n\n' + '\n'.join(s + f'#print axioms t{k}\n' for k, s in enumerate(srcs) if s)
    d = tempfile.mkdtemp(); fn = os.path.join(d, 'fol.lean'); open(fn, 'w').write(body)
    t0 = time.time(); p = subprocess.run([LEAN, '-DmaxErrors=100000', fn], capture_output=True, text=True); wall = time.time() - t0
    out = p.stdout + p.stderr
    # map errors to theorem index by source line
    starts = sorted((body[:m.start()].count('\n') + 1, int(m.group(1))) for m in re.finditer(r'^theorem t(\d+) ', body, re.M))
    def owner(line):
        o = None
        for s, k in starts:
            if s <= line: o = k
        return o
    err = collections.defaultdict(list)
    for m in re.finditer(r':(\d+):\d+: error: (.*)', out): err[owner(int(m.group(1)))].append(m.group(2)[:150])
    sorry = {int(k) for k in re.findall(r"'t(\d+)' depends on axioms: \[[^\]]*sorryAx", out)}
    rep = []; c = collections.Counter(); byrule = collections.Counter(); byrule_ok = collections.Counter()
    for k, r in enumerate(recs):
        ok = srcs[k] is not None and k not in err and k not in sorry
        c['ok' if ok else ('render_fail' if srcs[k] is None else 'lean_reject')] += 1
        for ru in set(r['rules']): byrule[ru] += 1; byrule_ok[ru] += ok
        rep.append({'i': k, 'ok': ok, 'errors': err.get(k, []), 'n_lines': r['n_lines'], 'rules': r['rules'], 'lean': srcs[k]})
    with open(a.out, 'w') as f:
        for x in rep: f.write(json.dumps(x) + '\n')
    print(f'n={len(recs)} {dict(c)} lean_wall_s={wall:.1f} lean_exit={p.returncode} lean_errors_total={len(re.findall(": error:", out))}')
    for ru in sorted(byrule, key=lambda x: -byrule[x]): print(f'  {ru:6s} {byrule_ok[ru]}/{byrule[ru]}')
    open(a.out + '.leanlog', 'w').write(out[-20000:])
if __name__ == "__main__":
    main()
