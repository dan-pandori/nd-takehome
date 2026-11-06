"""Per-constraint analysis (pre-registration Design 6), reviewer recount: for every IF reach / reverse candidate under
`strict` (my fates in out/stats.json), each constraint's success rate over all of the losing and winning model's draws
within 256 (from my re-graded per-constraint lists), the binding constraint (lowest rate for the losing model), and
whether the constraint id occurs in RL's IF data (Dolci-Think-RL-32B rows with dataset ['ifeval'], my own parse of
ground_truth), with the RL ids of the same family prefix as a mechanical 'closest kind' proxy.
Output: out/constraints.txt, out/constraints.json, out/rl_if_ids.json"""
import ast
import json
import os
from collections import Counter

import pyarrow.parquet as pq

import rv_core as C
import rv_stats as S


def rl_ids():
    c = Counter()
    n = 0
    for i in range(4):
        t = pq.read_table(os.path.join(C.BIG, "data", "dolci_rl", "data", f"train-0000{i}-of-00004.parquet"),
                          columns=["dataset", "ground_truth"]).to_pylist()
        for r in t:
            if r["dataset"] and r["dataset"][0] == "ifeval":
                n += 1
                gt = ast.literal_eval(r["ground_truth"][0])
                gt = gt[0] if isinstance(gt, list) else gt
                for iid in gt["instruction_id"]:
                    c[iid] += 1
    return n, c


def main():
    n, ids = rl_ids()
    json.dump({"rl_if_prompts": n, "ids": dict(ids.most_common())}, open(os.path.join(C.OUT, "rl_if_ids.json"), "w"),
              indent=1)
    P = C.load_problems()
    cells = S.load()
    st = json.load(open(os.path.join(C.OUT, "stats.json")))
    txt = [f"RL IF prompts {n}; distinct ids {len(ids)}"]
    out = {}
    fam_ids = {}
    for iid in ids:
        fam_ids.setdefault(iid.split(":")[0], []).append(iid)
    for key in ("ifbench|headline", "ifeval|headline"):
        g = st[key]["strict"]
        groups = [("R", p, g["R_fate"][p]["status"]) for p in g["R"]] + [("V", p, g["V_fate"][p]["status"]) for p in g["V"]]
        for side, p, status in groups:
            pr = P[p]
            rate = {}
            for m in ("dpo", "s2300"):
                c = cells[(m, p)]
                per = [x for x in c["per"][:256] if x is not None]
                rate[m] = [round(sum(x[j] for x in per) / len(per), 3) for j in range(len(pr["instruction_id_list"]))]
            loser = "dpo" if side == "R" else "s2300"
            j = min(range(len(rate[loser])), key=lambda k: rate[loser][k])
            iid = pr["instruction_id_list"][j]
            rec = {"task": key.split("|")[0], "side": side, "status": status, "ids": pr["instruction_id_list"],
                   "rate_dpo": rate["dpo"], "rate_s2300": rate["s2300"], "binding": iid,
                   "binding_in_rl": iid in ids, "binding_rl_count": ids.get(iid, 0),
                   "same_family_rl_ids": sorted(fam_ids.get(iid.split(":")[0], []))}
            out[p] = rec
            txt.append(f"{side} {p:12s} {status:22s} binding {iid:38s} in RL {str(iid in ids):5s} dpo {rate['dpo']}"
                       f" s2300 {rate['s2300']} ids {pr['instruction_id_list']}")
    # summary: binding ids among hand-independent reach prompts
    for key in ("ifbench", "ifeval"):
        rs = [v for v in out.values() if v["task"] == key and v["side"] == "R" and v["status"] == "reach"]
        txt.append(f"{key}: strict-reach prompts {len(rs)}; binding id in RL IF data: {sum(v['binding_in_rl'] for v in rs)};"
                   f" binding ids: {dict(Counter(v['binding'] for v in rs).most_common())}")
    json.dump(out, open(os.path.join(C.OUT, "constraints.json"), "w"), indent=1)
    open(os.path.join(C.OUT, "constraints.txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt[-6:]))


if __name__ == "__main__":
    main()
