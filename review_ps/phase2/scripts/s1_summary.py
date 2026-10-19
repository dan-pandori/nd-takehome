"""Print per-set shares needed by the blog audit, from the reviewer's summary_all.json (no recomputation of labels)."""
import json
S = json.load(open('/home/dan/review/proof-strategies/review_ps/out/summary_all.json'))
def pct(a, n): return f"{a} ({100*a/n:.2f} %)"
for s in ['k12','k12ko','k12dose1','cap6','k12_min990','charles_base','tb_schema_search','textbook72_search','rl_targets_gen']:
    d = S[s]; n = d['n']; u = d['uses']; w = d['work']; sub = d['sub']
    print(f"== {s} n={n} mean_lines={d.get('mean_lines'):.3f} boxfree={pct(d['boxfree'],n)}")
    print("  uses:", {k: f"{100*v/n:.2f}" for k, v in sorted(u.items())})
    print("  work:", {k: pct(v, n) for k, v in sorted(w.items())})
    keys = ['contradiction.working','contradiction.free','contradiction.neg_goal','contradiction.vacuous','contradiction.scaffolded',
            'contradiction.pointless','contradiction.template','contradiction.immediate','cases.genuine','cases.redundant','cases.trivial_merge',
            'cond_proof.vacuous','cond_proof.working','neg_intro.working','neg_intro.vacuous','ex_falso.inconsistent_premises',
            'dne.on_premise','dne.on_hypothesis','dne.on_derived','mod_tollens.strict','disj_syll.strict']
    print("  sub:", {k: pct(sub.get(k, 0), n) for k in keys})
