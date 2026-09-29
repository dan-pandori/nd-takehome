"""Reviewer recount of design A (re-sample of the 224 L_true>=11 transfer theorems at k=256).
Reads artifacts/sf2/rs/*.jsonl (per-theorem n_ok) and the bucket dumps rv/dumps/rs_*.jsonl.gz (literal text + verdict),
re-checks accepted texts with rv_lean (own harness), writes rv/resample.json."""
import json, gzip, glob, os, random, re, collections, sys
sys.path.insert(0, os.path.dirname(__file__))
import rv_lean

ROOT = os.path.expanduser('~/review/state-frontier')
pool = [json.loads(l) for l in open(f'{ROOT}/data/sf2/long.jsonl')]
L = {r['prompt']: r['L_true'] for r in pool}
NAME = {r['prompt']: r['name'] for r in pool}
GE13 = {p for p, l in L.items() if l >= 13}


def term_size(text):
    """own term-size: count proof-term atoms after deleting every type ascription.
    Deletes ': <type> :=' in have, and ': <type> )' in fun binders; then counts tokens that are names (hK/nK),
    constructors / eliminators (Or.inl, Or.inr, Or.elim, .elim, .1, .2, ⟨, fun, Classical.*, absurd, False.elim),
    i.e. every token except punctuation, 'by', 'have', 'exact', ';', ':=', '=>'."""
    t = text
    t = re.sub(r'have (\w+) : .*? := ', r'have \1 := ', t)          # lazy: type ends at first ' := '
    t = re.sub(r'\( (\w+) : [^=]*? \) =>', r'\1 =>', t)
    toks = t.replace('.1', ' .1').replace('.2', ' .2').replace('.elim', ' .elim').split()
    skip = {'(', ')', ',', ';', ':=', '=>', 'by', 'have', 'exact', '⟩'}
    return sum(1 for x in toks if x not in skip)


def n_lines(text):
    return text.count('have ') + 1


def main():
    random.seed(0)
    out = {}
    lean_items, lean_meta = [], []
    for f in sorted(glob.glob(f'{ROOT}/artifacts/sf2/rs/*.jsonl')):
        m = os.path.basename(f)[:-6]
        rows = [json.loads(l) for l in open(f)]
        assert len(rows) == 224 and {r['prompt'] for r in rows} == set(L)
        nok = {r['prompt']: r['n_ok'] for r in rows}
        assert all(r['n_tried'] == 256 for r in rows)
        dump = [json.loads(l) for l in gzip.open(f'{ROOT}/rv/dumps/rs_{m}.jsonl.gz', 'rt')]
        acc = collections.defaultdict(set)
        rej_samples = []
        for d in dump:
            if d['prompt'] not in L: continue
            if d['lean_ok']: acc[d['prompt']].add(d['lean_text'])
            else: rej_samples.append((d['prompt'], d['lean_text']))
        solved_json = {p for p, n in nok.items() if n > 0}
        solved_dump = set(acc)
        distinct_gt_nok = sum(1 for p in acc if len(acc[p]) > nok[p])
        # Lean re-check: every accepted text at >=13, plus 100 random accepted (theorem-stratified) others, plus 30 rejected
        ge = [(p, t) for p in acc if p in GE13 for t in sorted(acc[p])]
        rest = [(p, t) for p in acc if p not in GE13 for t in sorted(acc[p])]
        rest = random.sample(rest, min(100, len(rest)))
        rej = random.sample(rej_samples, min(30, len(rej_samples)))
        for kind, lst in (('acc13', ge), ('acc', rest), ('rej', rej)):
            for it in lst:
                lean_items.append(it); lean_meta.append((m, kind))
        def cnt(sel):
            return sum(1 for p in sel if nok[p] > 0), sum(nok[p] for p in sel)
        s13 = [p for p in L if L[p] >= 13]; s1112 = [p for p in L if L[p] < 13]
        n13, succ13 = cnt(s13); n1112, succ1112 = cnt(s1112)
        ts = [term_size(t) for p in acc if p in GE13 for t in acc[p]]
        nl = [n_lines(t) for p in acc if p in GE13 for t in acc[p]]
        out[m] = dict(N13=n13, succ13=succ13, rate13=succ13 / (len(s13) * 256), sol1112=n1112, succ1112=succ1112,
                      solved_total=len(solved_json), json_vs_dump_solved_mismatch=sorted(NAME[p] for p in solved_json ^ solved_dump),
                      distinct_acc_gt_nok=distinct_gt_nok,
                      solved13={NAME[p]: nok[p] for p in s13 if nok[p] > 0},
                      termsize13=ts, lines13=nl, n_lean=dict(acc13=len(ge), acc=len(rest), rej=len(rej)))
    res = rv_lean.check(lean_items)
    for (m, kind), (ok, why), it in zip(lean_meta, res, lean_items):
        o = out[m].setdefault('lean', collections.Counter())
        o[f'{kind}:{ok}'] += 1
        if (kind != 'rej') and not ok:
            out[m].setdefault('lean_rejects', []).append((NAME[it[0]], why, it[1][:400]))
    json.dump(out, open(f'{ROOT}/rv/resample.json', 'w'), indent=1)
    for m, o in out.items():
        print(f"{m:18s} N13 {o['N13']} succ13 {o['succ13']:4d} rate13 {o['rate13']:.5f} sol11-12 {o['sol1112']:3d} "
              f"mism {o['json_vs_dump_solved_mismatch']} dgt {o['distinct_acc_gt_nok']} lean {dict(o['lean'])}")


if __name__ == '__main__':
    main()
