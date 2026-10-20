#!/usr/bin/env python3
"""Calibration programs in the same RASP-L interpreter (run kalmar-complexity).

  python3 kalmar_complexity/programs/rasp/calibration.py [--cases 300] [--seed 0] [--out calibration.json]

Each task: a RASP-L (or flagged RASP) next-token / per-position program, a plain-Python reference, and a randomised
test (>= 200 cases).  Autoregressive tasks are checked teacher-forced at every output position (equivalent to
autoregressive decoding when every prediction is right).  Programs marked "Zhou et al." are ported from the paper's
listings (arXiv 2310.16028, appendix), with the published line count recorded.

Tasks: copy (unique tokens; induction head), reverse (unique tokens: RASP-L; with repeats: flagged index arithmetic),
sort (unique: Zhou's one-liner; with repeats: flagged count comparison), count (Zhou's counting task),
histogram (causal), mode (Zhou), parity (no scratchpad: flagged count arithmetic; Zhou's scratchpad format: RASP-L),
addition (Zhou's reverse-order, index-hinted program), eval (truth value of a K12 formula under a valuation prefix),
taut (truth-table validity of a sequent).
"""
import argparse, json, os, random, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rasp as R
from rasp import (tokens, indices, tok_map, seq_map, select, aggr, sel_width, kqv, shift_right, index_select,
                  where, mask, full, equals, lt, leq, gt, TRUE, kflag, pfn, induct, induct_prev, firsts, lasts,
                  has_seen, num_prev, maximum, cumsum)

START, END, SEP = -1, -2, -3


# ================================================================== programs
# COPY BEGIN
def copy_prog():
    seq = tokens()
    return induct(seq, seq, offset=1)
# COPY END


# REVERSE BEGIN
def reverse_prog():
    seq = tokens()
    prev = index_select(seq, firsts(seq, seq) - 1)
    return seq_map(prev, seq, lambda p, s: END if p == START else p)
# REVERSE END


# REVERSE_REP BEGIN
def reverse_rep_prog():
    seq, idx = tokens(), indices()
    e = firsts(seq, full(seq, END))
    src = seq_map(idx, e, lambda q, e: 2 * e - q - 1, vt='index', flag='index arithmetic: 2e - q - 1')
    prev = index_select(seq, src)
    return seq_map(prev, src, lambda p, s: END if s <= 0 else p)
# REVERSE_REP END


# SORT BEGIN
def sort_prog():
    x = tokens()
    return kqv(x, x, x, gt, default=END, reduction='min')
# SORT END


# SORT_REP BEGIN
def sort_rep_prog():
    x, idx = tokens(), indices()
    out = has_seen(x, full(x, SEP))
    inp = mask(x, ~out, -9)
    n_in = sel_width(select(inp, x, equals))
    n_out = sel_width(select(mask(x, out, -9), x, equals))
    again = seq_map(n_out, n_in, lambda a, b: int(a < b), flag='count comparison (two selector widths)')
    bigger = kqv(inp, x, inp, gt, default=END, reduction='min')
    return seq_map(seq_map(again, x, lambda a, t: t if (a and t >= 0) else -100), bigger,
                   lambda a, b: a if a != -100 else b)
# SORT_REP END


# COUNT BEGIN
def count_prog():
    seq, idx = tokens(), indices()
    start_idx = kqv(seq, full(seq, START), idx, equals, default=0, reduction='max')
    start_nums = index_select(seq, start_idx + 1)
    end_nums = index_select(seq, start_idx + 2)
    pred_first_pos = seq_map(idx, start_idx + 2, lambda a, b: int(a == b))
    pred_final_pos = (~pred_first_pos) & (seq == end_nums)
    return where(pred_first_pos, start_nums, where(pred_final_pos, full(seq, END), seq + 1))
# COUNT END


# HIST BEGIN
def hist_prog():
    seq = tokens()
    return num_prev(seq, seq)
# HIST END


# MODE BEGIN
def mode_prog():
    x = tokens()
    num_prev_matching = sel_width(select(x, x, equals))
    idx = kqv(num_prev_matching, maximum(num_prev_matching), indices(), equals, reduction='max')
    return index_select(x, idx)
