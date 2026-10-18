"""Check the 30 canonical examples: source match, reviewer labels, textbook72 class (all keys), Lean acceptance of the
shown Lean text, and that the shown Lean statement IS the ND sequent (an `example` restating the sequent in the
reviewer's own rendering must typecheck from it)."""
import gzip
import json
import re
from nd import parse_prompt, Proof
from cls import classify
from lean import lf, _rec
from sealkey import TB72, key_po, uncurry

E = json.load(open("../artifacts/ps/examples.json"))["examples"]
K = [json.loads(l) for l in gzip.open("../data/ps/in/train_k12.jsonl.gz", "rt")]
TS = [json.loads(l) for l in open("../data/ps/search/tb_schema.checked.jsonl")]
tb = TB72()
tbcur = set()
for r in map(json.loads, open("../data/bs/textbook72.jsonl")):
    p, c = parse_prompt(r["prompt"])
    tbcur.add(key_po(*uncurry(p, c)))
rows = []
srcs = []
for n, e in enumerate(E):
    src = K[e["index"]] if e["source"] == "K12" else TS[e["index"]]
    same = src["prompt"] == e["prompt"] and src.get("proof") == e["proof"]
    p, c = parse_prompt(e["prompt"])
    o = classify(p, c, e["proof"])
    hits = sorted(tb.hits(p, c) | ({"cur_ms"} if key_po(*uncurry(p, c)) in tbcur else set()))
    lean = e["lean"].replace("\n", "\n  ") if False else e["lean"]
    m = re.match(r"example \(([A-Z ]+) : Prop\)", lean)
    atoms = m.group(1).split() if m else []
    head = lean.split(":=", 1)[0]
    nh = len(re.findall(r"\(h\d+ :", head))
    thm = re.sub(r"^example", "theorem {NAME}_ex", lean, count=1)
    hyps = " ".join(f"(h{j + 1} : {lf(x)})" for j, x in enumerate(p))
    restate = f"example (P Q R S : Prop) {hyps} : {lf(c)} := {{NAME}}_ex {' '.join(atoms)} {' '.join(f'h{j + 1}' for j in range(nh))}"
    srcs.append(thm)
    srcs.append(restate)
    rows.append({"n": n, "strategy": e["strategy"], "role": e["role"].split(" (")[0], "source_match": same,
                 "uses": e["strategy"] in o["uses"], "primary": o["primary"], "curried": o["curried"],
                 "n_pruned": o["n_kept"], "tb72_hits": hits, "atoms": atoms, "nh": nh, "np": len(p)})

# Lean: one file, every example as theorem t<k>_ex plus its restatement; errors located by line
import os, subprocess, tempfile
LEANB = os.path.expanduser("~/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean")
lines = ["set_option linter.unusedVariables false"]
pos = []
for k in range(len(rows)):
    thm, rst = srcs[2 * k], srcs[2 * k + 1]
    start = len(lines) + 1
    tl = thm.replace("{NAME}", f"t{k}").split("\n")
    lines += tl
    end = len(lines)
    lines.append(f"#print axioms t{k}_ex")
    lines.append(rst.replace("{NAME}", f"t{k}"))
    pos.append((start, end, end + 1, end + 2))
with tempfile.NamedTemporaryFile("w", suffix=".lean", delete=False, dir="/tmp", prefix="rvps_ex_") as fh:
    fh.write("\n".join(lines) + "\n")
    path = fh.name
out = subprocess.run([LEANB, path], capture_output=True, text=True).stdout
os.unlink(path)
err = [int(x) for x in re.findall(re.escape(os.path.basename(path)) + r":(\d+):\d+: error", out)]
ax = {int(a): b for a, b in re.findall(r"'t(\d+)_ex' depends on axioms: \[([^\]]*)\]", out)}
noax = {int(a) for a in re.findall(r"'t(\d+)_ex' does not depend on any axioms", out)}
for k, r in enumerate(rows):
    s, e_, pa, rs = pos[k]
    r["lean_thm_ok"] = not any(s <= x <= e_ for x in err) and (k in noax or (k in ax and set(a.strip() for a in ax[k].split(",")) <= {"propext", "Classical.choice", "Quot.sound"}))
    r["statement_is_sequent"] = rs not in err and r["lean_thm_ok"]
    r["axioms"] = "none" if k in noax else ax.get(k)
for r in rows:
    print(r["n"], r["strategy"], r["role"], "| src", r["source_match"], "| uses", r["uses"], "| prim", r["primary"],
          "| Lp", r["n_pruned"], "| tb72", r["tb72_hits"] or "-", "| lean", r["lean_thm_ok"], "| stmt=seq",
          r["statement_is_sequent"], "| ax", r["axioms"])
json.dump(rows, open("out/examples_check.json", "w"), indent=1)
