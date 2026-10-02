# reviewer: A/B/C per seed from EI pend/r8 sample-seed-0 reads (tb72 + h250); exec'd by recheck.py
import json as _j
for _s in (0, 1, 2):
    _pe, _r8 = set(), set(); _names = []
    for _p in ('tb72', 'h250'):
        for _l in open(f'{R}/ei_eval/s{_s}_pend__{_p}_x0.jsonl'):
            _r = _j.loads(_l); _names.append(_r['name'])
            if _r['n_ok']: _pe.add(_r['name'])
        for _l in open(f'{R}/ei_eval/s{_s}_r8__{_p}_x0.jsonl'):
            _r = _j.loads(_l)
            if _r['n_ok']: _r8.add(_r['name'])
    groups[_s] = {n: 'A' if n in _pe else 'B' if n in _r8 else 'C' for n in _names}