# MODE END


# PARITY BEGIN
def parity_prog():
    seq = tokens()
    ones = sel_width(select(seq, seq, kflag(lambda k: k == 1, 'one')))
    return tok_map(ones, lambda c: c % 2, flag='arithmetic on a selector width (count mod 2)')
# PARITY END

PLUS_S, MINUS_S, GT_S = 2, 3, 4                   # parity scratchpad symbols; hints are letters 10..90


# PARITY_SP BEGIN
def parity_sp_prog():
    seq, idx = tokens(), indices()
    out = has_seen(seq, full(seq, GT_S))
    hint_out = mask(seq, out & (seq >= 10), 0)
    last_hint = aggr(select(hint_out, hint_out, kflag(lambda k: k != 0, 'hint')), hint_out, default=-50,
                     reduction='max', label='last output hint')
    last_pos = firsts(seq, last_hint)
    one_pos = mask(idx, (seq == 1) & ~out, -1)
    nxt_one = aggr(select(one_pos, last_pos + 1, gt), one_pos, default=-1, reduction='min')
    nxt_hint = index_select(seq, nxt_one - 1, default=END)
    flipped = tok_map(shift_right(seq, 1), lambda s: MINUS_S if s == PLUS_S else PLUS_S)
    return where(seq == GT_S, full(seq, PLUS_S), where(seq >= 10, flipped, nxt_hint))
# PARITY_SP END


# ---- Zhou et al.'s addition (reverse order, index hints), listing "next_tok_rev_addition_hinted"
START_PROMPT, PLUS, EQUALS_SIGN, END_RESPONSE, NONE = -1, -2, -3, -5, -88


# ADDITION BEGIN
def mask_between_tokens(seq, tok0, tok1):
    seen_tok0 = has_seen(seq, full(seq, tok0))
    seen_tok1 = has_seen(seq, full(seq, tok1))
    ind_between = seq_map(seen_tok0, seen_tok1, lambda a, b: int(bool(a) and not b))
    return ind_between


def _add_safe(x, y):
    return x + y if (x >= 0) else x


def addition_prog():
    seq = tokens()
    prompt_mask = tok_map(has_seen(seq, full(seq, EQUALS_SIGN)), lambda h: 1 - h)
    second_summand_mask = mask_between_tokens(seq, PLUS, EQUALS_SIGN)
    prompt = mask(seq, prompt_mask)
    other_summand_digit = induct(k=prompt, q=shift_right(prompt, 1), offset=1)
    pairsums = seq_map(seq, other_summand_digit, _add_safe)
    pairsums = mask(pairsums, second_summand_mask, NONE)
    pairsums_nh = mask(pairsums, (seq >= 0), NONE)
    curr_output_digit = shift_right(seq, 1)
    curr_pairsum = induct(pairsums, shift_right(seq, 2), offset=1)
    next_pairsum = induct(pairsums, seq, offset=1)
    direct_carry = curr_pairsum > 9
    indirect_carry = (curr_pairsum == 9) & (curr_output_digit == 0)
    next_tok_gets_carry = direct_carry | indirect_carry
    final_hint = full(seq, -100)
    first_hint = induct_prev(seq, full(seq, EQUALS_SIGN), offset=-2)
    next_hint = shift_right(seq, 1) + 1
    eos = (next_hint > final_hint)
    next_tok = next_pairsum
    next_tok = next_tok + next_tok_gets_carry
    next_tok = tok_map(next_tok, lambda v: v % 10)
    next_tok_is_index_hint = (seq > -100)
    eos = (eos & next_tok_is_index_hint)
    next_tok = where(next_tok_is_index_hint, next_hint, next_tok)
    next_tok = where(eos, full(seq, END_RESPONSE), next_tok)
    next_tok = where((seq == EQUALS_SIGN), first_hint, next_tok)
    return next_tok
# ADDITION END
ADD_PUBLISHED_LINES = None                      # filled in from the paper's listing below


