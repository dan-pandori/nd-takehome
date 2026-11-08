"""Was the pre-registered hand-gate protocol followed? (run olmo-transplant; reviewer's check of handcheck.csv)
Second reader on every gamed label and >= 15 % of genuine; third reader on splits; majority decides; adjudications.
Also the per-(prompt, cell) read caps. Output: out/protocol.txt"""
import collections
import csv
import json

from rvt_core import RAW, Tee
from rvt_labels import table

P = Tee("protocol.txt")
rows = list(csv.DictReader(open(RAW / "olmo_transplant" / "handcheck.csv")))
src = list(csv.DictReader(open(RAW / "olmo_transplant" / "handcheck_src.csv")))
for name, rs in (("run reads (handcheck.csv)", rows), ("calibration source reads (handcheck_src.csv)", src)):
    c = collections.Counter()
    first_gamed_single = []
    for r in rs:
        labs = [x.split(":")[-1] for x in r["reader_labels"].split()]
        c[(r["final_label"], len(labs))] += 1
        if labs and labs[0] == "gamed" and len(labs) < 2:
            first_gamed_single.append(r["item"])
        if len(set(labs)) > 1 and len(labs) < 3 and not r["adjudicated"]:
            c["split_without_third"] += 1
        if r["adjudicated"]:
            c[("adjudicated", r["adjudicated"], r["majority"])] += 1
        if r["final_label"] != r["majority"] and not r["adjudicated"]:
            c["final!=majority_unadjudicated"] += 1
    gen1 = [r for r in rs if r["reader_labels"].split()[0].split(":")[-1] == "genuine"]
    gen2 = [r for r in gen1 if int(r["n_readers"]) >= 2]
    P(f"{name}: {len(rs)} items; (final, n readers) {dict(sorted((k, v) for k, v in c.items() if isinstance(k, tuple) and k[0] != 'adjudicated'))}")
    P(f"   first-reader gamed with no second read: {len(first_gamed_single)}; first-reader genuine re-read: {len(gen2)} / {len(gen1)} "
      f"({100 * len(gen2) / max(1, len(gen1)):.1f} %); splits without a third read or adjudication: {c['split_without_third']}; "
      f"final != majority without adjudication: {c['final!=majority_unadjudicated']}")
    P(f"   adjudications (label, majority): {dict((k[1:], v) for k, v in c.items() if isinstance(k, tuple) and k[0] == 'adjudicated')}")
    P(f"   r6 flagged: {[(r['item'], r['pid'], r['final_label']) for r in rs if r.get('r6') == 'True']}")
# read caps per (prompt, run-condition)
CAP = {"T1": 2, "T2": 2, "T3": 4, "T4": 4, "T0": 4, "B": 1, "P": 1, "F": 2}
CAPC = {"T1": 1, "T2": 1, "T3": 1, "T4": 1, "T0": 1}
lab = table()
reads = collections.Counter((r["job"], r["pid"], r["cell"]) for r in lab if r["src"] == "read")
over = []
for (job, pid, cell), n in reads.items():
    base = cell if cell[0] == "T" else cell.rstrip("0123456789")
    cap = CAPC.get(base, 0) if job.startswith("C") else CAP[base]
    if n > cap:
        over.append((job, pid, cell, n, cap))
P(f"reads per (prompt, run-condition) above the pre-registered cap: {len(over)} {over[:10]}")
cal_bp = [k for k in reads if k[0].startswith("C") and (k[2].startswith("B") or k[2] == "P")]
P(f"calibration B / P cells with reads (pre-registered: strict only): {len(cal_bp)}")
