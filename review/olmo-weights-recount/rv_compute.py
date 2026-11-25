"""Reviewer (olmo-weights): compute and cost from the logs. Per job: engine wall seconds on one A40 (summary.json),
bytes downloaded; per pod: billed hours and dollars (~/podhours.log, registry rate), jobs run (bring-up scripts).
Usage: python3 rv_compute.py ROOT"""
import glob, json, os, sys
ROOT = sys.argv[1]
S = f"{ROOT}/artifacts/olmo_weights/stats"
tot_s = tot_b = 0
print("| job | engine wall s (1x A40) | compute s | downloaded TB | GB/s |")
print("|---|---|---|---|---|")
for j in sorted(os.listdir(S)):
    runs = json.load(open(f"{S}/{j}/summary.json"))["runs"]
    w = sum(r["wall_s"] for r in runs); c = sum(r["compute_s"] for r in runs); b = sum(r["downloaded_bytes"] for r in runs)
    tot_s += w; tot_b += b
    print(f"| {j} | {w:.0f} | {c:.0f} | {b/1e12:.3f} | {b/1e9/w:.2f} |")
print(f"| total | {tot_s:.0f} ({tot_s/3600:.2f} h) | | {tot_b/1e12:.3f} | |")
pods = [l.split() for l in open(os.path.expanduser("~/podhours.log")) if " olmo-weights " in l]
h = sum(float(p[3]) for p in pods); d = sum(float(p[4]) for p in pods)
print("\npods (podhours.log):")
for p in pods:
    print(" ", " ".join(p[:5]), " ".join(p[5:]))
print(f"total {h:.4f} h, ${d:.2f}")
