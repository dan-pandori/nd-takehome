#!/usr/bin/env bash
# One line per pod: stage / round / last round secs / targets solved / disk / GPU mem.  Usage: pod/coe/status.sh [pods...]
PODS=${@:-$(ls ~/.config/nd-rl/pods/ | grep '^coe-')}
for P in $PODS; do
  timeout 40 podrun $P 'cd /workspace/nd-takehome 2>/dev/null || exit 0
    for d in artifacts/coe/ladder/la_*; do [ -d $d ] || continue
      r=$(ls $d/round_*.json 2>/dev/null | sed "s/.*round_//; s/.json//" | sort -n | tail -1)
      if [ -n "$r" ]; then python3 -c "import json;d=json.load(open(\"$d/round_$r.json\"));print(\"$(basename $d) r$r\", int(d[\"secs\"]), \"s, targets\", d[\"targets_cum\"][\"solved\"], \"transfer\", d[\"transfer_cum\"][\"solved\"], \"mixRL\", d.get(\"mix_rl_records\"), \"peak\", round(d[\"env\"].get(\"peak_alloc_gb\",0),1))"; else echo "$(basename $d) no round yet"; fi
    done
    s=$(ls artifacts/coe/logs/seed_*.log 2>/dev/null | head -1); [ -n "$s" ] && tail -1 $s | cut -c1-90
    g=$(nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader); d=$(df -h / | tail -1 | awk "{print \$5}")
    rd=$(ls artifacts/coe/eval/*.json 2>/dev/null | grep -v args | wc -l)
    echo "gpu $g disk $d reads $rd fails $(grep -l FAILED artifacts/coe/logs/*.log 2>/dev/null | wc -l)"' 2>/dev/null | sed "s/^/$P: /"
done
