# reviewer's own Lean runner: one theorem per line, error line -> theorem index. Lean 4 core, no Mathlib.
import subprocess, tempfile, os, re, sys
from concurrent.futures import ThreadPoolExecutor
LEAN = os.path.expanduser('~/.elan/bin/lean')
ERR = re.compile(r':(\d+):\d+: error')
def _one(srcs):
    body = 'set_option linter.unusedVariables false\n' + ''.join(s.replace('theorem t ', f'theorem x{i} ', 1) + '\n' for i, s in enumerate(srcs))
    fd, fn = tempfile.mkstemp(suffix='.lean'); os.write(fd, body.encode()); os.close(fd)
    p = subprocess.run([LEAN, '-j', '1', '-DmaxErrors=100000000', fn], capture_output=True, text=True)
    os.remove(fn)
    o = p.stdout + p.stderr
    bad = {int(m.group(1)) - 2 for m in ERR.finditer(o)}
    if p.returncode not in (0, 1) or (p.returncode == 1 and not bad) or any(b < 0 or b >= len(srcs) for b in bad):
        if len(srcs) == 1: return [None]
        h = len(srcs) // 2
        return _one(srcs[:h]) + _one(srcs[h:])
    # 'sorry' / axioms cannot appear in this grammar; also reject any warning mentioning sorry
    if 'sorry' in o: raise SystemExit('sorry in output')
    return [i not in bad for i in range(len(srcs))]
def check(srcs, chunk=300, workers=2):
    parts = [srcs[i:i + chunk] for i in range(0, len(srcs), chunk)]
    with ThreadPoolExecutor(workers) as ex:
        return [x for r in ex.map(_one, parts) for x in r]
