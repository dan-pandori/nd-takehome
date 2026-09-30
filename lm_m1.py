#!/usr/bin/env python3
"""lit-measures M1: where the state base (SN base s0) finds SN EI s0's new proofs improbable.  Forward passes only, CPU.

  OMP_NUM_THREADS=2 ~/venv-cpu/bin/python lm_m1.py --ckpt /tmp/lm_m1/stage1_SN_s0.pt --ss /tmp/lm_m1/ss \
      --theorems /tmp/lm_m1/theorems.jsonl --dsum /tmp/lm_m1/d_summary_T08.json --out artifacts/lit-measures/m1

Inputs (fetch first, see the report): support-state's records `artifacts/ss/{S1,S2}*.jsonl` and
`data/sc/theorems.jsonl` (git branch origin/dan_support-state), part D's `artifacts/sf/d_summary_T08.json`
(origin/dan_support-followups), the checkpoint `state-env/ckpts/se/stage1_SN_s0.pt` (md5 ec3888d9...).

Spec: preregistration/lit-measures.md §M1.  Choices where the spec is silent (closest to support-followups part D):
  * Each proof (an ND body from the records) is turned into the environment's actions by
    `state_env.decompose(prompt, proof, canon=True)`; it is then REPLAYED through `Env(canon=True, assign=True, base=b)`
    for every base b used below: every action must apply, the attempt must close, the environment must not rename
    anything (its assigned names = ours), and `inverse(env.text)` must give back the recorded ND proof.  Any failure is
    counted and reported, and the proof is left out of the scores (listed in summary.json['replay_failures']).
  * Prompt = `tok.encode_toks(env.state_tokens())` (what `state_sample.prompt_ids` gives for lean_staten), target =
    the action tokens + <eos>.  Log p of each target token from the causal model on prompt + target (as state_train's
    loss).  Natural logs.  Temperature: log_softmax(logits / T), T = 0.8 (primary: the EI sampling temperature and the
    temperature of part D's `d_summary_T08.json` the pre-registration recounts) and T = 1.0 (secondary).
  * Name base: the environment names what a step introduces from a base (the sampler draws b ~ U[0, 32]; training used
    one random offset per proof).  As part D did for lean_seq's offset, the score is EXACTLY marginalised over the base:
    the proof at base b is a distinct token sequence, so p = sum_b p(proof_b), b = 0 .. 64 - max name index; with
    cum_b(t) = sum of step log p up to step t at base b, L(t) = logsumexp_b cum_b(t) and step t contributes L(t) - L(t-1)
    (the first name token is in step 1, so every step is on the marginalised side).  Step contributions sum to the
    proof's log p exactly (asserted).  The unmarginalised base-0 step scores are kept too (`raw_b0`).
  * Steps = the model's actions (a `have` line; a box-opening `have` up to `=> by`; an `exact`).  Part D's steps also
    had the second Or.elim branch opener, which here the environment supplies (not scored, no step).
  * Label: part D's `label` (sf_d_analysis: concentrated s2 >= 0.50 and w1 <= -6; spread s2 < 0.50 and w1 > -6; else
    mixed); s1 = w1/total, s2 = (w1+w2)/total, rest = total - w1 - w2 (w2 = 0 for a 1-step proof).
"""
import argparse, collections, glob, hashlib, json, math, os, random, statistics as stt, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import torch
import torch.nn.functional as F
from model import load_ckpt
from state_env import Env, decompose, is_name
from lean_tok import MAXN, ParseFail, inverse

S7 = ['la_transfer_' + x for x in '1108 1185 1352 198 2089 394 988'.split()]
W1_CUT, S2_CUT = -6.0, 0.50          # sf_d_analysis.py (support-followups part D)
TEMPS = (0.8, 1.0)
PRIMARY = '0.8'
N_PERM, PERM_SEED = 100_000, 0
N_E13 = {'N400000': 400_000, 'N200000': 200_000}


def label(sm):                        # verbatim rule of sf_d_analysis.label
    if sm['s2'] >= S2_CUT and sm['w1'] <= W1_CUT:
        return 'concentrated'
    if sm['s2'] < S2_CUT and sm['w1'] > W1_CUT:
        return 'spread'
    return 'mixed'


def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


