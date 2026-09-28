"""Reviewer's own ND-proof utilities (run4-grpo-review). Independent of patterns.py / normalize.py / prune.py."""
import re, json, glob, os
LAB = re.compile(r'^N(\d+)$')

def parse(proof):
    """-> list of (label, bars, formula, rule, refs); raises ValueError on malformed text."""
    body = proof.strip()
    if body.endswith('QED'):
        body = body[:-3]
    out = []
    for seg in body.split(';'):
        t = seg.split()
        if not t:
            continue
        if not LAB.match(t[0]) or ':' not in t:
            raise ValueError('bad line: ' + seg)
        c = t.index(':')
        bars = 0
        while 1 + bars < c and t[1 + bars] == '|':
            bars += 1
        formula = ' '.join(t[1 + bars:c])
        rule = t[c + 1] if c + 1 < len(t) else ''
        refs = [x for x in t[c + 2:] if LAB.match(x)]
        out.append((t[0], bars, formula, rule, refs))
    if not out:
        raise ValueError('empty')
    return out

def normalise(proof):
    """renumber labels N1..Nk in order of definition (start-index normalisation)."""
    lines = parse(proof)
    m = {l[0]: 'N%d' % (i + 1) for i, l in enumerate(lines)}
    segs = []
    for lab, bars, f, rule, refs in lines:
        segs.append(' '.join([m[lab]] + ['|'] * bars + [f, ':', rule] + [m.get(r, r) for r in refs]))
    return ' ; '.join(segs) + ' ; QED'

def pruned(lines):
    """indices of lines the last line depends on (transitively through references)."""
    idx = {l[0]: i for i, l in enumerate(lines)}
    keep, stack = set(), [len(lines) - 1]
    while stack:
        i = stack.pop()
        if i in keep:
            continue
        keep.add(i)
        for r in lines[i][4]:
            if r in idx:
                stack.append(idx[r])
    return sorted(keep)

def depth(proof, prune=True):
    lines = parse(proof)
    ks = pruned(lines) if prune else range(len(lines))
    return max(lines[i][1] for i in ks)

def is_d3(proof):
    return depth(proof) >= 3

def load_found(arm_dir):
    """all found_<r>.jsonl records of an arm -> {(name, normalised proof): min round}."""
    best = {}
    for f in sorted(glob.glob(os.path.join(arm_dir, 'found_[0-9]*.jsonl'))):
        for l in open(f):
            d = json.loads(l)
            k = (d['name'], normalise(d['proof']))
            r = int(d['round'])
            if k not in best or r < best[k]:
                best[k] = r
    return best
