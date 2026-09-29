"""Reviewer's own proof tooling for run ds-composition.

Written from scratch for review_ds-composition.md (phase 1).  Deliberately does
NOT import patterns.py, coverage.py, dsc_analysis.py or any of the executor's
analysis code.  nd_verify is used only where the protocol demands it (it is the
take-home's verifier and must stay unmodified).

Proof token format (one line):
    N<i> ['|']*depth <formula tokens> : <RULE> [N<r> ...] ;
terminated by QED.
"""
import json, gzip, re, collections

RULES = {'ANDI', 'ANDE1', 'ANDE2', 'IMPE', 'IMPI', 'ORI1', 'ORI2', 'ORE',
         'NEGE', 'NEGI', 'BOTE', 'DN', 'PR', 'AS', 'R'}
NREF = re.compile(r'^N(\d+)$')


class Bad(Exception):
    pass


def parse(proof):
    """-> list of line dicts {idx, depth, f (formula token string), rule, refs}.

    Raises Bad on anything that does not fit the grammar.  My own scanner: the
    formula is kept as its whitespace-normalised token string, which is a
    faithful identity for these fully-parenthesised formulas and is all the
    predicates below need.
    """
    t = proof.split()
    i, out = 0, []
    while i < len(t):
        if t[i] == 'QED':
            if not out:
                raise Bad('empty')
            return out
        m = NREF.match(t[i])
        if not m:
            raise Bad('index')
        idx = int(m.group(1)); i += 1
        d = 0
        while i < len(t) and t[i] == '|':
            d += 1; i += 1
        j = i
        while j < len(t) and t[j] != ':':
            j += 1
        if j >= len(t) or j == i:
            raise Bad('colon')
        f = ' '.join(t[i:j])
        i = j + 1
        if i >= len(t) or t[i] not in RULES:
            raise Bad('rule')
        rule = t[i]; i += 1
        refs = []
        while i < len(t) and NREF.match(t[i]):
            refs.append(int(NREF.match(t[i]).group(1))); i += 1
        if i >= len(t) or t[i] != ';':
            raise Bad('semi')
        i += 1
        out.append({'idx': idx, 'depth': d, 'f': f, 'rule': rule, 'refs': refs})
    raise Bad('no QED')


def try_parse(proof):
    try:
        return parse(proof)
    except Bad:
        return None


# ---------- start-index normalisation -------------------------------------
def render(lines):
    """Renumber from N1 by position and re-map every citation; canonical text."""
    pos = {ln['idx']: k + 1 for k, ln in enumerate(lines)}
    out = []
    for ln in lines:
        out.append('N%d' % pos[ln['idx']])
        out += ['|'] * ln['depth']
        out.append(ln['f']); out.append(':'); out.append(ln['rule'])
        out += ['N%d' % pos[r] for r in ln['refs'] if r in pos]
        out.append(';')
    out.append('QED')
    return ' '.join(out)


def norm(proof):
    """Start-index-normalised canonical form of a written proof, or None."""
    ln = try_parse(proof)
    return None if ln is None else render(ln)


# ---------- dependency pruning --------------------------------------------
def prune(lines):
    by = {ln['idx']: ln for ln in lines}
    keep = {ln['idx'] for ln in lines if ln['rule'] == 'PR'}
    st = [lines[-1]['idx']]
    while st:
        k = st.pop()
        if k in keep or k not in by:
            continue
        keep.add(k)
        st.extend(by[k]['refs'])
    return [ln for ln in lines if ln['idx'] in keep]


# ---------- predicates (my own) -------------------------------------------
def max_depth(lines):
    return max((ln['depth'] for ln in lines), default=0)


def is_depth3(lines):
    return max_depth(lines) >= 3


def is_derived_ore(lines):
    by = {ln['idx']: ln for ln in lines}
    for ln in lines:
        if ln['rule'] == 'ORE' and ln['refs']:
            src = by.get(ln['refs'][0])
            if src is None or src['rule'] != 'PR':
                return True
    return False


def is_derived_ore_strict(lines):
    by = {ln['idx']: ln for ln in lines}
    for ln in lines:
        if ln['rule'] != 'ORE' or not ln['refs']:
            continue
        s = by.get(ln['refs'][0])
        if s is None or s['rule'] in ('PR', 'AS'):
            continue
        d = split_or(s['f'])
        if d and d[0] != d[1]:
            return True
    return False


