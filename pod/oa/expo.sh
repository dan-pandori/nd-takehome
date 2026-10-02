#!/usr/bin/env bash
# organism-analysis Q2 exposure counts (CPU) for all 18 ladders.
. pod/oa/env.sh
for S in 0 1 2; do
  python3 oa/oa_exposure.py --ladder trajectory/artifacts/tj/la_T1_best12_s$S --out artifacts/oa/exposure/c12_s$S.json
  python3 oa/oa_exposure.py --ladder trajectory-cap6/artifacts/tj6/la_T1_best6_s$S --out artifacts/oa/exposure/c6_s$S.json
  for X in p1600 p5000 p12000 p16000; do
    python3 oa/oa_exposure.py --ladder rl-from-ckpt/artifacts/rfc/la_T1_best12_s${S}_$X --out artifacts/oa/exposure/rfc_s${S}_$X.json
  done
  up artifacts/oa
done
echo EXPO_DONE; touch artifacts/oa/expo.done; up artifacts/oa
