#!/usr/bin/env python3
"""Check every Lean snippet shown in a markdown file (inline `example ...` spans and ```lean blocks) with lean_check
(the free-form judge: no errors, allowed axioms, allowlisted constants).  The textbook72 guard is not run here: the
snippets' theorems are those of EXAMPLES.md (statement-identical up to hypothesis names), which sealed.py checked.

  python3 proof_strategies/blog_lean_check.py proof_strategies/blog.md
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..')); sys.path.insert(0, HERE)
import lean_check                                              # noqa: E402


def snippets(md):
    out = re.findall(r'```lean\n(.*?)```', md, re.S)
    out += [m for m in re.findall(r'`(example [^`]*)`', md)]
    return [s.strip() for s in out]


def main():
    fn = sys.argv[1]
    allsn = snippets(open(fn).read())
    sn = [s for s in allsn if ': Prop)' in s]          # skip schematic syntax notes such as `example (h : A) : B := t`
    srcs = [re.sub(r'^example', 'theorem t', s, count=1) for s in sn]
    res, _, _ = lean_check.check(srcs)
    bad = [(s[:90], r['reason'][:200]) for s, r in zip(sn, res) if not r['ok']]
    print(json.dumps({'file': fn, 'snippets': len(sn), 'accepted': len(sn) - len(bad), 'skipped_schematic': len(allsn) - len(sn), 'bad': bad},
                     ensure_ascii=False, indent=1))
    return not bad


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
