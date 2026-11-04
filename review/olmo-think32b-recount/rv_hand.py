"""Hand-check aggregation (reviewer). Joins the blinded reader labels (hand/reader_labels/*.json) and my classification
(hand/confirm.json) to hand/key.json, then applies the pre-registered rules under four label sets:
  reader    - the blinded readers' labels as given;
  strict    - sound only for class P: a general forward proof of the exact division by 3 (mod-9 expansion
              a = 3m+1, b = 3n+2, or an explicit S^2 - 3ab link) and of coprimality;
  exec_rule - the executor's uniform rule as applied in its notes: P or T (a general residue-representative
              transition) is sound; S (an S-divisibility induction on the recurrence) and C are flawed;
  lenient   - P, T, S or C sound (lowest terms only asserted is accepted; outside the pre-registered definition of
              'flawed', reported as a bound); X (a wrong step that happens to give 248) and G stay as they are.
Classes were assigned after reading my readers' labels: 16 items by my own reading, the rest from the readers'
step records (confirm.json: read_by_reviewer).
Rules (pre-registration): confirmed = >= 2 doubly-credited sound successes, >= 1 drawn after candidacy (defenders:
every success qualifies); hand 'No reach' needs dpo confirmed; hand 'reach' on a problem needs s2300 confirmed and no
sound dpo success among all its credited samples; the verdict needs >= 3 reach problems."""
import collections, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rv_core as C
key = json.load(open(os.path.join(C.HERE, "hand", "key.json")))
lab = {}
for f in sorted(glob.glob(os.path.join(C.HERE, "hand", "reader_labels", "*.json"))):
    for r in json.load(open(f)):
        lab[r["item"]] = r
conf = json.load(open(os.path.join(C.HERE, "hand", "confirm.json")))
missing = sorted(set(key) - set(lab))
SETS = ("reader", "strict", "exec_rule", "lenient")
cells = collections.defaultdict(list)
for i, k in key.items():
    row = dict(k, item=i, cls=conf[i]["class"], reader=lab[i]["label"] if i in lab else None)
    for s in SETS[1:]:
        row[s] = conf[i][s]
    row["doubly"] = bool(k["rl"] and k["final"])
    cells[(k["model"], k["pid"])].append(row)
lines = [f"labels {len(lab)} / {len(key)}; missing: {missing}"]
for c in sorted(cells):
    xs = sorted(cells[c], key=lambda r: r["draw"])
    lines.append(f"{c[0]} {c[1]}:")
    for r in xs:
        lines.append(f"  draw {r['draw']:3d} {r['job']:9s} {'D ' if r['doubly'] else 'rl'} {r['finish']:6s} {r['item']} "
                     f"class={r['cls']} reader={r['reader']} strict={r['strict']} exec_rule={r['exec_rule']} lenient={r['lenient']}")


def sound(model, pid, s, doubly_only):
    return [r["draw"] for r in sorted(cells[(model, pid)], key=lambda r: r["draw"])
            if r[s] == "sound" and (r["doubly"] or not doubly_only)]


def confirmed(model, pid, s, fresh_after):
    xs = sound(model, pid, s, True)
    return len(xs) >= 2 and any(d > fresh_after for d in xs)


res = {}
for s in SETS:
    r = {"dpo_R_sound_any": sound("dpo", "aime2025_28", s, False), "dpo_R_sound_doubly": sound("dpo", "aime2025_28", s, True),
         "dpo_R_confirmed": confirmed("dpo", "aime2025_28", s, 0)}
    for m in ("s2300", "s0750", "s0100"):
        r[f"{m}_R_sound_doubly"] = sound(m, "aime2025_28", s, True)
        r[f"{m}_R_confirmed"] = confirmed(m, "aime2025_28", s, 8)
    r["s2300_V_sound"] = sound("s2300", "aime2026_14", s, True)
    r["s2300_V_confirmed"] = confirmed("s2300", "aime2026_14", s, 0)
    r["dpo_V_sound"] = sound("dpo", "aime2026_14", s, True)
    reach = ["aime2025_28"] if (r["s2300_R_confirmed"] and not r["dpo_R_sound_any"]) else []
    r["hand_reach_problems"] = reach
    r["verdict"] = ("Reach candidates for scale-up" if len(reach) >= 3 else
                    "No reach at 256" if r["dpo_R_confirmed"] else "Inconclusive")
    res[s] = r
    lines.append(f"[{s}] " + json.dumps(r))
counts = collections.Counter((k["model"], k["pid"], conf[i]["class"]) for i, k in key.items())
lines.append("classes per cell: " + json.dumps({f"{a}|{b}|{c}": n for (a, b, c), n in sorted(counts.items())}))
for s2 in ("strict", "exec_rule", "lenient"):
    agree = collections.Counter((lab[i]["label"], conf[i][s2]) for i in key if i in lab)
    lines.append(f"reader vs {s2}: " + json.dumps({f"{a}->{b}": n for (a, b), n in sorted(agree.items())}))
open(os.path.join(C.HERE, "out", "hand.txt"), "w").write("\n".join(lines) + "\n")
json.dump({"result": res, "missing": missing}, open(os.path.join(C.HERE, "out", "hand.json"), "w"), indent=1)
print("\n".join(lines))
