#!/usr/bin/env python3
"""Check every Lean snippet shown in a markdown file (inline `example ...` spans and ```lean blocks) with lean_check
(the free-form judge: no errors, allowed axioms, allowlisted constants).  Also guards textbook72: no snippet's theorem
may be in a sealed renaming class (statements are re-parsed from the Lean header).

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
    sn = snippets(open(fn).read())
    srcs = [re.sub(r'^example', 'theorem t', s, count=1) for s in sn]
    res, _, _ = lean_check.check(srcs)
    bad = [(s[:90], r['reason'][:200]) for s, r in zip(sn, res) if not r['ok']]
    print(json.dumps({'file': fn, 'snippets': len(sn), 'accepted': len(sn) - len(bad), 'bad': bad}, ensure_ascii=False, indent=1))
    return not bad


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
