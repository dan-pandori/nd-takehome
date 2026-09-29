"""Reviewer's own ND-proof -> Lean 4 translator and Lean driver (long-pool review, phase 1).

Independent of nd2lean.py / lean_tok.py / lean_check.py / lean_judge.py: my own formula renderer, my own box
scoping (spec.md sec. 3-4, fixed citation orders), one `have` per ND line inside a tactic block, each box emitted
as `have b_s_e : A -> G := by intro n_s; ...; exact n_e` (so lines inside a closed box are out of Lean scope).
Only core Lean constants: And.intro, .1/.2, Or.inl/inr, Or.elim, False.elim, Classical.byContradiction.
relaxed=True (used only to classify strict rejections): PR lines may be omitted and BOTE may cite a negation
(Lean's `Not.elim`), the two ND/Lean divergences AGENT_POLICY names as Lean-valid.
Term size (my definition, `my_size`): inference nodes of the pruned proof: every non-PR/AS/R line counts 1;
ORE additionally counts its two box lambdas (so ORE = 3), DN = 3 (byContradiction + its implicit args, calibrated to
lean_check's count after a first pass disagreed on DN only), IMPI / NEGI = 1 (the lambda).
"""
import os, re, subprocess, tempfile
from rv import parse, Bad, prompt_parts

LEAN = os.path.expanduser('~/.elan/bin/lean')
PRELUDE = 'set_option linter.unusedVariables false\nset_option maxRecDepth 10000\n'
BAD = re.compile(r'\b(sorry|admit|exact\?|apply\?|decide|native_decide|aesop|simp|tauto|omega|axiom|sorryAx)\b')


def lf(fs):
    toks = fs.split()

    def go(i):
        t = toks[i]
        if t == '(':
            if toks[i + 1] == '~':
                a, j = go(i + 2)
                if toks[j] != ')':
                    raise Bad('fparen')
                return f'(¬{a})', j + 1
            a, j = go(i + 1)
            op = {'&': '∧', 'v': '∨', '>': '→'}.get(toks[j])
            if op is None:
                raise Bad('fop')
            b, j = go(j + 1)
            if toks[j] != ')':
                raise Bad('fparen2')
            return f'({a} {op} {b})', j + 1
        if t == 'F':
            return 'False', i + 1
        if t in ('P', 'Q', 'R', 'S'):
            return t, i + 1
        raise Bad('ftok ' + t)
    s, j = go(0)
    if j != len(toks):
        raise Bad('ftrail')
    return s


