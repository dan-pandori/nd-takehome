"""Hand-check bookkeeping (reviewer, olmo-ifomega): reader labels (hand/reader_labels/*.json) joined to the item keys
(hand/key_r*.json), my own overrides (hand/confirm.json: {item_id: {"label": ..., "note": ...}}), controls, and the
hand status of every candidate under two mappings of 'unsure': `strict` (unsure = not genuine / not sound) and
`lenient` (unsure = genuine / sound). good = genuine (IF) or sound (OMEGA).

Hand rules (pre-registration Design 3-5 and Verdict, read with the hand labels):
  reach R:  hand_reach      = s2300 has >= 2 good successes within 256, >= 1 of them fresh, AND every dpo success
                              within 256 has been read and none is good;
            hand_dpo_resolved = >= 2 good dpo successes;
            hand_dissolved  = dpo not resolved and every success of every challenger read, none confirmed
                              (with intermediate checkpoints never extended, only possible where s2300 is the only
                              challenger);
            open            = anything else (`need` lists what is missing).
  reverse V: mirrored (s2300 defender, dpo challenger).
Output: out/hand.json, out/hand.txt, out/hand_need_r<next>.json (what a next round must read)."""
import glob
import json
import os
import sys
from collections import Counter, defaultdict

import rv_core as C
import rv_stats as S

HAND = os.path.join(C.HERE, "hand")
GOOD = {"genuine", "sound"}
OM_SUCCESS = "union"  # OMEGA successes: credited by omega or rl ("union") or by both ("doubly"); argv[1]


def load_labels():
    key = {}
    for f in sorted(glob.glob(os.path.join(HAND, "key_r*.json"))):
        key.update(json.load(open(f)))
    lab = {}
    for f in sorted(glob.glob(os.path.join(HAND, "reader_labels", "*.json"))):
        for x in json.load(open(f)):
            lab[x["id"]] = dict(x, _file=os.path.basename(f))
    conf = {}
    cf = os.path.join(HAND, "confirm.json")
    if os.path.exists(cf):
        conf = json.load(open(cf))
    return key, lab, conf


def final_label(iid, lab, conf):
    if iid in conf:
        return conf[iid]["label"], "reviewer"
    if iid in lab:
        return lab[iid]["label"], "reader"
    return None, None


def is_good(label, mapping):
    if label is None:
        return None
    if label == "unsure":
        return mapping == "lenient"
    return label in GOOD