# ---- eval / taut on K12 formulas (token ids from kalmar_policy)
import kalmar_policy as KP
T = KP.T
EQ_T, ONE_T, ZERO_T = 120, 121, 122             # '=', '1', '0' for the valuation prefix
H_EVAL = 9


# EVAL BEGIN
def eval_prog(H=H_EVAL):
    tok, idx = tokens(), indices()
    opens = sel_width(select(tok, tok, kflag(lambda k: k == KP.LP, '(')))
    closes = sel_width(select(tok, tok, kflag(lambda k: k == KP.RP, ')')))
    D = seq_map(opens, closes, lambda a, b: a - b, vfn=np.subtract, flag='count arithmetic: Dyck depth = #( - #)')
    kcon = seq_map(D, tok, lambda d, t: d if t in KP.CONN_T else -1)
    qcl = seq_map(D, tok, lambda d, t: d + 1 if t == KP.RP else -2)
    opPos = kqv(kcon, qcl, idx, equals, default=-1, reduction='max')
    opc = seq_map(tok, index_select(tok, opPos, default=0),
                  lambda t, o: KP.ATOM_T.get(t, KP.CONN_T.get(o, 0) if t == KP.RP else 0))
    lc = seq_map(opPos, opc, lambda p, o: p - 1 if o in (7, 8, 9) else -1, vt='index')
    val = seq_map(index_select(tok, firsts(tok, tok) + 2, default=0), tok,
                  lambda v, t: int(v == ONE_T) if t in KP.ATOM_T and t != KP.FALSE_T else 0)
    code = seq_map(opc, val, lambda o, v: o * 2 + v)                 # atoms keep their value
    gsel = select(idx, lc, equals)
    for _ in range(H):
        val = seq_map(seq_map(code, shift_right(val, 1), lambda c, r: c * 2 + r), aggr(gsel, val, reduction='max'),
                      _vstep)
    return tok_map(shift_right(val, 1), lambda v: ONE_T if v else ZERO_T)
# EVAL END


def _vstep(a, l):
    o, v, r = a // 4, (a // 2) % 2, a % 2
    if 1 <= o <= 5:
        return v
    return _vapply(o, l, r)


def _vapply(o, l, r):
    if o == 6:
        return int(not r)
    if o == 7:
        return int(l and r)
    if o == 8:
        return int(l or r)
    if o == 9:
        return int((not l) or r)
    return 0


# TAUT BEGIN
def taut_prog(H=H_EVAL):
    tok, idx = tokens(), indices()
    opens = sel_width(select(tok, tok, kflag(lambda k: k == KP.LP, '(')))
    closes = sel_width(select(tok, tok, kflag(lambda k: k == KP.RP, ')')))
    D = seq_map(opens, closes, lambda a, b: a - b, vfn=np.subtract, flag='count arithmetic: Dyck depth = #( - #)')
    kcon = seq_map(D, tok, lambda d, t: d if t in KP.CONN_T else -1)
    qcl = seq_map(D, tok, lambda d, t: d + 1 if t == KP.RP else -2)
    opPos = kqv(kcon, qcl, idx, equals, default=-1, reduction='max')
    opc = seq_map(tok, index_select(tok, opPos, default=0),
                  lambda t, o: KP.ATOM_T.get(t, KP.CONN_T.get(o, 0) if t == KP.RP else 0))
    lc = seq_map(opPos, opc, lambda p, o: p - 1 if o in (7, 8, 9) else -1, vt='index')
    tt = tok_map(tok, lambda t: KP.TT_ATOM.get(KP.ATOM_T.get(t, 0), 0), vt='comp')
    gsel = select(idx, lc, equals)
    for _ in range(H):
        tt = seq_map(seq_map(opc, shift_right(tt, 1), lambda o, r: o * 65536 + r, vt='comp'),
                     aggr(gsel, tt, reduction='max'), lambda a, l: KP._tt_apply(a >> 16, l, a & KP.FULL), vt='comp')
    root = seq_map(D, opc, lambda d, o: int(d == 0 and o > 0))
    afterT = has_seen(tok, full(tok, T['⊢']))
    prem_tt = mask(tt, root & ~afterT, KP.FULL)
    conj = aggr(select(idx, idx, TRUE), prem_tt, default=KP.FULL, reduction='and', vt='comp')
    goal = shift_right(tt, 1)
    return seq_map(conj, goal, lambda c, g: ONE_T if (c & ~g & KP.FULL) == 0 else ZERO_T)
