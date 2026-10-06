#!/usr/bin/env bash
# Third GPU queue (after chain 2): phase 1b generation (sigma advisory + placebo, eag_lc1),
# Study 2 replications at 1.5B and 7B (4-bit), judge pass over all new outputs.
# Analyses are run afterwards, once new ambiguous cases have been audited.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8
CFG=configs/pilot_v0.1.yaml
LOG=09_reports/chain3.log
step() { echo "=== $(date '+%F %T') $*" | tee -a "$LOG"; }

step "1/4 phase 1b generate (eag_lc1, advisory + placebo)"
python -m eaa.eag.advisory generate --score-col eag_lc1 >>"$LOG" 2>&1
step "2/4 study2 run (Qwen2.5-1.5B)"
python -m eaa.study2 run --model 03_models/Qwen2.5-1.5B-Instruct --tag qwen2.5-1.5b >>"$LOG" 2>&1
step "3/4 study2 run (Qwen2.5-7B, 4-bit)"
python -m eaa.study2 run --model 03_models/Qwen2.5-7B-Instruct --tag qwen2.5-7b --load-in-4bit --batch-size 4 >>"$LOG" 2>&1   # bs 4: 8 GB VRAM spills at bs 8
step "4/4 judge all new outputs"
python -m eaa.judge --config $CFG --extra \
  05_outputs/pilot_v0.2_qwen2.5-3b/sigma_advisory_eag_lc1.jsonl \
  05_outputs/study2_qwen2.5-3b/generations.jsonl \
  05_outputs/study2_qwen2.5-1.5b/generations.jsonl \
  05_outputs/study2_qwen2.5-7b/generations.jsonl >>"$LOG" 2>&1
step "DONE"
