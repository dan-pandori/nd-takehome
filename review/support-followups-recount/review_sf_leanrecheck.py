#!/usr/bin/env python3
"""Reviewer's independent Lean re-check of counted proofs (support-followups; driver reused from review_sc_leanrecheck.py).

Independent of the run's judging path:
  * my own ND-sequent -> Lean statement builder (no lean_tok, no nd2lean),
  * the proof body is the LITERAL sampled text stored in each record (`lean_text`) -- which is what
    AGENT_POLICY requires for a `lean_seq` model,
  * my own Lean driver: one theorem per file, `-DmaxErrors=...`, my own error->theorem mapping,
  * plus an explicit scan of every accepted source for sorry / admit / exact? / decide / axiom /
    native_decide and a check that no `sorry` warning appears (lean exits 0 on `sorry`).
"""
import json, glob, collections, os, re, sys, subprocess, tempfile, random, time

LEAN = os.path.expanduser('~/.elan/bin/lean')
PRELUDE = 'set_option linter.unusedVariables false\nset_option maxRecDepth 4000\n'
ERRLINE = re.compile(r':(\d+):\d+: (error|warning)', re.M)
BAD = re.compile(r'\b(sorry|admit|exact\?|apply\?|decide|native_decide|aesop|simp|tauto|omega|axiom|sorryAx)\b')

# ---------- my own formula / statement rendering ----------
def tokenise(s):
    return s.split()

def parse_formula(toks, i):
    t = toks[i]
    if t == '(':
        # either ( ~ F ) or ( F op F )
        if toks[i+1] == '~':
            inner, j = parse_formula(toks, i+2)
            assert toks[j] == ')', (i, j, toks)
            return f'(¬ {inner})', j+1
        a, j = parse_formula(toks, i+1)
        op = {'&': '∧', 'v': '∨', '>': '→'}[toks[j]]
        b, j = parse_formula(toks, j+1)
        assert toks[j] == ')', (i, j, toks)
        return f'({a} {op} {b})', j+1
    if t == 'F':
        return 'False', i+1
    assert re.fullmatch(r'[A-Z]', t), (t, toks)
    return t, i+1

def statement(prompt):
    """'THM a , b SEQ c PRF' -> 'theorem t (P Q R S : Prop) (h1 : a) (h2 : b) : c := by'"""
    toks = tokenise(prompt)
    assert toks[0] == 'THM' and toks[-1] == 'PRF', prompt
    i = 1; prem = []
    if toks[i] != 'SEQ':
        while True:
            f, i = parse_formula(toks, i); prem.append(f)
            if toks[i] == ',':
                i += 1; continue
            break
    assert toks[i] == 'SEQ', prompt
    concl, i = parse_formula(toks, i+1)
    assert i == len(toks)-1 and toks[i] == 'PRF', prompt
    hs = ' '.join(f'(h{j+1} : {p})' for j, p in enumerate(prem))
    return f'theorem t (P Q R S : Prop) {hs} : {concl} := by'.replace('  ', ' ')

# ---------- my own Lean driver ----------
def lean_batch(srcs, chunk=60):
    """-> list of (ok, diagnostics). One file per chunk; a chunk with any anomaly is re-run one-per-file."""
    out = [None]*len(srcs)
    wd = tempfile.mkdtemp(prefix='revlean_')
    def run_file(text, fn):
        with open(fn, 'w') as f: f.write(text)
        try:
            p = subprocess.run([LEAN, '-DmaxErrors=1000000', fn], capture_output=True, text=True, timeout=300)
            return p.returncode, p.stdout + p.stderr
        except subprocess.TimeoutExpired:
            return -9, 'TIMEOUT'
    for c0 in range(0, len(srcs), chunk):
        part = srcs[c0:c0+chunk]
        text = PRELUDE; starts = []
        for k, s in enumerate(part):
            starts.append(text.count('\n')+1)
            text += s.replace('theorem t ', f'theorem t{k} ', 1).rstrip('\n') + '\n'
        rc, o = run_file(text, os.path.join(wd, f'c{c0}.lean'))
        flagged = {}
        stray = False
        for m in ERRLINE.finditer(o):
            ln = int(m.group(1)); kind = m.group(2)
            k = -1
            for j, s in enumerate(starts):
                if s <= ln: k = j
                else: break
            if 0 <= k < len(part): flagged.setdefault(k, []).append(f'{kind}@{ln}')
            else: stray = True
        if rc in (0, 1) and not stray:
            for k in range(len(part)):
                out[c0+k] = (k not in flagged, ';'.join(flagged.get(k, [])))
        else:                                     # fall back to one theorem per file
            for k, s in enumerate(part):
                rc2, o2 = run_file(PRELUDE + s + '\n', os.path.join(wd, f'one{c0}_{k}.lean'))
                diag = ';'.join(f'{m.group(2)}@{m.group(1)}' for m in ERRLINE.finditer(o2))
                out[c0+k] = (rc2 == 0 and not diag, diag or (f'rc={rc2}' if rc2 else ''))
        print(f'    lean chunk {c0}..{c0+len(part)-1}: rc={rc} flagged={len(flagged)} stray={stray}', flush=True)
    return out