# TAUT END


# ================================================================== tests
ASK = 123


def rand_formula(rng, d):
    if d == 0 or rng.random() < 0.25:
        return ('atom', rng.choice('PQRS')) if rng.random() < 0.93 else ('bot',)
    k = rng.choice(['not', 'and', 'or', 'imp'])
    if k == 'not':
        return ('not', rand_formula(rng, d - 1))
    return (k, rand_formula(rng, d - 1), rand_formula(rng, d - 1))


def ftok(f):
    return KP.formula_tokens(KP.F_SPAN, 0, 0, None, None) if False else _ft(f)


def _ft(f):
    k = f[0]
    if k == 'atom':
        return [f[1]]
    if k == 'bot':
        return ['False']
    if k == 'not':
        return ['(', '¬'] + _ft(f[1]) + [')']
    return ['('] + _ft(f[1]) + [{'and': '∧', 'or': '∨', 'imp': '→'}[k]] + _ft(f[2]) + [')']


def fval(f, v):
    k = f[0]
    if k == 'atom':
        return v[f[1]]
    if k == 'bot':
        return False
    if k == 'not':
        return not fval(f[1], v)
    a, b = fval(f[1], v), fval(f[2], v)
    return (a and b) if k == 'and' else (a or b) if k == 'or' else ((not a) or b)


def height(f):
    return 0 if f[0] in ('atom', 'bot') else 1 + max(height(g) for g in f[1:])


