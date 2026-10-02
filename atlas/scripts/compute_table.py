"""Compute behind each re-score arm (AGENT_POLICY: GPU-seconds + GPU type, generated tokens, attempts, training steps /
tokens, Lean checks), derived from the job logs in artifacts/atlas/logs/ (the scripts' own registry rows are in
hf://buckets/dan-pandori/nd-rl/registry/evidence-atlas/). Per read:
  gpu_seconds   = eval_set's 'generated N proofs in Xs' (sampling with pipelined Lean judging; GPU wall time of the job)
  gen_tokens    = sampler 'rowsteps' (decode steps summed over live rows)
  attempts      = sampler 'rows'
  lean_checks   = lean_gate 'lean on N texts' (distinct texts that reached Lean after the parser / prefilter)
Training steps / tokens are 0 (read-outs only). GPU: NVIDIA GeForce RTX 3090, two jobs per card for the max_new 512 reads.
Writes atlas/data/compute_rescore.csv; prints a per-arm table."""
import csv, glob, json, os, re, collections
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
L = os.path.join(ROOT, 'artifacts', 'atlas', 'logs')
rows, arm = [], collections.defaultdict(lambda: collections.Counter())
for f in sorted(glob.glob(os.path.join(L, '*.log'))):
    m = re.match(r'(c0fz|c0t1|k12fz|k12t1)_s(\d)__(tb72|dev|h250)(_mn1024)?\.log$', os.path.basename(f))
    if not m:
        continue
    t = open(f).read()
    g = re.search(r'generated (\d+) proofs in (\d+)s', t)
    gs = re.search(r'^genstats (\{.*\})$', t, re.M)
    lc = re.findall(r'lean on (\d+) texts', t)
    if not (g and gs):
        continue
    gs = json.loads(gs.group(1))
    r = dict(arm=m.group(1), seed=m.group(2), read=m.group(3), max_new=1024 if m.group(4) else 512,
             gpu_type='NVIDIA GeForce RTX 3090', gpu_seconds=int(g.group(2)), attempts=gs['rows'], gen_tokens=gs['rowsteps'],
             lean_checks=sum(map(int, lc)), train_steps=0, train_tokens=0)
    rows.append(r)
    arm[(r['arm'], r['max_new'])].update({k: r[k] for k in ('gpu_seconds', 'attempts', 'gen_tokens', 'lean_checks')})
with open(os.path.join(ROOT, 'atlas', 'data', 'compute_rescore.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(f'{"arm":6s} {"max_new":>7s} {"GPU-s":>7s} {"attempts":>9s} {"gen tokens":>12s} {"Lean checks":>11s}')
for (a, mn), c in sorted(arm.items()):
    print(f'{a:6s} {mn:7d} {c["gpu_seconds"]:7d} {c["attempts"]:9d} {c["gen_tokens"]:12d} {c["lean_checks"]:11d}')
