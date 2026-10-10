#!/usr/bin/env bash
# Study 3 (+3b): sigma on fresh items -> Qwen advice/placebo -> Gemma off/advice/placebo -> judge.
# Ollama and HF models are never on the GPU together (8 GB). Logs to 09_reports/chain5.log.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8
LOG=09_reports/chain5.log
step() { echo "=== $(date '+%F %T') $*" | tee -a "$LOG"; }
unload() { ollama stop gemma4:e4b >/dev/null 2>&1 || true; }

step "1/6 packets";                       python -m eaa.study3 packets >>"$LOG" 2>&1
unload
if [ ! -f 08_architecture/features_study3.pt ]; then
  step "2/6 features (Qwen2.5-3B frozen)"
  python -m eaa.eag.features --packets 01_data/study3_packets.jsonl --out 08_architecture/features_study3.pt --batch-size 4 >>"$LOG" 2>&1
fi
step "3/6 sigma (eag_lc1, no retraining)"; python -m eaa.study3 sigma >>"$LOG" 2>&1
step "4/6 generate Qwen advice + placebo"; python -m eaa.study3 generate --tag qwen2.5-3b --batch-size 4 >>"$LOG" 2>&1
step "5/6 generate Gemma off + advice + placebo"; python -m eaa.study3 generate --tag gemma4-e4b --batch-size 8 >>"$LOG" 2>&1
unload
step "6/6 judge new outputs"
python -m eaa.judge --config configs/pilot_v0.1.yaml --extra \
  05_outputs/study3_qwen2.5-3b/generations.jsonl 05_outputs/study3_gemma4-e4b/generations.jsonl >>"$LOG" 2>&1
step "DONE"
