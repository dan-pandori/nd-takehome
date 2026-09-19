"""Reviewer's own proof utilities for round3-run4b (written without reading patterns.py / prune.py / normalize.py).

parse(proof)        -> list of (idx, depth, formula_tokens, rule, refs)
normalise(proof)    -> text with the first line renumbered to N1 and every ref shifted (start-index normaliser)
pruned(lines)       -> the lines reachable from the last line through refs (dependency pruning)
max_depth_pruned    -> deepest '|' count among the kept lines (my depth counter)
is_depth3(proof)    -> max_depth_pruned >= 3 (my pattern predicate)
class_key(thm)      -> renaming class: lexicographically least text over the 24 atom permutations,
                       premises kept in order (key_ordered) or sorted (key_sorted)
"""
import itertools, re

RULES = {'ANDI', 'ANDE1', 'ANDE2', 'IMPE', 'IMPI', 'ORI1', 'ORI2', 'ORE', 'NEGE', 'NEGI', 'BOTE', 'DN', 'PR', 'AS', 'R'}
_N = re.compile(r'^N(\d+)$')


def parse(proof):
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
        raise ValueError('trailing tokens')
    out = []
    for ln in lines:
        m = _N.match(ln[0])
        if not m:
            raise ValueError('no index')
        idx = int(m.group(1))
        i = 1
        d = 0
        while ln[i] == '|':
            d += 1; i += 1
        c = ln.index(':')
        form = ln[i:c]
        rule = ln[c + 1]
        if rule not in RULES:
            raise ValueError('rule')
        refs = [int(_N.match(x).group(1)) for x in ln[c + 2:]]
        out.append((idx, d, form, rule, refs))
    return out


def render(lines):
    parts = []
    for idx, d, form, rule, refs in lines:
        parts.append(' '.join([f'N{idx}'] + ['|'] * d + form + [':', rule] + [f'N{r}' for r in refs] + [';']))
    return ' '.join(parts) + ' QED'


def normalise(proof):
    lines = parse(proof)
    off = lines[0][0] - 1
    return render([(idx - off, d, form, rule, [r - off for r in refs]) for idx, d, form, rule, refs in lines])


def pruned(lines):
    by = {l[0]: l for l in lines}
    keep, stack = set(), [lines[-1][0]]
    while stack:
        i = stack.pop()
        if i in keep or i not in by:
            continue
        keep.add(i)
        stack.extend(by[i][4])
    # premises are part of the statement, not of the dependency cone; they are depth 0 so irrelevant to depth
    return [l for l in lines if l[0] in keep]


def max_depth_pruned(proof):
    return max(l[1] for l in pruned(parse(proof)))


def max_depth_written(proof):
    return max(l[1] for l in parse(proof))


def is_depth3(proof):
    try:
        return max_depth_pruned(proof) >= 3
    except Exception:
        return False


def n_written(proof):
    return len(parse(proof))


def n_pruned(proof):
    ls = parse(proof)
    k = pruned(ls)
    prem = [l for l in ls if l[3] == 'PR' and l not in k]
    return len(k) + len(prem)   # premises are always counted (they must be written)


ATOMS = 'PQRS'


def _ren(text, perm):
    m = dict(zip(ATOMS, perm))
    return ' '.join(m.get(t, t) for t in text.split())


def split_thm(thm):
    prem, concl = thm.split('|-')
    prem = prem.strip()
    # split premises on top-level commas
    ps, depth, cur = [], 0, []
    for t in prem.split():
        if t == '(':
            depth += 1
        elif t == ')':
            depth -= 1
        if t == ',' and depth == 0:
            ps.append(' '.join(cur)); cur = []
        else:
            cur.append(t)
    if cur:
        ps.append(' '.join(cur))
    return ps, concl.strip()


def key_ordered(thm):
    ps, c = split_thm(thm)
    return min(_ren(' , '.join(ps) + ' |- ' + c, p) for p in itertools.permutations(ATOMS))


def key_sorted(thm):
    ps, c = split_thm(thm)
    best = None
    for p in itertools.permutations(ATOMS):
        s = ' , '.join(sorted(_ren(x, p) for x in ps)) + ' |- ' + _ren(c, p)
        if best is None or s < best:
            best = s
    return best


def prompt_to_thm(prompt):
    # "THM a , b SEQ c PRF" -> "a , b |- c"
    t = prompt.split()
    assert t[0] == 'THM' and t[-1] == 'PRF'
    i = t.index('SEQ')
    return ' '.join(t[1:i]) + ' |- ' + ' '.join(t[i + 1:-1])
