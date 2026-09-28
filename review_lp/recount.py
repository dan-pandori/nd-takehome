# reviewer recount (independent): re-run the final filter on every stored text; Lean verdicts from the files
import gzip, json, sys, glob, hashlib, collections, os
sys.path.insert(0, os.path.expanduser('~/review/lean-prefilter'))
from lean_prefilter import reject_reason
from lean_tok import LeanTokenizer
tok = LeanTokenizer('lean_seq')
stmt = {}
def st(p):
    if p not in stmt: stmt[p] = tok.statement(p)
    return stmt[p]
def h(p, t): return hashlib.blake2b((p + '\x00' + t).encode(), digest_size=12).digest()
A = 'artifacts/lp/'
out = {}
fr_examples = []
def run(name, files, lean_key):
    seen = {}; c = collections.Counter(); reasons = collections.Counter(); per = collections.Counter()
    for fn in files:
        for l in gzip.open(fn, 'rt'):
            d = json.loads(l)
            k = h(d['prompt'], d['lean_text'])
            c['rows'] += 1
            lean = d.get(lean_key)
            if lean is None: c['lean_null'] += 1; continue
            if k in seen:
                c['dup_rows'] += 1
                if seen[k] != lean: c['verdict_conflict'] += 1
                continue
            seen[k] = lean
            r = reject_reason(st(d['prompt']), d['lean_text'])
            if (r is None) != (d.get('filter') is None): c['filter_differs_from_stored'] += 1
            c['distinct'] += 1; c['lean_ok' if lean else 'lean_rej'] += 1
            if r is not None:
                reasons[r] += 1
                if lean:
                    c['FALSE_REJECT'] += 1
                    if len(fr_examples) < 20: fr_examples.append((name, d['prompt'], d['lean_text'], r))
                else: c['filter_rej'] += 1
            elif not lean: c['lean_rej_passed'] += 1
            per[os.path.basename(fn).split('.')[0]] += 1
    c['share_of_lean_rejects_pct'] = round(100 * c['filter_rej'] / max(1, c['lean_rej']), 3)
    out[name] = {'counts': dict(c), 'reasons': dict(reasons.most_common()), 'per_file_distinct_first_seen': dict(per)}
    print(name, json.dumps(out[name]['counts']), flush=True)
    return set(seen)
c1 = run('C1', sorted(glob.glob(A + 'corpus/*.dump.jsonl.gz')), 'lean')
c2 = run('C2', [A + 'c2/c2_checked.jsonl.gz'], 'lean')
c2r = run('C2r', [A + 'c2/c2r_checked.jsonl.gz'], 'lean')
c3 = run('C3', [A + 'c3/c3_checked.jsonl.gz'], 'lean')
out['union_distinct'] = len(c1 | c2 | c2r | c3)
out['false_reject_examples'] = fr_examples
json.dump(out, open('review_lp/recount.json', 'w'), indent=1, ensure_ascii=False)
print('union', out['union_distinct'], 'FR examples', len(fr_examples))
