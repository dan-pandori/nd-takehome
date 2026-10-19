#!/usr/bin/env python3
"""Phase-2 sub-audit (TAXONOMY §6 'the 12 snippets in blog.md'): extract the Lean snippets exactly as
blog_lean_check.py does and judge them with lean_check's own prelude via _run (not check(): no registry row).
Prints counts only."""
import os, re, sys, tempfile
os.environ["LEAN"] = os.path.expanduser("~/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean")
sys.path.insert(0, "/home/dan/work/proof-strategies")
import lean_check  # noqa: E402
md = open("/home/dan/work/proof-strategies/proof_strategies/blog.md").read()
allsn = re.findall(r'```lean\n(.*?)```', md, re.S) + re.findall(r'`(example [^`]*)`', md)
allsn = [s.strip() for s in allsn]
sn = [s for s in allsn if ': Prop)' in s]
srcs = [re.sub(r'^example', 'theorem t', s, count=1) for s in sn]
wd = tempfile.mkdtemp(prefix="tx_blog_", dir="/tmp")
res, _ = lean_check._run(srcs, wd, "b")
os.rmdir(wd)
print("snippets (all / with ': Prop)'):", len(allsn), "/", len(sn), "| accepted:", sum(r['ok'] for r in res),
      "| sizes:", [r['size'] for r in res])
EX = __import__('json').load(open("/home/dan/work/proof-strategies/artifacts/ps/examples.json"))["examples"]
exl = {e['lean'].strip() for e in EX}
print("snippets that are verbatim an examples.json Lean text:", sum(1 for s in sn if s in exl))
