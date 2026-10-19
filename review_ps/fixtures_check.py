"""Reviewer classifier on the second implementer's 25 hand-built fixtures (sub-types the data never exercise)."""
import json
from nd import parse_prompt
from cls import classify
from lean import render, check

ROUTES = {"immediate", "mt", "or_weaken", "and_elim", "and_intro", "imp_hyp", "cases", "self", "mixed", "vacuous", "other"}
rows = [json.loads(l) for l in open("../data/ps/validation/second_impl_fixtures_v1.2.jsonl")]
bad, items = [], []
for r in rows:
    p, c = parse_prompt(r["prompt"])
    o = classify(p, c, r["proof"])
    mine = set()
    for (s, t) in o["sub"]:
        if s == "contradiction" and t in ROUTES:
            mine.add("contradiction.route_" + t)
            if t == "vacuous":
                mine.add("contradiction.vacuous")
        else:
            mine.add(f"{s}.{t}")
    ok = (sorted(o["uses"]) == sorted(r["expect_u"]) and o["primary"] == r["expect_pri"]
          and all(x in mine for x in r["expect_sub_present"]) and not any(x in mine for x in r["expect_sub_absent"]))
    if not ok:
        bad.append(r["prompt"])
    items.append((p, c, render(p, c, r["proof"])))
res = check(items)
out = {"n": len(rows), "label_mismatches": len(bad), "lean_accepted": sum(ok for ok, _ in res)}
json.dump(out, open("out/fixtures_check.json", "w"))
print(out)
