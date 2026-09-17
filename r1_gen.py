#!/usr/bin/env python3
"""run1-lean: vLLM generation on the pod.

  python r1_gen.py --model Qwen/Qwen3-Coder-30B-A3B-Instruct --prompts data/r1/prompts.jsonl \
      --forms tokens,lean,english --draws 0,1,2,3,4 --n 8 --temperature 0.7 --greedy --out artifacts/r1/gen_coder30b.jsonl

One record per prompt: {id, form, draw, name, greedy: str|None, samples: [str]*n, prompt_tokens, gen_tokens}.
Resumable: prompts whose id is already in --out are skipped. Qwen3 hybrid models run in non-thinking mode.
"""
import argparse, json, os, sys, time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True)
    ap.add_argument('--prompts', required=True)
    ap.add_argument('--forms', default='tokens,lean,english')
    ap.add_argument('--draws', default='0,1,2,3,4')
    ap.add_argument('--names', default=None, help='file with one theorem name per line (restrict)')
    ap.add_argument('--n', type=int, default=8)
    ap.add_argument('--temperature', type=float, default=0.7)
    ap.add_argument('--greedy', action='store_true')
    ap.add_argument('--max_tokens', type=int, default=2048)
    ap.add_argument('--max_model_len', type=int, default=12288)
    ap.add_argument('--gpu_mem', type=float, default=0.90)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', required=True)
    ap.add_argument('--chunk', type=int, default=600, help='prompts per llm.chat call (checkpointing granularity)')
    ap.add_argument('--tp', type=int, default=1)
    a = ap.parse_args()

    forms = set(a.forms.split(','))
    draws = set(int(x) for x in a.draws.split(','))
    names = set(open(a.names).read().split()) if a.names else None
    done = set()
    if os.path.exists(a.out):
        for l in open(a.out):
            if l.strip():
                done.add(json.loads(l)['id'])
    todo = []
    for l in open(a.prompts):
        p = json.loads(l)
        if p['form'] in forms and p['draw'] in draws and (names is None or p['name'] in names) and p['id'] not in done:
            todo.append(p)
    todo.sort(key=lambda p: (p['draw'], p['form']))
    print(f'{len(todo)} prompts to do ({len(done)} already in {a.out})', flush=True)
    if not todo:
        return

    from vllm import LLM, SamplingParams
    llm = LLM(model=a.model, max_model_len=a.max_model_len, gpu_memory_utilization=a.gpu_mem, seed=a.seed,
              enable_prefix_caching=True, tensor_parallel_size=a.tp, dtype='bfloat16')
    sp_sample = SamplingParams(n=a.n, temperature=a.temperature, top_p=1.0, max_tokens=a.max_tokens, seed=a.seed) if a.n > 0 else None
    sp_greedy = SamplingParams(n=1, temperature=0.0, max_tokens=a.max_tokens) if a.greedy else None
    kw = {'chat_template_kwargs': {'enable_thinking': False}}
    t0 = time.time()
    with open(a.out, 'a') as f:
        for c in range(0, len(todo), a.chunk):
            chunk = todo[c:c + a.chunk]
            msgs = [p['messages'] for p in chunk]
            recs = [{'id': p['id'], 'form': p['form'], 'draw': p['draw'], 'name': p['name'], 'model': a.model,
                     'greedy': None, 'samples': [], 'prompt_tokens': None, 'gen_tokens': 0} for p in chunk]
            if sp_greedy is not None:
                outs = llm.chat(msgs, sp_greedy, use_tqdm=False, **kw)
                for r, o in zip(recs, outs):
                    r['greedy'] = o.outputs[0].text
                    r['prompt_tokens'] = len(o.prompt_token_ids)
                    r['gen_tokens'] += len(o.outputs[0].token_ids)
                    r['greedy_finish'] = o.outputs[0].finish_reason
            if sp_sample is not None:
                outs = llm.chat(msgs, sp_sample, use_tqdm=False, **kw)
                for r, o in zip(recs, outs):
                    r['samples'] = [x.text for x in o.outputs]
                    r['sample_finish'] = [x.finish_reason for x in o.outputs]
                    r['prompt_tokens'] = len(o.prompt_token_ids)
                    r['gen_tokens'] += sum(len(x.token_ids) for x in o.outputs)
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
            f.flush()
            print(f'{time.strftime("%H:%M:%S")} {c + len(chunk)}/{len(todo)} done, {time.time() - t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()
