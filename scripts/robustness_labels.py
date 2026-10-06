"""Label-robustness re-analysis (2026-10-06).

Recomputes the pre-registered confirmatory contrasts under three label sets:
  audit_then_judge  primary (audit labels override judge; judge fills the rest)
  judge             LLM judge only (EAA_LABELS=judge)
  strict            rule only (containment; ambiguous -> wrong)

Never overwrites primary outputs. Writes:
  07_analysis/robustness/evals/pilot_<labels>.csv      relabelled pilot eval (copy of the run dir in scratch)
  07_analysis/robustness/pilot_<labels>/contrasts_primary.csv (+ param_known / param_unknown strata)
  07_analysis/robustness/study2_<labels>/{contrasts,sources}.csv
EAG (H5/H6) is run separately via `python -m eaa.eag.evaluate --eval-csv ... --out 07_analysis/robustness/eag_<labels>`.

Usage: CUDA_VISIBLE_DEVICES="" python scripts/robustness_labels.py --scratch <dir>
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eaa import evaluate as E  # noqa: E402
from eaa import judge as J  # noqa: E402
from eaa.analyze import aurc_table, contrasts, holm, selective_risk_diff, summary_table  # noqa: E402
from eaa.data import load_items  # noqa: E402
from eaa.study2 import ITEMS as S2_ITEMS, PROMPTS, _source  # noqa: E402

MODES = ["audit_then_judge", "judge", "strict"]
OUT = Path("07_analysis/robustness")


_ORIG_LOAD = J.load_cache


def cache_for(mode: str) -> dict:
    return {} if mode == "strict" else _ORIG_LOAD(mode=mode)


def pilot(mode: str, scratch: Path, cfg: dict):
    src = Path("05_outputs") / cfg["run_name"]
    run_dir = scratch / f"pilot_{mode}" / cfg["run_name"]
    run_dir.mkdir(parents=True, exist_ok=True)
    for fn in ("generations.jsonl", "packets.jsonl"):
        shutil.copy2(src / fn, run_dir / fn)
    J.load_cache = lambda *a, **k: cache_for(mode)          # evaluate() imports it at call time
    ev_path = E.evaluate(run_dir, Path(cfg["items_path"]))  # writes into the scratch copy
    assert scratch in ev_path.parents, ev_path
    (OUT / "evals").mkdir(parents=True, exist_ok=True)
    dst = OUT / "evals" / f"pilot_{mode}.csv"
    shutil.copy2(ev_path, dst)
    df = pd.read_csv(dst)
    od = OUT / f"pilot_{mode}"
    od.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(cfg["seed"])
    for tag, sub in [("primary", df[df["primary"] == 1]),
                     ("primary_param_unknown", df[(df["primary"] == 1) & (df["param_known"] == 0)]),
                     ("primary_param_known", df[(df["primary"] == 1) & (df["param_known"] == 1)])]:
        summary_table(sub, rng)                      # consume RNG exactly as eaa.analyze.main does,
        con = contrasts(sub, cfg, rng)               # so the primary-label run reproduces its CIs
        aurc_table(sub, rng)
        con.to_csv(od / f"contrasts_{tag}.csv", index=False)
    print(f"[pilot {mode}] judge_missing={int(df['judge_missing'].sum())} -> {od}")
    return dst


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    ph = k / n
    c = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    m = (ph + z * z / (2 * n)) / (1 + z * z / n)
    return (m - c, m + c)


def study2(mode: str, tag: str = "qwen2.5-3b"):
    """Replicates eaa.study2.analyze (same RNG seed / order) with a chosen label set."""
    from scipy.stats import binomtest

    E.JUDGED.clear()
    E.JUDGED.update(cache_for(mode))
    out_dir = Path("05_outputs") / f"study2_{tag}"
    gold = {it["id"]: it["answer"] for it in load_items(S2_ITEMS)}
    pk = {(r["item_id"], r["level"], r["policy"]): r
          for r in map(json.loads, open(out_dir / "packets.jsonl", encoding="utf-8"))}
    rows = []
    for r in map(json.loads, open(out_dir / "generations.jsonl", encoding="utf-8")):
        p = pk[(r["item_id"], r["level"], r["policy"])]
        lab = E.label(r["output"], gold[r["item_id"]], r["item_id"])
        rows.append({**{k: r[k] for k in ("item_id", "level", "policy", "prompt", "output")},
                     "qclass": p["qclass"], "apd": p["answer_para_defined"],
                     "source": _source(E.normalize_answer(r["output"]), p["evidence"], p["gold_flags"],
                                       E.normalize_answer) if lab["hallucination"] else None, **lab})
    df = pd.DataFrame(rows)
    (OUT / "evals").mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "evals" / f"study2_{mode}.csv", index=False)
    prim = df[(df["qclass"] == "open") & (df["apd"] == True)]  # noqa: E712
    rng = np.random.default_rng(20261006)
    con = []
    for cid, prompt, lv in [("S2-H1", "extractive", "drop_ans"), ("S2-H2", "extractive", "drop_all"),
                            ("S2-H1(open)", "open", "drop_ans"), ("S2-H2(open)", "open", "drop_all")]:
        s = prim[(prim["prompt"] == prompt) & (prim["level"] == lv)]
        w = s.pivot_table(index="item_id", columns="policy", values="hallucination").dropna()
        a, b = w["entity_poor"].to_numpy(), w["entity_rich"].to_numpy()
        n01, n10 = int(((a == 0) & (b == 1)).sum()), int(((a == 1) & (b == 0)).sum())
        p = binomtest(min(n01, n10), n01 + n10).pvalue if n01 + n10 else 1.0
        ix = rng.integers(0, len(a), size=(2000, len(a)))
        d = b[ix].mean(1) - a[ix].mean(1)
        con.append({"id": cid, "prompt": prompt, "level": lv, "n_items": len(a),
                    "halluc_poor": a.mean(), "halluc_rich": b.mean(), "diff": b.mean() - a.mean(),
                    "ci_lo": np.percentile(d, 2.5), "ci_hi": np.percentile(d, 97.5),
                    "poor0_rich1": n01, "poor1_rich0": n10, "p": p})
    con = pd.DataFrame(con)
    fam = con["id"].isin(["S2-H1", "S2-H2", "S2-H1(open)"])
    con.loc[fam, "p_holm"] = holm(con.loc[fam, "p"].tolist())
    src = []
    for prompt in PROMPTS:
        for lv in ["full", "drop_ans", "drop_all"]:
            h = prim[(prim["prompt"] == prompt) & (prim["level"] == lv) & (prim["hallucination"] == 1)]
            k = int(h["source"].isin(["in_gold_unit", "in_filler_or_distractor"]).sum())
            lo, hi = wilson(k, len(h))
            vc = h["source"].value_counts(normalize=True)
            src.append({"prompt": prompt, "level": lv, "n_halluc": len(h),
                        "copied_from_packet": k / max(len(h), 1), "wilson_lo": lo, "wilson_hi": hi,
                        "from_gold_unit": vc.get("in_gold_unit", 0),
                        "from_filler": vc.get("in_filler_or_distractor", 0),
                        "not_in_packet": vc.get("not_in_packet", 0)})
    src = pd.DataFrame(src)
    od = OUT / f"study2_{mode}"
    od.mkdir(parents=True, exist_ok=True)
    con.to_csv(od / "contrasts.csv", index=False)
    src.to_csv(od / "sources.csv", index=False)
    print(f"[study2 {mode}] judge_missing={int(df['judge_missing'].sum())} primary items={prim['item_id'].nunique()}")


def selective_risk_jump(mode: str):
    """Exploratory finding (pilot) and its replication on fresh items (Study 2):
    selective risk = hallucinations / answered, full -> drop_ans, paired item bootstrap (B=2000).
    Not part of a pre-registered Holm family; reported with 95% CI only."""
    rows = []
    pe = pd.read_csv(OUT / "evals" / f"pilot_{mode}.csv")
    pe = pe[(pe["primary"] == 1) & (pe["system"] == "off")]
    rng = np.random.default_rng(20261006)
    rows.append({"study": "pilot (exploratory)", "prompt": "extractive", "policy": "length",
                 **selective_risk_diff(pe[pe["level"] == "full"], pe[pe["level"] == "drop_ans"], rng)})
    se = pd.read_csv(OUT / "evals" / f"study2_{mode}.csv")
    se = se[(se["qclass"] == "open") & (se["apd"] == True)]  # noqa: E712
    for prompt in PROMPTS:
        for pol in ["entity_poor", "entity_rich"]:
            s = se[se["prompt"] == prompt]
            rows.append({"study": "study2 (fresh items)", "prompt": prompt, "policy": pol,
                         **selective_risk_diff(s[s["level"] == "full"],
                                               s[(s["level"] == "drop_ans") & (s["policy"] == pol)], rng)})
    out = pd.DataFrame(rows)
    out.insert(0, "labels", mode)
    out.to_csv(OUT / f"selective_risk_{mode}.csv", index=False)
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--config", default="configs/pilot_v0.1.yaml")
    a = ap.parse_args()
    cfg = yaml.safe_load(open(a.config, encoding="utf-8"))
    orig_load = J.load_cache
    for m in MODES:
        J.load_cache = orig_load
        pilot(m, Path(a.scratch).resolve(), cfg)
        J.load_cache = orig_load
        study2(m)
        selective_risk_jump(m)


if __name__ == "__main__":
    main()
