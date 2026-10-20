#!/usr/bin/env python3
"""E2 / E3 / G1(b) / generalisation-greedy recount from the stored free-generation rows (artifacts/kalmar/free/*.rows.jsonl.gz).

Own definitions:
  success      the row is Lean-accepted (stored `valid`; the literal texts are re-checked in Lean by recheck.py)
  exact-follow the accepted text equals the algorithm's canonical text with every name shifted by the attempt's base
               (the environment's names); an exact follower is necessarily accepted, so this needs no invalid texts
  actions      'have' + 'exact' tokens of the text (= the state-env actions)
  deviation    first action whose tokens differ from the algorithm's (accepted deviating attempts only; for rejected
               attempts no text is stored, so the stored dev_* fields can only be checked for consistency with my tags)
Cut-offs: rows whose end is 'truncated' (action > max_action) or 'step_cap' (>= max_steps), per set and atom count.

  python3 review_kal/free.py -> out/free.json, stdout
"""
import collections, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kc
sys.path.insert(0, kc.ROOT)
from state_env import decompose

F = os.path.join(kc.ROOT, 'artifacts', 'kalmar', 'free')
NAME = re.compile(r'^n(\d+)$')


def shift(toks, b):
    return [f'n{int(m.group(1)) + b}' if (m := NAME.match(t)) else t for t in toks]


ALG = {}


def algo(path):
    """per input file: list of dicts (name, atoms, acts (tag, depth), canon tokens)"""
    if path not in ALG:
        out = []
        for r in kc.rows(os.path.join(kc.ROOT, path)):
            m = kc.kalmar(r['prompt'])
            assert m['proof'] == r['proof'], path
            steps, toks, env = decompose(r['prompt'], r['proof'], canon=True)
            assert len(steps) == len(m['acts'])
            out.append({'name': r.get('name'), 'atoms': m['n_atoms'], 'acts': m['acts'], 'toks': toks,
                        'n_prem': len(kc.split_prompt(r['prompt'])[0])})
        ALG[path] = out
    return ALG[path]


PROJ = re.compile(r'^(n\d+|h\d+)(\.\w+)$')


def ttoks(text):
    """literal text -> lean_seq tokens: the text joins a projection / eliminator to its name (`n36.elim`, `n4.1`)"""
    out = []
    for t in text.split():
        m = PROJ.match(t)
        out += [m.group(1), m.group(2)] if m else [t]
    return out


def n_actions(toks):
    return sum(1 for t in toks if t in ('have', 'exact'))


def first_dev(atoks, gtoks):
    p = next((i for i, (x, y) in enumerate(zip(atoks, gtoks)) if x != y), min(len(atoks), len(gtoks)))
    starts = sum(1 for t in gtoks[:p + 1] if t in ('have', 'exact'))
    return starts - 1


res = {}
for fn in sorted(os.listdir(F)):
    if not fn.endswith('.rows.jsonl.gz'):
        continue
    tag = fn.replace('.rows.jsonl.gz', '')
    summ = json.load(open(os.path.join(F, tag + '.json')))
    al = algo(summ['in'])
    c = collections.defaultdict(collections.Counter)
    chk = collections.Counter()
    per_thm = collections.defaultdict(list)
    devtags = collections.Counter(); devtags_valid = collections.Counter()
    for row in kc.rows(os.path.join(F, fn)):
        g = al[row['i']]
        assert row['name'] == g['name']
        gt = shift(g['toks'], row['base'])
        valid = bool(row['valid'])
        txt = row.get('text')
        if valid:
            at = ttoks(txt)
            follow = at == gt
            na = n_actions(at)
            chk['valid_rows'] += 1
            chk['nact_match'] += na == row['n_actions']
        else:
            follow = False; na = row['n_actions']
            if txt is not None:
                chk['text_on_invalid'] += 1
        chk['follow_match'] += follow == bool(row['follow'])
        chk['rows'] += 1
        if 'dev_step' in row:
            ds = row['dev_step']
            if ds < len(g['acts']):
                chk['devtag_n'] += 1
                chk['devtag_match'] += g['acts'][ds][0] == row['dev_tag'] and g['acts'][ds][1] == row['dev_depth']
        if valid and not follow:
            d = first_dev(ttoks(txt), gt)
            chk['devstep_valid_n'] += 1
            chk['devstep_valid_match'] += d == row.get('dev_step')
            if d < len(g['acts']):
                devtags_valid[g['acts'][d][0]] += 1
        if 'dev_tag' in row:
            devtags[row['dev_tag']] += 1
        for key in ('all', f'atoms={g["atoms"]}', f'prem={g["n_prem"]}'):
            x = c[key]
            x['n'] += 1; x['valid'] += valid; x['follow'] += follow
            x['dev_valid'] += valid and not follow
            x['dev_valid_shorter'] += valid and not follow and na < len(g['acts'])
            x['dev_valid_longer'] += valid and not follow and na > len(g['acts'])
            x['end=' + row['end']] += 1
        per_thm[row['i']].append(valid)
    k = summ['k']
    pk = {}
    for kk in (1, 8, 32):
        if kk <= k:
            pk[f'pass@{kk}'] = sum(kc.unbiased_pass(len(v), sum(v), kk) for v in per_thm.values())
    res[tag] = {'in': summ['in'], 'k': k, 'T': summ['temperature'], 'batch': summ['batch'], 'supply_pr': summ['supply_pr'],
                'max_steps': summ['max_steps'], 'n_theorems': len(per_thm), 'solved': sum(any(v) for v in per_thm.values()),
                'stored_solved': summ['solved_theorems'], 'pass': pk, 'by': {kk: dict(v) for kk, v in sorted(c.items())},
                'checks': dict(chk), 'dev_tags_stored': dict(devtags.most_common()), 'dev_tags_valid_mine': dict(devtags_valid.most_common())}
    a = c['all']
    print(f"{tag:42s} n {a['n']:5d} solved {res[tag]['solved']:4d}/{len(per_thm)} (stored {summ['solved_theorems']}) "
          f"valid {a['valid'] / a['n']:.4f} follow {a['follow'] / a['n']:.4f} devvalid {a['dev_valid']} shorter {a['dev_valid_shorter']} "
          f"trunc {a['end=truncated']} cap {a['end=step_cap']} | follow_match {chk['follow_match']}/{chk['rows']} "
          f"nact {chk['nact_match']}/{chk['valid_rows']} devtag {chk['devtag_match']}/{chk['devtag_n']} "
          f"devstep {chk['devstep_valid_match']}/{chk['devstep_valid_n']}", flush=True)
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'free.json'), 'w'), indent=1)
