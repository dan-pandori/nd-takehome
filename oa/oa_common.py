"""organism-analysis: shared definitions (step taxonomy, inputs).  Pure Python; no torch."""

CLASSES = ['box:imp', 'box:neg', 'box:orelim', 'box:bycontra', 'and_proj', 'app', 'or_intro', 'and_intro', 'prem', 'restate', 'false_elim', 'exact', 'other']


def step_class(action):
    """one state-env action (space-separated tokens, base-0 names) -> hard-step class (preregistration Q2).

    box:imp / box:neg / box:orelim: box openers (`( fun ( n : A ) => by`, `( fun ( n : ¬…`, `Or.elim n ( fun …`);
    and_proj: `n .1` / `n .2` (∧E); app: `n m` (→E, ¬E); or_intro: Or.inl / Or.inr; and_intro: ⟨ n , m ⟩; false_elim: `n .elim` (⊥E); restate: `n` alone;
    prem: `h<k>` restated; exact: closing a box / the proof; other: absurd, False.elim, a bare name, …
    Uses tj_score.step_kind's split for the box openers (the parse of the bound formula), re-implemented on text."""
    x = action.split()
    if x[0] == 'exact':
        return 'exact'
    j = x.index(':=')
    h = x[j + 1]
    if h == '(':
        # `( fun ( n : A ) => by`: ¬I iff the formula the box proves is a negation (tj_score: parse_ftoks(x, 3))
        f = x[3:j]
        if f[0] == '¬' or (f[0] == '(' and f[1] == '¬' and _closes_at_end(f + [')'])):
            return 'box:neg'
        return 'box:imp'
    if h == 'Or.elim':
        return 'box:orelim'
    if h == 'Classical.byContradiction':
        return 'box:bycontra'
    if h.startswith('h'):
        return 'prem'
    if h.startswith('n') and h[1:].isdigit():
        nx = x[j + 2] if len(x) > j + 2 else ';'
        if nx in ('.1', '.2'):
            return 'and_proj'
        if nx.startswith('n') and nx[1:].isdigit():
            return 'app'
        if nx == '.elim':
            return 'false_elim'
        if nx == ';':
            return 'restate'
        return 'other'
    if h in ('Or.inl', 'Or.inr'):
        return 'or_intro'
    if h == '⟨':
        return 'and_intro'
    return 'other'


def _closes_at_end(f):
    """f starts with '(' then '¬': True iff that '(' closes right before the binder's ')'."""
    d = 0
    for i, t in enumerate(f):
        d += (t == '(') - (t == ')')
        if d == 0:
            return f[i + 1:i + 2] == [')']
    return False


def nd_pruned_canon(proof):
    """ND proof text -> canonical pruned form: keep the lines the last line transitively cites (a box citation cites
    the AS line and the box's last line, which pull in what they cite), renumber them in order.  Two proofs that differ
    only by unused lines or numbering map to the same string.  A plain text parse (no checker); None if unparsable."""
    lines = [s.split() for s in proof.replace(' QED', '').split(' ; ') if s.strip() and s.strip() != 'QED']
    try:
        info = {}
        order = []
        for t in lines:
            lab = t[0]
            k = t.index(':', 1) if ':' in t[1:] else None
            # the rule's ':' is the last ':' token (formulas contain no ':')
            k = len(t) - 1 - t[::-1].index(':')
            refs = [x for x in t[k + 2:] if x.startswith('N')]
            info[lab] = (t[1:k], t[k + 1], refs)
            order.append(lab)
    except (ValueError, IndexError):
        return None
    keep, stack = set(), [order[-1]]
    while stack:
        i = stack.pop()
        if i in keep or i not in info:
            continue
        keep.add(i); stack.extend(info[i][2])
    ren = {lab: f'N{j + 1}' for j, lab in enumerate(l for l in order if l in keep)}
    return ' ; '.join(' '.join([ren[l]] + info[l][0] + [':', info[l][1]] + [ren.get(r, r) for r in info[l][2]])
                      for l in order if l in keep)
