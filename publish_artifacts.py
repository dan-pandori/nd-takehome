#!/usr/bin/env python3
"""Publish a run's bulk files to the public bucket and list them in artifacts/MANIFEST.jsonl (run repo-hygiene-2).

    python3 publish_artifacts.py <run-id> <dir>...          # e.g. publish_artifacts.py state-frontier artifacts/sf ckpts/sf
    python3 publish_artifacts.py --dry-run <run-id> <dir>   # show what would be uploaded; touch nothing

For every bulk file under <dir> (.jsonl, .jsonl.gz, .pt, or > 5 MB; fetch_artifacts.is_bulk):
  1. credential scan (scan_secrets.py); a hit stops the whole call before anything is uploaded;
  2. upload to hf://buckets/dan-pandori/nd-rl/<run-id>/<repo path> (`hf buckets cp`, size checked; record.bucket_cp);
  3. download the bucket copy again and compare bytes + sha256 with the local file;
  4. add or replace the file's manifest row {path, uri, bytes, sha256, run, run_src: publish, utc};
  5. `git rm --cached` it if it is tracked (the file stays on disk; .gitignore already ignores bulk kinds).
A file whose row already has the same sha256 is skipped, so re-running is cheap. Small files are left for git.
Then commit artifacts/MANIFEST.jsonl with the run's other files. The manifest is kept sorted by path and merged with
git's union driver (.gitattributes), so two runs publishing at once do not conflict."""
import argparse, datetime, json, os, subprocess, sys
import fetch_artifacts as fa
import scan_secrets

BUCKET = 'hf://buckets/dan-pandori/nd-rl'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('run_id')
    ap.add_argument('dirs', nargs='+')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--manifest', default=fa.MANIFEST)
    a = ap.parse_args()
    os.chdir(fa.ROOT)
    rows = fa.load(a.manifest)
    todo = []
    for d in a.dirs:
        d = os.path.relpath(os.path.abspath(d), fa.ROOT)
        assert not d.startswith('..'), f'{d} is outside the repository'
        for dp, _, fs in os.walk(d):
            for f in fs:
                p = os.path.join(dp, f)
                if p.endswith('.part') or os.path.islink(p) or not fa.is_bulk(p, os.path.getsize(p)):
                    continue
                if p == 'artifacts/MANIFEST.jsonl':
                    continue
                todo.append(p)
    todo.sort()
    known = scan_secrets.known_secrets()
    hits = {p: h for p in todo if (h := scan_secrets.scan_bytes_obj(p, open(p, 'rb').read(), known))}
    if hits:
        for p, h in hits.items():
            print(f'CREDENTIAL? {p}: {sorted(h)}')
        sys.exit('publish stopped: remove the credential (or the file) and re-run; nothing was uploaded')
    sha = {p: fa.sha256_file(p) for p in todo}
    new = [p for p in todo if rows.get(p, {}).get('sha256') != sha[p]]
    print(f'{len(todo)} bulk files under {a.dirs}; {len(todo) - len(new)} already published unchanged; '
          f'{len(new)} to publish ({sum(os.path.getsize(p) for p in new):,} bytes)')
    if a.dry_run:
        for p in new:
            print(f'  {os.path.getsize(p):>12,}  {p}  ->  {BUCKET}/{a.run_id}/{p}')
        return
    from record import bucket_cp
    utc = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    for i, p in enumerate(new):
        uri = f'{BUCKET}/{a.run_id}/{p}'
        bucket_cp(p, uri)
        n, h = fa.stream(uri)
        if (n, h) != (os.path.getsize(p), sha[p]):
            sys.exit(f'{p}: bucket copy differs after upload ({n} bytes, sha256 {h[:16]}); manifest not changed')
        rows[p] = dict(path=p, uri=uri, bytes=n, sha256=h, run=a.run_id, run_src='publish', utc=utc)
        with open(a.manifest + '.tmp', 'w') as f:        # write after every file: an interrupted call loses nothing
            for k in sorted(rows):
                f.write(json.dumps(rows[k]) + '\n')
        os.replace(a.manifest + '.tmp', a.manifest)
        print(f'  [{i + 1}/{len(new)}] {p}')
    tracked = [p for p in todo if subprocess.run(['git', 'ls-files', '--error-unmatch', p],
                                                 capture_output=True).returncode == 0]
    if tracked:
        subprocess.run(['git', 'rm', '-q', '--cached', '--', *tracked], check=True)
        print(f'untracked {len(tracked)} file(s) (kept on disk)')
    print(f'manifest: {len(rows)} rows. Now: git add {os.path.relpath(a.manifest)} && git commit')


if __name__ == '__main__':
    main()
