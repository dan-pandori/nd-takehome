#!/usr/bin/env python3
"""Reviewer (coe-dose01): classical-reductio subtypes of accepted TARGET proofs, own ND parser and predicate.

Definition (the pre-registration's 'free positive reductio', = create-or-elicit's sigma_subtype 'pos_free*', re-implemented):
  take the FIRST DN line (in line order) whose cited line, after following reiteration (R) lines back, was derived by a
  rule (not PR, not AS).  G = that DN line's formula.
    pos / neg   : G is not / is a negation
    free / scaff: neither ( ~ ( ~ G ) ) nor ( ( ~ G ) > F ) occurs in the theorem's prompt / it does
    route       : the cited origin is NEGI ('' ), IMPI ('_impi') or any other rule ('_other')
  Proofs with no such DN line get no subtype.
Streams <bucket>/<ladder>/found_<R>.jsonl (cumulative, each row carries its first-found round) and counts rows by round.

  python3 reductio.py la_dose01_s0 4 1          -> rounds {1}
  python3 reductio.py la_ko_s1 32 25-32
"""
import collections, gzip, json, re, subprocess, sys
sys.path.insert(0, '/home/dan/work/coe-dose01/review_cd01')
from common import BIG

BK = 'hf://buckets/dan-pandori/nd-rl/coe-dose01/artifacts/coe/ladder'
LINE = re.compile(r'^N(\d+)\s+((?:\|\s+)*)(.*)\s:\s([A-Z0-9]+)((?:\s+N\d+)*)\s*$')


def parse_nd(nd):
    """-> list of dicts idx, depth, formula (string), rule, refs; None if unparsable"""
    out = []
    for part in nd.split(' ; '):
        part = part.strip()
        if part == 'QED' or not part:
            continue
        m = LINE.match(part)
        if not m:
            return None
        out.append(dict(idx=int(m.group(1)), depth=m.group(2).count('|'), formula=m.group(3).strip(), rule=m.group(4),
                        refs=[int(x[1:]) for x in m.group(5).split()]))
    return out


def origin(by, i):
    seen = set()
    while i in by and by[i]['rule'] == 'R' and by[i]['refs'] and i not in seen:
        seen.add(i)
        i = by[i]['refs'][0]
    return by.get(i)


def subtype(nd, prompt):
    lines = parse_nd(nd)
    if lines is None:
        return 'UNPARSED'
    by = {l['idx']: l for l in lines}
    for l in lines:
        if l['rule'] != 'DN' or not l['refs']:
            continue
        o = origin(by, l['refs'][0])
        if o is None or o['rule'] in ('PR', 'AS'):
            continue
        G = l['formula']
        route = '' if o['rule'] == 'NEGI' else '_impi' if o['rule'] == 'IMPI' else '_other'
        free = f'( ~ ( ~ {G} ) )' not in prompt and f'( ( ~ {G} ) > F )' not in prompt
        return ('neg_' if G.startswith('( ~ ') else 'pos_') + ('free' if free else 'scaffold') + route
    return None


def main(lad, last, rspec):
    a, _, b = rspec.partition('-')
    rounds = set(range(int(a), int(b or a) + 1))
    url = f'{BK}/{lad}/found_{last}.jsonl'
    p = subprocess.Popen(['hf', 'buckets', 'cp', url, '-'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1 << 20)
    cnt = collections.defaultdict(collections.Counter)
    nrows = collections.Counter()
    keep = gzip.open(f'{BIG}/ft/{lad}_posfree_r{rspec}.jsonl.gz', 'wt')
    names_pf = collections.defaultdict(set)
    for line in p.stdout:
        # cheap pre-filter on the round before json parsing
        m = re.search(r'"round": (\d+)', line)
        r = int(m.group(1)) if m else None
        if r not in rounds:
            continue
        x = json.loads(line)
        r = x['round']
        nrows[r] += 1
        if ': DN ' not in x['proof']:
            cnt[r]['no DN line'] += 1
            continue
        st = subtype(x['proof'], x['prompt'])
        cnt[r][st or 'DN only on PR/AS'] += 1
        if st and st.startswith('pos_free'):
            names_pf[r].add(x['name'])
            keep.write(json.dumps({k: x[k] for k in ('name', 'prompt', 'proof', 'round')}) + '\n')
    keep.close()
    rc = p.wait()
    out = {'ladder': lad, 'file': url, 'rc': rc, 'rows_by_round': dict(sorted(nrows.items())),
           'subtypes_by_round': {r: dict(v) for r, v in sorted(cnt.items())},
           'pos_free_by_round': {r: sum(v for k, v in cnt[r].items() if k.startswith('pos_free')) for r in sorted(cnt)},
           'pos_free_targets_by_round': {r: len(names_pf[r]) for r in sorted(cnt)}}
    json.dump(out, open(f'/home/dan/work/coe-dose01/review_cd01/out/reductio_{lad}_r{rspec}.json', 'w'), indent=1)
    print(f"{lad} rounds {rspec}: rows {dict(sorted(nrows.items()))}; pos_free* proofs {out['pos_free_by_round']} "
          f"(targets {out['pos_free_targets_by_round']}); rc {rc}")


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3])
