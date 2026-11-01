#!/usr/bin/env python3
"""Reviewer (coe-dose01): strict follow-up of tb72scan hits -- does a line contain an EXPLICIT sequent (THM .. SEQ .. PRF,
'A , B |- C', 'A, B ⊢ C', or a Lean header '(h1 : A) .. : C :=') whose renaming class (premise-order invariant, premises
as a set) is a textbook72 class?  Reports file, line number, whether the line was added by this run, and the match type;
never the statement."""
import re, subprocess, sys
sys.path.insert(0, '/home/dan/work/coe-dose01/review_cd01')
from common import REPO, jl, seq_of_prompt, pf, fs, rename, PERMS
from tb72scan import toks_of, parse_any, tb72_variants

def tb_keys():
    K = set()
    for npre, nc, vs, p in tb72_variants():
        for pre, c in vs:
            K.add((pre, c))
    return K

def seqs(line):
    out = []
    t = ' '.join(toks_of(line))
    for m in re.finditer(r'THM(.*?)SEQ(.*?)PRF', t):
        out.append((m.group(1), m.group(2)))
    for m in re.finditer(r'([^|`;"]*?)\|- ([^`;"|]*)', t):
        out.append((m.group(1), m.group(2)))
    # Lean headers: balanced ( hN : A ) groups, then ' : C :='
    tk = t.split()
    i = 0
    prem = []
    while i < len(tk):
        if tk[i] == '(' and i + 2 < len(tk) and re.fullmatch(r'h\d+', tk[i + 1]) and tk[i + 2] == ':':
            d = 0
            for j in range(i, len(tk)):
                d += tk[j] == '('; d -= tk[j] == ')'
                if d == 0:
                    break
            prem.append(' '.join(tk[i + 3:j])); i = j + 1
            continue
        if tk[i] == ':' and (prem or (i >= 2 and tk[i - 1] == ')' and tk[i - 2] == 'Prop')):
            k = tk.index(':=', i) if ':=' in tk[i:] else len(tk)
            out.append((' , '.join(prem), ' '.join(tk[i + 1:k])))
            prem = []
        i += 1
    return out

def parse_seq(pre, c):
    """conclusion = longest parseable prefix; premises = top-level comma parts read from the right, the leftmost kept part
    reduced to its longest parseable suffix; returns every candidate split (prefer more premises)"""
    ct = c.split()
    C = None
    for j in range(len(ct), 0, -1):
        C = parse_any(ct[:j])
        if C:
            break
    if not C:
        return []
    parts = [x.split() for x in ' '.join(pre.split()).split(' , ')] if pre.strip() else []
    cands = [([], C)]
    P = []
    for k in range(len(parts) - 1, -1, -1):
        tt = parts[k]
        f = parse_any(tt)
        if f is None:
            for a in range(1, len(tt)):
                f = parse_any(tt[a:])
                if f:
                    break
            if f is not None:
                cands.append(([f] + P, C))
            break
        P = [f] + P
        cands.append((list(P), C))
    return cands

def main(files):
    K = tb_keys()
    base = '8e195390'
    for fn in files:
        added = set()
        d = subprocess.run(['git', '-C', REPO, 'diff', '-U0', base, 'HEAD', '--', fn], capture_output=True, text=True).stdout
        cur = None
        for l in d.splitlines():
            m = re.match(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', l)
            if m:
                cur = int(m.group(1)); continue
            if cur is not None and l.startswith('+') and not l.startswith('+++'):
                added.add(cur); cur += 1
        tracked = subprocess.run(['git', '-C', REPO, 'ls-files', '--error-unmatch', fn], capture_output=True).returncode == 0
        n_exp = n_exp_added = 0
        lines = open(f'{REPO}/{fn}' if not fn.startswith('/') else fn, errors='ignore').read().splitlines()
        for i, ln in enumerate(lines, 1):
            for pre, c in seqs(ln):
                hit = any((tuple(sorted(set(fs(x) for x in P))), fs(C)) in K for P, C in parse_seq(pre, c))
                if hit:
                    n_exp += 1
                    is_added = (i in added) or not tracked
                    n_exp_added += is_added
                    print(f'  explicit tb72-class sequent: {fn}:{i} (added by this run: {is_added})')
        print(f'{fn}: explicit tb72-class sequents {n_exp} (on lines added by this run / untracked: {n_exp_added})')

if __name__ == '__main__':
    main(sys.argv[1:])
