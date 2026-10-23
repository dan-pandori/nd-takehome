"""Theorem sampling and the stream / test split by renaming class (run `style-edl`).

Renaming class = kalmar-pretrain's premise-order-invariant key (`kalmar/make_sets.pkey`: min over the 24 atom
bijections of (sorted premises, goal)).  The split keeps every class on one side and balances the atom-count strata.
"""
import collections, os, random, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'kalmar'))
from nd2lean import parse_prompt


def pkey_of(prompt):
    from make_sets import pkey
    p, g = parse_prompt(prompt)
    return pkey(p, g)


def text_toks(text, stoi):
    """literal lean_seq text (tok.text: '.1' / '.2' / '.elim' glued to the previous token) -> token strings."""
    def split_word(w):
        if w in stoi:
            return [w]
        for suf in ('.elim', '.1', '.2'):
            if w.endswith(suf) and len(w) > len(suf):
                head = split_word(w[:-len(suf)])
                if head is not None:
                    return head + [suf]
        return None
    out = []
    for w in text.split():
        t = split_word(w)
        if t is None:
            raise ValueError(f'untokenisable word {w!r}')
        out += t
    return out


def sample_and_split(recs, n_total, seed):
    """recs: eligible records (name, prompt, n_atoms).  -> (stream records, test records), n_total // 2 each, every
    renaming class on one side, atom strata balanced; both lists in a seeded random order."""
    rng = random.Random(seed)
    pool = sorted(recs, key=lambda r: r['name'])
    rng.shuffle(pool)
    chosen = pool[:n_total]
    by_cls = collections.OrderedDict()
    for r in chosen:
        by_cls.setdefault(pkey_of(r['prompt']), []).append(r)
    strata = collections.defaultdict(list)            # atom count -> classes
    for k, rs in by_cls.items():
        strata[rs[0]['n_atoms']].append(rs)
    half = n_total // 2
    side = [[], []]
    for na in sorted(strata):
        cls = strata[na]
        rng.shuffle(cls)
        cls.sort(key=lambda rs: -len(rs))              # big classes first, then greedy balance within the stratum
        cnt = [0, 0]
        for rs in cls:
            s = 0 if (cnt[0] < cnt[1] or (cnt[0] == cnt[1] and len(side[0]) <= len(side[1]))) else 1
            side[s] += rs; cnt[s] += len(rs)
    # exact halves: move whole singleton classes from the larger side if needed (largest stratum first)
    while len(side[0]) != len(side[1]):
        big, small = (0, 1) if len(side[0]) > len(side[1]) else (1, 0)
        keys = collections.Counter(pkey_of(r['prompt']) for r in side[big])
        cand = [r for r in side[big] if keys[pkey_of(r['prompt'])] == 1]
        if not cand or abs(len(side[0]) - len(side[1])) < 2:
            break
        r = cand[rng.randrange(len(cand))]
        side[big].remove(r); side[small].append(r)
    for s in side:
        rng.shuffle(s)
    assert not ({pkey_of(r['prompt']) for r in side[0]} & {pkey_of(r['prompt']) for r in side[1]})
    return side[0][:half], side[1][:half]