def gen_case(task, rng):
    """-> (sequence, {position: expected prediction})."""
    if task == 'copy':
        n = rng.randint(1, 20)
        x = rng.sample(range(100), n)
        seq = [START] + x + [END] + [START] + x + [END]
        return seq, {p: seq[p + 1] for p in range(n + 2, 2 * n + 3)}
    if task in ('reverse', 'reverse_rep'):
        n = rng.randint(1, 20)
        x = rng.sample(range(100), n) if task == 'reverse' else [rng.randint(0, 1) for _ in range(n)]
        seq = [START] + x + [END] + x[::-1] + [END]
        return seq, {p: seq[p + 1] for p in range(n + 1, 2 * n + 2)}
    if task in ('sort', 'sort_rep'):
        n = rng.randint(1, 30)
        x = rng.sample(range(100), n) if task == 'sort' else [rng.randint(0, 9) for _ in range(n)]
        seq = x + [SEP] + sorted(x) + [END]
        return seq, {p: seq[p + 1] for p in range(n, 2 * n + 1)}
    if task == 'count':
        a = rng.randint(0, 100)
        b = rng.randint(a, min(a + 25, 120))
        seq = [START, a, b] + list(range(a, b + 1)) + [END]
        return seq, {p: seq[p + 1] for p in range(2, len(seq) - 1)}
    if task == 'hist':
        n = rng.randint(1, 40)
        x = [rng.randint(0, 5) for _ in range(n)]
        return x, {p: x[:p + 1].count(x[p]) for p in range(n)}
    if task == 'mode':
        while True:
            n = rng.randint(1, 40)
            al = rng.sample(range(50), 5)
            x = [rng.choice(al) for _ in range(n)]
            cnt = {t: x.count(t) for t in set(x)}
            top = max(cnt.values())
            if sum(1 for t in cnt if cnt[t] == top) == 1:
                return x, {n - 1: max(cnt, key=cnt.get)}
    if task == 'parity':
        n = rng.randint(1, 40)
        x = [rng.randint(0, 1) for _ in range(n)]
        return x, {p: sum(x[:p + 1]) % 2 for p in range(n)}
    if task == 'parity_sp':
        n = rng.randint(1, 40)
        bits = [rng.randint(0, 1) for _ in range(n)]
        seq = []
        for i, b in enumerate(bits):
            seq += [10 + i, b]
        seq.append(GT_S)
        par, outp = PLUS_S, [PLUS_S]
        for i, b in enumerate(bits):
            if b:
                par = MINUS_S if par == PLUS_S else PLUS_S
                outp += [10 + i, par]
        seq += outp + [END]
        p0 = 2 * n
        return seq, {p: seq[p + 1] for p in range(p0, len(seq) - 1)}
    if task == 'addition':
        n = rng.randint(1, 18)
        a, b = rng.randrange(10 ** n), rng.randrange(10 ** n)
        da, db = [int(c) for c in str(a).zfill(n + 1)], [int(c) for c in str(b).zfill(n + 1)]
        ds = [int(c) for c in str(a + b).zfill(n + 1)]
        seq = [START_PROMPT]
        for i, d in enumerate(da):
            seq += [-100 - i, d]
        seq.append(PLUS)
        for i, d in enumerate(db):
            seq += [-100 - i, d]
        seq.append(EQUALS_SIGN)
        p0 = len(seq) - 1
        for i in range(n, -1, -1):
            seq += [-100 - i, ds[i]]
        seq.append(END_RESPONSE)
        return seq, {p: seq[p + 1] for p in range(p0, len(seq) - 1)}
    if task == 'eval':
        f = rand_formula(rng, rng.randint(0, H_EVAL))
        v = {x: rng.random() < 0.5 for x in 'PQRS'}
        seq = []
        for x in 'PQRS':
            seq += [T[x], EQ_T, ONE_T if v[x] else ZERO_T]
        seq += [T[':']] + [T[t] for t in _ft(f)] + [ASK]
        return seq, {len(seq) - 1: ONE_T if fval(f, v) else ZERO_T}
    if task == 'taut':
        prem = [rand_formula(rng, rng.randint(0, 5)) for _ in range(rng.randint(0, 3))]
        g = rand_formula(rng, rng.randint(0, 6))
        r = rng.random()
        if r < 0.2 and prem:
            g = rng.choice(prem)
        elif r < 0.35:
            g = ('imp', g, g)
        import itertools
        ok = all((not all(fval(p, dict(zip('PQRS', vs))) for p in prem)) or fval(g, dict(zip('PQRS', vs)))
                 for vs in itertools.product([False, True], repeat=4))
        seq = [T['<st>']]
        for j, p in enumerate(prem):
            seq += [T[f'h{j + 1}'], T[':']] + [T[t] for t in _ft(p)] + [T['<nl>']]
        seq += [T['⊢']] + [T[t] for t in _ft(g)] + [T['<act>']]
        return seq, {len(seq) - 1: ONE_T if ok else ZERO_T}
    raise ValueError(task)


TASKS = {
    'copy': (copy_prog, 'COPY', 'Zhou et al. copy_unique: 2 lines (def + return; induct)'),
    'reverse': (reverse_prog, 'REVERSE', 'Weiss et al.: 1 statement (non-causal, length - indices - 1)'),
    'reverse_rep': (reverse_rep_prog, 'REVERSE_REP', 'Weiss et al.: 1 statement (non-causal)'),
    'sort': (sort_prog, 'SORT', 'Zhou et al.: 2 lines (def + return), unique tokens'),
    'sort_rep': (sort_rep_prog, 'SORT_REP', 'Weiss et al. sort: 12 lines (non-causal, selector_width)'),
    'count': (count_prog, 'COUNT', 'Zhou et al. count: 17 listing lines, 12 non-comment'),
    'hist': (hist_prog, 'HIST', 'Weiss et al. histf: 1 statement (3 lines)'),
    'mode': (mode_prog, 'MODE', 'Zhou et al. mode: 4 lines'),
    'parity': (parity_prog, 'PARITY', 'none: Zhou et al. say parity has no RASP-L program without a scratchpad'),
    'parity_sp': (parity_sp_prog, 'PARITY_SP', 'none published (scratchpad format from Zhou et al.)'),
    'addition': (addition_prog, 'ADDITION', 'Zhou et al. reverse addition with index hints: see published_lines'),
    'eval': (eval_prog, 'EVAL', 'none'),
    'taut': (taut_prog, 'TAUT', 'none'),
}