def translate(prompt, proof, name='t', relaxed=False):
    """-> Lean source of one theorem, or raises Bad (structural failure = rejection)."""
    prems, concl = prompt_parts(prompt)
    L = parse(proof)
    n = len(L)
    for k, ln in enumerate(L):
        if ln['idx'] != k + 1:
            raise Bad('numbering')
    # box structure: box[s] = (depth, [line positions in box])
    box_end_last = {}
    box_lines = {}
    for k, ln in enumerate(L):
        if ln['rule'] == 'AS':
            d = ln['depth']
            if d < 1:
                raise Bad('AS at depth 0')
            j = k + 1
            while j < n and L[j]['depth'] >= d and not (L[j]['depth'] == d and L[j]['rule'] == 'AS'):
                j += 1
            box_lines[k + 1] = list(range(k + 1, j + 1))   # 1-based idx
            own = [x for x in box_lines[k + 1] if L[x - 1]['depth'] == d]
            box_end_last[k + 1] = own[-1]
    # depth sanity: a non-AS line may not be deeper than the innermost open box
    cur = 0
    for ln in L:
        if ln['rule'] == 'AS':
            if ln['depth'] > cur + 1:
                raise Bad('AS depth jump')
            cur = ln['depth']
        else:
            if ln['depth'] > cur:
                raise Bad('depth jump')
            cur = ln['depth']
    if L[-1]['depth'] != 0:
        raise Bad('last not depth 0')
    # cited box ends
    cites = {}
    for ln in L:
        r = ln['refs']
        if ln['rule'] in ('IMPI', 'NEGI'):
            if len(r) != 2:
                raise Bad('refs')
            cites.setdefault(r[0], set()).add(r[1])
        elif ln['rule'] == 'ORE':
            if len(r) != 5:
                raise Bad('refs')
            cites.setdefault(r[1], set()).add(r[2]); cites.setdefault(r[3], set()).add(r[4])
    for s, es in cites.items():
        if s not in box_lines:
            raise Bad('box start not AS')
        d = L[s - 1]['depth']
        for e in es:
            if e not in box_lines[s] or L[e - 1]['depth'] != d:
                raise Bad('box end not in box at own depth')
    npr = 0
    out = [f'theorem {name} (P Q R S : Prop) ' + ' '.join(f'(h{j + 1} : {lf(p)})' for j, p in enumerate(prems))
           + f' : {lf(concl)} := by']

    def term(ln):
        nonlocal npr
        r, R_ = ln['refs'], ln['rule']
        need = {'R': 1, 'ANDI': 2, 'ANDE1': 1, 'ANDE2': 1, 'IMPE': 2, 'ORI1': 1, 'ORI2': 1, 'NEGE': 2, 'BOTE': 1,
                'DN': 1, 'PR': 0, 'IMPI': 2, 'NEGI': 2, 'ORE': 5}[R_]
        if len(r) != need:
            raise Bad('refs count')
        if any(x >= ln['idx'] for x in r):
            raise Bad('forward ref')
        if R_ == 'PR':
            npr += 1
            if ln['depth'] != 0 or npr > len(prems) or lf(prems[npr - 1]) != lf(ln['f']):
                raise Bad('PR mismatch')
            return f'h{npr}'
        m = {'R': 'n{0}', 'ANDI': 'And.intro n{0} n{1}', 'ANDE1': 'n{0}.1', 'ANDE2': 'n{0}.2', 'IMPE': 'n{0} n{1}',
             'ORI1': 'Or.inl n{0}', 'ORI2': 'Or.inr n{0}', 'NEGE': 'n{1} n{0}', 'BOTE': 'False.elim n{0}',
             'DN': 'Classical.byContradiction n{0}', 'IMPI': 'b{0}_{1}', 'NEGI': 'b{0}_{1}',
             'ORE': 'Or.elim n{0} b{1}_{2} b{3}_{4}'}[R_]
        if relaxed and R_ == 'BOTE':
            return 'by first | exact False.elim n{0} | exact Not.elim n{0}'.format(*r)
        return m.format(*r)

    def emit(pos_list, ind):
        """pos_list: 1-based idx of lines at this scope (the scope's own lines + nested boxes)."""
        i = 0
        while i < len(pos_list):
            k = pos_list[i]; ln = L[k - 1]
            if ln['rule'] == 'AS':
                body = box_lines[k]
                ends = sorted(cites.get(k, set()) | {box_end_last[k]})
                for e in ends:
                    out.append(' ' * ind + f'have b{k}_{e} : {lf(ln["f"])} → {lf(L[e - 1]["f"])} := by')
                    out.append(' ' * (ind + 2) + f'intro n{k}')
                    emit(body[1:], ind + 2)
                    out.append(' ' * (ind + 2) + f'exact n{e}')
                i += len(body)
                continue
            out.append(' ' * ind + f'have n{k} : {lf(ln["f"])} := {term(ln)}')
            i += 1
    emit(list(range(1, n + 1)), 2)
    if npr != len(prems) and not relaxed:
        raise Bad('PR count')
    out.append(f'  exact n{n}')
    return '\n'.join(out) + '\n'


ERR = re.compile(r':(\d+):\d+: error', re.M)


def _run(text, wd, tag):
    fn = os.path.join(wd, f'{tag}.lean')
    with open(fn, 'w') as f:
        f.write(text)
    try:
        p = subprocess.run([LEAN, '-DmaxErrors=1000000', fn], capture_output=True, text=True, timeout=900)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return -9, 'TIMEOUT'


def check(srcs, chunk=80):
    """srcs: list of Lean sources (or None = structural reject). -> list of (ok, why)."""
    res = [None] * len(srcs)
    wd = tempfile.mkdtemp(prefix='rvlp_')
    idx = [i for i, s in enumerate(srcs) if s is not None]
    for i, s in enumerate(srcs):
        if s is None:
            res[i] = (False, 'structural')
    for c0 in range(0, len(idx), chunk):
        part = idx[c0:c0 + chunk]
        text = PRELUDE; spans = []
        for i in part:
            a = text.count('\n') + 1
            text += srcs[i].replace('theorem t ', f'theorem t_{i} ', 1) + 'example : True := trivial\n'
            spans.append((i, a, text.count('\n')))
        rc, o = _run(text, wd, f'c{c0}')
        bad = set(int(m.group(1)) for m in ERR.finditer(o))
        for i, a, b in spans:
            hit = any(a <= x <= b for x in bad)
            res[i] = (not hit, 'lean error' if hit else '')
        if rc != 0 and not bad:
            # unattributed failure: re-run one per file
            for i, a, b in spans:
                rc1, o1 = _run(PRELUDE + srcs[i], wd, f's{i}')
                res[i] = (rc1 == 0 and not ERR.search(o1), o1[-200:])
        if 'sorry' in o or 'declaration uses' in o:
            for i, a, b in spans:
                res[i] = (False, 'sorry warning in chunk')
    for i, s in enumerate(srcs):
        if s is not None and BAD.search(s):
            res[i] = (False, 'banned token')
    return res


def my_size(prompt, proof):
    L = parse(proof)
    by = {ln['idx']: ln for ln in L}
    keep, st = set(), [L[-1]['idx']]
    while st:
        k = st.pop()
        if k in keep:
            continue
        keep.add(k); st.extend(by[k]['refs'])
    s = 0
    for k in keep:
        r = by[k]['rule']
        if r in ('PR', 'AS', 'R'):
            continue
        s += 3 if r in ('ORE', 'DN') else 1
    return s
