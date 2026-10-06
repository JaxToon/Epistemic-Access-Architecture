#!/usr/bin/env bash
# Replaces the tail of chain 2 + chain 3 after VRAM spill slowed Study 2 at batch 8 (2026-10-06 08:25).
# Study 2 runs are resumable (existing keys skipped). Logs to 09_reports/chain4.log.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8
CFG=configs/pilot_v0.1.yaml
LOG=09_reports/chain4.log
step() { echo "=== $(date '+%F %T') $*" | tee -a "$LOG"; }

step "1/6 study2 run Qwen2.5-3B (resume, bs 4; no-op if complete)"
python -m eaa.study2 run --model 03_models/Qwen2.5-3B-Instruct --tag qwen2.5-3b --batch-size 4 >>"$LOG" 2>&1
step "2/6 judge study2 3B"
python -m eaa.judge --config $CFG --extra 05_outputs/study2_qwen2.5-3b/generations.jsonl >>"$LOG" 2>&1
step "3/6 phase 1b generate (eag_lc1, advisory + placebo)"
python -m eaa.eag.advisory generate --score-col eag_lc1 >>"$LOG" 2>&1
step "4/6 study2 run Qwen2.5-1.5B"
python -m eaa.study2 run --model 03_models/Qwen2.5-1.5B-Instruct --tag qwen2.5-1.5b --batch-size 8 >>"$LOG" 2>&1
step "5/6 study2 run Qwen2.5-7B 4-bit"
python -m eaa.study2 run --model 03_models/Qwen2.5-7B-Instruct --tag qwen2.5-7b --load-in-4bit --batch-size 4 >>"$LOG" 2>&1
step "6/6 judge all new outputs"
python -m eaa.judge --config $CFG --extra \
  05_outputs/pilot_v0.2_qwen2.5-3b/sigma_advisory_eag_lc1.jsonl \
  05_outputs/study2_qwen2.5-3b/generations.jsonl \
  05_outputs/study2_qwen2.5-1.5b/generations.jsonl \
  05_outputs/study2_qwen2.5-7b/generations.jsonl >>"$LOG" 2>&1
step "DONE"