def run_task(task, cases, seed):
    R.reset()
    prog, tag, note = TASKS[task]
    out = prog()
    rng = random.Random(seed * 1000 + hash(task) % 1000)
    data = [gen_case(task, rng) for _ in range(cases)]
    seqs = [d[0] for d in data]
    res = R.run_program([out], seqs, all_positions=True)[out]
    ok = 0
    bad = None
    for (seq, exp), pred in zip(data, res):
        good = all(int(pred[p]) == v for p, v in exp.items())
        ok += good
        if not good and bad is None:
            bad = (seq, {p: (v, int(pred[p])) for p, v in exp.items() if int(pred[p]) != v})
    m = R.metrics([out])
    toks, lines = R.source_size(R.region(os.path.abspath(__file__), tag))
    return {'task': task, 'cases': cases, 'exact': ok, 'ops': m['ops'], 'by_kind': m['by_kind'],
            'attn_depth': m['attn_depth'], 'mlp_run': m['mlp_run'], 'flagged_ops': m['flagged_ops'],
            'flags': m['flags'], 'source_tokens': toks, 'source_lines': lines, 'published': note,
            'first_failure': None if bad is None else str(bad)[:400]}


PUBLISHED = {'count': (90, 12), 'mode': (32, 4), 'copy_unique': (17, 2), 'addition_reverse_hinted': (361, 39)}


def published_counts():
    """(tokens, non-comment lines) of the paper's listings, measured with rasp.source_size on the arXiv e-print source
    (`curl -L https://arxiv.org/e-print/2310.16028`, files rasp/count.py, rasp/mode.py (mode only),
    rasp/copy_unique.py (copy_unique only), app_rasp_addition.tex (the minted listing of
    next_tok_rev_addition_hinted with its helpers)).  If those files are in /tmp they are re-measured, otherwise the
    recorded values PUBLISHED are returned."""
    if not os.path.exists('/tmp/count.py'):
        return dict(PUBLISHED)
    out = {}
    src = {'count': '/tmp/count.py', 'mode': '/tmp/mode.py', 'copy_unique': '/tmp/copy_unique.py'}
    for k, p in src.items():
        if os.path.exists(p):
            text = open(p, encoding='utf-8').read()
            if k == 'mode':
                text = text.split('def binary_mode')[0]
            if k == 'copy_unique':
                text = text.split('def copy_unique_ar')[0]
            out[k] = R.source_size(text)
    p = '/tmp/app_rasp_addition.tex'
    if os.path.exists(p):
        t = open(p, encoding='utf-8').read()
        body = t.split('\\begin{minted}[linenos,fontsize=\\tiny,frame=single,highlightlines={33-43}]{python}')[1]
        body = body.split('\\end{minted}')[0].replace('next_tok %\n', 'next_tok % 10\n')
        out['addition_reverse_hinted'] = R.source_size(body)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', type=int, default=300)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--tasks', default=','.join(TASKS))
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    rows = []
    for t in a.tasks.split(','):
        r = run_task(t, a.cases, a.seed)
        rows.append(r)
        print(f"{t:12s} exact {r['exact']}/{r['cases']}  ops {r['ops']:4d}  attn {r['attn_depth']:3d}  "
              f"mlp {r['mlp_run']:3d}  flagged {r['flagged_ops']:3d}  src {r['source_tokens']} tok / "
              f"{r['source_lines']} lines  {r['flags'] or ''}", flush=True)
        if r['first_failure']:
            print('   first failure:', r['first_failure'])
    pub = published_counts()
    print('published (tokens, lines):', pub)
    if a.out:
        with open(a.out, 'w') as fh:
            json.dump({'rows': rows, 'published_tokens_lines': pub, 'cases': a.cases, 'seed': a.seed}, fh, indent=1)


if __name__ == '__main__':
    main()
