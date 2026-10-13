"""Harness controls for C5 (not pre-registered; added so that C5's "0 accepted" can be read).

Run on the same pod, dump and checker as C5 (review_coe/rlean.py, Lean 4.34.1 via LEAN_BIN):
- positive: 400 texts the run's in-loop Lean accepted (lean True), reservoir-sampled with seed 0, with their own
  theorem; all should be accepted;
- negative: the same 400 texts, each paired with the theorem of another sampled row with a different statement; all
  (bar coincidences) should be rejected.
Usage: python3 paper/scripts/c5_control.py <dump.jsonl.gz> <out.json>"""
import gzip, json, os, random, sys, time
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'review_coe'))
import rlean


def main():
    fn, out = sys.argv[1], sys.argv[2]
    rng = random.Random(0); res, seen = [], 0
    with gzip.open(fn, 'rt') as f:
        for l in f:
            r = json.loads(l)
            if r.get('lean') is True:
                seen += 1
                if len(res) < 400:
                    res.append((r['prompt'], r['lean_text']))
                elif rng.random() < 400 / seen:
                    res[rng.randrange(400)] = (r['prompt'], r['lean_text'])
    pos = res
    prompts = [p for p, _ in pos]
    neg = []
    for i, (p, t) in enumerate(pos):
        j = (i + 1) % len(pos)
        while prompts[j] == p:
            j = (j + 1) % len(pos)
        neg.append((prompts[j], t))
    t0 = time.time()
    rp = rlean.check_robust(pos, per_file=150, size=False)
    rn = rlean.check_robust(neg, per_file=150, size=False)
    summary = {'dump': os.path.basename(fn), 'lean_true_rows_seen': seen,
               'positive_n': len(pos), 'positive_accepted': sum(1 for x in rp if x[0]),
               'positive_rejected_examples': [(p, t[:400], x[1]) for (p, t), x in zip(pos, rp) if not x[0]][:10],
               'negative_n': len(neg), 'negative_accepted': sum(1 for x in rn if x[0]),
               'negative_accepted_examples': [(p, t[:400]) for (p, t), x in zip(neg, rn) if x[0]][:10],
               'lean_bin': rlean.LEAN_BIN, 'seconds': time.time() - t0}
    json.dump(summary, open(out, 'w'), indent=1)
    print('positive', summary['positive_accepted'], '/', summary['positive_n'],
          'negative accepted', summary['negative_accepted'], '/', summary['negative_n'], flush=True)


if __name__ == '__main__':
    main()
