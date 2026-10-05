"""H1–H4 analysis on 06_evaluation/<run>/eval.csv (v0.2).

* Unit of analysis = item. Every contrast is computed within ONE level (one row per item per
  side), so the exact McNemar test is valid; CIs are item bootstrap.
* Primary population: qclass == open and answer in exactly one gold paragraph (`primary`).
* Primary family (Holm-corrected), fixed in configs (pre-registration):
    H1a  off: full -> drop_ans          hallucination   (expect +)
    H1b  off: full -> drop_all          hallucination   (expect +)
    H2   off@restore_from -> restored   hallucination   (expect −)
    H3a  off -> advisory @ drop_ans     hallucination   (two-sided; prediction ≈ 0)
    H3b  advisory -> enforced @ drop_ans selective risk (expect −; 0 = gate no better than random)
    H4   off -> enforced @ full          false refusal   (must stay below pre-registered margin)
  plus H2-equivalence: restored vs restored_ctrl, TOST with pre-registered margin.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy.stats import binomtest

B = 2000
LEVELS = ["full", "drop_ans", "drop_other", "drop_all"]


def _md(df: pd.DataFrame, index: bool = False) -> str:
    try:
        return df.to_markdown(index=index)
    except ImportError:  # tabulate not installed
        return "```\n" + df.to_string(index=index) + "\n```"


def _pairs(a: pd.DataFrame, b: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    return a[["item_id"] + cols].merge(b[["item_id"] + cols], on="item_id", suffixes=("_a", "_b"))


def paired_rate(a, b, col, rng) -> dict:
    m = _pairs(a, b, [col])
    if m.empty:
        return {"n_items": 0}
    x, y = m[f"{col}_a"].to_numpy(), m[f"{col}_b"].to_numpy()
    idx = rng.integers(0, len(x), size=(B, len(x)))
    boots = y[idx].mean(1) - x[idx].mean(1)
    n01, n10 = int(((x == 0) & (y == 1)).sum()), int(((x == 1) & (y == 0)).sum())
    p = binomtest(min(n01, n10), n01 + n10, 0.5).pvalue if n01 + n10 else 1.0
    return {"n_items": len(m), "rate_a": x.mean(), "rate_b": y.mean(), "diff": y.mean() - x.mean(),
            "ci95_lo": np.percentile(boots, 2.5), "ci95_hi": np.percentile(boots, 97.5),
            "ci90_lo": np.percentile(boots, 5), "ci90_hi": np.percentile(boots, 95),
            "a0_b1": n01, "a1_b0": n10, "p": p, "test": "McNemar exact"}


def conditional_rate(a, b, col, cond, rng) -> dict:
    """Paired diff of P(col | cond) between a and b — e.g. false refusal = P(abstain | available)."""
    return paired_rate(a[a[cond] == 1], b[b[cond] == 1], col, rng)


def selective_risk_diff(adv, enf, rng) -> dict:
    """risk = hallucinations / answered. diff < 0 => gate removes wrong answers more than right ones,
    i.e. better than a random gate with the same abstention rate (expected diff = 0)."""
    m = _pairs(adv, enf, ["hallucination", "answered"])
    if m.empty:
        return {"n_items": 0}
    ha, aa = m["hallucination_a"].to_numpy(), m["answered_a"].to_numpy()
    hb, ab = m["hallucination_b"].to_numpy(), m["answered_b"].to_numpy()

    def risk(h, a):
        return h.sum(-1) / np.maximum(a.sum(-1), 1)

    est = risk(hb, ab) - risk(ha, aa)
    idx = rng.integers(0, len(m), size=(B, len(m)))
    boots = risk(hb[idx], ab[idx]) - risk(ha[idx], aa[idx])
    p = 2 * min((boots >= 0).mean(), (boots <= 0).mean())
    return {"n_items": len(m), "rate_a": risk(ha, aa), "rate_b": risk(hb, ab), "diff": est,
            "ci95_lo": np.percentile(boots, 2.5), "ci95_hi": np.percentile(boots, 97.5),
            "ci90_lo": np.percentile(boots, 5), "ci90_hi": np.percentile(boots, 95),
            "coverage_a": aa.mean(), "coverage_b": ab.mean(), "p": max(p, 1 / B),
            "test": "bootstrap (selective risk)"}


def aurc(df: pd.DataFrame, score: str, rng) -> dict:
    """Area under the risk-coverage curve when accepting rows in descending `score` order.
    Error = hallucination of the underlying (ungated) output. Lower is better.
    Random gate => AURC ≈ overall hallucination rate. CI: item bootstrap."""
    d = df[["item_id", score, "hallucination"]].dropna()
    if d.empty:
        return {}

    def curve(x):
        x = x.sort_values(score, ascending=False, kind="mergesort")
        err = x["hallucination"].to_numpy().cumsum()
        return float((err / np.arange(1, len(x) + 1)).mean())

    groups = [g for _, g in d.groupby("item_id")]
    boots = [curve(pd.concat([groups[i] for i in rng.integers(0, len(groups), len(groups))]))
             for _ in range(200)]
    return {"gate_score": score, "n": len(d), "aurc": curve(d),
            "ci95_lo": np.percentile(boots, 2.5), "ci95_hi": np.percentile(boots, 97.5),
            "random_gate": d["hallucination"].mean()}


def aurc_table(df: pd.DataFrame, rng) -> pd.DataFrame:
    """Gates applied to the advisory outputs across all levels (pooled; item-bootstrap CI)."""
    adv = df[df["system"] == "advisory"].copy()
    if adv.empty or "reader_p_suff" not in adv:
        return pd.DataFrame()
    adv["oracle"] = adv["answer_available"] + 1e-3 * rng.random(len(adv))  # tie-break
    rows = [aurc(adv, "reader_p_suff", rng), aurc(adv, "oracle", rng)]
    return pd.DataFrame([r for r in rows if r])


def holm(pvals: list[float]) -> list[float]:
    order = np.argsort(pvals)
    adj, running = [0.0] * len(pvals), 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (len(pvals) - rank) * pvals[i]))
        adj[i] = running
    return adj


def contrasts(df: pd.DataFrame, cfg: dict, rng) -> pd.DataFrame:
    S = lambda s, lv=None: df[(df["system"] == s) & ((df["level"] == lv) if lv else True)]
    rf = cfg["restore_from"]
    rows = []

    def add(cid, hyp, primary, name, res):
        rows.append({"id": cid, "hypothesis": hyp, "primary": primary, "contrast": name, **res})

    add("H1a", "H1", True, "off: full -> drop_ans [halluc]",
        paired_rate(S("off", "full"), S("off", "drop_ans"), "hallucination", rng))
    add("H1b", "H1", True, "off: full -> drop_all [halluc]",
        paired_rate(S("off", "full"), S("off", "drop_all"), "hallucination", rng))
    add("H1c", "H1", False, "off: full -> drop_other [halluc]",
        paired_rate(S("off", "full"), S("off", "drop_other"), "hallucination", rng))
    add("H2", "H2", True, f"off@{rf} -> restored [halluc]",
        paired_rate(S("off", rf), S("restored"), "hallucination", rng))
    add("H2eq", "H2", False, "restored_ctrl -> restored [halluc] (TOST)",
        paired_rate(S("restored_ctrl"), S("restored"), "hallucination", rng))
    add("H3a", "H3", True, "off -> advisory @drop_ans [halluc]",
        paired_rate(S("off", "drop_ans"), S("advisory", "drop_ans"), "hallucination", rng))
    add("H3b", "H3", True, "advisory -> enforced @drop_ans [selective risk]",
        selective_risk_diff(S("advisory", "drop_ans"), S("enforced", "drop_ans"), rng))
    add("H4", "H4", True, "off -> enforced @full [false refusal | answer available]",
        conditional_rate(S("off", "full"), S("enforced", "full"), "abstain", "answer_available", rng))
    for lv in ["full", "drop_other", "drop_all"]:
        add(f"H3a_{lv}", "H3", False, f"off -> advisory @{lv} [halluc]",
            paired_rate(S("off", lv), S("advisory", lv), "hallucination", rng))
        add(f"H3b_{lv}", "H3", False, f"advisory -> enforced @{lv} [selective risk]",
            selective_risk_diff(S("advisory", lv), S("enforced", lv), rng))
    for lv in LEVELS:
        if "enforced_score" in set(df["system"]):
            add(f"H3b_score_{lv}", "H3", False, f"advisory -> enforced_score @{lv} [selective risk]",
                selective_risk_diff(S("advisory", lv), S("enforced_score", lv), rng))
    add("leak", "control", False, "advisory -> advisory_missing @drop_ans [halluc]",
        paired_rate(S("advisory", "drop_ans"), S("advisory_missing", "drop_ans"), "hallucination", rng))

    out = pd.DataFrame(rows)
    prim = out["primary"] & out["p"].notna()
    out.loc[prim, "p_holm"] = holm(out.loc[prim, "p"].tolist())

    m = cfg["equivalence_margin"]
    eq = out["id"] == "H2eq"
    out.loc[eq, "tost_equivalent"] = (out.loc[eq, "ci90_lo"] > -m) & (out.loc[eq, "ci90_hi"] < m)
    h4 = out["id"] == "H4"
    out.loc[h4, "within_margin"] = out.loc[h4, "ci95_hi"] < cfg["max_false_refusal_increase"]
    return out


def summary_table(df: pd.DataFrame, rng) -> pd.DataFrame:
    rows = []
    for (s, lv), d in df.groupby(["system", df["level"].fillna("-")]):
        h = d["hallucination"].to_numpy()
        boots = h[rng.integers(0, len(h), size=(B, len(h)))].mean(1)
        avail, unavail = d[d.get("answer_available", 0) == 1], d[d.get("answer_available", 0) == 0]
        ab = d[d["abstain"] == 1]
        rows.append({
            "system": s, "level": lv, "n": len(d),
            "halluc": h.mean(), "h_lo": np.percentile(boots, 2.5), "h_hi": np.percentile(boots, 97.5),
            "correct": d["correct"].mean(), "abstain": d["abstain"].mean(),
            "non_answer": (d["response_class"] == "non_answer").mean(),
            "sel_risk": d["hallucination"].sum() / max(d["answered"].sum(), 1),
            "false_refusal": avail["abstain"].mean() if len(avail) else np.nan,
            "abst_precision": (1 - ab["answer_available"]).mean() if len(ab) and "answer_available" in ab else np.nan,
            "halluc_if_unavail": unavail["hallucination"].mean() if len(unavail) else np.nan,
            "unsup_correct": d["unsupported_correct"].mean(),
            "tokens": d["prompt_tokens"].mean(),
        })
    order = {s: i for i, s in enumerate(["closed_book", "off", "advisory", "advisory_missing",
                                          "enforced", "enforced_oracle", "restored_ctrl", "restored"])}
    out = pd.DataFrame(rows)
    out["_o"] = out["system"].map(order).fillna(99)
    out["_l"] = out["level"].map({l: i for i, l in enumerate(LEVELS)}).fillna(-1)
    return out.sort_values(["_o", "_l"]).drop(columns=["_o", "_l"])


def plot(df: pd.DataFrame, out_dir: Path, tag: str):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    systems = ["off", "advisory", "enforced", "enforced_oracle"]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    w = 0.2
    for k, s in enumerate(systems):
        g = df[df["system"] == s].groupby("level")[["hallucination", "abstain"]].mean().reindex(LEVELS)
        x = np.arange(len(LEVELS)) + (k - 1.5) * w
        axes[0].bar(x, g["hallucination"], w, label=s)
        axes[1].bar(x, g["abstain"], w, label=s)
        d = df[(df["system"] == s) & df["level"].isin(LEVELS)]
        cov = d.groupby("level")["answered"].mean().reindex(LEVELS)
        risk = (d.groupby("level")["hallucination"].sum() /
                d.groupby("level")["answered"].sum().clip(lower=1)).reindex(LEVELS)
        axes[2].plot(cov, risk, marker="o", label=s)
    for ax, t in zip(axes[:2], ["Hallucination rate", "Abstention rate"]):
        ax.set_xticks(range(len(LEVELS)), LEVELS)
        ax.set_title(f"{t} — {tag}")
        ax.grid(alpha=.3, axis="y")
    axes[2].set_xlabel("coverage (answered)")
    axes[2].set_ylabel("selective risk (halluc / answered)")
    axes[2].set_title("Risk–coverage per level")
    axes[2].grid(alpha=.3)
    axes[0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out_dir / f"channel_levels_{tag}.png", dpi=150)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--run-name", default=None)
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config, encoding="utf-8"))
    run = args.run_name or cfg["run_name"]
    df = pd.read_csv(Path("06_evaluation") / run / "eval.csv")
    out_dir = Path("07_analysis") / run
    out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(cfg["seed"])

    items = df.groupby("item_id").first()
    md = [f"# Analysis — {run}\n",
          f"Items: {len(items)} · primary population: {int(items['primary'].sum())} · "
          f"qclass: {items['qclass'].value_counts().to_dict()}\n"]
    off = df[df["system"] == "off"]
    md += ["## Channel manipulation check (off)\n",
           _md(off.groupby("level").agg(answer_available=("answer_available", "mean"),
                                        gold_kept=("gold_kept_frac", "mean"),
                                        len_ratio_min=("len_ratio_vs_full", "min"),
                                        len_ratio_max=("len_ratio_vs_full", "max"),
                                        tokens=("prompt_tokens", "mean")).reindex(LEVELS), index=True),
           "\n## Reader verdict vs answer availability (off rows)\n",
           _md(pd.crosstab(off["reader_verdict"], off["answer_available"]), index=True),
           f"\nReader `missing` leak rate: {off['reader_missing_leak'].mean():.2%}\n"]

    strata = [("primary", df[df["primary"] == 1]),
              ("primary_param_unknown", df[(df["primary"] == 1) & (df["param_known"] == 0)]),
              ("primary_param_known", df[(df["primary"] == 1) & (df["param_known"] == 1)]),
              ("all", df)]
    for tag, sub in strata:
        if sub["item_id"].nunique() < 2:
            continue
        tab, con = summary_table(sub, rng), contrasts(sub, cfg, rng)
        tab.to_csv(out_dir / f"summary_{tag}.csv", index=False)
        con.to_csv(out_dir / f"contrasts_{tag}.csv", index=False)
        plot(sub, out_dir, tag)
        rs = sub[sub["system"] == "restored"].groupby("turn1_status")[["hallucination", "correct"]].agg(["mean", "count"])
        au = aurc_table(sub, rng)
        au.to_csv(out_dir / f"aurc_{tag}.csv", index=False)
        md += [f"\n## Stratum: {tag} (items={sub['item_id'].nunique()})\n",
               _md(tab.round(3)), "\n### Risk–coverage (gates on advisory outputs, all levels)\n",
               _md(au.round(4)) if not au.empty else "(no reader scores)",
               "\n### Contrasts (diff = b − a)\n",
               _md(con.round(4)), "\n### Restored, by turn-1 status\n", _md(rs.round(3), index=True)]
    (out_dir / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {out_dir / 'summary.md'}")


if __name__ == "__main__":
    main()
