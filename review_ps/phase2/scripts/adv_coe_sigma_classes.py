"""create-or-elicit's own per-round proof classes for proofs of the 123 strict σ-covered RL targets
(artifacts/coe/rounds/la_<arm>.json on the reviewed branch, key proof_classes_by_round_sigma_targets; same found files:
round-1 class totals equal the review's round-1 distinct-proof counts). 'dn_pr_as' and 'lemma_route' proofs have every
DN citing a premise or a hypothesis, so none can carry the taxonomy's #10. Also checks the σ-target set equals the review's 123."""
import gzip, json, subprocess
W = '/home/dan/work/proof-strategies'
def show(path):
    return subprocess.run(['git', '-C', W, 'show', 'HEAD:' + path], capture_output=True, text=True, check=True).stdout
fam = json.loads(show('data/coe/families.json'))
sig = set()
for f, d in fam['families'].items():
    if d.get('classical'):
        sig |= set(d.get('strict_trained', []))
tg = [json.loads(l) for l in open('/home/dan/review/proof-strategies/data/ladder/rl_targets.jsonl')]
th = [json.loads(l) for l in gzip.open('/home/dan/review/proof-strategies/review_ps/out/thm_rl_targets.jsonl.gz', 'rt')]
sc = {r['name'] for r, t in zip(tg, th) if t['sc_sem']}
print('coe strict sigma targets', len(sig), 'review sigma-covered', len(sc), 'equal', sig == sc)
tot = 0
for arm in ['full_s3', 'full_s4', 'full_s5', 'dose1_s0', 'dose1_s1', 'dose1_s2', 'ko_s0', 'ko_s1', 'ko_s2', 'ko_s3', 'ko_s4', 'ko_s5']:
    d = json.loads(show(f'artifacts/coe/rounds/la_{arm}.json'))
    r1 = sum(d['proof_classes_by_round'].get('1', {}).values())
    rv = json.load(open(f'/home/dan/review/proof-strategies/review_ps/out/rl_{arm}.json'))['new_by_round']['1']
    pcs = d['proof_classes_by_round_sigma_targets']
    no10 = sum(v.get('dn_pr_as', 0) + v.get('lemma_route', 0) for r, v in pcs.items() if int(r) <= 16)
    sigma = sum(v.get('sigma', 0) for r, v in pcs.items() if int(r) <= 16)
    tot += no10
    print(arm, 'r1 total coe/review', r1, rv, '| sigma-target proofs r1-16: sigma', sigma, 'dn_pr_as+lemma_route (no #10 possible)', no10)
print('total no-#10 proofs of sigma-covered targets, r1-16, 12 ladders:', tot)
