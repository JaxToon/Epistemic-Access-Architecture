#!/usr/bin/env bash
# Chain 7 (28 Okt 2026): EAG v2 pilot (doc 21). Waits for chain 6b (Phase 5b) to finish, then:
# smoke train+decode -> full train -> decode on dev -> judge -> analyze. Never touches the Study 4 test pool.
set -euo pipefail
cd "$(dirname "$0")/.."
LOG=07_analysis/chain7.log
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }
gpu_idle() { ! tasklist 2>/dev/null | grep -qi "python.exe"; }

# wait: chain 6b prints "phase 5b done"; fall back to two idle checks 60 s apart (in case 6b stopped early)
until grep -q "phase 5b done" 07_analysis/chain6.log 2>/dev/null || { gpu_idle && sleep 60 && gpu_idle; }; do sleep 30; done
sleep 30
say "GPU free; start EAG v2"

python -m eaa.eag.pointer train --smoke >> "$LOG" 2>&1
python -m eaa.eag.pointer decode --smoke >> "$LOG" 2>&1
test -s 07_analysis/eag_v2_smoke/out/generations.jsonl
say "smoke ok"

python -m eaa.eag.pointer train >> "$LOG" 2>&1
say "train done"
sleep 15
python -m eaa.eag.pointer decode >> "$LOG" 2>&1
say "decode done"
sleep 15
python -m eaa.judge --config configs/pilot_v0.1.yaml --extra 05_outputs/eag_v2_dev/generations.jsonl >> "$LOG" 2>&1
python -m eaa.eag.pointer analyze > 07_analysis/eag_v2_summary.txt 2>&1
say "eag v2 pilot done"