# ------------------------------------------------------------------ sets
def load_sets(ss, thm_path):
    TH = {}
    for l in open(thm_path):
        if l.strip():
            r = json.loads(l); TH[r['name']] = r
    files = sorted(f for f in glob.glob(os.path.join(ss, '*.jsonl'))
                   if os.path.basename(f).startswith(('S1_', 'S2')))
    ei, base, base_ok = collections.defaultdict(dict), collections.defaultdict(dict), collections.Counter()
    ok_s1b, ok_s2b, ok_s1e = collections.Counter(), collections.Counter(), collections.Counter()
    for f in files:
        for l in open(f):
            r = json.loads(l)
            tgt = ei if r['model'] == 'ei' else base
            if r['model'] == 'base':
                base_ok[r['name']] += r['n_ok']
                (ok_s1b if os.path.basename(f).startswith('S1_') else ok_s2b)[r['name']] += r['n_ok']
            elif os.path.basename(f).startswith('S1_'):
                ok_s1e[r['name']] += r['n_ok']
            for p in r['proofs']:
                e = tgt[r['name']].setdefault(p['proof'], {'name': r['name'], 'proof': p['proof'], 'n_lines': p.get('n_lines'),
                                                           'term_size': p.get('term_size'), 'count': 0, 'src': []})
                e['count'] += p.get('count', 1); e['src'].append(f'{os.path.basename(f)}@T{r["temperature"]}')
    assert all(base_ok[n] == 0 for n in S7), 'an S theorem is reached by the base in S1/S2'
    reached = {n for n, k in base_ok.items() if k > 0}
    Lt = {n: TH[n]['L_true'] for n in TH}
    # C1: reached theorems with EI proofs, L_true 7-11; per L_true at most 5 theorems per S theorem of that L_true (seed 0)
    nS = collections.Counter(Lt[n] for n in S7)
    rng = random.Random(0)
    c1_thms, c1_pool = [], {}
    for L in range(7, 12):
        cand = sorted(n for n in reached if Lt[n] == L and ei.get(n) and n not in S7)
        k = min(5 * nS[L], len(cand))
        pick = sorted(rng.sample(cand, k)) if k else []
        c1_pool[L] = {'candidates': len(cand), 'S_theorems': nS[L], 'picked': len(pick)}
        c1_thms += pick
    recs = []
    for n in S7:
        recs += [dict(e, set='S') for e in ei[n].values()]
    for n in c1_thms:
        recs += [dict(e, set='C1') for e in ei[n].values()]
    for n in c1_thms:
        recs += [dict(e, set='C2') for e in base[n].values()]
    # C1x (post hoc, NOT pre-registered; coordinator 2026-09-30): forward-crux theorems (SN base 0 in S1's 10,000 at
    # T 0.8, SN EI >= 1 there) that the SN base DOES reach in the S2 deepening; all their EI proofs, no length sampling
    c1x_thms = sorted(n for n in ok_s1e if ok_s1e[n] > 0 and ok_s1b[n] == 0 and ok_s2b[n] > 0 and n not in S7)
    for n in c1x_thms:
        recs += [dict(e, set='C1x') for e in ei[n].values()]
    for r in recs:
        r['L_true'] = Lt[r['name']]; r['prompt'] = TH[r['name']]['prompt']
    meta = {'record_files': [os.path.basename(f) for f in files], 'S_theorems': S7, 'C1_theorems': c1_thms,
            'C1_sampling': {str(k): v for k, v in c1_pool.items()}, 'n_reached_by_base_S1_S2': len(reached),
            'C1x_theorems': c1x_thms, 'C1x_note': 'post hoc, NOT pre-registered: forward-crux (SN base 0/10,000 in S1 at T 0.8, SN EI >= 1) and reached by SN base in S2; all EI proofs',
            'C1x_L_true': dict(sorted(collections.Counter(TH[n]['L_true'] for n in c1x_thms).items())),
            'C1x_base_S2_ok': {n: ok_s2b[n] for n in c1x_thms},
            'C2_theorems_with_base_proofs': sorted({r['name'] for r in recs if r['set'] == 'C2'})}
    return recs, meta


# ------------------------------------------------------------------ replay
def shift(toks, b):
    return [f'n{int(t[1:]) + b}' if is_name(t) else t for t in toks]


