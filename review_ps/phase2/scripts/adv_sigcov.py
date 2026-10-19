"""Adversarial check: syntactic (create-or-elicit literal) sigma-covered counts, from prompts + executor classical labels.
Prints counts only (no theorem text)."""
import gzip, json, sys
sys.path.insert(0, '/home/dan/review/proof-strategies/review_ps')
from nd import parse_prompt

SETS = {'k12': 'train_k12.jsonl.gz', 'cap6': 'train_depth3_f0_a1.jsonl.gz', 'k12ko': 'train_k12ko.jsonl.gz',
        'k12dose1': 'train_k12dose1.jsonl.gz'}
IN = '/home/dan/review/proof-strategies/data/ps/in/'
EX = '/home/dan/work/proof-strategies/artifacts/ps/theorem/'
RV = '/home/dan/review/proof-strategies/review_ps/out/'

def subs(f, acc):
    acc.append(f)
    if isinstance(f, tuple):
        for g in f[1:]:
            subs(g, acc)
    return acc

def has_negimp_bot(prem, concl):
    # a subformula ( ( ~ X ) > F )
    for f in prem + [concl]:
        for s in subs(f, []):
            if isinstance(s, tuple) and s[0] == '>' and s[2] == 'F' and isinstance(s[1], tuple) and s[1][0] == '~':
                return True
    return False

def has_other_sem(prem, concl):
    # other semantic double-negation shapes: ~(X > F), (X > F) > F
    for f in prem + [concl]:
        for s in subs(f, []):
            if isinstance(s, tuple) and s[0] == '~' and isinstance(s[1], tuple) and s[1][0] == '>' and s[1][2] == 'F':
                return True
            if isinstance(s, tuple) and s[0] == '>' and s[2] == 'F' and isinstance(s[1], tuple) and s[1][0] == '>' and s[1][2] == 'F':
                return True
    return False

for name, fn in SETS.items():
    ex = [json.loads(l) for l in gzip.open(EX + name + '.jsonl.gz', 'rt')]
    rv = [json.loads(l) for l in gzip.open(RV + 'thm_' + name + '.jsonl.gz', 'rt')]
    n = 0; co = 0; lit_dneg = 0; sc_lit = 0; sc_lit_negimp = 0; sc_lit_other = 0; sc_lit_neither = 0
    ex_sc = 0; rv_scsyn = 0; rv_scsem = 0; mism_co = 0; mism_scsyn = 0; ex_dneg = 0
    sc_sem_but_lit = 0
    for k, l in enumerate(gzip.open(IN + fn, 'rt')):
        r = json.loads(l)
        e = ex[k]; v = rv[k]
        assert e['i'] == k and v['i'] == k
        n += 1
        c = e['classical']
        co += c
        if c != v['co']:
            mism_co += 1
        lit = '( ~ ( ~' in r['prompt']
        lit_dneg += lit
        ex_sc += e['sigma_cov']
        ex_dneg += e['dneg']
        rv_scsyn += v['sc_syn']; rv_scsem += v['sc_sem']
        s = c and not lit
        if s != v['sc_syn']:
            mism_scsyn += 1
        if s:
            sc_lit += 1
            prem, concl = parse_prompt(r['prompt'])
            a = has_negimp_bot(prem, concl); b = has_other_sem(prem, concl)
            sc_lit_negimp += a
            sc_lit_other += (b and not a)
            sc_lit_neither += (not a and not b)
            if e['sigma_cov']:
                sc_sem_but_lit += 1
    print(name, json.dumps(dict(n=n, classical=co, lit_dneg=lit_dneg, lit_dneg_pct=round(100*lit_dneg/n, 2), ex_dneg_sem=ex_dneg,
        sc_literal=sc_lit, sc_literal_pct=round(100*sc_lit/n, 2), of_which_negimp_bot=sc_lit_negimp, other_sem_only=sc_lit_other,
        neither=sc_lit_neither, of_which_ex_sigma_cov=sc_sem_but_lit, ex_sigma_cov=ex_sc, rv_sc_syn=rv_scsyn, rv_sc_sem=rv_scsem,
        mism_co=mism_co, mism_scsyn=mism_scsyn)), flush=True)