# ---------- pick the sample (support-followups arms) ----------
def fsize(s):
    return sum(1 for t in s.split() if t in ('~','&','v','>','F') or re.fullmatch(r'[A-Z]', t))
def my_term(nd):
    tot = 0
    for seg in nd.split(';'):
        seg = seg.strip()
        if not seg or seg == 'QED': continue
        m = re.match(r'N\d+\s+((?:\|\s*)*)(.*?)\s:\s', seg + ' ')
        if m: tot += fsize(m.group(2))
    return tot
def my_lines(nd): return sum(1 for s in nd.split(';') if s.strip() and s.strip() != 'QED')
PROMPT = {json.loads(l)['name']: json.loads(l)['prompt'] for l in open('data/sc/theorems.jsonl')}
ARMS = {'A_base_s1': 'artifacts/sf/a_base_T08_s1.s*.jsonl', 'A_ei_s1rerun': 'artifacts/sf/a_ei_T08_s1rerun.s*.jsonl',
        'B_base_s0_T1': 'artifacts/sf/b_*.jsonl', 'C_big_s0': 'artifacts/sf/c[12]_big_*_s0*.jsonl',
        'C_big_s1': 'artifacts/sf/c[12]_big_*_s1*.jsonl'}
TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 130
rng = random.Random(4242)
sel = {}; allstats = {}
for arm, pat in ARMS.items():
    bythm = collections.defaultdict(list)
    for f in sorted(glob.glob(pat)):
        for l in open(f):
            r = json.loads(l)
            for p in r['proofs']: bythm[r['name']].append((os.path.basename(f), p))
    n = sum(len(v) for v in bythm.values())
    order = sorted(bythm); rng.shuffle(order)
    picked = []; depth = 0
    while len(picked) < min(TARGET, n):
        for nm in order:
            if depth < len(bythm[nm]):
                picked.append((nm,) + bythm[nm][depth])
                if len(picked) >= TARGET: break
        depth += 1
    sel[arm] = picked
    allp = [p for v in bythm.values() for _, p in v]
    allstats[arm] = {'distinct_proofs': n, 'theorems': len(bythm),
                     'n_lines_mismatch_all': sum(1 for p in allp if p['n_lines'] != my_lines(p['proof'])),
                     'term_size_mismatch_all': sum(1 for p in allp if p['term_size'] != my_term(p['proof'])),
                     'dup_normalised_within_thm': sum(len(v) - len({p['proof'] for _, p in v}) for v in bythm.values())}
    print(arm, allstats[arm], '-> re-check', len(picked), flush=True)

report = {}
# negative control: a deliberately wrong body on the first A_ei theorem
nm0, _, p0 = sel['A_ei_s1rerun'][0]
neg = statement(PROMPT[nm0]) + ' ' + re.sub(r'exact n\d+\s*$', 'exact h1', p0['lean_text'].strip())
neg2 = statement(PROMPT[nm0]) + ' sorry'
res = lean_batch([neg, neg2], chunk=1)
report['negative_control'] = {'wrong_exact_accepted': res[0][0], 'sorry_accepted_by_lean_exitcode': res[1][0], 'sorry_flagged_by_BAD': bool(BAD.search(neg2))}
print(report['negative_control'], flush=True)
for arm, picked in sel.items():
    srcs = [statement(PROMPT[nm]) + ' ' + p['lean_text'] for nm, _, p in picked]
    t0 = time.time(); res = lean_batch(srcs)
    rej = [(picked[i][0], picked[i][1], res[i][1]) for i in range(len(srcs)) if not res[i][0]]
    report[arm] = {**allstats[arm], 'rechecked': len(srcs), 'lean_ok': sum(1 for x in res if x[0]), 'rejected': rej[:10],
                   'banned_token_hits': sum(1 for s in srcs if BAD.search(s)), 'secs': round(time.time() - t0, 1)}
    print(arm, report[arm], flush=True)
json.dump(report, open('rev_sf/lean_recheck.json', 'w'), indent=1)
