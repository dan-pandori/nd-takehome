#!/usr/bin/env bash
# kill.sh: stop the sampler, vLLM's EngineCore and its TP workers on this pod (bracket patterns do not match this shell).
pkill -f 'olmo32/[r]unq' ; pkill -f 'olmo32/[j]ob.sh'; pkill -f 'olmo32/[s]ample.py'; sleep 3
pkill -9 -f 'VLLM::[E]ngineCore'; pkill -9 -f 'VLLM::[W]orker'; pkill -9 -f 'olmo32/[s]ample.py'; sleep 2
nvidia-smi --query-gpu=memory.used --format=csv,noheader | tr '\n' ' '; echo
