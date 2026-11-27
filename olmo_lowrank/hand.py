#!/usr/bin/env python3
"""Hand gate of run olmo-lowrank (pre-registration preregistration/olmo-lowrank.md, "Grading and hand gate").
VPS side, standard library only; olmo-ifcurve's hand.py machinery (screen, reads, confirmations, identity
inheritance, items, rounds) with this run's scope.

A cell is (job, reach prompt): the 8 arms (16 draws each) and the s2300 endpoint B_s2300 (32 draws, olmo-ifcurve).
Labels needed: per cell the first min(strict, LOOK = 8) strict successes in draw order (chunk, i). Two reads for every
item of the dpo, T1 and T4 arms and for a seeded quarter of the rest (crc32 of the draw key % 4 == 0); a 1-1 split
gets a third read. A draw's label comes from, in order: screen (mechanical rule-1 pre-screen, gamed, no reader);
read (my confirm.csv label, else the majority of reads); inherited (identical whitespace-collapsed answer on the same
prompt with a screen or read label in this run).

  hand.py screen <job> ...            -> hand/screen.csv
  hand.py round <name> [--size N]     needed reads -> items (hand/items/<id>.md, key hand/key.csv), batches
  hand.py status                      pending counts
  hand.py cells                       -> olmo_lowrank/hand_cells.csv (per cell: draws, strict, labelled, genuine, gamed,
                                         estimated genuine rate) and per-arm totals to stdout
  hand.py table                       -> olmo_lowrank/handcheck.csv (every item)
  hand.py calib                       B_s2300 items: this run's label vs olmo-ifcurve's final label -> stdout
  hand.py audit <pid> ...             every label of these prompts across arms, with reader evidence
  hand.py selftest                    screen unit tests (olmo-ifcurve's cases)
"""
import ast
import csv
import gzip
import json
import random
import re
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cells  # noqa: E402

H = cells.A / "hand"
LOOK = 8
JOBS = cells.ARMS + ["B_s2300"]
TWO_READ_ARMS = {"dpo", "T1", "T4"}
PER_SENT = {"sentence:increment", "sentence:alliteration_increment", "words:last_first", "format:emoji"}
_P = None


def problems():
    global _P
    if _P is None:
        _P = {r["pid"]: r for r in map(json.loads, open("olmo_ifomega/problems.jsonl"))}
    return _P


def ids_of(p):
    x = p["instruction_id_list"]
    return list(ast.literal_eval(x) if isinstance(x, str) else x)


def dkey(d):
    return (d["job"], d["pid"], int(d["chunk"]), int(d["i"]))


def one_sentence(a):  # olmo-ifcurve hand.py, verbatim
    t = a.strip()
    for m in re.finditer(r"[.!?]", t):
        rest = re.sub(r"^[.!?\"'”’)\]]*", "", t[m.end():])
        if rest.strip():
            return False
    return True


def screen_reason(pid, ans):  # olmo-ifcurve hand.py, verbatim
    ids = set(ids_of(problems()[pid]))
    a = ans or ""
    if ids & PER_SENT and one_sentence(a):
        return "one sentence (per-sentence constraint)"
    if "format:line_indent" in ids and len([ln for ln in a.splitlines() if ln.strip()]) <= 1:
        return "one non-empty line (line_indent)"
    if "format:sub-bullets" in ids and not any(ln.lstrip().startswith("*") for ln in a.splitlines()):
        return "no line starting with * (sub-bullets)"
    return None


def selftest():
    cases = [("One sentence only.", True), ("No punctuation at all", True), ("Hi. 😀 Next one.", False),
             ("Hello.</i> Next", False), ("Hi.<br>There", False), ("Ends here. 😀", False), ("Wait... what", False),
             ('He said "stop." Then left.', False), ('He said "stop."', True), ("A? B!", False), ("A?!", True),
             ("x.y", False), ("Line one\nLine two", True)]
    bad = [(t, e) for t, e in cases if one_sentence(t) != e]
    print("one_sentence:", "ok" if not bad else f"FAIL {bad}")
    return not bad


