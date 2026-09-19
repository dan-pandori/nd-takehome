#!/usr/bin/env python3
"""Reviewer's independent helpers for round3-run4a (written without reading patterns.py / normalize.py / prune.py code
or run4a_analysis.py): proof parser, start-index normaliser, dependency pruner, strict-reductio predicate, depth counter,
renaming-class canonicaliser. Only nd_verify (unmodified) is imported from the repository."""
import re, itertools

NTOK = re.compile(r'N(\d+)$')


def parse(proof):
    """-> list of dicts {idx, depth, formula (token tuple), rule, refs (ints)}; None if malformed."""
    toks = proof.split()
    if toks and toks[-1] == 'QED':
        toks = toks[:-1]
    lines, cur = [], []
    for t in toks:
        if t == ';':
            lines.append(cur); cur = []
        else:
            cur.append(t)
    if cur:
        return None
    out = []
    for l in lines:
        if ':' not in l:
            return None
        c = l.index(':')
        head, tail = l[:c], l[c + 1:]
        m = NTOK.match(head[0]) if head else None
        if not m or not tail:
            return None
        d = 0
        while 1 + d < len(head) and head[1 + d] == '|':
            d += 1
        refs = []
        for t in tail[1:]:
            mm = NTOK.match(t)
            if not mm:
                return None
            refs.append(int(mm.group(1)))
        out.append({'idx': int(m.group(1)), 'depth': d, 'formula': tuple(head[1 + d:]), 'rule': tail[0], 'refs': refs})
    return out


def render(lines):
    return ' ; '.join(' '.join([f"N{l['idx']}"] + ['|'] * l['depth'] + list(l['formula']) + [':', l['rule']] + [f'N{r}' for r in l['refs']])
                      for l in lines) + ' ; QED'


def normalise(proof):
    """Renumber so the first line is N1 (all line labels and references shifted by the same offset)."""
    ls = parse(proof)
    if not ls:
        return proof
    off = ls[0]['idx'] - 1
    for l in ls:
        l['idx'] -= off
        l['refs'] = [r - off for r in l['refs']]
    return render(ls)


def prune(lines):
    """Lines the conclusion transitively cites (a box citation Ns Ne keeps both s and e, whose own refs are followed),
    plus every PR line. Returned in order, NOT renumbered (predicates below do not need renumbering)."""
    by = {l['idx']: l for l in lines}
    keep, stack = set(), [lines[-1]['idx']]
    while stack:
        i = stack.pop()
        if i in keep or i not in by:
            continue
        keep.add(i)
        stack.extend(by[i]['refs'])
    return [l for l in lines if l['idx'] in keep or l['rule'] == 'PR']


def is_neg(f):
    return len(f) >= 4 and f[0] == '(' and f[1] == '~' and f[-1] == ')'


def strict_reductio(lines):
    """A NEGI line closing a box whose AS hypothesis is ( ~ G ), and a DN line citing that NEGI line (so it yields G)."""
    by = {l['idx']: l for l in lines}
    for l in lines:
        if l['rule'] != 'DN' or len(l['refs']) != 1:
            continue
        n = by.get(l['refs'][0])
        if not n or n['rule'] != 'NEGI' or len(n['refs']) != 2:
            continue
        a = by.get(n['refs'][0])
        if a and a['rule'] == 'AS' and is_neg(a['formula']) and tuple(a['formula'][2:-1]) == tuple(l['formula']):
            return True
    return False


def classify(proof):
    """-> dict(written, pruned, reductio (on pruned), reductio_written (on unpruned), max_depth, uses_dn) or None."""
    ls = parse(proof)
    if not ls:
        return None
    pr = prune(ls)
    return {'written': len(ls), 'pruned': len(pr), 'reductio': strict_reductio(pr), 'reductio_written': strict_reductio(ls),
            'max_depth': max(l['depth'] for l in pr), 'uses_dn': any(l['rule'] == 'DN' for l in pr)}


ATOMS = 'PQRS'
PERMS = [dict(zip(ATOMS, p)) for p in itertools.permutations(ATOMS)]


def canon(thm, sort_premises=False):
    """Renaming class of a sequent string 'prem , prem |- concl': minimum over the 24 atom bijections.
    sort_premises=True additionally identifies premise reorderings (stricter than the repository's notion)."""
    toks = thm.split()
    best = None
    for p in PERMS:
        s = [p.get(t, t) for t in toks]
        if sort_premises:
            k = s.index('|-')
            prem, depth, cur = [], 0, []
            for t in s[:k]:
                if t == ',' and depth == 0:
                    prem.append(' '.join(cur)); cur = []
                else:
                    depth += (t == '(') - (t == ')'); cur.append(t)
            if cur:
                prem.append(' '.join(cur))
            s2 = ' , '.join(sorted(prem)) + ' |- ' + ' '.join(s[k + 1:])
        else:
            s2 = ' '.join(s)
        if best is None or s2 < best:
            best = s2
    return best


def thm_of_prompt(prompt):
    body = prompt.strip()
    assert body.startswith('THM') and body.endswith('PRF')
    body = body[3:-3].strip()
    a, b = body.split('SEQ')
    return (a.strip() + ' |- ' + b.strip()).strip()
