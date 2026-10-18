"""Markdown tables for review §Recount, generated from review_ps/out/ (no hand-typed numbers)."""
import gzip
import json
import os

S = json.load(open("out/summary_all.json"))
STR = ["direct", "and_intro", "cond_proof", "or_intro", "cases", "disj_syll", "neg_intro", "mod_tollens", "ex_falso",
       "contradiction", "dne", "lem", "lemma_reuse"]
WORK = {"cond_proof", "cases", "neg_intro", "contradiction"}


def p(c, n):
    return f"{100.0 * c / n:.2f}"


def k12_table():
    k = S["k12"]
    n = k["n"]
    out = ["| # | strategy | uses | uses % | working % | primary % | curried primary % |", "|---|---|---:|---:|---:|---:|---:|"]
    for i, s in enumerate(STR, 1):
        w = p(k["work"][s], n) if s in WORK else "–"
        out.append(f"| {i} | {s} | {k['uses'][s]:,} | {p(k['uses'][s], n)} | {w} | {p(k['primary'].get(s, 0), n)} | {p(k['curried'].get(s, 0), n)} |")
    out.append(f"| – | trivial | – | – | – | {p(k['primary'].get('trivial', 0), n)} | {p(k['curried'].get('trivial', 0), n)} |")
    out.append(f"| – | box-free (no AS line) | {k['boxfree']:,} | {p(k['boxfree'], n)} | | | |")
    return "\n".join(out)


def sets_table():
    sets = ["k12", "cap6", "k12ko", "k12dose1", "rl_targets_gen", "transfer_gen", "holdout250_gen", "charles_base",
            "k12_min990", "tb_schema_search", "textbook72_search"]
    head = "| strategy (uses %) | " + " | ".join(f"{s} ({S[s]['n']:,})" for s in sets) + " |"
    out = [head, "|---|" + "---:|" * len(sets)]
    for s in STR:
        out.append(f"| {s} | " + " | ".join(p(S[x]["uses"][s], S[x]["n"]) for x in sets) + " |")
    out.append("| working #10 | " + " | ".join(p(S[x]["work"]["contradiction"], S[x]["n"]) for x in sets) + " |")
    out.append("| primary #10 | " + " | ".join(p(S[x]["primary"].get("contradiction", 0), S[x]["n"]) for x in sets) + " |")
    out.append("| vacuous →I (sub-type) | " + " | ".join(p(S[x]["sub"].get("cond_proof.vacuous", 0), S[x]["n"]) for x in sets) + " |")
    out.append("| box-free | " + " | ".join(p(S[x]["boxfree"], S[x]["n"]) for x in sets) + " |")
    return "\n".join(out)


def thm_table():
    names = ["k12", "cap6", "k12ko", "k12dose1", "rl_targets", "transfer", "holdout250", "charles_base", "textbook72", "tb_schema"]
    out = ["| set | n | classical-only | dneg (semantic) | σ-covered (semantic dneg) | σ-covered (syntactic ¬¬ only) | inconsistent premises |",
           "|---|---:|---:|---:|---:|---:|---:|"]
    for nm in names:
        T = [json.loads(l) for l in gzip.open(f"out/thm_{nm}.jsonl.gz", "rt")]
        n = len(T)
        c = lambda k: sum(bool(t[k]) for t in T)  # noqa: E731
        out.append(f"| {nm} | {n:,} | {c('co'):,} ({p(c('co'), n)} %) | {c('dneg_sem'):,} ({p(c('dneg_sem'), n)} %) | {c('sc_sem'):,} | {c('sc_syn'):,} | {c('inc'):,} ({p(c('inc'), n)} %) |")
    return "\n".join(out)


def rl_table():
    E = json.load(open("../artifacts/ps/rl_found.json"))
    out = ["| ladder | distinct proofs r1–16 | r1 (base model) | with #10 | working #10 r1 | working #10 r2–16 | free-working r2–16 | σ-covered targets with a working #10 (r1 / by r16) | cells = executor |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for arm in E:
        fn = f"out/rl_{arm}.json"
        if not os.path.exists(fn):
            out.append(f"| {arm} | (pending) |||||||")
            continue
        M = json.load(open(fn))
        g = lambda k, r: M[k][str(r)]  # noqa: E731
        tot = sum(g("new_by_round", r) for r in range(1, 17))
        red = sum(g("reductio_by_round", r) for r in range(1, 17))
        w1 = g("working_by_round", 1)
        w2 = sum(g("working_by_round", r) for r in range(2, 17))
        f2 = sum(g("free_working_by_round", r) for r in range(2, 17))
        sc = M["sigma_cov_first_working_round"]
        same = all(M[k][str(r)] == E[arm][k][str(r)] for k in ("new_by_round", "reductio_by_round", "working_by_round",
                   "template_only_by_round", "free_working_by_round", "neg_goal_working_by_round") for r in range(1, 17)) and sc == E[arm]["sigma_cov_first_working_round"]
        out.append(f"| {arm} | {tot:,} | {g('new_by_round', 1):,} | {red:,} | {w1:,} | {w2:,} | {f2:,} | {sum(1 for v in sc.values() if v == 1)} / {len(sc)} | {'yes' if same else 'NO'} |")
    return "\n".join(out)


if __name__ == "__main__":
    import sys
    what = sys.argv[1]
    print({"k12": k12_table, "sets": sets_table, "thm": thm_table, "rl": rl_table}[what]())
