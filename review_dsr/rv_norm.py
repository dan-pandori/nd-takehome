"""Reviewer's own normalisers for ds-rendering. Written independently of the run's code."""
import re, json

VARS = re.compile(r'\b[A-Z][A-Za-z0-9_]*\b')
# tokens that are not propositional variables in the ND surface syntax
NONVAR = {'F'}          # falsum (a sequent string contains no rule names, so nothing else is excluded)
RULES = {'PR','AS','QED','IMPI','IMPE','ANDI','ANDE1','ANDE2','ORI1','ORI2','ORE',
         'NEGI','NEGE','DN','BOTE','R','SEQ','THM','PRF'}


def renaming_key(thm: str) -> str:
    """Canonical representative of the renaming class of a sequent string.

    Propositional variables are replaced by v0, v1, ... in order of first
    appearance, reading the sequent left to right.  Falsum F is left alone.
    """
    out, seen = [], {}
    pos = 0
    for m in VARS.finditer(thm):
        tok = m.group(0)
        if tok in NONVAR:          # falsum only; a theorem string contains no rule names
            continue
        out.append(thm[pos:m.start()])
        if tok not in seen:
            seen[tok] = 'v%d' % len(seen)
        out.append(seen[tok])
        pos = m.end()
    out.append(thm[pos:])
    return ''.join(out)


LINE = re.compile(r'^N(\d+)\s+(.*)$')
REF = re.compile(r'\bN(\d+)\b')


def norm_proof(proof: str) -> str:
    """Start-index normalisation: renumber the proof's line labels to N1, N2, ...
    in order of appearance and rewrite every citation accordingly."""
    parts = [p.strip() for p in proof.split(';')]
    mapping, k = {}, 0
    for p in parts:
        m = LINE.match(p)
        if m:
            k += 1
            mapping[m.group(1)] = 'N%d' % k
    def sub(p):
        return REF.sub(lambda m: mapping.get(m.group(1), m.group(0)), p)
    return ' ; '.join(sub(p) for p in parts)


def nd_lines(proof: str):
    """The ND lines of a proof (excluding QED)."""
    return [p.strip() for p in proof.split(';') if LINE.match(p.strip())]


def nd_len(proof: str) -> int:
    return len(nd_lines(proof))


def box_depth(proof: str) -> int:
    """Maximum nesting depth of AS boxes, counted from the '|' gutter marks."""
    d = 0
    for ln in nd_lines(proof):
        body = LINE.match(ln).group(2)
        bars = 0
        for ch in body:
            if ch == '|':
                bars += 1
            elif ch != ' ':
                break
        d = max(d, bars)
    return d


def term_size(text: str) -> int:
    """Size of a Lean text in whitespace-separated tokens."""
    return len(text.split())
