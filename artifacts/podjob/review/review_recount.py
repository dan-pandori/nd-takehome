#!/usr/bin/env python3
"""Reviewer recount of podjob acceptance tests T1-T5 from the raw files (independent of summarize.sh).
Usage: review_recount.py [tests_dir]   (default ~/runs/podjob/tests)"""
import json, os, re, sys, glob
D = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "~/runs/podjob/tests")
L = f"{D}/local/artifacts"
def kv(t):
    s = open(f"{D}/{t}.txt").read()
    g = lambda p: (m := re.search(p, s)) and m.group(1)
    return dict(name=g(r"name (\S+)"), t0=g(r"t0=(\d+)"), exit=g(r"podjob exit (\d+)"),
                absent=g(r"absent from account listing at (\d+)"), kill=g(r"kill \w+(?: \(during creation\))? at (\d+)"))
def rcs(name):
    return [tuple(map(int, open(f).read().split())) for f in sorted(glob.glob(f"{L}/podjob/{name}/job*.rc"))]
def bucket(t):
    return [l.split()[-1] for l in open(f"{D}/{t}.bucket.txt") if f"pjtest/{t}/" in l]
log = open(os.path.expanduser("~/podjob.log")).read().splitlines()
for t in ["T1", "T2", "T3", "T4", "T5", "T1_first", "T5_sigint_ignored"]:
    k = kv(t); r = rcs(k["name"]); ref = int(k["kill"]) if k["kill"] else (max(e for _, e in r) if r else None)
    ready = [l for l in log if k["name"] in l and " READY " in l]
    pods = [l.split()[2] for l in open(os.path.expanduser("~/pods.log")) if k["name"] in l]
    print(f"{t:18s} {k['name']:22s} exit={k['exit']:>3} rcs={r} ref={'signal' if k['kill'] else 'last rc end'} "
          f"gone_s={int(k['absent'])-ref if ref else None} bucket={len(bucket(t)) if t in 'T1T2T3T4T5' else '-'} "
          f"READY_lines={len(ready)} pods_log_ids={pods}")
print("-- T4 per-job files")
iv = []
for f in sorted(glob.glob(f"{L}/pjtest/T4/*.txt")):
    s = open(f).read(); h = re.search(r"host=(\S+) pod=(\S+) start=(\d+)", s); e = re.search(r"end=(\d+)", s)
    iv.append((int(h.group(3)), int(e.group(1)))); print(os.path.basename(f), h.group(1), "RUNPOD_POD_ID=" + h.group(2), iv[-1])
print("overlap(all):", max(a for a, _ in iv) < min(b for _, b in iv), "wall_s:", max(b for _, b in iv) - min(a for a, _ in iv))
print("-- pj- pods in each saved listing")
for t in ["T1", "T2", "T3", "T4", "T5"]:
    print(t, [p["name"] for p in json.load(open(f"{D}/{t}.listing.json")) if p["name"].startswith("pj-")])
h = [l.split() for l in open(os.path.expanduser("~/podhours.log")) if "pj-podjob" in l]
print("-- podhours: n=%d hours=%.4f usd=%.2f" % (len(h), sum(float(x[3]) for x in h), sum(float(x[4]) for x in h)))
