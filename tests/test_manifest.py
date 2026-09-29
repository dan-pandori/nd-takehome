#!/usr/bin/env python3
"""CI (run repo-hygiene-2): artifacts/MANIFEST.jsonl is well-formed and disjoint from git; fetch_artifacts.py fetches,
checks sha256, is idempotent, and replaces a corrupted local copy. Offline: the "bucket" is a file:// tree in a temp dir.
    python3 tests/test_manifest.py"""
import hashlib, importlib, json, os, re, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

rows = [json.loads(l) for l in open(os.path.join(ROOT, 'artifacts', 'MANIFEST.jsonl'))]
tracked = set(subprocess.run(['git', 'ls-files'], cwd=ROOT, capture_output=True, text=True).stdout.split('\n'))
import fetch_artifacts as fa
paths = [r['path'] for r in rows]
assert len(paths) == len(set(paths)), 'duplicate manifest paths'
for r in rows:
    assert r['uri'].startswith('hf://buckets/dan-pandori/nd-rl/'), r
    assert re.fullmatch(r'[0-9a-f]{64}', r['sha256']) and isinstance(r['bytes'], int), r
    assert fa.is_bulk(r['path'], r['bytes']) or r['path'].startswith('data/'), f"not a bulk file: {r['path']}"
    assert r['path'] not in tracked, f"manifest path is tracked in git: {r['path']}"
print(f'  {len(rows)} rows well-formed, none tracked')

with tempfile.TemporaryDirectory() as d:
    blobs = {'artifacts/x/a.jsonl': b'{"a": 1}\n', 'artifacts/x/sub/b.pt': os.urandom(3000), 'ckpts/c.pt': b'c'}
    man = []
    for p, b in blobs.items():
        f = os.path.join(d, 'bucket', 'ns', 'bk', 'resolve', 'run', p); os.makedirs(os.path.dirname(f), exist_ok=True)
        open(f, 'wb').write(b)
        man.append(dict(path=p, uri=f'hf://buckets/ns/bk/run/{p}', bytes=len(b), sha256=hashlib.sha256(b).hexdigest()))
    mf = os.path.join(d, 'M.jsonl'); open(mf, 'w').write(''.join(json.dumps(r) + '\n' for r in man))
    wt = os.path.join(d, 'wt'); os.makedirs(wt)
    env = dict(os.environ, ND_BUCKET_HTTP='file://' + os.path.join(d, 'bucket'))
    run = lambda *a: subprocess.run([sys.executable, os.path.join(ROOT, 'fetch_artifacts.py'), '--manifest', mf,
                                     '--root', wt, *a], env=env, capture_output=True, text=True)
    p = run('artifacts/x/'); assert p.returncode == 0 and 'fetched 2' in p.stderr, p.stderr
    assert open(os.path.join(wt, 'artifacts/x/sub/b.pt'), 'rb').read() == blobs['artifacts/x/sub/b.pt']
    assert not os.path.exists(os.path.join(wt, 'ckpts/c.pt'))
    p = run('artifacts/x/'); assert p.returncode == 0 and 'have 2' in p.stderr, p.stderr          # idempotent
    open(os.path.join(wt, 'artifacts/x/a.jsonl'), 'w').write('corrupt\n')
    p = run('all'); assert p.returncode == 0 and 'fetched 2' in p.stderr and 'have 1' in p.stderr, p.stderr
    assert open(os.path.join(wt, 'artifacts/x/a.jsonl'), 'rb').read() == blobs['artifacts/x/a.jsonl']
    open(os.path.join(d, 'bucket/ns/bk/resolve/run/ckpts/c.pt'), 'wb').write(b'X')            # bucket copy differs
    os.remove(os.path.join(wt, 'ckpts/c.pt'))
    p = run('ckpts/c.pt'); assert p.returncode == 1 and not os.path.exists(os.path.join(wt, 'ckpts/c.pt')), p.stderr
    p = run('artifacts/nope/'); assert p.returncode != 0 and 'not in the manifest' in p.stderr
print('  fetch: prefix select, sha256 check, idempotent, corrupted copy re-fetched, bad bucket copy refused')
print('PASS test_manifest')
