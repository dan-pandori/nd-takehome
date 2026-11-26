#!/usr/bin/env bash
# bringup2.sh <adapter|f448> ... (pod side): a Part-2 sampling pod. setup.sh (FETCH dpo, plus s2300 when f448 is
# asked for), the GPU gate, the named adapters from this run's bucket path with every file's sha256 checked against
# artifacts/olmo_lowrank/stage0/adapters_verify.json (written on the pod that built them), the F448 weights built and
# checked (adapters.py f448) when asked for, then one queue worker per GPU (start.sh). Run detached.
cd /workspace/nd-takehome; A=artifacts/olmo_lowrank; mkdir -p $A/logs $A/meta /workspace/lowrank/adapters
L=$A/logs/bringup2.log; log() { echo "$(date -u +%FT%TZ) $*" >> $L; }
log START "$*"
F="dpo"; for x in "$@"; do [ "$x" = f448 ] && F="dpo s2300"; done
FETCH="$F" bash pod/olmo_lowrank/setup.sh > $A/logs/setup.log 2>&1
grep -q SETUP_DONE $A/logs/setup.log && touch $A/meta/setup.done
grep -q "^GPU_OK" $A/meta/gpu_status 2>/dev/null || { log GPU_BAD; exit 1; }
log SETUP_OK
until [ -x /opt/hfv/bin/hf ] || grep -q -i error $A/logs/hfv.log; do sleep 5; done
for x in "$@"; do
  [ "$x" = f448 ] && continue
  /opt/hfv/bin/hf buckets sync hf://buckets/dan-pandori/nd-rl/olmo-lowrank/artifacts/olmo_lowrank/adapters/$x /workspace/lowrank/adapters/$x >> $A/logs/adapters_dl.log 2>&1
done
python - "$@" >> $L 2>&1 <<'PY'
import hashlib, json, sys
V = json.load(open("artifacts/olmo_lowrank/stage0/adapters_verify.json"))["files"]
bad = 0
for x in sys.argv[1:]:
    if x == "f448":
        continue
    h = hashlib.sha256(open(f"/workspace/lowrank/adapters/{x}/adapter_model.safetensors", "rb").read()).hexdigest()
    c = hashlib.sha256(open(f"/workspace/lowrank/adapters/{x}/adapter_config.json", "rb").read()).hexdigest()
    ok = h == V[x]["sha256"] and c == V[x]["config_sha256"]
    bad += not ok
    print("ADAPTER_SHA", x, "ok" if ok else f"MISMATCH {h}")
print("ADAPTERS_SHA_PASS" if not bad else "ADAPTERS_SHA_FAIL")
PY
grep -q ADAPTERS_SHA_PASS $L || { log ADAPTER_CHECK_FAILED; exit 1; }
case " $* " in *" f448 "*)
  until [ -f /workspace/models/dpo/.complete ] && [ -f /workspace/models/s2300/.complete ]; do sleep 15; done
  python olmo_lowrank/shacheck.py /workspace/models/dpo 32B/dpo /workspace/models/s2300 32B/rl/2300 > $A/meta/sha_check_$(hostname).txt 2>&1
  grep -q SHA_FAIL $A/meta/sha_check_$(hostname).txt && { log SHA_FAIL; exit 1; }
  python olmo_lowrank/adapters.py f448 --dpo /workspace/models/dpo --rl /workspace/models/s2300 --dst /workspace/models/f448 > $A/logs/f448_build.log 2>&1
  grep -q "f448 PASS" $A/logs/f448_build.log || { log F448_FAIL; exit 1; }
  cp /workspace/models/f448/f448_check.json $A/meta/f448_check.json; log F448_OK ;;
esac
bash pod/olmo_lowrank/start.sh >> $L 2>&1
log WORKERS
