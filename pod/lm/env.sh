# sourced by every lit-measures pod job
export PATH=$HOME/.elan/bin:$PATH OMP_NUM_THREADS=8 MKL_NUM_THREADS=8
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True ND_SAMPLE_PATH=fast ND_RUN_ID=lit-measures
cd /workspace/nd-takehome
mkdir -p artifacts/lit-measures/m2/logs ckpts/lm