def cmd_screen(jobs):
    f = H / "screen.csv"
    old = [r for r in csv.DictReader(open(f))] if f.exists() else []
    old = [r for r in old if r["job"] not in jobs]
    new = []
    R = set(cells.reach())
    for job in jobs:
        strict = {(x["pid"], x["chunk"], x["i"]) for x in cells.rows(job) if x["strict"] and x["pid"] in R}
        sp, _ = cells.paths(job)
        with gzip.open(sp, "rt") as fh:
            it = iter(fh)
            while True:
                try:
                    r = json.loads(next(it))
                except (StopIteration, EOFError, json.JSONDecodeError):
                    break
                k = (r["pid"], int(r["chunk"]), int(r["i"]))
                if k in strict:
                    why = screen_reason(r["pid"], cells.answer_of(r["text"]))
                    if why:
                        new.append({"job": job, "pid": k[0], "chunk": k[1], "i": k[2], "reason": why})
        print(f"screen {job}: {len(strict)} strict reach draws, {sum(1 for x in new if x['job'] == job)} screened")
    H.mkdir(parents=True, exist_ok=True)
    with open(f, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["job", "pid", "chunk", "i", "reason"])
        w.writeheader()
        w.writerows(old + new)


def load_key():
    f = H / "key.csv"
    return list(csv.DictReader(open(f))) if f.exists() else []


def reads():
    out = {}
    for f in sorted((H / "labels").glob("*.json")):
        try:
            data = json.load(open(f))
        except json.JSONDecodeError as e:
            print(f"bad json {f}: {e}", file=sys.stderr)
            continue
        for r in data:
            if r.get("label") in ("genuine", "gamed"):
                out.setdefault(r["item"], []).append((f.stem, r["label"], r))
    return out


def confirms():
    f = H / "confirm.csv"
    return {r["item"]: r for r in csv.DictReader(open(f))} if f.exists() else {}


class Labels:  # olmo-ifcurve hand.py's Labels, unchanged in logic
    def __init__(self):
        self.key = load_key()
        self.item_of = {(r["job"], r["pid"], int(r["chunk"]), int(r["i"])): r["item"] for r in self.key}
        self.row_of = {r["item"]: r for r in self.key}
        self.reads = reads()
        self.conf = confirms()
        self.screen = {}
        f = H / "screen.csv"
        if f.exists():
            for r in csv.DictReader(open(f)):
                self.screen[(r["job"], r["pid"], int(r["chunk"]), int(r["i"]))] = r["reason"]
        self.ans = {}
        for job in JOBS:
            for x in cells.rows(job):
                self.ans[dkey(x)] = x["ans_key"]
        self._inh = None

    def item_label(self, item):
        c = self.conf.get(item)
        if c and c.get("label") in ("genuine", "gamed"):
            return c["label"], "confirmed"
        ls = [lab for _, lab, _ in self.reads.get(item, [])]
        if not ls:
            return None, "unread"
        g, b = ls.count("genuine"), ls.count("gamed")
        if len(ls) == 1:
            return ls[0], "single"
        if g == b:
            return None, "split"
        return ("genuine" if g > b else "gamed"), "majority"

    def inherit_map(self):
        if self._inh is None:
            m = {}
            for k in self.screen:
                ak = self.ans.get(k)
                if ak:
                    m.setdefault((k[1], ak), set()).add("gamed")
            for r in self.key:
                lab, _ = self.item_label(r["item"])
                if lab and r.get("ans_key"):
                    m.setdefault((r["pid"], r["ans_key"]), set()).add(lab)
            self._inh = m
        return self._inh

    def label(self, d):
        k = dkey(d)
        if k in self.screen:
            return "gamed", "screen"
        it = self.item_of.get(k)
        if it:
            lab, st = self.item_label(it)
            if lab:
                return lab, "read"
            if st == "split":
                return None, "split"
        labs = self.inherit_map().get((d["pid"], d["ans_key"])) if d.get("ans_key") else None
        if labs and len(labs) == 1:
            return next(iter(labs)), "inherited"
        if labs:
            return None, "conflict"
        return None, "unread"


