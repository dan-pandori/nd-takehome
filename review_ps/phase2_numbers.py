"""Every ad hoc number quoted in review §Compare / §Verdict that no other script prints (auditability)."""
import gzip
import json
from nd import parse_prompt, Proof
from cls import A

out = {}
Lab = [json.loads(l) for l in gzip.open("out/labels_k12.jsonl.gz", "rt")]
T = [json.loads(l) for l in gzip.open("out/thm_k12.jsonl.gz", "rt")]
K = [json.loads(l) for l in gzip.open("../data/ps/in/train_k12.jsonl.gz", "rt")]
# C6 glosses
pc = [i for i, r in enumerate(Lab) if r["primary"] == "cases"]
expl = 0
for i in pc:
    p, c = parse_prompt(K[i]["prompt"]); P = Proof(p, c, K[i]["proof"]); a = A(P)
    expl += P.L[a.o(P.L[a.root]["refs"][0])]["rule"] == "BOTE"
out["cases_primary"] = {"n": len(pc), "inconsistent_premises": sum(T[i]["inc"] for i in pc), "root_split_on_exploded": expl,
                        "any_redundant_split": sum("cases.redundant" in Lab[i]["sub"] for i in pc)}
p10 = [i for i, r in enumerate(Lab) if r["primary"] == "contradiction"]
negG_imp_F = dd_prem = 0
for i in p10:
    p, c = parse_prompt(K[i]["prompt"])
    negG_imp_F += (">", ("~", c), "F") in p
    dd_prem += ("~", ("~", c)) in p
out["contradiction_primary"] = {"n": len(p10), "premise_negG_implies_F": negG_imp_F, "premise_negneg_G": dd_prem,
                                "any_scaffolded": sum("contradiction.scaffolded" in Lab[i]["sub"] for i in p10),
                                "any_vacuous": sum("contradiction.vacuous" in Lab[i]["sub"] for i in p10)}
pcp = [i for i, r in enumerate(Lab) if r["primary"] == "cond_proof"]
two_unused = 0
for i in pcp:
    p, c = parse_prompt(K[i]["prompt"]); P = Proof(p, c, K[i]["proof"]); a = A(P)
    unused = sum(1 for k in a.keep if P.L[k]["rule"] == "IMPI" and P.L[k]["refs"][0] != P.L[k]["refs"][1]
                 and not a.dep(P.L[k]["refs"][1], P.L[k]["refs"][0]))
    two_unused += unused >= 2
out["cond_proof_primary"] = {"n": len(pcp), "two_or_more_unused_assumptions": two_unused}
# RL totals
arms = ["full_s3", "full_s4", "full_s5", "dose1_s0", "dose1_s1", "dose1_s2", "ko_s0", "ko_s1", "ko_s2", "ko_s3", "ko_s4", "ko_s5"]
out["rl_distinct_proofs_total"] = sum(sum(json.load(open(f"out/rl_{a}.json"))["new_by_round"].values()) for a in arms)
rc = json.load(open("out/rl_recheck.json"))
out["rl_recheck"] = {"n": sum(v["n"] for v in rc.values()), "accepted": sum(v["accepted"] for v in rc.values()),
                     "working": sum(v["n_working"] for v in rc.values())}
out["k12_working_negI"] = {"records": json.load(open("out/summary_all.json"))["k12"]["work"]["neg_intro"]}
# template-only reductio proofs in K12 and dose set
S = json.load(open("out/summary_all.json"))
out["template_only"] = {s: S[s]["uses"]["contradiction"] - S[s]["work"]["contradiction"] for s in ("k12", "k12dose1")}
# syntactic σ-covered by set and whether each has a (~X > F) subformula
for s in ("k12", "cap6", "k12dose1"):
    th = [json.loads(l) for l in gzip.open(f"out/thm_{s}.jsonl.gz", "rt")]
    out[f"sc_syn_{s}"] = {"sc_syn": sum(t["sc_syn"] for t in th), "sc_sem": sum(t["sc_sem"] for t in th),
                          "sc_syn_not_sem": sum(t["sc_syn"] and not t["sc_sem"] for t in th)}
json.dump(out, open("out/phase2_numbers.json", "w"), indent=1)
print(json.dumps(out, indent=1))
