"""C5/C6/C7 Lean spot-check with negative controls. Own Lean driver (nd2lean.translate used only for ND->Lean text).
Positives: random accepted sampled proofs (fixed seed 20261002) from the raw reads of each claim. Negatives (Lean-source
level, each guaranteed invalid): (a) wrong theorem: proof body paired with another sample's statement (different
statement); (b) final `exact` target's defining `have` line removed (unbound name); (c) goal replaced by `(P ∧ (¬P))`.
Every negative must be rejected, else the harness is invalid. Any error message => rejected; 'sorry' => rejected."""
import json, os, sys, random, re, subprocess, tempfile, glob, hashlib
sys.path.insert(0, '/home/dan/work/claim-audit')
from nd2lean import translate
H = os.path.expanduser('~'); LEAN = H + '/.elan/bin/lean'
OUT = '/home/dan/work/claim-audit/audit/out/'
rng = random.Random(20261002)

def collect(files, n, name_filter=None):
    pool = []
    for f in files:
        for l in open(f):
            r = json.loads(l)
            if r.get('n_ok', 0) > 0 and r['proofs'] and (name_filter is None or r['name'] in name_filter):
                pool.append((os.path.basename(f), r['name'], r['prompt'], r['proofs'][0]))
    return rng.sample(pool, min(n, len(pool))), len(pool)

def run_lean(srcs):
    d = tempfile.mkdtemp(prefix='ca_c567_'); text = ''; spans = []
    for k, s in enumerate(srcs):
        a = text.count('\n') + 1; text += s.replace('theorem t ', f'theorem t{k} ', 1) + '\n'; spans.append((a, text.count('\n')))
    fn = d + '/all.lean'; open(fn, 'w').write(text)
    p = subprocess.run(['flock', '/tmp/ca_lean.lock', 'nice', '-n', '10', LEAN, '-DmaxErrors=100000', fn], capture_output=True, text=True)
    outp = p.stdout + p.stderr; bad = {}; unattributed = 0
    for m in re.finditer(r'^[^\n]*?:(\d+):(\d+): (error|warning)[^:]*: ([^\n]*)', outp, re.M):
        line = int(m.group(1)); kind = m.group(3); msg = m.group(4)
        if kind == 'warning' and 'sorry' not in msg: continue
        ks = [k for k, (a, b) in enumerate(spans) if a <= line <= b]
        if ks: bad.setdefault(ks[0], []).append(msg[:80])
        else: unattributed += 1
    n_err_lines = len(re.findall(r': error', outp))
    return [k not in bad for k in range(len(srcs))], unattributed, p.returncode, n_err_lines, sum(len(v) for v in bad.values())

def mutate(src, other_src, kind):
    head, body = src.split(':= by\n', 1)
    if kind == 'wrong_thm':
        return other_src.split(':= by\n', 1)[0] + ':= by\n' + body
    if kind == 'drop_final_have':
        lines = body.split('\n'); m = re.search(r'exact n(\d+)\s*$', body.rstrip())
        tgt = f'  have n{m.group(1)} :'
        idx = [i for i, l in enumerate(lines) if l.startswith(tgt)]
        if not idx: return None
        i = idx[0]; j = i + 1
        while j < len(lines) and lines[j].startswith('    '): j += 1   # drop the whole (possibly multi-line) have block
        return head + ':= by\n' + '\n'.join(lines[:i] + lines[j:])
    if kind == 'false_goal':
        # statement = 'theorem t (P Q R S : Prop) <hyps> : <concl>'; hyps are '(hK : F)'; cut at the last top-level ' : '
        depth = 0; cut = None
        for k, ch in enumerate(head):
            if ch == '(': depth += 1
            elif ch == ')': depth -= 1
            elif ch == ':' and depth == 0: cut = k
        return head[:cut] + ': (P ∧ (¬P)) := by\n' + body

SETS = {
 'C5': (sorted(glob.glob(H + '/work/trajectory/artifacts/tj/eval/s?_r8__*_x0.jsonl')) + sorted(glob.glob(H + '/work/trajectory-cap6/artifacts/tj6/eval/s?_r8__*_x0.jsonl'))
        + sorted(glob.glob(H + '/work/trajectory/artifacts/tj/eval/s?_pend__*_x0.jsonl')), 40),
 'C6': (sorted(glob.glob(H + '/work/rl-from-ckpt/artifacts/rfc/eval/s?_p*_r8__*_x1.jsonl')), 40),
 'C7': (sorted(glob.glob(H + '/work/lit-measures/artifacts/lit-measures/m2/heldout_i0_d100*.jsonl')), 40),
}
report = {}
for claim, (files, n) in SETS.items():
    samp, npool = collect(files, n)
    if claim == 'C6':   # add the one theorem only early starts solve (textbook_35e75d37...) if present
        extra, _ = collect(files, 10, {'textbook_35e75d37fcd6e6fc7dfe'}); samp += extra
    srcs, meta, terr = [], [], 0
    for f, name, prompt, proof in samp:
        try: srcs.append(translate(prompt, proof, require_all_pr=False)); meta.append((f, name))
        except Exception as e: terr += 1; meta.append((f, name, 'TRANSLATION ' + str(e)[:60]))
    pos_ok, un, rc, nerr, attr = run_lean(srcs)
    negs = []
    for i, s in enumerate(srcs):
        j = (i + 1) % len(srcs)
        while srcs[j].split(':= by')[0] == s.split(':= by')[0]: j = (j + 1) % len(srcs)
        for kind in ('wrong_thm', 'drop_final_have', 'false_goal'):
            m = mutate(s, srcs[j], kind)
            if m is not None: negs.append((kind, i, m))
    neg_ok, un2, rc2, nerr2, attr2 = run_lean([m for _, _, m in negs])
    by = {}
    for (kind, i, _), ok in zip(negs, neg_ok): by.setdefault(kind, [0, 0]); by[kind][0] += 1; by[kind][1] += (not ok)
    report[claim] = dict(pool_size=npool, sampled=len(samp), translation_errors=terr, pos_accepted=sum(pos_ok), pos_total=len(srcs),
                         pos_rejected=[meta[k] for k, ok in enumerate(pos_ok) if not ok], unattributed_pos=un, neg_rejected_by_kind=by,
                         neg_rejected=sum(not x for x in neg_ok), neg_total=len(negs), unattributed_neg=un2,
                         lean_err_lines=nerr2, attributed_errs=attr2, files_md5={os.path.basename(f): hashlib.md5(open(f, 'rb').read()).hexdigest()[:8] for f in sorted({m[0] for m in meta}) for f in [next(x for x in files if os.path.basename(x) == f)]})
    r = report[claim]
    print(f"{claim}: pool {npool} accepted proofs; sampled {len(samp)}; translation errors {terr}; Lean accepted {r['pos_accepted']}/{r['pos_total']} "
          f"(unattributed {un}); negatives rejected {r['neg_rejected']}/{r['neg_total']} by kind {by} (unattributed {un2})")
json.dump(report, open(OUT + 'c567_lean.json', 'w'), indent=1)