def nreads(d):
    if d["job"] in TWO_READ_ARMS:
        return 2
    return 2 if zlib.crc32("|".join(map(str, dkey(d))).encode()) % 4 == 0 else 1


def cell_draws(job, pid):
    return sorted(cells.by_pid(job).get(pid, []), key=lambda x: (x["chunk"], x["i"]))


def needed(L):
    """draw key -> (draw, reads required) for the first min(strict, LOOK) strict successes of every cell."""
    req = {}
    for job in JOBS:
        for pid in cells.reach():
            s = [x for x in cell_draws(job, pid) if x["strict"]]
            for d in s[:LOOK]:
                req[dkey(d)] = (d, nreads(d))
    return req


def write_item(item, d, text, p):  # olmo-ifcurve hand.py, verbatim
    ids = ids_of(p)
    kw = p["kwargs"]
    kw = ast.literal_eval(kw) if isinstance(kw, str) else kw
    g = None
    for ln in open(cells.paths(d["job"])[1]):
        r = json.loads(ln)
        if (r["pid"], int(r["chunk"]), int(r["i"])) == (d["pid"], int(d["chunk"]), int(d["i"])):
            g = r
            break
    per = (g or {}).get("per") or [True] * len(ids)
    cons = "\n".join(f"- `{i}` {json.dumps({a: b for a, b in k.items() if b is not None})}: "
                     f"{'followed' if ok else 'NOT followed'} (official strict checker)"
                     for i, k, ok in zip(ids, kw, per))
    body = (f"# Item {item}\n\n## Prompt (as the model received it)\n\n{p['prompt']}\n\n"
            f"## Verifiable constraints\n\n{cons}\n\n## Answer\n\n{cells.answer_of(text)}\n")
    (H / "items" / f"{item}.md").write_text(body)


