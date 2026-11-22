"""Mechanical rule-5 pass (pre-registered confirming rule, olmo-ifomega rule 5): for prompts whose only constraint is
a fixed-output one (`repeat:repeat_span`, `repeat:repeat_simple`: the checker compares the whole stripped answer with
one fixed string), a strict success IS that string, which is 'the only answer that follows the constraint' -> genuine.
Affected prompts among my items: ifbench_284 (repeat_span), ifbench_64 (repeat_simple). Every read group of theirs that
my readers labelled gamed gets a confirm.json entry (round R5). I missed this in my first confirmation pass (readers
agreed and flagged no checker disagreement, so no adjudication was triggered); found through the agreement table with
the executor's labels (out/compare.txt), then applied by rule, not by copying any executor label."""
import json

import rvc_hand as H
from rvc_core import upstream_record

FIXED = {"repeat:repeat_span", "repeat:repeat_simple"}


def main():
    rd = H.reads()
    cf = H.HAND / "confirm.json"
    conf = json.load(open(cf))
    n = 0
    for g, rs in rd.items():
        ids = set(upstream_record(g[0])[1]["instruction_id_list"])
        if not ids or not ids <= FIXED:
            continue
        key = json.dumps(list(g))
        labs = [r[1] for r in rs]
        cur = conf.get(key, {}).get("label")
        if cur == "genuine" or (cur is None and labs and labs[0] == "genuine" and len(set(labs)) == 1):
            continue
        conf[key] = {"label": "genuine", "reason": "rule 5 (high): fixed-output constraint (" + ",".join(sorted(ids)) +
                     "); a strict success is exactly the fixed string, the only answer that follows the constraint",
                     "reads": labs, "round": "R5"}
        n += 1
    json.dump(conf, open(cf, "w"), indent=1)
    print("rule-5 confirmations added:", n, "| total confirmations", len(conf))


if __name__ == "__main__":
    main()