def replay(r):
    """-> (list of base-0 actions, max name index, None) or (None, None, reason)."""
    try:
        steps, toks, env0 = decompose(r['prompt'], r['proof'], canon=True)
    except (ParseFail, ValueError, KeyError, IndexError, AssertionError) as e:
        return None, None, f'decompose: {e}'
    acts = [a for _, a, _ in steps]
    mx = max((int(t[1:]) for t in toks if is_name(t)), default=0)
    return acts, mx, None


def states_at(r, acts, b):
    """replay at base b in the sampler's environment; -> list of state token lists, or raise ParseFail."""
    env = Env(r['prompt'], canon=True, base=b, assign=True)
    sts = []
    for a in acts:
        sts.append(env.state_tokens())
        ok, why = env.apply(shift(a, b))
        if not ok:
            raise ParseFail(f'replay b={b}: {why}')
    if not env.done:
        raise ParseFail(f'replay b={b}: not closed')
    if env.renamed:
        raise ParseFail(f'replay b={b}: env renamed {env.renamed}')
    nd = inverse(env.text)
    if nd != r['proof']:
        raise ParseFail(f'replay b={b}: ND mismatch')
    return sts


# ------------------------------------------------------------------ scoring
@torch.no_grad()
def score_seqs(model, seqs, batch):
    """seqs: dict key -> (prompt ids, target ids).  -> key -> {T: sum log p of the target}"""
    keys = sorted(seqs, key=lambda k: len(seqs[k][0]) + len(seqs[k][1]))
    out = {}
    t0 = time.time()
    for b0 in range(0, len(keys), batch):
        ch = keys[b0:b0 + batch]
        L = max(len(seqs[k][0]) + len(seqs[k][1]) for k in ch)
        x = torch.zeros((len(ch), L), dtype=torch.long)
        for i, k in enumerate(ch):
            ids = seqs[k][0] + seqs[k][1]
            x[i, :len(ids)] = torch.tensor(ids)
        logits = model(x[:, :-1]).float()
        tgt = x[:, 1:, None]
        for T in TEMPS:
            lp = F.log_softmax(logits / T, -1).gather(-1, tgt).squeeze(-1).double()
            for i, k in enumerate(ch):
                p, q = seqs[k]
                out.setdefault(k, {})[T] = float(lp[i, len(p) - 1:len(p) + len(q) - 1].sum())
        if (b0 // batch) % 50 == 0:
            print(f'  scored {b0 + len(ch)}/{len(keys)} seqs  {time.time() - t0:.0f}s', flush=True)
    return out


@torch.no_grad()
def direct_logp(model, pid, qid, T):
    """independent check: token-by-token, prefix re-fed each time, no batching or padding."""
    s, ids = 0.0, list(pid)
    for q in qid:
        lg = model(torch.tensor([ids]))[0, -1].float()
        s += float(F.log_softmax(lg.double() / T, -1)[q]); ids.append(q)
    return s


def summarise(step_lp):
    tot = sum(step_lp)
    o = sorted(step_lp)
    w1 = o[0]; w2 = o[1] if len(o) > 1 else 0.0
    d = {'total': tot, 'w1': w1, 'w2': w2, 'rest': tot - w1 - w2,
         's1': w1 / tot if tot < 0 else 0.0, 's2': (w1 + w2) / tot if tot < 0 else 0.0,
         'worst_step': step_lp.index(w1), 'n_steps': len(step_lp)}
    d['label'] = label(d)
    return d


def perm_test(wS, wC, cname):
    wS, wC = np.array(wS), np.array(wC)
    obs = float(np.median(wC) - np.median(wS))
    allw = np.concatenate([wS, wC]); nS = len(wS)
    g = np.random.default_rng(PERM_SEED)
    ge = 0
    for _ in range(N_PERM // 1000):
        P = np.argsort(g.random((1000, len(allw))), 1)
        A = allw[P]
        st_ = np.median(A[:, nS:], 1) - np.median(A[:, :nS], 1)
        ge += int((st_ >= obs - 1e-12).sum())
    p = (ge + 1) / (N_PERM + 1)
    return {'control': cname, 'median_w1_S': float(np.median(wS)), 'median_w1_C': float(np.median(wC)), 'gap_C_minus_S': obs,
            'n_S': nS, 'n_C': len(wC), 'n_perm': N_PERM, 'seed': PERM_SEED,
            'statistic': f'median({cname} w1) - median(S w1), theorem level (best proof each); p = (#perm >= obs + 1)/(N + 1), numpy default_rng(0)',
            'p_one_sided': p,
            'verdict': ('falsified (S median above control)' if np.median(wS) > np.median(wC) else
                        'holds (gap >= 2 and p < 0.10)' if obs >= 2 and p < 0.10 else 'not met')}


def med(xs):
    return stt.median(xs) if xs else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ckpt', default='/tmp/lm_m1/stage1_SN_s0.pt')
    ap.add_argument('--ss', default='/tmp/lm_m1/ss')
    ap.add_argument('--theorems', default='/tmp/lm_m1/theorems.jsonl')
    ap.add_argument('--dsum', default='/tmp/lm_m1/d_summary_T08.json')
    ap.add_argument('--out', default='artifacts/lit-measures/m1')
    ap.add_argument('--batch', type=int, default=256)
    ap.add_argument('--reuse', default='', help='steps.jsonl of an earlier run: proofs already scored there are copied, not re-scored')
    ap.add_argument('--limit', type=int, default=0, help='debug: first N proofs per set only')
    a = ap.parse_args()
    torch.set_num_threads(int(os.environ.get('OMP_NUM_THREADS', '2')))
    os.makedirs(a.out, exist_ok=True)
    ck_md5 = md5(a.ckpt)
    model, tok, extra = load_ckpt(a.ckpt, 'cpu')
    assert tok.mode == 'lean_staten' and tok.canon and not tok.with_history
    n_params = sum(p.numel() for p in model.parameters())
    recs, meta = load_sets(a.ss, a.theorems)
    if a.limit:
        cnt = collections.Counter(); keep = []
        for r in recs:
            cnt[r['set']] += 1
            if cnt[r['set']] <= a.limit: keep.append(r)
        recs = keep
    print({s: sum(r['set'] == s for r in recs) for s in ('S', 'C1', 'C2', 'C1x')}, 'proofs', flush=True)

    # ---- replay + build the scoring jobs (identical (state, action) sequences scored once)
    fails, seqs, plan = [], {}, []
    reuse = {}
    if a.reuse and os.path.exists(a.reuse):
        for l in open(a.reuse):
            o = json.loads(l); reuse[(o['name'], o['proof'])] = o
    reused_rows = []
    for i, r in enumerate(recs):
        if (r['name'], r['proof']) in reuse:
            o = dict(reuse[(r['name'], r['proof'])]); o['set'] = r['set']; reused_rows.append(o); continue
        acts, mx, why = replay(r)
        if acts is None:
            fails.append({'set': r['set'], 'name': r['name'], 'proof': r['proof'], 'why': why}); continue
        bases = list(range(0, MAXN - mx + 1))
        per_b = []
        try:
            for b in bases:
                sts = states_at(r, acts, b)
                ks = []
                for st, act in zip(sts, acts):
                    pid = tuple(tok.encode_toks(st)); qid = tuple(tok.encode_toks(shift(act, b)) + [tok.eos])
                    seqs.setdefault((pid, qid), (list(pid), list(qid))); ks.append((pid, qid))
                per_b.append(ks)
        except (ParseFail, ValueError, KeyError, IndexError) as e:
            fails.append({'set': r['set'], 'name': r['name'], 'proof': r['proof'], 'why': str(e)}); continue
        plan.append((i, acts, mx, bases, per_b))
    n_tot_jobs = sum(len(b) * len(p[4][0]) for p in plan for b in [p[3]])
    print(f'replay: {len(plan)} ok, {len(fails)} failed; {n_tot_jobs} (proof, base, step) jobs -> {len(seqs)} distinct sequences',
          flush=True)
    res = score_seqs(model, seqs, a.batch)

    # ---- per proof
    rows = list(reused_rows)
    print(f'reused {len(reused_rows)} proofs from {a.reuse}', flush=True)
    for i, acts, mx, bases, per_b in plan:
        r = recs[i]
        o = {k: r[k] for k in ('set', 'name', 'L_true', 'n_lines', 'term_size', 'count', 'src', 'proof')}
        o.update({'n_steps': len(acts), 'max_name_b0': mx, 'n_bases': len(bases),
                  'actions_b0': [' '.join(x) for x in acts],
                  'step_kind': [('exact' if x[0] == 'exact' else 'have:' + (
                      'box' if x[x.index(':=') + 1] == '(' else 'orelim' if x[x.index(':=') + 1] == 'Or.elim'
                      else 'prem' if x[x.index(':=') + 1].startswith('h') else x[x.index(':=') + 1] if not is_name(x[x.index(':=') + 1])
                      else 'name')) for x in acts]})
        for T in TEMPS:
            M = torch.tensor([[res[k][T] for k in ks] for ks in per_b], dtype=torch.float64)   # [base, step]
            cum = M.cumsum(1)
            Lc = torch.logsumexp(cum, 0)
            contrib = torch.diff(Lc, prepend=torch.zeros(1, dtype=Lc.dtype)).tolist()
            assert abs(sum(contrib) - float(Lc[-1])) < 1e-6
            sm = summarise(contrib)
            sm['step_lp'] = [round(v, 4) for v in contrib]
            raw = M[0].tolist()
            sm['raw_b0'] = dict({k: v for k, v in summarise(raw).items()}, step_lp=[round(v, 4) for v in raw])
            sm['sampler_mix_logp'] = float(torch.logsumexp(cum[:min(33, len(bases)), -1], 0) - math.log(min(33, len(bases))))
            o[f'T{T}'] = sm
        o['worst_step_kind'] = o['step_kind'][o[f'T{PRIMARY}']['worst_step']]
        rows.append(o)

    # ---- sanity: step sums vs direct token-by-token log p of the whole action sequence
    sanity = []
    rng = random.Random(0)
    for idx in rng.sample(range(len(plan)), min(4, len(plan))):  # (on a --reuse run: among the newly scored proofs)
        i, acts, mx, bases, per_b = plan[idx]
        for b in sorted({0, min(3, bases[-1])}):
            sts = states_at(recs[i], acts, b)
            for T in TEMPS:
                d = sum(direct_logp(model, tok.encode_toks(st), tok.encode_toks(shift(ac, b)) + [tok.eos], T)
                        for st, ac in zip(sts, acts))
                s = sum(res[k][T] for k in per_b[b])
                sanity.append({'name': recs[i]['name'], 'set': recs[i]['set'], 'base': b, 'T': T, 'batched_step_sum': s,
                               'direct_tokenwise': d, 'abs_diff': abs(s - d)})
    print('sanity max |diff|', max(x['abs_diff'] for x in sanity), flush=True)

    with open(os.path.join(a.out, 'steps.jsonl'), 'w') as f:
        for o in rows:
            f.write(json.dumps(o, ensure_ascii=False) + '\n')

    # ---- analysis
    Tk = f'T{PRIMARY}'
    ln = {k: math.log(3 / v) for k, v in N_E13.items()}

    def best_of(set_, T):
        b = {}
        for o in rows:
            if o['set'] == set_ and (o['name'] not in b or o[T]['total'] > b[o['name']][T]['total']):
                b[o['name']] = o
        return b

    summary = {'model': {'ckpt': 'state-env ckpts/se/stage1_SN_s0.pt', 'md5': ck_md5, 'params': n_params,
                         'format': tok.mode, 'training': extra.get('args', {})},
               'spec': 'preregistration/lit-measures.md §M1', 'primary_temperature': PRIMARY,
               'choices': __doc__.split('Choices where the spec is silent (closest to support-followups part D):')[1].strip(),
               'sets_meta': meta, 'replay_failures': fails, 'n_replay_failures': len(fails),
               'n_distinct_sequences_scored': len(seqs), 'sanity_direct_vs_batched': sanity, 'by_T': {}}
    dsum = json.load(open(a.dsum))
    d29 = [x['w1'] for x in dsum['primary']['rows']]
    for T in (f'T{t}' for t in TEMPS):
        out = {'sets': {}}
        best = {s: best_of(s, T) for s in ('S', 'C1', 'C2', 'C1x')}
        for s in ('S', 'C1', 'C2', 'C1x'):
            rs = [o for o in rows if o['set'] == s]
            bs = list(best[s].values())
            out['sets'][s] = {
                'n_proofs': len(rs), 'n_theorems': len(bs),
                'all': {'total_med': med([o[T]['total'] for o in rs]), 'w1_med': med([o[T]['w1'] for o in rs]),
                        's2_med': med([o[T]['s2'] for o in rs]), 'steps_med': med([o['n_steps'] for o in rs]),
                        'labels': dict(collections.Counter(o[T]['label'] for o in rs))},
                'best': {'total_med': med([o[T]['total'] for o in bs]), 'w1_med': med([o[T]['w1'] for o in bs]),
                         'w2_med': med([o[T]['w2'] for o in bs]), 'rest_med': med([o[T]['rest'] for o in bs]),
                         's1_med': med([o[T]['s1'] for o in bs]), 's2_med': med([o[T]['s2'] for o in bs]),
                         'steps_med': med([o['n_steps'] for o in bs]),
                         'labels': dict(collections.Counter(o[T]['label'] for o in bs)),
                         'worst_step_kind': dict(collections.Counter(o['step_kind'][o[T]['worst_step']] for o in bs)),
                         'raw_b0_w1_med': med([o[T]['raw_b0']['w1'] for o in bs])}}
        out['S_rows'] = [{'name': n, 'L_true': o['L_true'], 'n_lines': o['n_lines'], 'term_size': o['term_size'],
                          'n_ei_proofs': sum(1 for x in rows if x['set'] == 'S' and x['name'] == n),
                          'n_steps': o['n_steps'], 'total': o[T]['total'], 'w1': o[T]['w1'], 'w2': o[T]['w2'],
                          'rest': o[T]['rest'], 's1': o[T]['s1'], 's2': o[T]['s2'], 'label': o[T]['label'],
                          'worst_step_kind': o['step_kind'][o[T]['worst_step']],
                          'worst_action_b0': o['actions_b0'][o[T]['worst_step']], 'raw_b0_w1': o[T]['raw_b0']['w1']}
                         for n, o in sorted(best['S'].items(), key=lambda kv: (kv[1]['L_true'], kv[0]))]
        # E1.1
        labs = collections.Counter(x['label'] for x in out['S_rows'])
        nc = labs['concentrated']
        out['E1.1'] = {'labels': dict(labs), 'concentrated': nc, 'of': len(out['S_rows']),
                       'verdict': 'holds (>=5/7)' if nc >= 5 else 'falsified (<=3/7)' if nc <= 3 else 'neither (4/7)'}
        # E1.2 (and the same test against C1x, post hoc)
        for cs, key in (('C1', 'E1.2'), ('C1x', 'E1.2_C1x_not_preregistered')):
            out[key] = perm_test([o[T]['w1'] for o in best['S'].values()], [o[T]['w1'] for o in best[cs].values()], cs)
        # E1.3
        e13 = {'thresholds': ln}
        for s in ('S', 'C1', 'C1x'):
            w = [o[T]['w1'] for o in best[s].values()]
            e13[s] = {k: {'below': sum(x < v for x in w), 'of': len(w), 'frac': sum(x < v for x in w) / len(w)} for k, v in ln.items()}
        e13['partD_29'] = {k: {'below': sum(x < v for x in d29), 'of': len(d29), 'frac': sum(x < v for x in d29) / len(d29)}
                           for k, v in ln.items()}
        e13['partD_field'] = f'{os.path.basename(a.dsum)} primary.rows[].w1 (WP base s0, T 0.8, best EI proof per survivor, rounded to 0.01)'
        e13['verdict_S_N400000'] = 'holds (>=4/7)' if e13['S']['N400000']['below'] >= 4 else 'not met'
        out['E1.3'] = e13
        summary['by_T'][T] = out
    json.dump(summary, open(os.path.join(a.out, 'summary.json'), 'w'), indent=1, ensure_ascii=False)
    write_report(summary, os.path.join(a.out, 'report.txt'))
    print(open(os.path.join(a.out, 'report.txt')).read())


def write_report(S, path):
    m = S['model']; tr = m['training']
    L = [f"MODEL: SN base s0 = {m['ckpt']}  md5 {m['md5']}  {m['params']:,} params  format {m['format']}  "
         f"from scratch on {tr.get('data')} ({tr.get('steps')} steps x {tr.get('recs')} proofs, cap {tr.get('cap')}, seed {tr.get('seed')})",
         f"Scored in Env(canon=True, assign=True). Logs are NATURAL logs (nats). log p exactly marginalised over the name base (part D's rule).",
         f"Primary temperature T {S['primary_temperature']} (log_softmax(logits/0.8)): the SN EI proofs were sampled at T 0.8 and the part D file this pre-registration",
         "  recounts (d_summary_T08.json) is part D's T 0.8 scoring.  NOTE: part D's own PRIMARY was T 1.0 (scored at T 1.0); T 1.0 is reported below as secondary.",
         f"C1x (post hoc, NOT pre-registered): {len(S['sets_meta']['C1x_theorems'])} forward-crux theorems reached by the base only in S2; L_true {S['sets_meta']['C1x_L_true']}.",
         f"Replay failures: {S['n_replay_failures']}.  Distinct (state, action) sequences scored: {S['n_distinct_sequences_scored']:,}.  "
         f"Sanity (batched step sums vs token-by-token direct): max |diff| {max(x['abs_diff'] for x in S['sanity_direct_vs_batched']):.2e} "
         f"over {len(S['sanity_direct_vs_batched'])} (proof, base, T) checks.",
         f"C1 theorems ({len(S['sets_meta']['C1_theorems'])}): sampling per L_true {S['sets_meta']['C1_sampling']}", '']
    for T in (f"T{S['primary_temperature']}", *[k for k in S['by_T'] if k != f"T{S['primary_temperature']}"]):
        o = S['by_T'][T]
        L.append(f'==================== {T} ' + ('(primary)' if T == f"T{S['primary_temperature']}" else '(secondary)'))
        L.append('S: best (highest total) EI proof per theorem')
        L.append(f"{'name':18s} L lines term nEI steps   total     w1     w2    rest    s1    s2  label         worst step (base-0 action)")
        for x in o['S_rows']:
            L.append(f"{x['name']:18s} {x['L_true']:2d} {x['n_lines']:4d} {x['term_size']:4d} {x['n_ei_proofs']:3d} {x['n_steps']:5d} "
                     f"{x['total']:7.2f} {x['w1']:6.2f} {x['w2']:6.2f} {x['rest']:7.2f} {x['s1']:5.2f} {x['s2']:5.2f}  {x['label']:12s}  "
                     f"{x['worst_step_kind']}: {x['worst_action_b0'][:70]}")
        L.append('')
        L.append('set  proofs thms | best/thm: total med  w1 med  w2 med  rest med  s2 med  steps | labels(best)  | all proofs: w1 med labels')
        for s, d in o['sets'].items():
            b = d['best']; al = d['all']
            f = lambda v: f'{v:7.2f}' if v is not None else '    n/a'
            L.append(f"{s:4s} {d['n_proofs']:6d} {d['n_theorems']:4d} | {f(b['total_med'])} {f(b['w1_med'])} {f(b['w2_med'])} "
                     f"{f(b['rest_med'])} {f(b['s2_med'])} {b['steps_med']} | {b['labels']} | {f(al['w1_med'])} {al['labels']}")
        e1, e2, e3 = o['E1.1'], o['E1.2'], o['E1.3']
        L.append('')
        L.append(f"E1.1 concentrated {e1['concentrated']}/{e1['of']}  labels {e1['labels']}  -> {e1['verdict']}")
        for key, tag in (('E1.2', 'E1.2 '), ('E1.2_C1x_not_preregistered', 'E1.2x (post hoc, not pre-registered)')):
            e2 = o[key]
            L.append(f"{tag} median w1 S {e2['median_w1_S']:.2f}  {e2['control']} {e2['median_w1_C']:.2f}  gap {e2['gap_C_minus_S']:.2f}  "
                     f"one-sided perm p {e2['p_one_sided']:.4f} ({e2['n_perm']:,} perms, seed {e2['seed']}, n {e2['n_S']} vs {e2['n_C']})  -> {e2['verdict']}")
        for k, v in e3['thresholds'].items():
            L.append(f"E1.3 w1 < ln(3/{k[1:]}) = {v:.2f}:  S {e3['S'][k]['below']}/{e3['S'][k]['of']}  C1 {e3['C1'][k]['below']}/{e3['C1'][k]['of']}  "
                     f"C1x(post hoc) {e3['C1x'][k]['below']}/{e3['C1x'][k]['of']}  "
                     f"part D {e3['partD_29'][k]['below']}/{e3['partD_29'][k]['of']}")
        L.append(f"     S at N=400,000 -> {e3['verdict_S_N400000']};  part D field: {e3['partD_field']}")
        L.append('')
    open(path, 'w').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