def main():
    global OM_SUCCESS
    if len(sys.argv) > 1:
        OM_SUCCESS = sys.argv[1]
    key, lab, conf = load_labels()
    cells = S.load()
    st = json.load(open(os.path.join(C.OUT, "stats.json")))
    out = {"n_items": len(key), "n_labelled": sum(1 for i in key if i in lab)}
    txt = []
    # ---- controls
    reals = {}
    for iid, k in key.items():
        if k["kind"] == "real":
            reals[(k["pid"], k["job"], k["chunk"], k["i"])] = iid
    dup = []
    for iid, k in key.items():
        if k["kind"] == "duplicate":
            twin = reals.get((k["pid"], k["job"], k["chunk"], k["i"]))
            dup.append((iid, twin, final_label(iid, lab, {})[0], final_label(twin, lab, {})[0]))
    sw = [(iid, final_label(iid, lab, {})[0], lab.get(iid, {}).get("main_request")) for iid, k in key.items()
          if k["kind"] == "swapped"]
    out["controls"] = {"duplicates": dup, "swapped": sw}
    txt.append(f"items {len(key)}, labelled {out['n_labelled']}, reviewer overrides {len(conf)}")
    txt.append(f"duplicates agree: {sum(1 for d in dup if d[2] == d[3] and d[2])}/{sum(1 for d in dup if d[2] and d[3])}"
               f" {[d for d in dup if d[2] != d[3]]}")
    txt.append(f"swapped controls labelled gamed: {sum(1 for s in sw if s[1] == 'gamed')}/{sum(1 for s in sw if s[1])} {sw}")
    # ---- labels by (task, pid, model, draw)
    by = defaultdict(dict)
    for iid, k in key.items():
        if k["kind"] != "real":
            continue
        L, src = final_label(iid, lab, conf)
        by[(k["task"], k["pid"], k["model"])][k["draw"]] = (L, src, iid, k["fixed"])
    # label counts
    cnt = Counter()
    for iid, k in key.items():
        if k["kind"] == "real":
            cnt[(k["task"], k["model"], final_label(iid, lab, conf)[0])] += 1
    out["label_counts"] = {"|".join(map(str, k)): v for k, v in sorted(cnt.items(), key=str)}
    txt.append("label counts (task, model, label): " + json.dumps(out["label_counts"]))
    need = []
    res = {}
    for mapping in ("strict", "lenient"):
        res[mapping] = {}
        for tkey, grades in (("ifbench|headline", ("strict",)), ("ifeval|headline", ("strict",)),
                             ("omega_out|headline", ("omega", "rl"))):
            task = tkey.split("|")[0]
            R = sorted(set().union(*[set(st[tkey][g]["R"]) for g in grades]))
            V = sorted(set().union(*[set(st[tkey][g]["V"]) for g in grades]))

            def side(m, p):
                c = cells[(m, p)]
                if task.startswith("if"):
                    fl = c["g"]["strict"][:256]
                elif OM_SUCCESS == "doubly":
                    fl = [a and b for a, b in zip(c["g"]["omega"][:256], c["g"]["rl"][:256])]
                else:
                    fl = [a or b for a, b in zip(c["g"]["omega"][:256], c["g"]["rl"][:256])]
                succ = [(j + 1, c["fixed"][j]) for j, f in enumerate(fl) if f]
                labs = by.get((task, p, m), {})
                read = [(d, fx, is_good(labs[d][0], mapping)) for d, fx in succ if d in labs and labs[d][0]]
                unread = [(d, fx) for d, fx in succ if d not in labs or not labs[d][0]]
                good = [d for d, fx, g in read if g]
                good_fresh = [d for d, fx, g in read if g and not fx]
                read_fresh = [d for d, fx, g in read if not fx]
                return {"n": len(fl), "succ": len(succ), "read": len(read), "unread": len(unread),
                        "good": len(good), "good_fresh": len(good_fresh), "unread_draws": [d for d, _ in unread],
                        "complete": len(fl) >= 256, "fresh_draws": sum(1 for x in c["fixed"][:256] if not x),
                        "read_fresh": len(read_fresh),
                        "unread_fresh": sum(1 for d, fx in unread if not fx)}

            def stop_rule(x):
                # reviewer's stopping rule for reading a challenger (fixed 2026-11-06 08:15 UTC, before reading any
                # executor hand-check file): >= 9 read, >= 6 of them fresh, <= 1 good -> stop, prompt open
                return x["read"] >= 9 and x["read_fresh"] >= 6 and x["good"] <= 1

            tres = {}
            for p in R:
                d = side("dpo", p)
                s = side("s2300", p)
                chal = ["s2300"] + [m for m in ("s0100", "s0750") if (m, p) in cells
                                    and sum(cells[(m, p)]["g"][grades[0]][:8]) > 0]
                s_conf = s["good"] >= 2 and s["good_fresh"] >= 1
                if d["good"] >= 2:
                    status = "dpo_resolved"
                elif s_conf and d["good"] == 0 and d["unread"] == 0 and d["complete"]:
                    status = "reach"
                elif (d["unread"] == 0 and d["good"] < 2 and s["unread"] == 0 and s["complete"] and not s_conf
                      and chal == ["s2300"]):
                    status = "dissolved"
                else:
                    status = "open"
                    if s["fresh_draws"] == 0 and not s_conf:
                        status = "open_challenger_unextended"
                    elif stop_rule(s) and not s_conf:
                        status = "open_gamed_dominated"
                    elif d["good"] == 1 and d["unread"] == 0:
                        status = "open_dpo_one_good"
                    if d["good"] < 2 and d["unread"]:
                        need.append((mapping, tkey, p, "dpo", d["unread_draws"]))
                    if (not s_conf and s["unread_fresh"] and not (d["good"] >= 2) and not stop_rule(s)
                            and s["fresh_draws"] > 0):
                        need.append((mapping, tkey, p, "s2300", s["unread_draws"]))
                tres[p] = {"status": status, "dpo": d, "s2300": s, "challengers": chal, "side": "R"}
            for p in V:
                s = side("s2300", p)
                d = side("dpo", p)
                d_conf = d["good"] >= 2 and d["good_fresh"] >= 1
                if s["good"] >= 2:
                    status = "s2300_resolved"
                elif d_conf and s["good"] == 0 and s["unread"] == 0 and s["complete"]:
                    status = "reverse"
                elif s["unread"] == 0 and d["unread"] == 0 and not d_conf:
                    status = "dissolved"
                else:
                    status = "open"
                    if s["good"] < 2 and s["unread"]:
                        need.append((mapping, tkey, p, "s2300", s["unread_draws"]))
                    if not d_conf and d["unread"] and not (s["good"] >= 2):
                        need.append((mapping, tkey, p, "dpo", d["unread_draws"]))
                tres[p] = {"status": status, "dpo": d, "s2300": s, "side": "V"}
            res[mapping][tkey] = tres
            stc = Counter(v["status"] for v in tres.values() if v["side"] == "R")
            vtc = Counter(v["status"] for v in tres.values() if v["side"] == "V")
            nreach = stc["reach"]
            verdict = ("Reach" if nreach >= 3 else "No reach at 256" if all(
                v["status"] in ("dpo_resolved", "dissolved") for v in tres.values() if v["side"] == "R") else "Inconclusive")
            txt.append(f"[{mapping}] {tkey}: R {dict(stc)} V {dict(vtc)} -> {verdict}")
            for p, v in sorted(tres.items()):
                if v["status"] not in ("dpo_resolved", "s2300_resolved"):
                    txt.append(f"    {v['side']} {p}: {v['status']} dpo succ {v['dpo']['succ']} read {v['dpo']['read']}"
                               f" good {v['dpo']['good']} | s2300 succ {v['s2300']['succ']} read {v['s2300']['read']}"
                               f" good {v['s2300']['good']} fresh {v['s2300']['good_fresh']}")
    out["status"] = res
    sfx = "" if OM_SUCCESS == "union" else "_doubly"
    json.dump(out, open(os.path.join(C.OUT, f"hand{sfx}.json"), "w"), indent=1)
    nxt = len(glob.glob(os.path.join(HAND, "key_r*.json"))) + 1
    json.dump(need, open(os.path.join(HAND, f"need_r{nxt}{sfx}.json"), "w"), indent=0)
    open(os.path.join(C.OUT, f"hand{sfx}.txt"), "w").write("\n".join(txt) + "\n")
    print("\n".join(txt))
    print(f"need for round {nxt}: {len(need)} (side, prompt) entries")


if __name__ == "__main__":
    main()
