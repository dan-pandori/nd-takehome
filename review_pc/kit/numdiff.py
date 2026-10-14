#!/usr/bin/env python3
"""Reviewer (paper-clean) E1/E6 aid: number-by-number diff, marked reading copy vs clean copy.
Numbers are extracted from LaTeX after removing comments, \\label/\\ref/\\cref/\\cite*/\\input/\\includegraphics
arguments and \\rv wrappers (kept content), and from the blog after removing the YAML front matter and the
librarian's header note. Each file's number sequence is aligned with difflib; every non-equal opcode is printed with
both contexts, so each changed / dropped / added number can be judged in place."""
import re, sys, difflib, collections, os
M, C = sys.argv[1], sys.argv[2]
FILES = ['main.tex'] + [f'sections/{f}' for f in sorted(os.listdir(os.path.join(C, 'sections')))] + ['blog.md']
NUM = re.compile(r'\d+(?:[.,]\d+)*')

def clean_tex(s):
    s = re.sub(r'(?<!\\)%.*', '', s)
    s = re.sub(r'\\(label|ref|cref|Cref|eqref|autoref|pageref|input|include|bibliography|bibliographystyle|url|href)\*?(\[[^\]]*\])?\{[^}]*\}', ' ', s)
    s = re.sub(r'\\(cite[a-z]*)\*?(\[[^\]]*\])*\{[^}]*\}', ' ', s)
    s = re.sub(r'\\includegraphics(\[[^\]]*\])?\{[^}]*\}', ' ', s)
    s = re.sub(r'\\(hspace|vspace|setlength|addtolength)\*?\{[^}]*\}(\{[^}]*\})?', ' ', s)
    s = re.sub(r'(\[|,\s*)(width|height|scale|trim|angle)\s*=\s*[^,\]]*', ' ', s)
    s = s.replace('{,}', ',').replace('\\,', ' ').replace('\\!', '')
    return s

def clean_md(s):
    s = re.sub(r'\A---\n.*?\n---\n', '', s, flags=re.S)
    s = re.sub(r'\A\s*(>.*\n)+', '', s)             # librarian header note (blockquote at top)
    s = re.sub(r'\]\([^)]*\)', ']', s)               # link targets (figure paths)
    return s

def nums(path):
    s = open(path, encoding='utf-8').read()
    s = clean_md(s) if path.endswith('.md') else clean_tex(s)
    out = []
    for i, line in enumerate(s.split('\n'), 1):
        for m in NUM.finditer(line):
            out.append((m.group().replace(',', ''), i, line))
    return out

tot = collections.Counter()
for f in FILES:
    a, b = nums(os.path.join(M, f)), nums(os.path.join(C, f))
    sa, sb = [x[0] for x in a], [x[0] for x in b]
    ops = [o for o in difflib.SequenceMatcher(None, sa, sb, autojunk=False).get_opcodes() if o[0] != 'equal']
    ca, cb = collections.Counter(sa), collections.Counter(sb)
    print(f'=== {f}: marked {len(sa)} numbers, clean {len(sb)}; multiset only-marked {sum((ca-cb).values())}, only-clean {sum((cb-ca).values())}; aligned diff ops {len(ops)}')
    for tag, i1, i2, j1, j2 in ops:
        tot[tag] += 1
        ma = ' '.join(sa[i1:i2]); mb = ' '.join(sb[j1:j2])
        ctxa = a[i1][2].strip()[:230] if i2 > i1 else (a[i1-1][2].strip()[:120] if i1 > 0 else '')
        ctxb = b[j1][2].strip()[:230] if j2 > j1 else (b[j1-1][2].strip()[:120] if j1 > 0 else '')
        print(f'  [{tag}] marked L{a[i1][1] if i2>i1 else "-"} {{{ma}}} -> clean L{b[j1][1] if j2>j1 else "-"} {{{mb}}}')
        if f != 'blog.md' or tag != 'delete':
            print(f'      M: {ctxa}\n      C: {ctxb}')
print('opcode totals', dict(tot))
