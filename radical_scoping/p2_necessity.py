"""P2 knockout feasibility: which textbook72 problems REQUIRE Or.elim (ORE) or classical DN, by minlen's bounded search
(labelling only; minlen's internal nd_verify self-check of found proofs is not used as a judge — a label comes from
search success / failure).  Three searches per problem at --bound, same space: full, no-ORE (Search.disj emptied by a
subclass; minlen.py is not edited), no-DN (minlen's own --forbid DN, which also removes the reductio template).
requires_X = full search finds a proof <= bound AND the restricted one fails without timeout.  Bounded and restricted to
minlen's formula space, so `requires` is a label of this search space, as in necessity.py.
  python3 radical_scoping/p2_necessity.py data/bs/textbook72.jsonl 12 20 > radical_scoping/p2_necessity_textbook72.jsonl"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import minlen
from multiprocessing import Pool
class NoORE(minlen.Search):
    def __init__(self, *a, **k):
        super().__init__(*a, **k); self.disj = []
def run(prompt, bound, tl, cls=minlen.Search, forbid=()):
    orig = minlen.Search; minlen.Search = cls
    try:
        r = minlen.minlen(prompt, bound, tl, forbid=forbid)
    finally:
        minlen.Search = orig
    return r
def work(args):
    rec, bound, tl = args; p = rec['prompt']
    out = {'name': rec['name'], 'prompt': p, 'reference_lines': rec.get('reference_lines')}
    for tag, kw in (('full', {}), ('no_ore', {'cls': NoORE}), ('no_dn', {'forbid': ('DN',)})):
        r = run(p, bound, tl, **kw)
        out[tag] = r.get('min_lines_ub'); out[tag + '_timeout'] = r.get('timeout'); out[tag + '_err'] = r.get('error')
    return out
if __name__ == '__main__':
    recs = [json.loads(l) for l in open(sys.argv[1])]; bound = int(sys.argv[2]); tl = float(sys.argv[3])
    with Pool(2) as pool:
        for o in pool.imap(work, [(r, bound, tl) for r in recs]):
            print(json.dumps(o), flush=True)
