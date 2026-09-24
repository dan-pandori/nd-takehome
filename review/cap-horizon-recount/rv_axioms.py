"""Reviewer's own allowlist + axiom check on the same sampled counted proofs.
Proposal 9's `lean_check` does not exist in this repository, so the two checks it specifies
are implemented here: (a) every identifier in the generated Lean term is on an allowlist,
(b) `#print axioms` reports nothing beyond the three standard classical axioms and never
`sorryAx`."""
import sys, os, json, re, subprocess, tempfile
sys.path.insert(0, '/home/dan/review/cap-horizon')
from nd2lean import translate, LEAN

ALLOWED_IDENT = {
    'theorem', 'Prop', 'by', 'have', 'exact', 'fun', 'set_option', 'maxRecDepth', 'False',
    'Classical.byContradiction', 'False.elim', 'Or.elim', 'Or.inl', 'Or.inr', 'axioms',
    'P', 'Q', 'R', 'S',
}
IDENT = re.compile(r'[A-Za-z_][A-Za-z0-9_.]*')
OKAX = {'propext', 'Classical.choice', 'Quot.sound'}


def idents_ok(src):
    bad = set()
    for m in IDENT.finditer(src):
        t = m.group(0)
        if t in ALLOWED_IDENT:
            continue
        if re.fullmatch(r'[nh]\d+|hh|t\d*', t):     # generated hypothesis / line names
            continue
        bad.add(t)
    return bad


def run(arm, fn):
    recs = [json.loads(l) for l in open(fn)]
    srcs = [translate(r['prompt'], r['proof']) for r in recs]
    bad_idents = {}
    for r, s in zip(recs, srcs):
        b = idents_ok(s)
        if b:
            bad_idents.setdefault(r['name'], sorted(b))
    res = {'arm': arm, 'n': len(recs), 'identifiers_off_allowlist': bad_idents}
    ax_bad, checked = {}, 0
    d = tempfile.mkdtemp(prefix='rvax_')
    per = 25
    for b in range(0, len(srcs), per):
        chunk = srcs[b:b + per]
        text = 'set_option maxRecDepth 4000\n'
        for k, s in enumerate(chunk):
            text += s.replace('theorem t ', f'theorem t{b}_{k} ', 1) + '\n'
            text += f'#print axioms t{b}_{k}\n'
        p = os.path.join(d, f'c{b}.lean')
        open(p, 'w').write(text)
        out = subprocess.run([LEAN, p], capture_output=True, text=True)
        blob = out.stdout + out.stderr
        if ': error' in blob:
            ax_bad.setdefault('_lean_errors', []).append(blob[:400])
        for m in re.finditer(r"'(t\d+_\d+)' does not depend on any axioms", blob):
            checked += 1
        for m in re.finditer(r"'(t\d+_\d+)' depends on axioms: \[([^\]]*)\]", blob):
            checked += 1
            ax = {x.strip() for x in m.group(2).split(',') if x.strip()}
            if ax - OKAX:
                ax_bad.setdefault(m.group(1), sorted(ax))
    res['axiom_prints_seen'] = checked
    res['axiom_violations'] = ax_bad
    res['sorry_in_sources'] = sum('sorry' in s for s in srcs)
    return res


if __name__ == '__main__':
    out = {}
    for arm in ('K6', 'K8flat', 'K8add', 'K10', 'K12', 'K14'):
        out[arm] = run(arm, f'/home/dan/review/cap-horizon/rv/leansample/{arm}.jsonl')
        print(json.dumps(out[arm])[:600])
        sys.stdout.flush()
    json.dump(out, open('/home/dan/review/cap-horizon/rv/out_axioms.json', 'w'), indent=1)
