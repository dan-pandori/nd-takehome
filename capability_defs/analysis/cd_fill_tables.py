#!/usr/bin/env python3
"""capability-defs: replace the §3 tables in REPORT.md with the ones `cd_report_tables.py` just rendered
(out/report_tables.md), so no table is hand-copied.  Tables are located by their header line; the J9 and compute
tables fill the ⟨S38 TABLE⟩ / ⟨COMPUTE TABLE⟩ slots the first time and are located by header afterwards.

  python3 capability_defs/analysis/cd_report_tables.py > capability_defs/analysis/out/report_tables.md
  python3 capability_defs/analysis/cd_fill_tables.py
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPORT = os.path.join(HERE, '..', 'REPORT.md')
TABLES = os.path.join(HERE, 'out', 'report_tables.md')


def blocks(md):
    out, cur, title = {}, [], None
    for line in md.splitlines():
        if line.startswith('## '):
            if title:
                out[title] = '\n'.join(l for l in cur if l.startswith('|'))
            title, cur = line[3:].strip(), []
        else:
            cur.append(line)
    if title:
        out[title] = '\n'.join(l for l in cur if l.startswith('|'))
    return out


def replace_table(text, header_prefix, new):
    lines = text.split('\n')
    for i, l in enumerate(lines):
        if l.startswith(header_prefix):
            j = i
            while j < len(lines) and lines[j].startswith('|'):
                j += 1
            return '\n'.join(lines[:i] + new.split('\n') + lines[j:]), True
    return text, False


def main():
    s = open(REPORT).read()
    B = blocks(open(TABLES).read())
    done = []
    for title, header in (('bracket verdicts at K_eval-set', '| r8-solved hard theorems, verdict at K_eval-set'),
                          ('created sets', '| definition (card) | r8, x0'),
                          ('coverage', '| seed | base within reach at K_eval-set')):
        s, ok = replace_table(s, header, B[title])
        done.append((title, ok))
    for title, slot, header in (('J9', '⟨S38 TABLE⟩', '| seed | theorem | r8 pass@1'),
                                ('compute', '⟨COMPUTE TABLE⟩', '| job | A40-hours')):
        if slot in s:
            s = s.replace(slot, B[title]); done.append((title, True))
        else:
            s, ok = replace_table(s, header, B[title]); done.append((title, ok))
    open(REPORT, 'w').write(s)
    print('replaced:', done)


if __name__ == '__main__':
    main()
