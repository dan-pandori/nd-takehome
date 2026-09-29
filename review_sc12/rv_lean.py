"""Reviewer's own Lean re-check of literal lean_seq texts: one theorem per line, error line -> theorem.
Rejects on any error, on any 'sorry' warning, and on any token outside the grammar's alphabet."""
import json, os, sys, re, random, subprocess, tempfile, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(__file__))
from rv_common import rd, header

LEAN = os.path.expanduser('~/.elan/bin/lean')
B = os.path.expanduser(os.environ.get('RV_BASE', '~/review/state-cap12'))
ALLOWED = re.compile(r'^(have|:=|;|by|exact|fun|=>|\(|\)|,|⟨|⟩|:|[PQRS]|∨|∧|→|¬|False|h\d+|n\d+|'
                     r'Or\.elim|Or\.inl|Or\.inr|absurd|False\.elim|Not\.elim|And\.left|And\.right|\.1|\.2|'
                     r'[nh]\d+\.(1|2|elim)|hh|Classical\.byContradiction)$')
ERR = re.compile(r':(\d+):\d+: (error|warning)(.*)')


def check(items):
    """items: list of (prompt, text) -> list of (ok, why)"""
    res = [None] * len(items)
    lines = ['set_option maxRecDepth 4000']
    for k, (p, t) in enumerate(items):
        bad = [x for x in t.split() if not ALLOWED.match(x)]
        if bad:
            res[k] = (False, 'alphabet:' + ' '.join(sorted(set(bad))[:5]))
        lines.append(header(p).replace('theorem t ', f'theorem t{k} ', 1) + ' ' + t)
    with tempfile.NamedTemporaryFile('w', suffix='.lean', delete=False, dir='/tmp') as f:
        f.write('\n'.join(lines) + '\n'); fn = f.name
    pr = subprocess.run([LEAN, '-DmaxErrors=100000000', fn], capture_output=True, text=True, timeout=3600)
    os.unlink(fn)
    o = pr.stdout + pr.stderr
    errs = collections.defaultdict(list)
    for m in ERR.finditer(o):
        ln = int(m.group(1)); errs[ln - 2].append(m.group(2) + m.group(3)[:80])
    for k in range(len(items)):
        if res[k] is not None:
            continue
        e = errs.get(k, [])
        hard = [x for x in e if x.startswith('error') or 'sorry' in x]
        res[k] = (not hard, '; '.join(e)[:200] if e else 'ok')
    if pr.returncode != 0 and not errs:
        raise RuntimeError(o[:2000])
    return res


def run(items, chunk=150, workers=2):
    chunks = [items[i:i + chunk] for i in range(0, len(items), chunk)]
    with ThreadPoolExecutor(workers) as ex:
        outs = list(ex.map(check, chunks))
    return [x for o in outs for x in o]


if __name__ == '__main__':
    inp, outp = sys.argv[1], sys.argv[2]
    recs = list(rd(inp))
    res = run([(r['prompt'], r['text']) for r in recs])
    with open(outp, 'w') as f:
        for r, (ok, why) in zip(recs, res):
            r['rv_ok'] = ok; r['rv_why'] = why
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    c = collections.Counter((r.get('kind', 'pos'), r['expect'], ok) for r, (ok, _) in zip(recs, res))
    print(c)
