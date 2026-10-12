#!/usr/bin/env python3
"""create-or-elicit: summarise reads (state_eval plain reads: <tag>.json + <tag>.jsonl.gz; guided_eval reads: <tag>.json +
<tag>.rows.jsonl.gz) on data/coe/read1054.jsonl (tb72 + h250 + 732 tracked transfer) or data/coe/fam_extra.jsonl.

Per read: solved per set (textbook72 dev58 / train14 / combined, holdout250, tracked); held-out key-step members solved
per classical family and the 55 generated sigma-covered held-out theorems (of 178 sigma-covered held-out in all); families
acquired (>= 50 % of held-out key-step members solved); proof classes of the accepted proofs of sigma-covered members
(sigma / sigma+ only / lemma route / DN on premise or hypothesis / no DN); share of attempts cut by the action or step cap.
Lean-text proofs (guided reads) are mapped back to ND by lean_tok.inverse(text.split()) (the text is the space-joined
lean_seq tokens) and classified like the ND proofs of plain reads (coe_rounds.classify).

  python3 coe/coe_reads.py --tags pend_ko_s0_x0 r16_ko_s0_x0 ... [--dir artifacts/coe/eval] --out artifacts/coe/reads_summary.json
"""
import argparse, collections, glob, gzip, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from coe.coe_rounds import classify as classify_nd
from lean_tok import inverse

DN_RE = re.compile(r'Classical\.byContradiction \(fun hh => (n\d+) hh\)')
HAVE_RE = re.compile(r'have (n\d+) : (.*?) := (.*)$')


def classify_lean(text):
    """Lean text of one proof (one line or many) -> proof class (see module doc)."""
    lines = re.split(r'\n|;', text)
    defs = {}
    binders = set(re.findall(r'fun \((n\d+) :', text))
    for ln in lines:
        m = HAVE_RE.search(ln.strip())
        if m:
            defs[m.group(1)] = m.group(3).strip()
    cited = DN_RE.findall(text)
    if not cited:
        return 'no_dn'
    cls = 'dn_pr_as'
    for n in cited:
        if n in binders and n not in defs:
            continue
        d = defs.get(n)
        if d is None:
            continue
        if re.match(r'^\(?h\d+\)?$', d):
            continue
        if d.startswith('(fun ') or d.startswith('fun '):
            return 'sigma'
        cls = 'sigma_plus_only'
    return cls


def load_rows(base):
    for fn, kind in ((base + '.jsonl.gz', 'plain'), (base + '.jsonl', 'plain'), (base + '.rows.jsonl.gz', 'guided')):
        if os.path.exists(fn):
            op = gzip.open(fn, 'rt') if fn.endswith('.gz') else open(fn)
            return [json.loads(l) for l in op if l.strip()], kind
    return None, None


def summarise(base, fam, read_sets):
    rows, kind = load_rows(base)
    if rows is None:
        return None
    sig_ho = {f: set(d['strict_heldout']) for f, d in fam['families'].items() if d['classical']}   # Addendum 2: strict
    sig_ho['generated'] = set(fam['generated_classical']['transfer']['strict'])
    all_sig = set().union(*sig_ho.values())
    solved = {}
    cut = att = 0
    cls = collections.Counter()
    for r in rows:
        name = r['name']
        if kind == 'plain':
            s = bool(r['solved'])
            att += r['n_tried']
            cut += sum(1 for x in r['reasons'] if 'action truncated' in x or 'step cap' in x)
            if s and name in all_sig:
                for p in r['proofs']:
                    cls[classify_nd(p)] += 1
        else:
            s = r['n_ok'] > 0
            att += len(r['status'])
            cut += sum(1 for x in r['status'] if x and ('trunc' in x or 'cap' in x))
            if s and name in all_sig:
                for t in r['accepted']:
                    try:
                        cls[classify_nd(inverse(t.split()))] += 1
                    except Exception:
                        cls['lean_text_unparsed'] += 1
        solved[name] = s
    out = {'kind': kind, 'n': len(rows), 'solved_total': sum(solved.values()), 'cut_share': cut / max(1, att), 'attempts': att}
    for st, names in read_sets.items():
        present = [n for n in names if n in solved]
        if present:
            out[f'solved_{st}'] = sum(solved[n] for n in present); out[f'n_{st}'] = len(present)
    fams = {}
    for f, m in sig_ho.items():
        present = [n for n in m if n in solved]
        fams[f] = {'solved': sum(solved[n] for n in present), 'n': len(present)}
    out['families_heldout'] = fams
    out['sigma_covered_solved'] = sum(v['solved'] for v in fams.values())
    out['sigma_covered_n'] = sum(v['n'] for v in fams.values())
    out['families_acquired'] = sorted(f for f, v in fams.items() if f != 'generated' and v['n'] and v['solved'] / v['n'] >= 0.5)
    out['proof_classes_sigma_covered'] = dict(cls)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tags', nargs='+', required=True)
    ap.add_argument('--dir', default='artifacts/coe/eval')
    ap.add_argument('--families', default='data/coe/families.json')
    ap.add_argument('--readset', default='data/coe/read1054.jsonl')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    fam = json.load(open(a.families))
    rs = [json.loads(l) for l in open(a.readset)]
    tb = {json.loads(l)['name']: json.loads(l) for l in open('data/bs/textbook72.jsonl')}
    dev58 = {n for n, r in tb.items() if n.startswith('textbook_') and r.get('source', {}) != 'rl_train'} if False else None
    sets = collections.defaultdict(list)
    for r in rs:
        sets[r['set']].append(r['name'])
    # textbook72 dev58 / train14 split from the canonical files
    sets['tb72_dev58'] = [json.loads(l).get('name') for l in open('data/eval_only/textbook72/textbook_dev.jsonl')]
    sets['tb72_train14'] = [json.loads(l).get('name') for l in open('data/eval_only/textbook72/textbook_train.jsonl')]
    res = {}
    for t in a.tags:
        s = summarise(os.path.join(a.dir, t), fam, sets)
        if s is None:
            print(f'{t}: missing'); continue
        res[t] = s
        f = s['families_heldout']
        print(f"{t}: {s['kind']} solved tb72 {s.get('solved_tb72', '-')}/{s.get('n_tb72', '-')} (dev58 {s.get('solved_tb72_dev58', '-')}, train14 {s.get('solved_tb72_train14', '-')}) "
              f"h250 {s.get('solved_h250', '-')}/{s.get('n_h250', '-')} track {s.get('solved_track', '-')}/{s.get('n_track', '-')}; "
              f"σ-covered held-out {s['sigma_covered_solved']}/{s['sigma_covered_n']} " +
              ' '.join(f"{k[:6]} {v['solved']}/{v['n']}" for k, v in f.items()) +
              f"; acquired {s['families_acquired']}; classes {s['proof_classes_sigma_covered']}; cut {100 * s['cut_share']:.2f} %")
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(res, open(a.out, 'w'), indent=1)


if __name__ == '__main__':
    main()
