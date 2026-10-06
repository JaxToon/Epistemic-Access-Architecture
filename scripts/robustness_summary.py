"""Builds 07_analysis/robustness/summary.md (+ forest plot) from the outputs of robustness_labels.py
and the eaa.eag.evaluate runs in 07_analysis/robustness/eag_<labels>/."""
from __future__ import annotations

import ast
import re
from pathlib import Path

import numpy as np
import pandas as pd

R = Path("07_analysis/robustness")
MODES = ["audit_then_judge", "judge", "strict"]
SHORT = {"audit_then_judge": "primary (audit→judge)", "judge": "judge-only", "strict": "strict (rule)"}


def f(x, d=3):
    return "–" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:+.{d}f}" if d else str(x)


def pv(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "–"
    return "<0.001" if x < 0.001 else f"{x:.3f}"


def pilot_rows(mode):
    c = pd.read_csv(R / f"pilot_{mode}" / "contrasts_primary.csv").set_index("id")
    out = []
    for hid, expect in [("H1a", "+"), ("H1b", "+"), ("H2", "-"), ("H3a", "0"), ("H3b", "-")]:
        r = c.loc[hid]
        lo, hi, ph = r["ci95_lo"], r["ci95_hi"], r["p_holm"]
        if expect == "0":
            v = "no effect detected (≈0 predicted; no equivalence test)" if lo < 0 < hi else "effect ≠ 0"
        else:
            sig = ph < 0.05
            right = (r["diff"] > 0) == (expect == "+")
            v = "supported" if sig and right else ("not supported (sig. opposite direction)" if sig else "not supported")
        out.append((hid, f"{r['rate_a']:.3f}→{r['rate_b']:.3f}", f(r["diff"]), f"[{lo:+.3f}, {hi:+.3f}]", pv(ph), v))
    r = c.loc["H2eq"]
    eq = bool(r["tost_equivalent"])
    out.append(("H2eq (TOST ±0.05)", f"{r['rate_a']:.3f}→{r['rate_b']:.3f}", f(r["diff"]),
                f"90% [{r['ci90_lo']:+.3f}, {r['ci90_hi']:+.3f}]", "–",
                "equivalent" if eq else "inconclusive (not equivalent within margin)"))
    r = c.loc["H4"]
    out.append(("H4 (false refusal; margin +0.10)", f"{r['rate_a']:.3f}→{r['rate_b']:.3f}", f(r["diff"]),
                f"[{r['ci95_lo']:+.3f}, {r['ci95_hi']:+.3f}]", pv(r["p_holm"]),
                "supported" if bool(r["within_margin"]) else "not supported (cost exceeds margin)"))
    return out


def eag_rows(mode):
    c = pd.read_csv(R / f"eag_{mode}" / "contrasts_primary.csv").set_index("id")
    out = []
    for hid in ["H5a", "H5b", "H5c"]:
        r = c.loc[hid]
        sig = r["p_holm"] < 0.05
        v = "supported" if sig and r["diff"] < 0 else ("not supported (sig. opposite)" if sig else "not supported")
        if not sig and (r["ci_hi"] < 0 or r["ci_lo"] > 0):
            v += " (unadj. CI excl. 0, " + ("favours eag" if r["diff"] < 0 else "favours comparator") + ")"
        out.append((hid, r["contrast"], f(r["diff"]), f"[{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}]", pv(r["p_holm"]), v))
    txt = (R / f"eag_{mode}" / "summary.md").read_text(encoding="utf-8")
    m = re.search(r"\{'H6:.*\}", txt)
    d = {k: float(re.sub(r"np\.float32\((.*?)\)", r"\1", str(v))) for k, v in
         ast.literal_eval(re.sub(r"np\.float32\((.*?)\)", r"\1", m.group(0))).items()}
    vals = list(d.values())
    ds_ok = d["ci_lo"] > 0
    r = c.loc["H6-AURC"]
    ni = bool(r["non_inferior"])
    out.append(("H6 part 1: Δσ_untrained lc1−lc0", "label-independent", f(vals[0]),
                f"[{d['ci_lo']:+.3f}, {d['ci_hi']:+.3f}]", pv(d["p"]), "met" if ds_ok else "not met"))
    out.append(("H6 part 2: AURC lc1−lc0 < +0.005", "eag_lc1 − eag_lc0", f(r["diff"]),
                f"[{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}]", pv(r["p"]), "met" if ni else "not met"))
    out.append(("H6 (both parts)", "", "", "", "", "supported" if ds_ok and ni else "not supported"))
    return out


def s2_rows(mode):
    c = pd.read_csv(R / f"study2_{mode}" / "contrasts.csv").set_index("id")
    s = pd.read_csv(R / f"study2_{mode}" / "sources.csv")
    out = []
    for hid in ["S2-H1", "S2-H2", "S2-H1(open)"]:
        r = c.loc[hid]
        sig = r["p_holm"] < 0.05
        v = "supported" if sig and r["diff"] > 0 else ("not supported (sig. opposite)" if sig else "not supported")
        out.append((hid, f"poor {r['halluc_poor']:.3f} / rich {r['halluc_rich']:.3f}", f(r["diff"]),
                    f"[{r['ci_lo']:+.3f}, {r['ci_hi']:+.3f}]", pv(r["p_holm"]), v))
    for hid, prompt in [("S2-H3 (extractive)", "extractive"), ("S2-H4 (open)", "open")]:
        r = s[(s["prompt"] == prompt) & (s["level"] == "drop_ans")].iloc[0]
        v = "supported" if r["wilson_lo"] > 0.5 else "not supported"
        out.append((hid, f"n_halluc={int(r['n_halluc'])}; gold-unit {r['from_gold_unit']:.2f} / filler {r['from_filler']:.2f}",
                    f"{r['copied_from_packet']:.3f}", f"Wilson [{r['wilson_lo']:.3f}, {r['wilson_hi']:.3f}]", "–", v))
    # S2-H4 also requires S2-H1(open): the copy proportion half is reported here; S2-H1(open) row above.
    return out


def sr_rows(mode):
    s = pd.read_csv(R / f"selective_risk_{mode}.csv")
    out = []
    for _, r in s.iterrows():
        out.append((f"SR jump {r['study'].split()[0]} {r['prompt']}/{r['policy']}",
                    f"{r['rate_a']:.3f}→{r['rate_b']:.3f}", f(r["diff"]),
                    f"[{r['ci95_lo']:+.3f}, {r['ci95_hi']:+.3f}]", "–",
                    "increase (CI > 0)" if r["ci95_lo"] > 0 else "no clear increase"))
    return out


def build():
    fams = [("Pilot H1–H4 (primary population, 311 items; Holm over H1a,H1b,H2,H3a,H3b,H4)", pilot_rows),
            ("EAG phase 1 (AURC on primary & answered; Holm over H5a–c)", eag_rows),
            ("Study 2, Qwen2.5-3B (255 primary items; Holm over S2-H1, S2-H2, S2-H1(open))", s2_rows),
            ("Selective risk full→drop_ans (exploratory in pilot; replication on Study 2 items; no Holm)", sr_rows)]
    md = ["# Label robustness of confirmatory contrasts (2026-10-06)\n",
          "Label sets: **primary** = audit labels (Claude, documented per item) override the Qwen2.5-7B judge, "
          "judge fills the rest; **judge-only** = `EAA_LABELS=judge`; **strict** = rule only (EM / gold ⊂ pred; "
          "rule-ambiguous predictions count as wrong). Abstention labels are identical across sets, so H4 and "
          "H6 part 1 cannot change. diff = b − a; 95% item-bootstrap CI unless stated; p = Holm-adjusted where "
          "the contrast belongs to a pre-registered family (McNemar exact for rates, bootstrap for selective "
          "risk / AURC). Primary-label numbers reproduce `07_analysis/pilot_v0.2_qwen2.5-3b`, "
          "`07_analysis/eag_phase1` and `07_analysis/study2_qwen2.5-3b` exactly.\n",
          "Script: `scripts/robustness_labels.py`, `scripts/robustness_summary.py`; EAG: "
          "`python -m eaa.eag.evaluate --eval-csv 07_analysis/robustness/evals/pilot_<labels>.csv "
          "--out 07_analysis/robustness/eag_<labels>`.\n"]
    flags = []
    for title, fn in fams:
        res = {m: fn(m) for m in MODES}
        md += [f"\n## {title}\n", "| contrast | labels | rates / detail | estimate | 95% CI | p (Holm) | verdict |",
               "|---|---|---|---|---|---|---|"]
        for i, row in enumerate(res[MODES[0]]):
            verdicts = [res[m][i][5].split(" (")[0] for m in MODES]
            changed = len(set(verdicts)) > 1
            if changed:
                flags.append(f"{row[0]}: " + "; ".join(f"{SHORT[m]} = {res[m][i][5]}" for m in MODES))
            for m in MODES:
                r = res[m][i]
                name = (r[0] + (" **⚑ verdict changes**" if changed else "")) if m == MODES[0] else ""
                md.append(f"| {name} | {SHORT[m]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |")
    md.insert(3, "\n## Verdict changes across label sets\n\n" +
              ("\n".join(f"- ⚑ {x}" for x in flags) if flags else "- none") + "\n")
    md.append("\n## Notes\n\n"
              "- Strict labels count correct paraphrases (\"Al Capone\" for \"Alphonse Gabriel Capone\") as "
              "hallucinations. These occur mostly when the answer is in the evidence (`full`, `restored`), so "
              "strict labels inflate hallucination at `full` (0.49 vs 0.28 primary). This is why H1a and H2 "
              "become *significant in the opposite direction* under strict labels; their verdict (not supported) "
              "does not change.\n"
              "- H2eq under judge-only: restored − ctrl = +0.045, 90% CI [+0.006, +0.084] (unadjusted McNemar "
              "p = 0.065): a hint of anchoring that is absent under primary (+0.013) and strict (+0.013) labels. "
              "Verdict (inconclusive) unchanged.\n"
              "- H6 under strict labels: the AURC error target changes (strict errors include correct "
              "paraphrases, which are concentrated at `full`, where σ is high), so eag_lc1 vs eag_lc0 ranks "
              "differently. Under both labels that correct the paraphrase artefact, H6 part 2 fails. We treat "
              "H6 as not supported and flag it as label-sensitive.\n"
              "- H5b: under judge-only and strict labels the unadjusted CI excludes 0 *in favour of the probe* "
              "(probe ≥ eag), consistent with the primary reading that evidence access adds no value over the "
              "generator state at 3B.\n"
              "- H3b under judge-only: 95% CI excludes 0 ([−0.441, −0.009]) but Holm p = 0.152; verdict unchanged.\n"
              "- param_known stratum is tiny (14 / 12 / 5 primary items by label set); param_unknown results "
              "mirror the primary ones (files `pilot_<labels>/contrasts_primary_param_{known,unknown}.csv`). "
              "In param_unknown, H3b primary = −0.274 [−0.499, −0.058], Holm p = 0.072. Study 2 has no "
              "closed-book run, so no param_known split there.\n")
    (R / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


def plot():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = []
    for m in MODES:
        c = pd.read_csv(R / f"pilot_{m}" / "contrasts_primary.csv").set_index("id")
        for hid in ["H1a", "H1b", "H2", "H2eq", "H3a", "H3b", "H4"]:
            rows.append((f"pilot {hid}", m, c.loc[hid, "diff"], c.loc[hid, "ci95_lo"], c.loc[hid, "ci95_hi"]))
        c = pd.read_csv(R / f"study2_{m}" / "contrasts.csv").set_index("id")
        for hid in ["S2-H1", "S2-H2", "S2-H1(open)"]:
            rows.append((hid, m, c.loc[hid, "diff"], c.loc[hid, "ci_lo"], c.loc[hid, "ci_hi"]))
        c = pd.read_csv(R / f"eag_{m}" / "contrasts_primary.csv").set_index("id")
        for hid in ["H5a", "H5b", "H5c", "H6-AURC"]:
            rows.append((f"EAG {hid}", m, c.loc[hid, "diff"], c.loc[hid, "ci_lo"], c.loc[hid, "ci_hi"]))
    d = pd.DataFrame(rows, columns=["c", "m", "est", "lo", "hi"])
    labels = list(dict.fromkeys(d["c"]))
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(labels) + 1))
    for k, m in enumerate(MODES):
        s = d[d["m"] == m].set_index("c").reindex(labels)
        y = np.arange(len(labels)) + (k - 1) * 0.25
        ax.errorbar(s["est"], y, xerr=[s["est"] - s["lo"], s["hi"] - s["est"]], fmt="o", ms=4,
                    capsize=2, label=SHORT[m])
    ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(range(len(labels)), labels)
    ax.invert_yaxis()
    ax.set_xlabel("estimate (b − a), 95% CI")
    ax.set_title("Confirmatory contrasts under three label sets")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(alpha=.3, axis="x")
    fig.tight_layout()
    fig.savefig(R / "forest_label_robustness.png", dpi=150)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    build()
    plot()
