#!/usr/bin/env python3
"""results-registry acceptance checks (pre-registration E1-E5), re-derivable from pulled files.

  python3 registry_acceptance.py      # needs the `hf` CLI (E1 downloads the checkpoints); writes
                                      # artifacts/results-registry/acceptance.json and prints the tables
E1  every live `ckpt_saved` row: its URI downloads to a file whose md5 equals the row's md5 (and the pulled local copy's)
E2  negative control: the first downloaded checkpoint with one byte flipped fails the md5 check
    (the other two controls are tests/test_registry.py cases, run on the VPS and on the pod: artifacts/rr/setup.log)
E3  "every held-out accuracy of the control checkpoints, by run": one filter over the merged table
E4  three headline numbers, looked up by metric name, compared with the numbers printed in the runs' write-ups
E5  record() cost per row (timed here) and the upload seconds stored in each checkpoint's sidecar
"""
import collections, glob, gzip, hashlib, json, os, subprocess, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import registry_merge as M
import record

ROOT = record.ROOT
REG = os.path.join(ROOT, 'artifacts', 'results-registry', 'registry')
OUT = os.path.join(ROOT, 'artifacts', 'results-registry', 'acceptance.json')


def md5(p):
    return hashlib.md5(open(p, 'rb').read()).hexdigest()


rows = M.load(sorted(glob.glob(REG + '/*.jsonl') + glob.glob(REG + '/*.jsonl.gz')))
live = [r for r in rows if not r.get('backfilled')]
res = {'rows_total': len(rows), 'rows_live': len(live), 'rows_backfilled': len(rows) - len(live)}
print(f"{len(rows)} rows ({len(live)} live from the smoke run, {len(rows) - len(live)} backfilled)")

# ---- E1 / E2
e1 = []
tmp = tempfile.mkdtemp(prefix='rr_acc_')
for r in [r for r in live if r['metric'] == 'ckpt_saved']:
    dl = os.path.join(tmp, str(len(e1)) + '.pt')
    p = subprocess.run([record.hf_bin(), 'buckets', 'cp', r['ckpt_uri'], dl], capture_output=True, text=True)
    got = md5(dl) if p.returncode == 0 and os.path.exists(dl) else None
    loc = os.path.join(ROOT, r['ckpt'])
    e1.append({'ckpt': r['ckpt'], 'uri': r['ckpt_uri'], 'row_md5': r['ckpt_md5'], 'download_md5': got,
               'local_md5': md5(loc) if os.path.exists(loc) else None, 'bytes': r['value'],
               'upload_s': r['labels'].get('upload_s'), 'ok': got is not None and got == r['ckpt_md5']})
print('\nE1  checkpoint URIs -> md5')
for x in e1:
    print(f"  {'OK  ' if x['ok'] else 'FAIL'} {x['ckpt']:42s} {x['row_md5']} local={'same' if x['local_md5'] == x['row_md5'] else x['local_md5']} "
          f"{x['bytes'] / 1e6:6.1f} MB upload {x['upload_s']}s")
res['E1'] = {'n': len(e1), 'ok': sum(x['ok'] for x in e1), 'rows': e1}
b = bytearray(open(os.path.join(tmp, '0.pt'), 'rb').read())
b[len(b) // 2] ^= 1
res['E2_flip_detected'] = hashlib.md5(bytes(b)).hexdigest() != e1[0]['row_md5']
print(f"E2  one flipped byte detected: {res['E2_flip_detected']}")

# ---- E3
q = ['metric=heldout_greedy_acc', 'role=stage1,init,frozen', 'L=', 'slice=']
sel = [r for r in rows if M.match(r, q)]
by = collections.defaultdict(list)
for r in sel:
    by[r['run_id']].append(r)
print(f"\nE3  registry_merge.py --q {' '.join(q)}   ->  {len(sel)} rows, {len(by)} runs")
print(f"  {'run':18s} {'rows':>5s} {'ckpts':>5s}  {'data files':34s} min / median / max")
e3 = {}
for rid, v in sorted(by.items()):
    vals = sorted(x['value'] for x in v)
    files = sorted({str(x.get('data')) for x in v})
    e3[rid] = {'rows': len(v), 'ckpts': len({x['ckpt'] for x in v}), 'data': files,
               'min': vals[0], 'median': vals[len(vals) // 2], 'max': vals[-1]}
    print(f"  {rid:18s} {len(v):5d} {e3[rid]['ckpts']:5d}  {','.join(files)[:34]:34s} {vals[0]:.4f} / {vals[len(vals)//2]:.4f} / {vals[-1]:.4f}")
res['E3'] = {'query': q, 'runs': len(by), 'rows': len(sel), 'by_run': e3}

# ---- E4: (run, metric, extra filter, value printed in the run's write-up, where)
E4 = [('lean-format', 'summary:P1_heldout_greedy/token_full', [], 0.948,
       'STATUS.md lean-format: token held-out 0.883 / 0.883 / 0.948'),
      ('ds-generator', 'summary:rows[0]/ladder/frozen/transfer_solved', [], 158,
       'STATUS.md ds-generator: frozen ladder solves C0 158 / 114 (rows[0] = arm c0 seed 0)'),
      ('ds-generator', 'summary:rows[1]/ladder/frozen/transfer_solved', [], 114, 'same, rows[1] = arm c0 seed 1'),
      ('state-env', 'summary:headline/S/s0/T1_solved', [], 1348,
       'run_state_env.md: Transfer solved after T1: S 1,348 / 1,389 (substitute for lean-prefilter, log.md 01:05)'),
      ('state-env', 'transfer_solved_cum', ['arm=la_T1_S_s0', 'round=8'], 1348,
       'same number from the round file via round_stats (labels.solved)')]
print('\nE4  headline numbers')
e4 = []
for rid, metric, extra, want, where in E4:
    hit = [r for r in rows if r['run_id'] == rid and r['metric'] == metric and M.match(r, extra)]
    got = [r['labels'].get('solved') if metric == 'transfer_solved_cum' else r['value'] for r in hit]
    ok = len(hit) >= 1 and all(repr(g) == repr(want) for g in got)
    e4.append({'run': rid, 'metric': metric, 'filter': extra, 'want': want, 'got': got, 'ok': ok, 'where': where,
               'source': hit[0]['source'] if hit else None})
    print(f"  {'OK  ' if ok else 'FAIL'} {rid:13s} {metric:48s} {' '.join(extra):22s} want {want!r:6s} got {got}")
res['E4'] = e4

# ---- E5
os.environ.update({'ND_OFFLINE': '1', 'ND_REGISTRY_DIR': tmp, 'ND_RUN_ID': 'acceptance-timing'})
record.set_config({'seed': 0, 'lr': 1e-3, 'data': None})
t = time.time()
for i in range(2000):
    record.record('timing', i, n=1, split='x', L=str(i % 7))
res['E5_record_ms_per_row'] = (time.time() - t) / 2000 * 1e3
res['E5_upload_s'] = [x['upload_s'] for x in e1]
print(f"\nE5  record(): {res['E5_record_ms_per_row']:.3f} ms/row (VPS); uploads on the pod: {res['E5_upload_s']} s")
json.dump(res, open(OUT, 'w'), indent=1, default=str)
print('\nwrote', os.path.relpath(OUT, ROOT))
