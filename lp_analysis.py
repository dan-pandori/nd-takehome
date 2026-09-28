"""lean-prefilter: the soundness table (test a) from the pulled corpus files.  python3 lp_analysis.py [OUT.json]
  C1  artifacts/lp/corpus/<ckpt>.dump.jsonl[.gz]   shadow-mode gate dumps: 'lean' = Lean's verdict, 'filter' = reason|null
  C2  artifacts/lp/c2/c2_checked.jsonl[.gz]        edge mutants (lp_edge.py -> lp_check.py), 'src' = mutation kind
  C3  artifacts/lp/c3/c3_checked.jsonl[.gz]        stored bucket records re-checked in Lean (lp_check.py)
Rows are distinct (prompt, lean_text) pairs; C1 is also deduplicated across checkpoints for the corpus total.
false_rej = filter rejected AND Lean accepted: must be 0.  coverage = filter rejects / Lean rejects.
The filter verdict is RECOMPUTED here with the current lean_prefilter.py (the stored 'filter' field was written by the
code of the day); 'stored_filter_differs' counts rows where the two disagree on reject-vs-pass."""
import glob, gzip, json, sys, collections, os, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lean_tok import LeanTokenizer
from lean_prefilter import reject_reason, _split, _P
_tok = LeanTokenizer('lean_seq'); _st = {}
ndiff = collections.Counter()


def refilter(d):
    p = d['prompt']
    if p not in _st:
        _st[p] = _tok.statement(p)
    r = reject_reason(_st[p], d['lean_text'])
    if (r is None) != (d.get('filter') is None):
        ndiff['stored_filter_differs'] += 1
    d['filter'] = r
    return d


def rd(fn):
    op = gzip.open if fn.endswith('.gz') else open
    with op(fn, 'rt') as f:
        for l in f:
            yield json.loads(l)


def feats(text):
    """features of a Lean-ACCEPTED text that a naive checker would get wrong: `→ False` written for a negation, and
    `n.elim` by the declared head of n's type (names declared more than once count as `shadowed`)."""
    t = _split(text); decl = {}; out = set()
    if '→ False )' in text:
        out.add('arrow_false_written')
    for i, x in enumerate(t):
        if x == ':' and i > 0 and t[i - 1][0] == 'n' and t[i - 1][1:].isdigit():
            p = _P(t); p.i = i + 1
            try:
                h = p.formula()[0]
                decl[t[i - 1]] = h if t[i - 1] not in decl else 'shadowed'   # declared twice: scope decides, not counted
            except Exception:
                pass
        if x == '.elim' and i > 0:
            out.add('elim_on_' + decl.get(t[i - 1], '?'))
    return out


def row():
    return collections.Counter()


def add(c, lean, filt, text=None):
    if lean and text is not None:
        for f in feats(text):
            c['acc_' + f] += 1
    c['n'] += 1; c['lean_ok'] += bool(lean); c['lean_rej'] += (not lean)
    c['filter_rej'] += filt is not None; c['false_rej'] += (filt is not None and bool(lean))
    c['filter_pass_lean_rej'] += (filt is None and not lean)


tab = collections.OrderedDict(); reasons = collections.Counter(); fr = []
seen = set(); tot = row()
for fn in sorted(glob.glob('artifacts/lp/corpus/*.dump.jsonl*')):
    name = os.path.basename(fn).split('.dump')[0]
    c = tab.setdefault('C1 ' + name, row()); loc = set()
    for d in rd(fn):
        k = hashlib.blake2b((d['prompt'] + '\x00' + d['lean_text']).encode(), digest_size=12).digest()
        if k in loc: continue
        loc.add(k); refilter(d)
        add(c, d['lean'], d['filter'])
        if d['filter'] is not None and d['lean']: fr.append(('C1', name, d))
        if k not in seen:
            seen.add(k); add(tot, d['lean'], d['filter'], d['lean_text'])
            if d['filter']: reasons[d['filter']] += 1
tab['C1 all checkpoints (distinct)'] = tot
del seen
for label, pat in (('C2', 'artifacts/lp/c2/c2*_checked.jsonl*'), ('C3', 'artifacts/lp/c3/c3_checked.jsonl*')):
    for fn in sorted(glob.glob(pat)):
        for d in rd(fn):
            refilter(d); src = d['src']
            if label == 'C3':
                src = 'disagree (Lean-only accepts)' if 'disagree' in src else 'leanrej samples' if 'leanrej' in src else 'lean-judge t5 dump'
            add(tab.setdefault(f'{label} {src}', row()), d['lean'], d['filter'])
            add(tab.setdefault(f'{label} all', row()), d['lean'], d['filter'], d['lean_text'])
            if d['filter'] is not None and d['lean']: fr.append((label, src, d))
out = {'stored_filter_differs': ndiff['stored_filter_differs'], 'rows': {k: dict(v) for k, v in tab.items()}, 'filter_reasons_C1': dict(reasons.most_common()),
       'false_rejects': [{'corpus': a, 'src': b, 'prompt': d['prompt'], 'lean_text': d['lean_text'], 'filter': d['filter']} for a, b, d in fr]}
json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else 'artifacts/lp/soundness.json', 'w'), indent=1, ensure_ascii=False)
print('| corpus | distinct texts | Lean accepts | Lean rejects | filter rejects | **false rejects** | coverage of Lean rejects |')
print('|---|---:|---:|---:|---:|---:|---:|')
for k, c in tab.items():
    cov = f"{100 * c['filter_rej'] / c['lean_rej']:.2f} %" if c['lean_rej'] else '–'
    print(f"| {k} | {c['n']:,} | {c['lean_ok']:,} | {c['lean_rej']:,} | {c['filter_rej']:,} | **{c['false_rej']}** | {cov} |")
print('\nLean-ACCEPTED texts by feature (all of them passed the filter unless false_rej > 0):')
for k in ('C1 all checkpoints (distinct)', 'C2 all', 'C3 all'):
    if k in tab:
        print(f'  {k}:', {f[4:]: v for f, v in sorted(tab[k].items()) if f.startswith('acc_')})
print('\nfilter reasons (C1 distinct):', dict(reasons.most_common()))
print('false rejects total:', len(fr), '; stored filter field differs from recomputed:', ndiff['stored_filter_differs'])
