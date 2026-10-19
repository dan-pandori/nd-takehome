"""Does the reviewer's classifier label a disguised reductio as #10 when the self-built ~~P reaches DN through a box
hypothesis? Three proofs of one classical-only, sigma-covered sequent (checked outside every textbook72 class):
  plain_sigma      ~I builds ~~P, DN on it                       (expected: #10)
  lemma_route_impi ~~P > P proved by DN on the ->I hypothesis, applied by ->E to the ~I line (create-or-elicit's 'lemma route')
  ore_route_c7     ~I builds ~~P, vI makes P v ~~P, vE with DN on the case hypothesis (the review's C7 shape)
Prints ND validity, G4ip status and labels only."""
import sys
sys.path.insert(0, '/home/dan/review/proof-strategies/review_ps')
from nd import parse_prompt, Proof
from cls import classify
from ipc import classically_valid, intuitionistic
from sealkey import TB72, keys

prompt = "THM ( ( ~ P ) > Q ) , ( ~ Q ) , R SEQ P PRF"
p, c = parse_prompt(prompt)
tb = TB72(path='/home/dan/review/proof-strategies/data/bs/textbook72.jsonl')
k = keys(p, c)
print('sequent in a textbook72 class (any key):', any(k[x] in tb.K[x] for x in tb.K),
      '| classically valid:', classically_valid(p, c), '| intuitionistic:', intuitionistic(p, c))
core = ("N1 ( ( ~ P ) > Q ) : PR ; N2 ( ~ Q ) : PR ; N3 R : PR ; N4 | ( ~ P ) : AS ; N5 | Q : IMPE N1 N4 ; "
        "N6 | F : NEGE N5 N2 ; N7 ( ~ ( ~ P ) ) : NEGI N4 N6 ; ")
proofs = {
    'plain_sigma': core + "N8 P : DN N7 ; QED",
    'lemma_route_impi': core + "N8 | ( ~ ( ~ P ) ) : AS ; N9 | P : DN N8 ; N10 ( ( ~ ( ~ P ) ) > P ) : IMPI N8 N9 ; N11 P : IMPE N10 N7 ; QED",
    'ore_route_c7': core + "N8 ( P v ( ~ ( ~ P ) ) ) : ORI2 N7 ; N9 | P : AS ; N10 | ( ~ ( ~ P ) ) : AS ; N11 | P : DN N10 ; N12 P : ORE N8 N9 N9 N10 N11 ; QED",
}
for name, pr in proofs.items():
    P = Proof(p, c, pr)
    lab = classify(p, c, pr)
    subs = sorted('.'.join(t) for t in lab['sub'] if t[0] in ('dne', 'contradiction', 'neg_intro'))
    print(name, '| nd_ok', P.check(), '| uses', sorted(lab['uses']), '| work', sorted(lab['work']), '| sub', subs,
          '| sigma', lab['sigma'], 'sigma_plus', lab['sigma_plus'])
