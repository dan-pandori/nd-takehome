"""A3b (Addendum 5, post hoc): A3 restricted to RL-phase gains. Among strict held-out members with a known sigma proof that
are NOT proved at r0 (r0 x0 evaluation rows from the bucket), AUC of the base's best-known-proof log p for "proved at r16 x0".
Per-member log p from paper/data/a3_member_values.json (a3_member_prior.py). Output paper/data/a3b_member_prior_gained.json."""
import collections, gzip, json, os, subprocess
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SCR = os.path.expanduser('~/runs/create-or-elicit-paper/scratch/coe')
BK = 'hf://buckets/dan-pandori/nd-rl/create-or-elicit/artifacts/coe'
V = json.load(open(os.path.join(ROOT, 'paper/data/a3_member_values.json')))


def fetch(rel, local):
    p = os.path.join(SCR, local)
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        subprocess.run(['flock', '/tmp/coep_dl.lock', 'hf', 'buckets', 'cp', f'{BK}/{rel}', p], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return p


def solved(tags):
    s = collections.defaultdict(bool)
    for tg in tags:
        with gzip.open(fetch(f'eval/{tg}.jsonl.gz', f'{tg}.jsonl.gz'), 'rt') as f:
            for line in f:
                r = json.loads(line)
                s[r['name']] |= bool(r.get('n_ok', 0) > 0)
    return s


def auc(pos, neg):
    return sum((1.0 if p > q else 0.5 if p == q else 0.0) for p in pos for q in neg) / (len(pos) * len(neg)) if pos and neg else None


out = {}
for lad, mem in V.items():
    arm, s = lad.rsplit('_s', 1); s = int(s)
    tags = [f'pend_{arm}_s{s}_x0e', f'pend_{arm}_s{s}_x0h'] if (arm == 'full' and s < 3) else [f'pend_{arm}_s{s}_x0']
    r0 = solved(tags)
    rows = [(m, v['logp'], v['solved_r16']) for m, v in mem.items() if not r0.get(m)]
    pos = [x for _, x, y in rows if y]; neg = [x for _, x, y in rows if not y]
    out[lad] = {'members_not_proved_at_r0': len(rows), 'gained': len(pos), 'auc_gained': auc(pos, neg),
                'proved_at_r0': sum(1 for m in mem if r0.get(m))}
    print(lad, out[lad])
json.dump(out, open(os.path.join(ROOT, 'paper/data/a3b_member_prior_gained.json'), 'w'), indent=1)
