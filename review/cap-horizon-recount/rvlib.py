"""Reviewer's own primitives for cap-horizon. No import from the run's analysis code."""
import re, json, gzip, collections

TOKEN = re.compile(r'N(\d+)')
ATOMS = ['P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W']


# ---------- formulas ----------
def tokenize(s):
    return s.split()


def parse_formula(toks, i):
    """(node, next_i). node = ('atom',name) | ('bot',) | ('not',a) | (op,a,b)."""
    t = toks[i]
    if t == '(':
        # either ( ~ X ) or ( A op B )
        if toks[i + 1] == '~':
            a, j = parse_formula(toks, i + 2)
            assert toks[j] == ')', toks[j]
            return ('not', a), j + 1
        a, j = parse_formula(toks, i + 1)
        op = toks[j]
        assert op in ('&', 'v', '>'), op
        b, k = parse_formula(toks, j + 1)
        assert toks[k] == ')', toks[k]
        return (op, a, b), k + 1
    if t == 'F':
        return ('bot',), i + 1
    assert re.fullmatch(r'[A-EG-Z]', t), t
    return ('atom', t), i + 1


def fnodes(node):
    """number of nodes in a formula tree (atoms/F are 1)."""
    if node[0] in ('atom', 'bot'):
        return 1
    if node[0] == 'not':
        return 1 + fnodes(node[1])
    return 1 + fnodes(node[1]) + fnodes(node[2])


def atoms_in_order(toks):
    seen = []
    for t in toks:
        if re.fullmatch(r'[A-EG-Z]', t) and t not in seen:
            seen.append(t)
    return seen


def renaming_key(thm_or_prompt):
    """Canonical form of a sequent under atom renaming: atoms get P,Q,R,S,... in order of
    first appearance in the string.  Works on 'A , B |- C' and on 'THM ... SEQ ... PRF'."""
    s = thm_or_prompt
    if s.startswith('THM '):
        s = s[4:]
        if s.endswith(' PRF'):
            s = s[:-4]
        s = s.replace(' SEQ ', ' |- ')
    toks = tokenize(s)
    order = atoms_in_order(toks)
    m = {a: ATOMS[i] for i, a in enumerate(order)}
    return ' '.join(m.get(t, t) for t in toks)


# ---------- proofs ----------
LINE = re.compile(r'^N(\d+)\s+((?:\|\s*)*)(.+?)\s+:\s+([A-Z0-9]+)\s*(.*)$')


def parse_proof(body):
    """list of {idx, depth, formula_toks, rule, refs}.  Reviewer's own line splitter."""
    body = body.strip()
    if body.endswith('QED'):
        body = body[:-3].strip()
        if body.endswith(';'):
            body = body[:-1]
    out = []
    for chunk in body.split(';'):
        chunk = chunk.strip()
        if not chunk:
            continue
        m = LINE.match(chunk)
        if not m:
            return None
        idx = int(m.group(1))
        depth = m.group(2).count('|')
        ftoks = m.group(3).split()
        rule = m.group(4)
        refs = [int(x) for x in re.findall(r'N(\d+)', m.group(5))]
        out.append({'idx': idx, 'depth': depth, 'ftoks': ftoks, 'rule': rule, 'refs': refs})
    return out or None


def pruned_lines(body):
    """indices of the lines the final line transitively cites (reviewer's own closure)."""
    lines = parse_proof(body)
    if lines is None:
        return None
    by = {l['idx']: l for l in lines}
    keep, stack = set(), [lines[-1]['idx']]
    while stack:
        i = stack.pop()
        if i in keep or i not in by:
            continue
        keep.add(i)
        stack.extend(by[i]['refs'])
    return keep


def pruned_length(body):
    k = pruned_lines(body)
    if k is None:
        return len([c for c in body.split(';') if c.strip() and c.strip() != 'QED'])
    return len(k)


def written_length(body):
    lines = parse_proof(body)
    if lines is None:
        return len([c for c in body.split(';') if c.strip() and c.strip() != 'QED'])
    return len(lines)


def term_size(body):
    """formula nodes summed over the pruned lines."""
    lines = parse_proof(body)
    if lines is None:
        return None
    keep = pruned_lines(body)
    tot = 0
    for l in lines:
        if l['idx'] in keep:
            node, j = parse_formula(l['ftoks'], 0)
            assert j == len(l['ftoks']), l['ftoks']
            tot += fnodes(node)
    return tot


def max_box_depth(body):
    lines = parse_proof(body)
    if lines is None:
        return None
    return max(l['depth'] for l in lines)


def pruned_box_depth(body):
    lines = parse_proof(body)
    if lines is None:
        return None
    keep = pruned_lines(body)
    return max(l['depth'] for l in lines if l['idx'] in keep)


def norm_start(body):
    """renumber the line indices from N1 (start-index normalisation)."""
    base = None
    out = []
    for t in body.split():
        m = re.fullmatch(r'N(\d+)', t)
        if m:
            n = int(m.group(1))
            if base is None:
                base = n
            out.append('N%d' % (n - base + 1))
        else:
            out.append(t)
    return ' '.join(out)


def rd(fn):
    op = gzip.open if fn.endswith('.gz') else open
    with op(fn, 'rt') as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)
