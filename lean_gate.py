"""Lean is the only checker in the loop (run lean-only, proposal 9).  Rewritten from the lean-format gate.

gate(tok, prompts, texts) is called by sample.generate() for a Lean tokenizer (LeanTokenizer, FreeTokenizer).  Every distinct
(prompt, canonical text) whose sample ended with <eos> is sent to lean_check (elaborated-term allowlist + axiom check; term
size).  The REWARD IS lean_check ALONE.  Beside it, for the audit table, the ND proof the text denotes (tok.denote: the strict
fragment inverse, then the general term->ND converter of lean_free.py) is checked with nd_verify; the 2 x 2 table, timings and
every disagreement are logged ($LEAN_GATE_LOG, default artifacts/lean_gate.jsonl, one json line per call; disagreements in
<log>.disagree.jsonl).  "nd_verify accepts, Lean rejects" is a bug and is printed loudly.

Returns one proof string per sample:
  - accepted: the denoted ND proof ('N1 … QED') when it exists and nd_verify accepts it (so lines, pruning, patterns and
    normalisation work unchanged), otherwise the canonical Lean text (names renumbered by first appearance);
  - rejected: 'LEANREJ <reason>'; a sample without <eos>: 'LEANPARSE no-eos'.
VERDICT[(prompt, proof string)] = {'size', 'text', 'nd', 'lam_depth'} for the accepted strings of the LAST call (eval_set.judge
reads it; it is cleared at each call).
"""
import os, sys, json, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nd_verify import verify_text
from lean_check import check, WORKERS, CHUNK
import lean_free

VERDICT = {}


def gate(tok, prompts, texts):
    logfn = os.environ.get('LEAN_GATE_LOG', 'artifacts/lean_gate.jsonl')
    keys = {}
    for p, tx in zip(prompts, texts):
        if tx is not None:
            keys.setdefault((p, lean_free.canonical(tx)), tx)
    items = list(keys.items())
    srcs = [tok.statement(p) + ' ' + tx for (p, _), tx in items]
    res, wall, cpu = check(srcs)
    t0 = time.time()
    out_map = {}; tab = collections.Counter(); kinds = collections.Counter(); dis = []; rej = collections.Counter()
    VERDICT.clear()
    for ((p, ctx), tx), r in zip(items, res):
        nd = tok.denote(p, tx)
        nd_ok, nd_reason = (verify_text(p + ' ' + nd)[:2] if nd else (False, 'no denotation'))
        nd_ok = bool(nd_ok)
        if r['ok']:
            proof = nd if nd_ok else ctx
            VERDICT[(p, proof)] = {'size': r['size'], 'text': tx, 'nd': nd_ok, 'lam_depth': lean_free.lam_depth(tx)}
        else:
            proof = 'LEANREJ ' + r['reason'].split(' | ')[0][:60]
            rej[r['reason'].split(' | ')[0].split(':')[0][:20]] += 1
        out_map[(p, ctx)] = proof
        tab[(nd_ok, r['ok'])] += 1
        if nd_ok != r['ok']:
            kind = 'ND_YES_LEAN_NO' if nd_ok else ('no-denotation' if nd is None else nd_reason.split(' (line')[0][:60])
            kinds[kind] += 1
            dis.append({'prompt': p, 'lean_text': tx, 'nd': nd, 'nd_ok': nd_ok, 'nd_reason': nd_reason, 'lean_ok': r['ok'], 'lean_reason': r['reason'], 'kind': kind})
    t_nd = time.time() - t0
    n_noeos = sum(1 for tx in texts if tx is None)
    rec = {'utc': time.strftime('%FT%TZ', time.gmtime()), 'samples': len(prompts), 'no_eos': n_noeos, 'distinct_checked': len(items),
           'both_ok': tab[(True, True)], 'nd_ok_lean_rej': tab[(True, False)], 'nd_rej_lean_ok': tab[(False, True)], 'both_rej': tab[(False, False)],
           'disagreement_kinds': dict(kinds.most_common()), 'lean_reject_kinds': dict(rej.most_common(8)),
           'lean_wall_s': wall, 'lean_proc_s': cpu, 'denote_nd_verify_s': t_nd, 'workers': WORKERS, 'chunk': CHUNK, 'mode': tok.mode}
    os.makedirs(os.path.dirname(logfn) or '.', exist_ok=True)
    with open(logfn, 'a') as f:
        f.write(json.dumps(rec) + '\n')
    if dis:
        with open(logfn.replace('.jsonl', '') + '.disagree.jsonl', 'a') as f:
            for d in dis:
                f.write(json.dumps(d, ensure_ascii=False) + '\n')
    print(f'[lean_gate] {len(prompts)} samples, no-eos {n_noeos}, distinct checked {len(items)}: both ok {tab[(True, True)]}, lean-only {tab[(False, True)]}, '
          f'nd-only {tab[(True, False)]}, both rej {tab[(False, False)]}; lean {wall:.1f}s wall ({cpu:.1f}s proc, {WORKERS} workers), denote+nd_verify {t_nd:.1f}s', flush=True)
    if tab[(True, False)]:
        print(f'[lean_gate] BUG: nd_verify accepts {tab[(True, False)]} proofs that lean_check rejects (see disagree log)', flush=True)
    return [out_map[(p, lean_free.canonical(tx))] if tx is not None else 'LEANPARSE no-eos' for p, tx in zip(prompts, texts)]
