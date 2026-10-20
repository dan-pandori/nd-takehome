#!/usr/bin/env python3
"""Read a checkpoint's metadata (`extra`: training curve, final_val, steps, ...) without torch (run kalmar-complexity).

A torch .pt file is a zip whose data.pkl references tensor storages; this unpickler stubs the storages and tensor
rebuilds, so plain-Python fields (the curve) come back intact.  `python3 kalmar_complexity/ckpt_meta.py <ckpt>`.
"""
import json, pickle, sys, zipfile


class _Stub:
    def __init__(self, *a, **k):
        pass

    def __call__(self, *a, **k):
        return None


class _U(pickle.Unpickler):
    def find_class(self, mod, name):
        if mod.startswith('torch') or mod.startswith('collections') and name == 'OrderedDict' and False:
            return _Stub()
        try:
            return super().find_class(mod, name)
        except Exception:
            return _Stub()

    def persistent_load(self, pid):
        return None


def meta(fn):
    z = zipfile.ZipFile(fn)
    pk = next(n for n in z.namelist() if n.endswith('data.pkl'))
    obj = _U(z.open(pk)).load()
    return obj


if __name__ == '__main__':
    o = meta(sys.argv[1])
    print(type(o), list(o.keys()) if isinstance(o, dict) else '')
    ex = o.get('extra', {}) if isinstance(o, dict) else {}
    print({k: (v if k != 'curve' else f'{len(v)} points') for k, v in ex.items()} if isinstance(ex, dict) else ex)
