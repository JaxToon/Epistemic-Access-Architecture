#!/usr/bin/env bash
# Second GPU queue: judge-based relabelling of the pilot, re-analysis, EAG re-evaluation on the
# corrected labels, then Study 2 (3B) + its judge pass + analysis. Logs to 09_reports/chain2.log.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8
CFG=configs/pilot_v0.1.yaml
LOG=09_reports/chain2.log
step() { echo "=== $(date '+%F %T') $*" | tee -a "$LOG"; }

step "1/8 judge pilot ambiguous answers";  python -m eaa.judge --config $CFG >>"$LOG" 2>&1
step "2/8 judge vs Claude audit agreement"; python -m eaa.judge_agreement >>"$LOG" 2>&1
step "3/8 re-evaluate pilot";               python -m eaa.evaluate --config $CFG >>"$LOG" 2>&1
step "4/8 re-analyze pilot";                python -m eaa.analyze  --config $CFG >>"$LOG" 2>&1
if [ -f 08_architecture/eag_runs/train_summary.json ]; then
  step "5/8 EAG evaluate on corrected labels"; python -m eaa.eag.evaluate >>"$LOG" 2>&1
fi
step "6/8 study2 run (Qwen2.5-3B)";          python -m eaa.study2 run --model 03_models/Qwen2.5-3B-Instruct --tag qwen2.5-3b >>"$LOG" 2>&1
step "7/8 judge study2";                     python -m eaa.judge --config $CFG --extra 05_outputs/study2_qwen2.5-3b/generations.jsonl >>"$LOG" 2>&1
step "8/8 study2 analyze";                   python -m eaa.study2 analyze --tag qwen2.5-3b >>"$LOG" 2>&1
step "DONE"
