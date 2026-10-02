#!/usr/bin/env python3
"""C3/C4 Lean spot-check with an own driver (Lean 4 core, NO `import Lean`, so ~200 MB per process).

Statement rendered here from the ND prompt (own renderer: P Q R S atoms, F = False, ~ ¬, > →, v ∨, & ∧),
proof = the dump's literal `lean_text` (as the gate sent it).  A text is ACCEPTED iff
  - no `error` message attributed to its lines (any error rejects: parse recovery can accept truncated terms),
  - `#print axioms` lists no sorryAx (and the theorem exists),
  - the text contains none of: sorry, simp, decide, tauto, omega, native, Classical.em, admit, axiom, Decidable.
Negative controls per sampled text (all must be REJECTED):
  (a) the text under a different theorem's statement (next sampled theorem with a different prompt),
  (b) the statement's conclusion C replaced by ¬C (text unchanged),
  (c) the final `exact ...` removed,
  (d) the final `exact ...` replaced by `exact sorry`.
Usage: c34_lean.py OUT_TAG N_PER_FILE dump1[.gz] dump2 ...   (samples only lean_ok == true records, seed 20261002)
"""
import gzip, json, os, random, re, subprocess, sys, tempfile, collections

LEAN = os.path.expanduser('~/.elan/bin/lean')
SYM = {'~': '¬', '>': '→', 'v': '∨', '&': '∧', 'F': 'False', '<>': '↔'}
BAD = re.compile(r'\b(sorry|simp|decide|tauto|omega|native_decide|admit|axiom|Decidable)\b|Classical\.em')


def f2l(s):
    return ' '.join(SYM.get(t, t) for t in s.split())


def statement(prompt, neg=False):
    p = prompt.strip()
    assert p.startswith('THM') and p.endswith('PRF'), p
    prem, concl = (' ' + p[3:-3].strip() + ' ').split(' SEQ ')
    prems = [x.strip() for x in prem.split(' , ')] if prem.strip() else []
    hyps = ' '.join(f'(h{j + 1} : {f2l(x)})' for j, x in enumerate(prems))
    c = f2l(concl.strip())
    if neg:
        c = f'¬ ({c})'
    return f'theorem t (P Q R S : Prop) {hyps} : {c} := by'


def opener(p):
    return gzip.open(p, 'rt') if p.endswith('.gz') else open(p)


def run(items):
    """items: list of (statement, text) -> list of (ok, reason)"""
    src = ['set_option maxRecDepth 4000', 'set_option linter.unusedVariables false']
    starts = []
    line = len(src) + 1
    for k, (st, tx) in enumerate(items):
        starts.append(line)
        sep = '\n' if '\n' in tx else ' '      # multi-line (indented) bodies keep their layout
        body = st.replace('theorem t ', f'theorem t{k} ', 1) + sep + tx.rstrip('\n')
        src.append(body)
        src.append(f'#print axioms t{k}')
        line += body.count('\n') + 2
    with tempfile.NamedTemporaryFile('w', suffix='.lean', delete=False, dir='/tmp') as f:
        f.write('\n'.join(src) + '\n')
        fn = f.name
    try:
        p = subprocess.run(['flock', '/tmp/ca_lean.lock', 'nice', '-n', '10', LEAN, '-DmaxErrors=100000000', fn],
                           capture_output=True, text=True, timeout=1800)
        o = p.stdout + p.stderr
    finally:
        os.remove(fn)
    errs = collections.defaultdict(list)
    for m in re.finditer(r'^[^\n]*?:(\d+):\d+: error: ([^\n]*)', o, re.M):
        ln = int(m.group(1))
        ks = [j for j, s in enumerate(starts) if s <= ln]
        if ks:
            errs[ks[-1]].append(m.group(2)[:100])
    ax = {}
    for m in re.finditer(r"'t(\d+)' depends on axioms: \[([^\]]*)\]", o):
        ax[int(m.group(1))] = m.group(2)
    for m in re.finditer(r"'t(\d+)' does not depend on any axioms", o):
        ax[int(m.group(1))] = ''
    res = []
    for k, (st, tx) in enumerate(items):
        if errs.get(k):
            res.append((False, 'error: ' + errs[k][0]))
        elif k not in ax:
            res.append((False, 'no axioms line'))
        elif 'sorryAx' in ax[k]:
            res.append((False, 'sorryAx'))
        elif BAD.search(tx):
            res.append((False, 'blocked token'))
        else:
            res.append((True, ax[k]))
    return res


