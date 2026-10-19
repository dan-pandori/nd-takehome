#!/usr/bin/env python3
"""Equivalence test for run kalmar-pretrain's trainer changes (GPU pod; needs torch).

  python3 kalmar/test_loader_equiv.py <records.jsonl> [n]

1. state_train.load with a process pool returns exactly the serial result (same pairs, same order, same skips).
2. state_train_best.to_device built in blocks returns exactly the tensors of the original one-shot code (copied here
   verbatim), on CPU and on the GPU, for two block sizes.
Exit 1 on any difference.
"""
import os, sys, json, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import torch
from tokenizer import make_tokenizer
import state_train, state_train_best


def to_device_ref(data, dev):    # state_train_best.to_device before run kalmar-pretrain, verbatim
    pairs = [(p, q) for rec in data for p, q in rec]
    lens = torch.tensor([len(p) + len(q) for p, q in pairs], dtype=torch.long)
    plen = torch.tensor([len(p) for p, q in pairs], dtype=torch.long)
    N, T = len(pairs), int(lens.max())
    flat = torch.frombuffer(bytearray(b''.join(p + q for p, q in pairs)), dtype=torch.uint8)
    row = torch.repeat_interleave(torch.arange(N), lens)
    col = torch.arange(len(flat)) - torch.repeat_interleave(lens.cumsum(0) - lens, lens)
    ids = torch.zeros((N, T), dtype=torch.uint8)    # pad = 0
    ids[row, col] = flat
    return ids.to(dev), plen.to(dev), lens, lens.to(dev)


def main():
    fn, n = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    lines = [l for l in open(fn) if l.strip()][:n]
    sub = tempfile.NamedTemporaryFile('w', suffix='.jsonl', delete=False)
    sub.write(''.join(lines)); sub.close()
    tok = make_tokenizer('lean_staten')
    a, sa = state_train.load(sub.name, tok, 0)
    b, sb = state_train.load(sub.name, tok, 0, procs=8)
    ok = True
    print('load: serial', len(a), 'skipped', sa, '| pool', len(b), 'skipped', sb, '| equal', a == b and sa == sb)
    ok &= a == b and sa == sb
    devs = ['cpu'] + (['cuda'] if torch.cuda.is_available() else [])
    for dev in devs:
        ref = to_device_ref(a, dev)
        for ch in (777, 10 ** 9):
            new = state_train_best.to_device(a, dev, chunk=ch)
            eq = all(torch.equal(x.cpu(), y.cpu()) for x, y in zip(ref, new))
            print(f'to_device {dev} chunk {ch}: shapes {tuple(ref[0].shape)} equal {eq}')
            ok &= eq
    os.unlink(sub.name)
    print('ALL EQUAL' if ok else 'DIFFERENCE FOUND')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
