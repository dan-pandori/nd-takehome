#!/usr/bin/env python3
"""Fetch bulk files that are not in git (run repo-hygiene-2) from the public bucket, by repo path.

    python3 fetch_artifacts.py artifacts/lp/                 # every manifest row under this prefix
    python3 fetch_artifacts.py artifacts/nf/x.jsonl ckpts/   # files and prefixes, any mix
    python3 fetch_artifacts.py --list artifacts/lp/          # show what would be fetched (and what is already here)
    python3 fetch_artifacts.py --verify-remote all           # stream every bucket object, check bytes + sha256, write nothing

Rows come from artifacts/MANIFEST.jsonl ({path, uri, bytes, sha256, run, ...}; `all` = every row). Each file is written
to its repo path, so the scripts that read artifacts/ keep their paths. A file already on disk with the manifest's
sha256 is skipped (idempotent); a file with another sha256 is re-fetched. A download is written to <path>.part, checked
(bytes + sha256) and renamed into place, so an interrupted fetch never leaves a wrong file at <path>.
Standard library only: the bucket is public, so no `hf` CLI or token is needed (HF_TOKEN is sent if set).
Bulk = .jsonl, .jsonl.gz, .pt, or > 5 MB (BULK_BYTES); publish_artifacts.py and ci/check_sizes.sh use the same rule."""
import argparse, hashlib, json, os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(ROOT, 'artifacts', 'MANIFEST.jsonl')
BULK_EXT = ('.jsonl', '.jsonl.gz', '.pt')
BULK_BYTES = 5 * 1024 * 1024
HTTP = os.environ.get('ND_BUCKET_HTTP', 'https://huggingface.co/buckets')


def is_bulk(path, nbytes):
    return path.endswith(BULK_EXT) or nbytes > BULK_BYTES


def load(manifest=MANIFEST):
    rows = {}
    if os.path.exists(manifest):
        for line in open(manifest):
            if line.strip():
                r = json.loads(line); rows[r['path']] = r
    return rows


def url(uri):
    assert uri.startswith('hf://buckets/'), uri
    ns, bucket, path = uri[len('hf://buckets/'):].split('/', 2)
    return f'{HTTP}/{ns}/{bucket}/resolve/{urllib.request.quote(path)}'


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def stream(uri, out=None, tries=3):
    """Download uri; write to `out` if given. Returns (bytes, sha256)."""
    req = urllib.request.Request(url(uri))
    if os.environ.get('HF_TOKEN'):
        req.add_header('Authorization', 'Bearer ' + os.environ['HF_TOKEN'])
    for t in range(tries):
        try:
            h, n = hashlib.sha256(), 0
            f = open(out, 'wb') if out else None
            with urllib.request.urlopen(req, timeout=300) as r:
                for b in iter(lambda: r.read(1 << 20), b''):
                    h.update(b); n += len(b)
                    if f: f.write(b)
            if f: f.close()
            return n, h.hexdigest()
        except Exception as e:
            if t == tries - 1:
                raise RuntimeError(f'{uri}: {type(e).__name__}: {e}')


def select(rows, targets):
    if targets == ['all']:
        return sorted(rows)
    out, missing = [], []
    for t in targets:
        t = os.path.relpath(os.path.abspath(t), ROOT) + ('/' if t.endswith('/') else '') if os.path.isabs(t) else t
        hit = [p for p in rows if p == t or p.startswith(t.rstrip('/') + '/')]
        (out.extend(hit) if hit else missing.append(t))
    if missing:
        sys.exit(f'not in the manifest: {missing}  (small files are in git; see CONTRIBUTING.md)')
    return sorted(set(out))


def fetch_one(r, root=ROOT):
    dst = os.path.join(root, r['path'])
    if os.path.exists(dst) and os.path.getsize(dst) == r['bytes'] and sha256_file(dst) == r['sha256']:
        return 'have'
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    n, h = stream(r['uri'], dst + '.part')
    if (n, h) != (r['bytes'], r['sha256']):
        os.remove(dst + '.part')
        raise RuntimeError(f"{r['path']}: bucket copy has {n} bytes sha256 {h[:16]}, manifest {r['bytes']} {r['sha256'][:16]}")
    if os.path.lexists(dst):
        os.remove(dst)        # never write through a hard link shared with another worktree
    os.rename(dst + '.part', dst)
    return 'fetched'


def verify_one(r):
    n, h = stream(r['uri'])
    return 'ok' if (n, h) == (r['bytes'], r['sha256']) else f'MISMATCH bytes={n} sha256={h}'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('targets', nargs='+', help='repo paths or prefixes (a directory prefix ends with /), or `all`')
    ap.add_argument('--manifest', default=MANIFEST)
    ap.add_argument('--root', default=ROOT, help='worktree to write into (default: the one this script is in)')
    ap.add_argument('--jobs', type=int, default=8)
    ap.add_argument('--list', action='store_true', help='print the rows and whether each is present; fetch nothing')
    ap.add_argument('--verify-remote', metavar='TSV', nargs='?', const='-',
                    help='download every selected object, compare bytes + sha256 with the manifest, write nothing '
                         'locally except the report (TSV path, or stdout)')
    a = ap.parse_args()
    rows = load(a.manifest)
    paths = select(rows, a.targets)
    if a.list:
        for p in paths:
            d = os.path.join(a.root, p)
            print(f"{'here' if os.path.exists(d) else '-   '}\t{rows[p]['bytes']}\t{p}\t{rows[p]['uri']}")
        return
    fn = verify_one if a.verify_remote else (lambda r: fetch_one(r, a.root))
    res, bad = {}, 0
    with ThreadPoolExecutor(a.jobs) as ex:
        futs = {p: ex.submit(fn, rows[p]) for p in paths}
        for i, p in enumerate(paths):
            try:
                res[p] = futs[p].result()
            except Exception as e:
                res[p] = f'ERROR {e}'
            bad += res[p] not in ('ok', 'have', 'fetched')
            if (i + 1) % 200 == 0:
                print(f'  {i + 1}/{len(paths)}', file=sys.stderr)
    if a.verify_remote:
        f = sys.stdout if a.verify_remote == '-' else open(a.verify_remote, 'w')
        f.write('path\tbytes\tsha256\tresult\n')
        for p in paths:
            f.write(f"{p}\t{rows[p]['bytes']}\t{rows[p]['sha256']}\t{res[p]}\n")
    else:
        for p in paths:
            if res[p] not in ('have', 'fetched'):
                print(p, res[p])
    c = {}
    for v in res.values():
        c[v.split()[0]] = c.get(v.split()[0], 0) + 1
    print(f'{len(paths)} rows: ' + ', '.join(f'{k} {v}' for k, v in sorted(c.items())), file=sys.stderr)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
