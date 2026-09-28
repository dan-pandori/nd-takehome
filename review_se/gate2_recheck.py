#!/usr/bin/env python3
"""Reviewer re-derivation of gate 2 ("the environment's state is Lean's state"): re-run Lean on every stored case
source, parse Lean's trace_state output with my own precedence parser, compare hypotheses (names, types) and goal with
the stored renderer state.  Run from the review copy."""
import json, re, subprocess, sys, os, glob, tempfile
LEAN = os.path.expanduser('~/.elan/bin/lean')
PREC = {'∧': (35, 'r'), '∨': (30, 'r'), '→': (25, 'r')}
def tok(s):
    return re.findall(r'False|[PQRS]|[()¬∧∨→]', s)
def parse(ts):
    pos = [0]
    def atom():
        t = ts[pos[0]]; pos[0] += 1
        if t == '(':
            e = expr(0); assert ts[pos[0]] == ')'; pos[0] += 1; return e
        if t == '¬':
            return ('not', atom())
        return t
    def expr(minp):
        lhs = atom()
        while pos[0] < len(ts) and ts[pos[0]] in PREC and PREC[ts[pos[0]]][0] >= minp:
            op = ts[pos[0]]; pos[0] += 1
            p, a = PREC[op]
            rhs = expr(p if a == 'r' else p + 1)
            lhs = (op, lhs, rhs)
        return lhs
    e = expr(0); assert pos[0] == len(ts), ts
    return e
def canon_ours(s):
    return parse(s.split())
def main():
    out = {}
    for fn in sorted(glob.glob('artifacts/se/gate2*_cases.jsonl')):
        C = [json.loads(l) for l in open(fn)]
        lines = []
        for k, c in enumerate(C):
            lines.append(f'#print "CASE {k}"')
            lines.append(c['src'].replace('theorem t ', f'theorem t{k} ', 1))
        tf = tempfile.mktemp(suffix='.lean'); open(tf, 'w').write('\n'.join(lines) + '\n')
        o = subprocess.run([LEAN, tf], capture_output=True, text=True).stdout
        os.remove(tf)
        parts = re.split(r'^CASE (\d+)\n', o, flags=re.M)
        got = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}
        mism = []; kinds = {}
        for k, c in enumerate(C):
            txt = got.get(k, '')
            txt = re.sub(r'^\S+:\d+:\d+: warning: declaration uses .sorry.\n?', '', txt, flags=re.M)
            if 'error' in txt: mism.append((k, 'lean error')); continue
            hyps = []; goal = None; cur = None
            for ln in txt.split('\n'):
                if not ln.strip(): continue
                if ln.startswith('⊢ '): cur = ('goal', ln[2:]); goal = ln[2:]; continue
                if ln.startswith(' ') and cur is not None:     # continuation of a wrapped type
                    if cur[0] == 'goal': goal += ' ' + ln.strip()
                    else: hyps[-1] = (hyps[-1][0], hyps[-1][1] + ' ' + ln.strip())
                    continue
                m = re.match(r'^(.+?) : (.*)$', ln)
                if not m: mism.append((k, 'unparsed ' + ln)); break
                names = m.group(1).split()
                if m.group(2) == 'Prop': cur = ('prop',); continue
                for nm in names: hyps.append((nm, m.group(2)))
                cur = ('hyp',)
            # regroup continuation: we appended continuation only to the last hyp; for grouped names types are equal
            try:
                lean_h = [(n, parse(tok(t))) for n, t in hyps]
                ours_h = [(n, canon_ours(t)) for n, t in c['ours']]
                ok = lean_h == ours_h and parse(tok(goal)) == canon_ours(c['ours_goal'])
            except Exception as e:
                ok = False
            kinds[c['kind']] = kinds.get(c['kind'], 0) + 1
            if not ok: mism.append((k, 'differs', hyps, goal))
        out[os.path.basename(fn)] = {'n': len(C), 'mismatches': len(mism), 'by_kind': kinds, 'examples': mism[:3]}
        print(fn, len(C), 'mismatches', len(mism), kinds, mism[:2], flush=True)
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gate2_recheck.json'), 'w'), indent=1)
main()
