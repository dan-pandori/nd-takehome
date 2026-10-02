# start checkpoint of (seed, start): trajectory's kept Stage-1 checkpoints.  start = p0 p1600 p5000 p12000 p16000 pend
startck() { local S=$1 P=$2; if [ $P = pend ]; then echo ckpts/tj/stage1_best12_s${S}_b1200.pt; else echo ckpts/tj/stage1_best12_s${S}_b1200_step${P#p}.pt; fi; }
