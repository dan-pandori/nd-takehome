#!/usr/bin/env python3
"""run1-lean step 3: the RL-found proof classes as Lean prompts (draw-0 examples and card of step 2).

  python r1_scale_prompts.py --out data/r1   # writes scale_theorems.jsonl, scale_prompts.jsonl

Classes (pre-registered):
  depth3   : theorems of artifacts/p2/novelty_depth3_f0_a1_s0_proofs.jsonl whose pruned RL proof has box depth >= 3
             (521; a seed-0 sample of 60)
  reductio : all theorems of artifacts/p2/novelty_reductio_f0_s0_t2_proofs.jsonl whose pruned proof is patterns.reductio (88)
  nine     : theorems of artifacts/novelty_phase1_theorems.jsonl (final transfer + targets) with min_written >= 9 (60)
Each record carries the Phase-1 base log-probability of its RL-found proof(s) (base_logp_T08_any; base_logp_T1_any),
the RL proof with the highest base log-prob, its written length, and the source arm.
Prompt schema = data/r1/prompts.jsonl (forms 'lean' and 'tokens', draw 0) so r1_gen.py / r1_judge.py run unchanged;
the tokens form is an extra (Coder-30B only): the exact task RL solved, in-context.
"""
import argparse, json, os, sys, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import patterns
import nd2lean as L
from r1_prompts import CARD, SYSTEM, render_example, render_target, load_jsonl


def collect(fn, pred, label):
    """-> dict name -> record with the best (highest base logp) pattern proof."""
    out = {}
    for r in load_jsonl(fn):
        c = patterns.classify(r['proof'])
        if not c or not c[pred]:
            continue
        cur = out.get(r['name'])
        if cur is None or r['base_logp_T08'] > cur['rl_logp_T08']:
            out[r['name']] = {'name': r['name'], 'cls': label, 'src': r['src'], 'thm': r['thm'], 'prompt': r['prompt'],
                              'rl_proof': r['proof'], 'rl_written': r['written'], 'gen_lines': r.get('gen_lines'),
                              'rl_logp_T08': r['base_logp_T08'], 'rl_logp_T1': r['base_logp_T1'], 'arm': os.path.basename(fn)}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='data/r1')
    ap.add_argument('--n_depth3', type=int, default=60)
    a = ap.parse_args()
    rng = random.Random(0)

    d3 = collect('artifacts/p2/novelty_depth3_f0_a1_s0_proofs.jsonl', 'depth3', 'depth3')
    d3_names = sorted(d3)
    d3_pick = [d3[n] for n in sorted(rng.sample(d3_names, a.n_depth3))]
    red = collect('artifacts/p2/novelty_reductio_f0_s0_t2_proofs.jsonl', 'reductio', 'reductio')
    red_pick = [red[n] for n in sorted(red)]
    # nine-line: theorem-level file for the class, proof-level file for the best proof
    T = {(t['src'], t['name']): t for t in load_jsonl('artifacts/novelty_phase1_theorems.jsonl')}
    P = collections.defaultdict(list)
    for p in load_jsonl('artifacts/novelty_phase1_proofs.jsonl'):
        P[(p['src'], p['name'])].append(p)
    nine_pick = []
    for (src, name), t in sorted(T.items()):
        if src in ('final_transfer', 'final_targets') and t['min_written'] >= 9:
            best = max(P[(src, name)], key=lambda p: p['base_logp_T08'])
            nine_pick.append({'name': name, 'cls': 'nine', 'src': src, 'thm': t['thm'], 'prompt': t['prompt'],
                              'rl_proof': best['proof'], 'rl_written': best['written'], 'gen_lines': t['gen_lines'],
                              'rl_logp_T08': best['base_logp_T08'], 'rl_logp_T1': best['base_logp_T1'],
                              'arm': 'novelty_phase1 (ei_abs_s0_cont r16)', 'min_written': t['min_written']})
    # theorem-level logp (sum over the theorem's proofs) for the theorem-level comparison
    for r in nine_pick:
        t = T[(r['src'], r['name'])]
        r['thm_logp_T08_any'] = t['base_logp_T08_any']
    for fn, picks in (('artifacts/p2/novelty_depth3_f0_a1_s0_theorems.jsonl', d3_pick), ('artifacts/p2/novelty_reductio_f0_s0_t2_theorems.jsonl', red_pick)):
        tt = {t['name']: t for t in load_jsonl(fn)}
        for r in picks:
            r['thm_logp_T08_any'] = tt[r['name']]['base_logp_T08_any']
    thms = d3_pick + red_pick + nine_pick
    names = [t['name'] for t in thms]
    assert len(set(names)) == len(names)
    for t in thms:
        assert L.verify_text(t['prompt'] + ' ' + t['rl_proof'])[0]
    ex = [e for e in load_jsonl(f'{a.out}/examples.jsonl') if e['draw'] == 0]
    from gen import canon_key
    cls_keys = {canon_key(t['thm'].strip()) for t in thms}
    test_keys = {t['key'] for t in load_jsonl(f'{a.out}/theorems.jsonl')} | cls_keys
    # draw-0 examples that share a renaming class with a class theorem are replaced by a same-length,
    # non-overlapping proof from the same pool (deterministic, seed 0); everything else is draw 0 verbatim
    pools = {}
    for n in range(2, 7):
        pools[n] = [r for r in load_jsonl('data/train.jsonl.gz') if r['n_lines'] == n]
    for n in range(7, 17):
        pools[n] = [r for r in load_jsonl('data/rl_targets.jsonl') if r['n_lines'] == n]
    replaced = []
    used = {e['key'] for e in ex}
    for i, e in enumerate(ex):
        if e['key'] in cls_keys:
            cand = [r for r in pools[e['n_lines']] if r['key'] not in test_keys and r['key'] not in used]
            r = rng.choice(cand)
            ok = L.verify_text(r['prompt'] + ' ' + (r.get('proof') or r['gen_proof']))[0]
            assert ok
            replaced.append((e['name'], r['name']))
            ex[i] = {'draw': 0, 'name': r['name'], 'prompt': r['prompt'], 'proof': r.get('proof') or r['gen_proof'], 'n_lines': r['n_lines'], 'key': r['key']}
            used.add(r['key'])
    print('replaced examples (overlapping a class theorem):', replaced)
    assert not ({e['key'] for e in ex} & cls_keys)
    with open(f'{a.out}/scale_examples.jsonl', 'w') as f:
        for e in ex:
            f.write(json.dumps(e) + '\n')
    bodies = {form: CARD[form] + '\n\nWorked examples:\n\n' + '\n\n'.join(render_example(form, e['prompt'], e['proof'], k + 1) for k, e in enumerate(ex))
              for form in ('lean', 'tokens')}
    with open(f'{a.out}/scale_theorems.jsonl', 'w') as f:
        for t in thms:
            f.write(json.dumps(t) + '\n')
    with open(f'{a.out}/scale_prompts.jsonl', 'w') as f:
      for form in ('lean', 'tokens'):
        for t in thms:
            user = bodies[form] + '\n\n' + render_target(form, t['prompt'])
            rec = {'id': f'{form}/d0/{t["cls"]}/{t["name"]}', 'form': form, 'draw': 0, 'name': t['name'], 'src': t['src'],
                   'stratum': t['cls'], 'gen_lines': t['gen_lines'], 'nd_prompt': t['prompt'],
                   'lean_header': L.lean_header(t['prompt'], name='target'),
                   'messages': [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': user}]}
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    print(collections.Counter(t['cls'] for t in thms), collections.Counter((t['cls'], t['rl_written']) for t in thms))


if __name__ == '__main__':
    main()