def drop_last_exact(tx):
    i = tx.rfind('exact')
    return tx[:i].rstrip(' ;') if i > 0 else tx + ' ;'


def main():
    tag, nper, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
    rng = random.Random(20261002)
    samp = []
    for fp in files:
        acc = []
        with opener(fp) as f:
            for l in f:
                r = json.loads(l)
                if r.get('lean_ok') and r.get('lean_text'):
                    acc.append((r['prompt'], r['lean_text']))
        # one per distinct prompt first (spread over theorems), then random
        byp = collections.defaultdict(list)
        for a in acc:
            byp[a[0]].append(a)
        ps = sorted(byp)
        rng.shuffle(ps)
        pick = [rng.choice(byp[p]) for p in ps[:nper]]
        samp += [(os.path.basename(fp),) + x for x in pick]
        print(f'{os.path.basename(fp)}: {len(acc)} accepted texts over {len(byp)} prompts; sampled {len(pick)}', flush=True)
    pos = [(statement(p), tx) for _, p, tx in samp]
    nega, negb, negc, negd = [], [], [], []
    for i, (_, p, tx) in enumerate(samp):
        j = (i + 1) % len(samp)
        while samp[j][1] == p:
            j = (j + 1) % len(samp)
        nega.append((statement(samp[j][1]), tx))
        negb.append((statement(p, neg=True), tx))
        negc.append((statement(p), drop_last_exact(tx)))
        negd.append((statement(p), drop_last_exact(tx) + ' ; exact sorry'))
    allit = pos + nega + negb + negc + negd
    out = []
    B = 400
    for i in range(0, len(allit), B):
        out += run(allit[i:i + B])
    n = len(pos)
    rp, ra, rb, rc, rd = out[:n], out[n:2 * n], out[2 * n:3 * n], out[3 * n:4 * n], out[4 * n:]
    print(f'[{tag}] positives accepted {sum(o for o, _ in rp)}/{n}; controls accepted: other-theorem {sum(o for o, _ in ra)}/{n}, '
          f'negated-goal {sum(o for o, _ in rb)}/{n}, last-exact-dropped {sum(o for o, _ in rc)}/{n}, exact-sorry {sum(o for o, _ in rd)}/{n}')
    bad = [(samp[i][0], samp[i][1][:80], rp[i][1][:120]) for i in range(n) if not rp[i][0]]
    for b in bad[:10]:
        print('  REJECTED positive:', b)
    for nm, r in (('other', ra), ('neg', rb), ('drop', rc), ('sorry', rd)):
        for i in range(n):
            if r[i][0]:
                print(f'  control {nm} ACCEPTED:', samp[i][0], samp[i][1][:80])
    os.makedirs(os.path.expanduser('~/work/claim-audit/audit/out'), exist_ok=True)
    with open(os.path.expanduser(f'~/work/claim-audit/audit/out/c34_lean_{tag}.json'), 'w') as f:
        json.dump({'files': files, 'n': n, 'pos_ok': sum(o for o, _ in rp), 'ctrl_other_ok': sum(o for o, _ in ra),
                   'ctrl_neg_ok': sum(o for o, _ in rb), 'ctrl_drop_ok': sum(o for o, _ in rc), 'ctrl_sorry_ok': sum(o for o, _ in rd),
                   'axioms': collections.Counter(r for o, r in rp if o).most_common(5)}, f, indent=1)


if __name__ == '__main__':
    main()