def is_reductio(lines):
    """DN of a NEGI that closed a box assuming ( ~ G ), concluding G."""
    by = {ln['idx']: ln for ln in lines}
    for ln in lines:
        if ln['rule'] != 'DN' or not ln['refs']:
            continue
        neg = by.get(ln['refs'][0])
        if neg is None or neg['rule'] != 'NEGI' or len(neg['refs']) != 2:
            continue
        hyp = by.get(neg['refs'][0])
        if hyp is not None and hyp['rule'] == 'AS' and hyp['f'] == '( ~ %s )' % ln['f']:
            return True
    return False


def is_derived_dn(lines):
    by = {ln['idx']: ln for ln in lines}
    for ln in lines:
        if ln['rule'] == 'DN' and ln['refs']:
            s = by.get(ln['refs'][0])
            if s is not None and s['rule'] not in ('PR', 'AS'):
                return True
    return False


def split_or(fs):
    """'( A v B )' -> (A, B) at the top level, else None.  Own paren scanner."""
    t = fs.split()
    if len(t) < 3 or t[0] != '(' or t[-1] != ')':
        return None
    d, i = 0, 1
    while i < len(t) - 1:
        if t[i] == '(':
            d += 1
        elif t[i] == ')':
            d -= 1
        elif d == 0 and t[i] in ('&', 'v', '>'):
            return (' '.join(t[1:i]), ' '.join(t[i + 1:-1])) if t[i] == 'v' else None
        i += 1
    return None


# ---------- sizes ----------------------------------------------------------
ATOMS = {'P', 'Q', 'R', 'S', 'F'}


def fsize(fs):
    """Node count of a formula: atoms + connectives (parens/whitespace ignored)."""
    return sum(1 for x in fs.split() if x in ATOMS or x in ('~', '&', 'v', '>'))


def term_size(lines):
    """Total formula node count over the proof's lines (the 'term size')."""
    return sum(fsize(ln['f']) for ln in lines)


def token_len(proof):
    return len(proof.split())


def classify(proof, pruned=True):
    ln = try_parse(proof)
    if ln is None:
        return None
    w = len(ln)
    p = prune(ln)
    q = p if pruned else ln
    return {'written_len': w, 'pruned_len': len(p), 'max_depth': max_depth(q),
            'depth3': is_depth3(q), 'derived_ore': is_derived_ore(q),
            'derived_ore_strict': is_derived_ore_strict(q),
            'reductio': is_reductio(q), 'derived_dn': is_derived_dn(q),
            'rules': sorted({x['rule'] for x in q}),
            'term_size': term_size(q), 'term_size_written': term_size(ln)}


# ---------- renaming-class key (my own) -----------------------------------
def prompt_parts(prompt):
    """'THM <prem> , <prem> SEQ <concl> PRF' -> ([prem...], concl)."""
    t = prompt.split()
    assert t[0] == 'THM' and t[-1] == 'PRF', prompt
    t = t[1:-1]
    k = t.index('SEQ')
    pre, concl = t[:k], ' '.join(t[k + 1:])
    prems, cur, d = [], [], 0
    for x in pre:
        if x == '(':
            d += 1
        elif x == ')':
            d -= 1
        if x == ',' and d == 0:
            prems.append(' '.join(cur)); cur = []
        else:
            cur.append(x)
    if cur:
        prems.append(' '.join(cur))
    return prems, concl


def rkey(prompt):
    """Renaming class of a theorem: atoms renamed in order of first appearance
    over premises-then-conclusion, premise order preserved."""
    prems, concl = prompt_parts(prompt)
    seq = ' , '.join(prems) + ' |- ' + concl
    m, nxt = {}, 0
    out = []
    for x in seq.split():
        if x in ('P', 'Q', 'R', 'S'):
            if x not in m:
                m[x] = 'A%d' % nxt; nxt += 1
            out.append(m[x])
        else:
            out.append(x)
    return ' '.join(out)


def rkey_thm(thm):
    """Same, from a 'prem , prem |- concl' string."""
    m, nxt = {}, 0
    out = []
    for x in thm.split():
        if x in ('P', 'Q', 'R', 'S'):
            if x not in m:
                m[x] = 'A%d' % nxt; nxt += 1
            out.append(m[x])
        else:
            out.append(x)
    return ' '.join(out)


def load(path):
    op = gzip.open if path.endswith('.gz') else open
    with op(path, 'rt') as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)