def cmd_round(name, size=40, s2300_max=None):
    L = Labels()
    req = needed(L)
    todo_new, todo_read = [], []
    for k, (d, nreq) in req.items():
        lab, src = L.label(d)
        if src == "screen":
            continue
        it = L.item_of.get(k)
        if it is None:
            if src == "inherited":
                continue
            todo_new.append(d)
            continue
        lab_i, st = L.item_label(it)
        if st == "confirmed":
            continue
        want = max(nreq, 3) if st == "split" else nreq
        if len(L.reads.get(it, [])) < want:
            todo_read.append(it)
    for k, (d, nreq) in req.items():  # inherited draws whose source item must carry 2 reads
        if nreq == 2 and k not in L.item_of and k not in L.screen:
            for r in L.key:
                if r["pid"] == d["pid"] and r.get("ans_key") == d.get("ans_key"):
                    it = r["item"]
                    if len(L.reads.get(it, [])) < 2 and L.item_label(it)[1] != "confirmed" and it not in todo_read:
                        todo_read.append(it)
    if s2300_max is not None:  # spread the endpoint's items over rounds, mixed with the arms' (seeded choice), before
        # de-duplication so an answer shared with an arm draw is never dropped (ifbench_64 fixed-output answers, r1)
        ns = sorted((d for d in todo_new if d["job"] == "B_s2300"), key=dkey)
        keep = set(map(dkey, random.Random(f"olmo-lowrank-s2300-{name}").sample(ns, min(len(ns), s2300_max))))
        todo_new = [d for d in todo_new if d["job"] != "B_s2300" or dkey(d) in keep]
    seen, new_items = set(), []
    for d in sorted(todo_new, key=dkey):
        ak = (d["pid"], d.get("ans_key"))
        if d.get("ans_key") and ak in seen:
            continue
        seen.add(ak)
        new_items.append(d)
    (H / "items").mkdir(parents=True, exist_ok=True)
    used = {r["item"] for r in L.key}
    rng = random.Random(f"olmo-lowrank-items-{len(L.key)}")
    want_keys = {dkey(d) for d in new_items}
    texts = {}
    for job in sorted({d["job"] for d in new_items}):
        sp, _ = cells.paths(job)
        with gzip.open(sp, "rt") as fh:
            it = iter(fh)
            while True:
                try:
                    r = json.loads(next(it))
                except (StopIteration, EOFError, json.JSONDecodeError):
                    break
                k = (job, r["pid"], int(r["chunk"]), int(r["i"]))
                if k in want_keys:
                    texts[k] = r["text"]
    P = problems()
    added = []
    for d in new_items:
        while True:
            item = "l%06x" % rng.randrange(16 ** 6)
            if item not in used:
                used.add(item)
                break
        write_item(item, d, texts[dkey(d)], P[d["pid"]])
        added.append({"item": item, "job": d["job"], "pid": d["pid"], "chunk": d["chunk"], "i": d["i"],
                      "ans_key": d.get("ans_key", "")})
    key = L.key + added
    with open(H / "key.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["item", "job", "pid", "chunk", "i", "ans_key"])
        w.writeheader()
        w.writerows(key)
    items = [a["item"] for a in added] + todo_read
    random.Random(f"olmo-lowrank-round-{name}").shuffle(items)
    (H / "batches").mkdir(parents=True, exist_ok=True)
    nb = 0
    for k in range(0, len(items), size):
        nb += 1
        (H / "batches" / f"{name}_{nb}.txt").write_text("\n".join(items[k:k + size]) + "\n")
    print(f"round {name}: {len(req)} draws need labels; {len(added)} new items, {len(todo_read)} further reads; "
          f"{nb} batches of <= {size}")


def cmd_status():
    L = Labels()
    pend = {"unread": 0, "split": 0, "conflict": 0, "need2": 0}
    req = needed(L)
    src_n = {}
    for k, (d, nreq) in req.items():
        lab, src = L.label(d)
        src_n[src] = src_n.get(src, 0) + 1
        if lab is None:
            pend[src if src in pend else "unread"] += 1
        it = L.item_of.get(k)
        if it and nreq == 2 and len(L.reads.get(it, [])) < 2 and L.item_label(it)[1] != "confirmed":
            pend["need2"] += 1
    print(f"draws needing labels {len(req)}; sources {src_n}; pending {pend}")
    return pend


def cell_table(L=None):
    L = L or Labels()
    out = []
    for job in JOBS:
        for pid in cells.reach():
            ds = cell_draws(job, pid)
            s = [x for x in ds if x["strict"]]
            labs = [L.label(d) for d in s[:LOOK]]
            g = sum(1 for lab, _ in labs if lab == "genuine")
            b = sum(1 for lab, _ in labs if lab == "gamed")
            unres = sum(1 for lab, _ in labs if lab is None)
            n = len(ds)
            lab_n = g + b
            unl = len(s) - lab_n
            share = g / lab_n if lab_n else 0.0
            est = (g + unl * share) / n if n else None
            srcs = {}
            for lab, src in labs:
                srcs[src] = srcs.get(src, 0) + 1
            out.append({"job": job, "pid": pid, "n": n, "strict": len(s), "labelled": lab_n, "genuine": g, "gamed": b,
                        "unresolved": unres, "est_genuine_rate": "" if est is None else round(est, 6),
                        "sources": " ".join(f"{k}:{v}" for k, v in sorted(srcs.items()))})
    return out


def cmd_cells():
    out = cell_table()
    with open("olmo_lowrank/hand_cells.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print("job       draws strict labelled genuine gamed unresolved mean_est_genuine")
    summ = []
    for job in JOBS:
        xs = [r for r in out if r["job"] == job and r["n"]]
        if not xs:
            continue
        src = {}
        for r in xs:
            for kv in r["sources"].split():
                k, v = kv.split(":")
                src[k] = src.get(k, 0) + int(v)
        g, b = sum(r["genuine"] for r in xs), sum(r["gamed"] for r in xs)
        summ.append({"job": job, "prompts": len(xs), "draws": sum(r["n"] for r in xs), "strict": sum(r["strict"] for r in xs),
                     "labelled": g + b, "genuine": g, "gamed": b, "gamed_share": round(b / (g + b), 4) if g + b else "",
                     "read": src.get("read", 0), "screen": src.get("screen", 0), "inherited": src.get("inherited", 0),
                     "unresolved": sum(r["unresolved"] for r in xs),
                     "est_genuine_rate": round(sum(r["est_genuine_rate"] for r in xs) / len(xs), 6)})
        print(f"{job:9s} {sum(r['n'] for r in xs):5d} {sum(r['strict'] for r in xs):6d} {sum(r['labelled'] for r in xs):8d} "
              f"{sum(r['genuine'] for r in xs):7d} {sum(r['gamed'] for r in xs):5d} {sum(r['unresolved'] for r in xs):10d} "
              f"{sum(r['est_genuine_rate'] for r in xs) / len(xs):.4f}")
    if summ:
        with open("olmo_lowrank/hand_arm_summary.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(summ[0]))
            w.writeheader()
            w.writerows(summ)


def cmd_table():
    L = Labels()
    rows = []
    for r in L.key:
        rs = L.reads.get(r["item"], [])
        lab, st = L.item_label(r["item"])
        c = L.conf.get(r["item"])
        rows.append({"item": r["item"], "job": r["job"], "pid": r["pid"], "chunk": r["chunk"], "i": r["i"],
                     "ans_key": r["ans_key"], "n_reads": len(rs),
                     "reads": " ".join(f"{b}:{lab_}" for b, lab_, _ in rs), "final_label": lab or "", "state": st,
                     "checker_disagree": sum(1 for _, _, x in rs if x.get("checker_agrees") is False),
                     "my_note": (c or {}).get("note", ""),
                     "evidence_1": (rs[0][2].get("evidence", "") if rs else "")[:400]})
    with open("olmo_lowrank/handcheck.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"table: {len(rows)} items -> olmo_lowrank/handcheck.csv")


def cmd_calib():
    L = Labels()
    old = {(r["job"], r["pid"], int(r["chunk"]), int(r["i"])): r["final_label"]
           for r in csv.DictReader(open("olmo_ifcurve/handcheck.csv")) if r["final_label"]}
    agree = dis = 0
    for k, it in L.item_of.items():
        if k[0] != "B_s2300" or k not in old:
            continue
        lab, _ = L.item_label(it)
        if lab is None:
            continue
        agree += lab == old[k]
        dis += lab != old[k]
        if lab != old[k]:
            print("DISAGREE", it, k, "this run:", lab, "olmo-ifcurve:", old[k])
    print(f"B_s2300 items with an olmo-ifcurve final label: {agree + dis}; agree {agree}; disagree {dis}")


def cmd_audit(pids):
    L = Labels()
    for r in sorted(L.key, key=lambda r: (r["pid"], JOBS.index(r["job"]))):
        if r["pid"] not in pids:
            continue
        lab, st = L.item_label(r["item"])
        ev = " || ".join(x.get("evidence", "")[:160] for _, _, x in L.reads.get(r["item"], []))
        print(f"{r['pid']} {r['job']} {r['item']} {lab}/{st}: {ev}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "screen":
        cmd_screen(sys.argv[2:])
    elif cmd == "round":
        cmd_round(sys.argv[2], int(sys.argv[sys.argv.index("--size") + 1]) if "--size" in sys.argv else 40,
                  int(sys.argv[sys.argv.index("--s2300-max") + 1]) if "--s2300-max" in sys.argv else None)
    elif cmd == "status":
        cmd_status()
    elif cmd == "cells":
        cmd_cells()
    elif cmd == "table":
        cmd_table()
    elif cmd == "calib":
        cmd_calib()
    elif cmd == "audit":
        cmd_audit(sys.argv[2:])
    elif cmd == "selftest":
        sys.exit(0 if selftest() else 1)
