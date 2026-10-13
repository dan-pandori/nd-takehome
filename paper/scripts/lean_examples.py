"""Render the paper's example proofs (Box 1) from the ND strings the models wrote, and check each with Lean.

Sources (ND text exactly as decoded from the sampled proofs):
  - review_coe/cert_proofs.log: knockout s1 *base* (no RL) large-k successes on la_transfer_916 and la_transfer_1246
    (the review's certification recount, R§6).
  - artifacts/coe/examples/knockout_first_sigma.md item 1: knockout s0 base, la_transfer_916 at T 1.0 (DN on an IMPI line).
Each is translated by nd2lean.translate and checked by nd2lean.lean_check (Lean 4 core on the VPS); a negative control
replaces the goal by its negation and must be rejected.  Output: paper/data/lean_examples.json and paper/lean_examples.tex.
"""
import json, os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)
os.environ.setdefault('PATH', '')
os.environ['PATH'] = os.path.expanduser('~/.elan/bin') + ':' + os.environ['PATH']
import nd2lean

EX = [
    ('free_sigma_916', 'knockout s1 base (no RL), la_transfer_916, a large-k success',
     'THM ( ( ~ S ) > ( ~ P ) ) , P SEQ ( R > S ) PRF',
     'N1 ( ( ~ S ) > ( ~ P ) ) : PR ; N2 P : PR ; N3 | R : AS ; N4 | | ( ~ S ) : AS ; N5 | | ( ~ P ) : IMPE N1 N4 ; '
     'N6 | | F : NEGE N2 N5 ; N7 | ( ~ ( ~ S ) ) : NEGI N4 N6 ; N8 | S : DN N7 ; N9 ( R > S ) : IMPI N3 N8 ; QED'),
    ('contraposition_conv_1246', 'knockout s1 base (no RL), la_transfer_1246 (contraposition_conv, held-out), a large-k success',
     'THM ( ( ~ S ) > ( ~ ( ( S & R ) v R ) ) ) SEQ ( ( ( S & R ) v R ) > S ) PRF',
     'N1 ( ( ~ S ) > ( ~ ( ( S & R ) v R ) ) ) : PR ; N2 | ( ( S & R ) v R ) : AS ; N3 | | ( ~ S ) : AS ; '
     'N4 | | ( ~ ( ( S & R ) v R ) ) : IMPE N1 N3 ; N5 | | F : NEGE N2 N4 ; N6 | ( ~ ( ~ S ) ) : NEGI N3 N5 ; '
     'N7 | | ( S & R ) : AS ; N8 | | S : DN N6 ; N9 | | R : AS ; N10 | | S : DN N6 ; N11 | S : ORE N2 N7 N8 N9 N10 ; '
     'N12 ( ( ( S & R ) v R ) > S ) : IMPI N2 N11 ; QED'),
    ('impi_dn_916', 'knockout s0 base (no RL), la_transfer_916 at T 1.0: DN on an IMPI line (not a NEGI line)',
     'THM ( ( ~ S ) > ( ~ P ) ) , P SEQ ( R > S ) PRF',
     'N1 ( ( ~ S ) > ( ~ P ) ) : PR ; N2 P : PR ; N3 | ( ~ S ) : AS ; N4 | ( ~ P ) : IMPE N1 N3 ; N5 | F : NEGE N2 N4 ; '
     'N6 ( ( ~ S ) > F ) : IMPI N3 N5 ; N7 | R : AS ; N8 | S : DN N6 ; N9 ( R > S ) : IMPI N7 N8 ; QED'),
]

def negate_goal(prompt):
    m = re.match(r'THM (.*) SEQ (.*) PRF$', prompt)
    return f'THM {m.group(1)} SEQ ( ~ {m.group(2)} ) PRF' if m.group(1).strip() else f'THM SEQ ( ~ {m.group(2)} ) PRF'

out = []
for key, label, prompt, proof in EX:
    src = nd2lean.translate(prompt, proof)
    try:
        bad = nd2lean.translate(negate_goal(prompt), proof)
    except Exception as e:                       # the translator may refuse a mismatched goal: that is a rejection too
        bad = None
    res = nd2lean.lean_check([src] + ([bad] if bad else []))
    out.append({'key': key, 'label': label, 'prompt': prompt, 'nd': proof, 'lean': src,
                'lean_ok': bool(res[0][0]), 'negctl_rejected': (not res[1][0]) if bad else True})
    print(key, 'lean_ok', res[0], 'negated goal rejected', out[-1]['negctl_rejected'])
json.dump(out, open(os.path.join(ROOT, 'paper/data/lean_examples.json'), 'w'), indent=1)
