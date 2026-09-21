"""Lean as the in-loop checker for Lean-format models (run lean-format).

gate(tok, prompts, nd_proofs, texts) is called by sample.generate() for a LeanTokenizer.  For every distinct
(prompt, literal Lean text) whose text parsed in the strict grammar it (i) asks Lean (core) whether the literal text proves
the theorem, (ii) asks nd_verify whether the denoted ND proof does, logs the 2 x 2 table and the timings, writes every
disagreement to <log>.disagree.jsonl, and returns the ND proofs with Lean-rejected ones prefixed 'LEANREJ ' (so that
nd_verify-based judging downstream accepts exactly the samples that BOTH checkers accept).

One theorem per line in a chunk file, `lean -DmaxErrors=...` so every error is reported; error line -> theorem.  A chunk
whose lean process crashes / times out is split recursively; a single theorem that crashes is rejected.
Log: $LEAN_GATE_LOG (default artifacts/lean_gate.jsonl), one json line per generate() call.
"""
import os, re, sys, json, time, subprocess, tempfile, shutil, collections
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text

LEAN = os.path.expanduser('~/.elan/bin/lean')
CHUNK = int(os.environ.get('LEAN_GATE_CHUNK', '400'))
WORKERS = int(os.environ.get('LEAN_GATE_WORKERS', str(max(1, (os.cpu_count() or 2) // 2))))
ERR = re.compile(r'^[^\n]*?:(\d+):\d+: error', re.M)


def _run(lines, workdir, tag, depth=0):
    """lines: list of one-line theorem sources -> (list of bool, cpu seconds)"""
    fn = os.path.join(workdir, f'c_{tag}.lean')
    with open(fn, 'w') as f:
        f.write('set_option linter.unusedVariables false\n' + '\n'.join(lines) + '\n')
    t0 = time.time()
    try:
        p = subprocess.run([LEAN, '-DmaxErrors=100000000', fn], capture_output=True, text=True, timeout=60 + 2 * len(lines))
        o = p.stdout + p.stderr; rc = p.returncode
    except subprocess.TimeoutExpired:
        o = ''; rc = -9
    cpu = time.time() - t0
    os.remove(fn)
    bad = {int(m.group(1)) - 2 for m in ERR.finditer(o)}
    crashed = rc not in (0, 1) or (rc == 1 and not bad) or any(b < 0 or b >= len(lines) for b in bad)
    if crashed:
        if len(lines) == 1:
            return [False], cpu
        h = len(lines) // 2
        a, ca = _run(lines[:h], workdir, tag + 'a', depth + 1); b, cb = _run(lines[h:], workdir, tag + 'b', depth + 1)
        return a + b, cpu + ca + cb
    return [k not in bad for k in range(len(lines))], cpu


def lean_check(items):
    """items: list of (statement text, tactic text) -> (list of bool, wall seconds, summed process seconds)"""
    if not items:
        return [], 0.0, 0.0
    lines = [f'{s.replace("theorem t ", f"theorem t{k} ", 1)} {b}' for k, (s, b) in enumerate(items)]
    wd = tempfile.mkdtemp(prefix='leangate_')
    t0 = time.time()
    chunks = [(lines[i:i + CHUNK], i) for i in range(0, len(lines), CHUNK)]
    with ThreadPoolExecutor(WORKERS) as ex:
        res = list(ex.map(lambda c: _run(c[0], wd, str(c[1])), chunks))
    shutil.rmtree(wd, ignore_errors=True)
    ok = [x for r, _ in res for x in r]
    return ok, time.time() - t0, sum(c for _, c in res)


def gate(tok, prompts, nd_proofs, texts):
    logfn = os.environ.get('LEAN_GATE_LOG', 'artifacts/lean_gate.jsonl')
    keys = {}
    for p, nd, tx in zip(prompts, nd_proofs, texts):
        if tx is not None and not nd.startswith('LEANPARSE'):
            keys.setdefault((p, tx), nd)
    items = list(keys.items())
    lean_ok, wall, cpu = lean_check([(tok.statement(p), tx) for (p, tx), _ in items])
    t0 = time.time()
    nd_ok = [verify_text(p + ' ' + nd)[0] for (p, tx), nd in items]
    t_nd = time.time() - t0
    verdict = {k: lo for (k, _), lo in zip(items, lean_ok)}
    tab = collections.Counter((bool(a), bool(b)) for a, b in zip(nd_ok, lean_ok))
    dis = [{'prompt': p, 'lean_text': tx, 'nd': nd, 'nd_ok': bool(a), 'lean_ok': bool(b)} for ((p, tx), nd), a, b in zip(items, nd_ok, lean_ok) if bool(a) != bool(b)]
    n_parse = sum(1 for nd in nd_proofs if nd.startswith('LEANPARSE'))
    rec = {'utc': time.strftime('%FT%TZ', time.gmtime()), 'samples': len(prompts), 'parse_fail': n_parse, 'distinct_checked': len(items),
           'both_ok': tab[(True, True)], 'nd_ok_lean_rej': tab[(True, False)], 'nd_rej_lean_ok': tab[(False, True)], 'both_rej': tab[(False, False)],
           'lean_wall_s': wall, 'lean_proc_s': cpu, 'nd_verify_s': t_nd, 'workers': WORKERS, 'chunk': CHUNK}
    os.makedirs(os.path.dirname(logfn) or '.', exist_ok=True)
    with open(logfn, 'a') as f:
        f.write(json.dumps(rec) + '\n')
    if dis:
        with open(logfn.replace('.jsonl', '') + '.disagree.jsonl', 'a') as f:
            for d in dis:
                f.write(json.dumps(d, ensure_ascii=False) + '\n')
    print(f'[lean_gate] {len(prompts)} samples, parse-fail {n_parse}, distinct checked {len(items)}: both ok {tab[(True, True)]}, nd-only {tab[(True, False)]}, '
          f'lean-only {tab[(False, True)]}, both rej {tab[(False, False)]}; lean {wall:.1f}s wall ({cpu:.1f}s proc, {WORKERS} workers), nd_verify {t_nd:.1f}s', flush=True)
    out = []
    for p, nd, tx in zip(prompts, nd_proofs, texts):
        if tx is None or nd.startswith('LEANPARSE') or verdict[(p, tx)]:
            out.append(nd)
        else:
            out.append('LEANREJ ' + nd)
    return out
