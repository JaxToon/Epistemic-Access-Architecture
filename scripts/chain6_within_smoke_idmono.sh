#!/usr/bin/env bash
# Chain 6 (28 Okt 2026): within-item steering pilot (doc 19) -> random control -> Study 4 smoke test on dev
# -> Phase 5b Indonesian (doc 20). Never touches the Study 4 test pool (no lock file is written).
set -euo pipefail
cd "$(dirname "$0")/.."
LOG=07_analysis/chain6.log
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }
judge() { sleep 15; python -m eaa.judge --config configs/pilot_v0.1.yaml --extra "$@"; }
JUDGE=judge

# 0. wait for the running grid_within process
while tasklist 2>/dev/null | grep -qi "python.exe"; do sleep 30; done
sleep 30
say "grid_within finished"

# 1. label + analyze; pick the best within-item config with the pre-set criterion (doc 19)
$JUDGE 05_outputs/steer_dev_qwen2.5-3b/generations.jsonl >> "$LOG" 2>&1
python -m eaa.steer_dev analyze > 07_analysis/steer_dev_after_within.txt 2>&1
read L R < <(python - <<'PY'
import pandas as pd
T = pd.read_csv("07_analysis/steer_dev/grid.csv")
ok = T[(T.family == "di dalam item") & (T.trigger == "all") & (T.d_halu_drop <= 0.02)]
b = ok.loc[(ok.pulih - ok.rusak).idxmax()]
L, r = b.config.split("_")[1][1:], b.config.split("_r")[1]
print(L, r)
PY
)
say "best within-item config: L=$L r=$R"

# 2. random-direction control at that config
python -m eaa.steer_dev random_within --layer "$L" --rel "$R" >> "$LOG" 2>&1
$JUDGE 05_outputs/steer_dev_qwen2.5-3b/generations.jsonl >> "$LOG" 2>&1
python -m eaa.steer_dev analyze > 07_analysis/steer_dev_after_within.txt 2>&1
say "random control done"

# 3. Study 4 pipeline smoke test on 5 DEV items (separate out dir + smoke lock; test pool untouched)
SM=07_analysis/study4_smoke
mkdir -p "$SM"
python -m eaa.study4 direction --kind within --layer "$L" --rel "$R" >> "$LOG" 2>&1
python -m eaa.study4 packets --items 01_data/hotpot_dev_study2_n400_seed20261006.jsonl --out "$SM" >> "$LOG" 2>&1
python - <<PY
import json, pathlib
rows = [json.loads(l) for l in open("$SM/prompts.jsonl", encoding="utf-8")]
keep = list(dict.fromkeys(r["item_id"] for r in rows))[:5]
with open("$SM/prompts.jsonl", "w", encoding="utf-8") as f:
    for r in rows:
        if r["item_id"] in keep:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
pathlib.Path("$SM/smoke_lock.json").write_text(json.dumps({"version": "SMOKE", "steer_file": "08_architecture/study4_steer_within_L$L.pt"}))
PY
python -m eaa.eag.features --packets "$SM/prompts.jsonl" --out "$SM/features.pt" >> "$LOG" 2>&1
python -m eaa.study4 sigma --out "$SM" >> "$LOG" 2>&1
python -m eaa.study4 generate --items 01_data/hotpot_dev_study2_n400_seed20261006.jsonl --out "$SM" --lock "$SM/smoke_lock.json" >> "$LOG" 2>&1
$JUDGE "$SM/generations.jsonl" >> "$LOG" 2>&1
python -m eaa.study4 k1 --items 01_data/hotpot_dev_study2_n400_seed20261006.jsonl --out "$SM" >> "$LOG" 2>&1
python -m eaa.study4 analyze --items 01_data/hotpot_dev_study2_n400_seed20261006.jsonl --out "$SM" >> "$LOG" 2>&1 || say "smoke analyze FAILED (see log)"
say "study4 smoke test done"

# 4. Phase 5b: translate with Gemma 4 E4B (Ollama), then free its VRAM before Qwen runs
python -m eaa.idmono translate >> "$LOG" 2>&1
curl -s http://localhost:11434/api/generate -d '{"model":"gemma4:e4b","keep_alive":0}' > /dev/null || true
sleep 10
python -m eaa.idmono packets >> "$LOG" 2>&1
python -m eaa.idmono quality >> "$LOG" 2>&1
python -m eaa.idmono generate >> "$LOG" 2>&1
python -m eaa.eag.features --packets 01_data/idmono_packets.jsonl --out 08_architecture/features_idmono.pt >> "$LOG" 2>&1
python -m eaa.idmono sigma >> "$LOG" 2>&1
$JUDGE 05_outputs/idmono_qwen2.5-3b/generations.jsonl >> "$LOG" 2>&1
python -m eaa.idmono analyze > 07_analysis/idmono_summary.txt 2>&1
say "phase 5b done"
