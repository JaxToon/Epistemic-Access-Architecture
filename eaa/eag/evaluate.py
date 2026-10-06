"""Evaluate trained heads on the pilot test set (HotpotQA dev sample, never used for training).

All gates rank the SAME generator outputs (pilot `off`, Qwen2.5-3B). v0.2 (methodology review,
amended before any test result — see 05_preregistration_EAG_phase1.md §5):

  PRIMARY population  primary items, answered == 1 (a gate can only withhold substantive answers;
                      rows the generator already abstained on would otherwise be ranked as err=0)
  AURC                tie-aware (expected risk under random order within tied scores)
  H5a/H5b/H5c         eag_lc1 − {reader_p_suff, probe_lc1, qe_lc1}, one paired item bootstrap,
                      Holm over the three two-sided p
  H6                  untrained intervention: Δσ(full − drop_other) [drop_other never seen in
                      training], eag_lc1 − eag_lc0, bootstrap CI; plus AURC non-inferiority margin
  extra baselines     cue_only (logistic regression on surface cues of the packet: titles,
                      question-title overlap, length) and oracles (level==full, answer_available)
Also writes sigma_test.csv (consumed by advisory.py) and the test packets (--make-test-packets).
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from .. import prompts as P
from ..analyze import holm
from ..data import load_items
from .features import question_of
from .model import EpistemicHead
from .train import HELD_OUT_LEVELS, auroc, predict

H6_AURC_MARGIN = 0.005
B = 1000


def make_test_packets(pilot_dir: Path, items_path: Path, out: Path):
    q = {it["id"]: it["question"] for it in load_items(items_path)}
    with open(pilot_dir / "packets.jsonl", encoding="utf-8") as f, open(out, "w", encoding="utf-8") as g:
        for line in f:
            p = json.loads(line)
            g.write(json.dumps({"item_id": p["item_id"], "level": p["level"], "split": "test",
                                "prompt": P.GENERATOR.format(evidence=p["evidence"], advisory="",
                                                             question=q[p["item_id"]])},
                               ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- AURC (tie-aware, vectorised)
def aurc(score: np.ndarray, err: np.ndarray) -> float:
    n = len(score)
    if n == 0:
        return float("nan")
    o = np.argsort(-score, kind="mergesort")
    s, e = score[o], err[o].astype(float)
    blk = np.r_[0, np.cumsum(s[1:] != s[:-1])]
    size = np.bincount(blk)
    bsum = np.bincount(blk, weights=e)
    start = np.r_[0, np.cumsum(size)[:-1]]
    before = np.r_[0.0, np.cumsum(bsum)[:-1]]
    pos_in = np.arange(n) - start[blk] + 1
    exp_cum = before[blk] + bsum[blk] * pos_in / size[blk]
    return float((exp_cum / np.arange(1, n + 1)).mean())


# ---------------------------------------------------------------- surface-cue baseline
_UNIT = re.compile(r"^\[e\d+\] \((.*?)\) (.*)$", flags=re.M)


def cue_features(prompt: str) -> list[float]:
    units = _UNIT.findall(prompt)
    titles = [t for t, _ in units]
    qtok = {w for w in re.findall(r"\w+", question_of(prompt).lower()) if len(w) > 3}
    ttok = set(re.findall(r"\w+", " ".join(titles).lower()))
    etok = set(re.findall(r"\w+", " ".join(x for _, x in units).lower()))
    counts = pd.Series(titles).value_counts()
    return [len(set(titles)), len(units), counts.max(), (counts >= 2).sum(),
            len(qtok & ttok) / max(len(qtok), 1), len(qtok & etok) / max(len(qtok), 1),
            sum(len(x) for _, x in units) / 1000]


def fit_cue_baseline(train_packets: Path):
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    X, y = [], []
    for line in open(train_packets, encoding="utf-8"):
        r = json.loads(line)
        if r["split"] == "train" and r["level"] not in HELD_OUT_LEVELS:
            X.append(cue_features(r["prompt"]))
            y.append(int(r["level"] == "full"))
    return make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(X, y)


# ---------------------------------------------------------------- main
def load_sigmas(features_path: str, runs_dir: Path, test_packets: Path, train_packets: Path):
    data = torch.load(features_path, weights_only=False)
    meta, feats = data["meta"], data["feats"]
    sig = pd.DataFrame([{"item_id": m["item_id"], "level": m["level"]} for m in meta])
    device = "cuda" if torch.cuda.is_available() else "cpu"
    summary = json.loads((runs_dir / "train_summary.json").read_text())
    names = [r["name"] for r in summary]
    idx = list(range(len(meta)))
    for name in names:
        c = torch.load(runs_dir / f"{name}.pt", weights_only=False, map_location="cpu")
        model = EpistemicHead(c["d"], c["n_layers_g"], c["variant"]).to(device)
        model.load_state_dict(c["state"])
        sig[name] = 1 / (1 + np.exp(-predict(model, feats, idx, device)))
    cfgs = sorted({n.rsplit("_s", 1)[0] for n in names})
    for cfg in cfgs:
        sig[cfg] = sig[[n for n in names if n.rsplit("_s", 1)[0] == cfg]].mean(1)
    # surface-cue baseline
    cue = fit_cue_baseline(train_packets)
    prompts = {(r["item_id"], r["level"]): r["prompt"]
               for r in map(json.loads, open(test_packets, encoding="utf-8"))}
    X = [cue_features(prompts[(i, l)]) for i, l in zip(sig["item_id"], sig["level"])]
    sig["cue_only"] = cue.predict_proba(X)[:, 1]
    return sig, cfgs, names


def paired_boot(d: pd.DataFrame, gates: list[str], rng) -> dict:
    """Point AURC + bootstrap replicates for every gate on the same resampled items."""
    items = d["item_id"].unique()
    rows_of = {i: g.index.to_numpy() for i, g in d.groupby("item_id")}
    err = d["hallucination"].to_numpy()
    S = {g: d[g].to_numpy() for g in gates}
    point = {g: aurc(S[g], err) for g in gates}
    reps = {g: np.empty(B) for g in gates}
    for b in range(B):
        ix = np.concatenate([rows_of[i] for i in rng.choice(items, len(items))])
        for g in gates:
            reps[g][b] = aurc(S[g][ix], err[ix])
    return point, reps


def _p(diff):
    return float(min(1.0, max(2 * min((diff >= 0).mean(), (diff <= 0).mean()), 1 / len(diff))))


def main():
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--make-test-packets", action="store_true")
    ap.add_argument("--pilot-dir", default="05_outputs/pilot_v0.2_qwen2.5-3b")
    ap.add_argument("--items", default="01_data/hotpot_dev_n500_seed20261005.jsonl")
    ap.add_argument("--test-packets", default="01_data/eag_test_packets.jsonl")
    ap.add_argument("--train-packets", default="01_data/eag_train_packets.jsonl")
    ap.add_argument("--features", default="08_architecture/features_test.pt")
    ap.add_argument("--runs", default="08_architecture/eag_runs")
    ap.add_argument("--eval-csv", default="06_evaluation/pilot_v0.2_qwen2.5-3b/eval.csv")
    ap.add_argument("--out", default="07_analysis/eag_phase1")
    ap.add_argument("--seed", type=int, default=20261005)
    args = ap.parse_args()

    if args.make_test_packets:
        make_test_packets(Path(args.pilot_dir), Path(args.items), Path(args.test_packets))
        print(f"wrote {args.test_packets}")
        return

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    sig, cfgs, names = load_sigmas(args.features, Path(args.runs), Path(args.test_packets),
                                   Path(args.train_packets))
    sig.to_csv(out / "sigma_test.csv", index=False)

    ev = pd.read_csv(args.eval_csv)
    off = ev[ev["system"] == "off"].merge(sig, on=["item_id", "level"], how="inner")
    off["oracle_full"] = (off["level"] == "full").astype(float)
    off["oracle_answer"] = off["answer_available"].astype(float)
    gates = cfgs + ["reader_p_suff", "cue_only", "oracle_full", "oracle_answer"]
    rng = np.random.default_rng(args.seed)
    md = ["# EAG phase 1 — gates on pilot `off` outputs\n",
          f"configs: {cfgs}; seeds per config: {len(names) // max(len(cfgs), 1)}\n"]

    pops = [("PRIMARY: primary & answered", off[(off["primary"] == 1) & (off["answered"] == 1)]),
            ("primary, all rows", off[off["primary"] == 1]),
            ("all items, answered", off[off["answered"] == 1])]
    for k, (tag, d) in enumerate(pops):
        d = d.reset_index(drop=True)
        point, reps = paired_boot(d, gates, rng)
        tab = pd.DataFrame([{"gate": g, "aurc": point[g], "ci_lo": np.percentile(reps[g], 2.5),
                             "ci_hi": np.percentile(reps[g], 97.5)} for g in gates])
        tab.loc[len(tab)] = {"gate": "random", "aurc": d["hallucination"].mean(),
                             "ci_lo": np.nan, "ci_hi": np.nan}
        con = []
        if "eag_lc1" in point:
            for hid, ref in [("H5a", "reader_p_suff"), ("H5b", "probe_lc1"), ("H5c", "qe_lc1"),
                             ("cue", "cue_only"), ("H6-AURC", "eag_lc0")]:
                if ref not in point:
                    continue
                diff = reps["eag_lc1"] - reps[ref]
                con.append({"id": hid, "contrast": f"eag_lc1 − {ref}",
                            "diff": point["eag_lc1"] - point[ref],
                            "ci_lo": np.percentile(diff, 2.5), "ci_hi": np.percentile(diff, 97.5),
                            "p": _p(diff)})
            con = pd.DataFrame(con)
            fam = con["id"].isin(["H5a", "H5b", "H5c"])
            con.loc[fam, "p_holm"] = holm(con.loc[fam, "p"].tolist())
            h6 = con["id"] == "H6-AURC"
            con.loc[h6, "non_inferior"] = con.loc[h6, "ci_hi"] < H6_AURC_MARGIN
        md += [f"\n## {tag} (rows={len(d)}, items={d['item_id'].nunique()})\n",
               "```\n" + tab.round(4).to_string(index=False) + "\n```\n"]
        if len(con):
            md += ["Contrasts (AURC diff; negative = eag_lc1 better):\n",
                   "```\n" + con.round(4).to_string(index=False) + "\n```\n"]
        if k == 0:
            tab.to_csv(out / "aurc_primary.csv", index=False)
            if len(con):
                con.to_csv(out / "contrasts_primary.csv", index=False)
            # per-level AURC and per-seed spread (secondary)
            lv = pd.DataFrame([{"level": l, **{g: aurc(x[g].to_numpy(), x["hallucination"].to_numpy())
                                               for g in gates}, "n": len(x)}
                               for l, x in d.groupby("level")])
            seeds = pd.DataFrame([{"run": n, "aurc": aurc(d[n].to_numpy(), d["hallucination"].to_numpy())}
                                  for n in names])
            md += ["Per-level AURC (secondary):\n", "```\n" + lv.round(4).to_string(index=False) + "\n```\n",
                   "Per-seed AURC:\n", "```\n" + seeds.round(4).to_string(index=False) + "\n```\n"]

    # access sensitivity on all primary rows (independent of the generator's output)
    prim = off[off["primary"] == 1]
    sens = []
    piv = {g: prim.pivot_table(index="item_id", columns="level", values=g)
           for g in gates[:-2] if g in prim}
    for g, p in piv.items():
        sens.append({"gate": g,
                     "dsig_full-drop_ans": (p["full"] - p["drop_ans"]).mean(),
                     "dsig_full-drop_other (UNTRAINED)": (p["full"] - p["drop_other"]).mean(),
                     "pairacc_full>drop_ans": (p["full"] > p["drop_ans"]).mean(),
                     "pairacc_full>drop_other": (p["full"] > p["drop_other"]).mean(),
                     "auroc_suff(full)": auroc((prim["level"] == "full").to_numpy().astype(int), prim[g].to_numpy())})
    sens = pd.DataFrame(sens)
    h6 = {}
    if "eag_lc1" in piv and "eag_lc0" in piv:
        a = (piv["eag_lc1"]["full"] - piv["eag_lc1"]["drop_other"]).to_numpy()
        b = (piv["eag_lc0"]["full"] - piv["eag_lc0"]["drop_other"]).to_numpy()
        ix = rng.integers(0, len(a), size=(B, len(a)))
        diff = a[ix].mean(1) - b[ix].mean(1)
        h6 = {"H6: Δσ_untrained(eag_lc1) − Δσ_untrained(eag_lc0)": a.mean() - b.mean(),
              "ci_lo": np.percentile(diff, 2.5), "ci_hi": np.percentile(diff, 97.5), "p": _p(diff)}
    sens.to_csv(out / "sensitivity_primary.csv", index=False)
    md += ["\n## Access sensitivity (primary items, all rows; drop_other never seen in training)\n",
           "```\n" + sens.round(4).to_string(index=False) + "\n```\n", f"{h6}\n"]
    (out / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
