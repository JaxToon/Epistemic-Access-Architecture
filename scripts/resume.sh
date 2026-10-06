#!/usr/bin/env bash
# Resume everything after the 2026-10-05 pause.
# Already done & saved: pilot generations, EAG features (train + test).
# Re-runs: EAG head training (12 runs, ~6 min; partial runs are overwritten), EAG evaluation,
# then chain 2 (judge -> pilot re-evaluation -> EAG re-evaluation -> Study 2 -> analysis).
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONIOENCODING=utf-8
bash scripts/after_pilot_chain.sh      # skips feature extraction (files exist), trains + evaluates EAG
bash scripts/chain2_judge_study2.sh
