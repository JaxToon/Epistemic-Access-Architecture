#!/usr/bin/env bash
# Runs, in order, everything that follows the pilot generation run. Each step is idempotent-ish
# and logs to 09_reports/chain.log. Stops at the first failure.
set -euo pipefail
cd "$(dirname "$0")/.."
CFG=configs/pilot_v0.1.yaml
LOG=09_reports/chain.log
mkdir -p 09_reports 08_architecture
step() { echo "=== $(date '+%F %T') $*" | tee -a "$LOG"; }

step "1/6 evaluate pilot";  python -m eaa.evaluate --config $CFG >>"$LOG" 2>&1
step "2/6 analyze pilot";   python -m eaa.analyze  --config $CFG >>"$LOG" 2>&1
if [ ! -f 08_architecture/features_train.pt ]; then
  step "3/6 features train (27.7k packets)"
  python -m eaa.eag.features --packets 01_data/eag_train_packets.jsonl --out 08_architecture/features_train.pt --batch-size 4 >>"$LOG" 2>&1
fi
if [ ! -f 08_architecture/features_test.pt ]; then
  step "4/6 features test (pilot packets)"
  python -m eaa.eag.features --packets 01_data/eag_test_packets.jsonl --out 08_architecture/features_test.pt --batch-size 4 >>"$LOG" 2>&1
fi
step "5/6 train heads";     python -m eaa.eag.train --features 08_architecture/features_train.pt --ablate-contrast >>"$LOG" 2>&1
step "6/6 evaluate EAG";    python -m eaa.eag.evaluate >>"$LOG" 2>&1
step "DONE"
