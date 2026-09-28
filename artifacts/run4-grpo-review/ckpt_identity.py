"""Is round3-run1's stage1_depth3_f0_a1_s<s>.pt the model run4-grpo scored its novelty files with?
Re-score stored proofs at their stored best shift (T=1, fp32 CPU) and compare with base_logp_best_T1."""
import sys, json, torch, torch.nn.functional as F
sys.path.insert(0, '..')
from model import load_ckpt
A = '../artifacts/r4/'
out = {}
for s in range(20, 26):
    model, tok, meta = load_ckpt('/tmp/r4g_ck/stage1_depth3_f0_a1_s%d.pt' % s)
    model.eval()
    rows = [json.loads(l) for l in open(A + 'novelty_depth3_f0_a1_s%d_proofs.jsonl' % s)][:400:40]
    diffs = []
    for r in rows:
        pid = tok.encode_prompt(r['prompt']); qid = tok.encode_proof(r['proof']); sh = r['base_best_shift']
        ids = pid + [x + sh if x >= tok.ref0 else x for x in qid]
        x = torch.tensor([ids])
        with torch.no_grad():
            lg = model(x[:, :-1]).float()
        lp = F.log_softmax(lg, -1).gather(-1, x[:, 1:, None]).squeeze(-1)[0, len(pid) - 1:].sum().item()
        diffs.append(round(lp - r['base_logp_best_T1'], 3))
    ok = all(abs(d) < 0.15 for d in diffs)
    out[s] = dict(diffs=diffs, identical_model=ok)
    print(s, ok, diffs, {k: v for k, v in (meta or {}).items() if not hasattr(v, 'shape')} if isinstance(meta, dict) else type(meta))
json.dump(out, open('ckpt_identity.json', 'w'), indent=1)
