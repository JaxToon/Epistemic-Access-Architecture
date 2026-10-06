"""Phase 1b — the SAME epistemic score sigma used advisorily vs authoritatively.

Generation (pilot generator, same evidence, greedy):
  sigma_advisory  generator prompt additionally states sigma for this packet; generator decides
  sigma_placebo   identical text, but sigma is shuffled across rows (same marginal distribution)
                  -> separates "generator uses the value" from "extra text triggers abstention"
Derived (no extra generation):
  authority@matched  off output, hard-gated at the threshold tau* whose answer rate equals the
                     advisory answer rate (coverage-matched => differences are about WHO decides,
                     not how often the system abstains)                          [PRIMARY]
  authority@0.5      fixed threshold (secondary)
Outcomes are 3-way (correct / abstain / hallucination). Primary contrast: selective risk
(hallucination / answered) of authority@matched − advisory, paired item bootstrap.
Pre-registered in 00_docs/05_preregistration_EAG_phase1.md §5.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .. import prompts as P
from ..data import load_items
from ..evaluate import label

ADVISORY_SIGMA = ("Epistemic module: the estimated probability that the evidence above supports an "
                  "answer is {s:.2f} ({word}).\n\n")
TAU_FIXED = 0.5
B = 2000


def _word(s: float) -> str:
    return "high" if s >= 0.67 else "medium" if s >= 0.33 else "low"


def generate(args):
    import yaml
    from tqdm import tqdm

    from ..backends import make_backend
    from ..run import _msgs

    cfg = yaml.safe_load(open(args.config, encoding="utf-8"))
    sig = pd.read_csv(args.sigma)[["item_id", "level", args.score_col]].rename(columns={args.score_col: "s"})
    rng = np.random.default_rng(cfg["seed"])
    sig["s_placebo"] = rng.permutation(sig["s"].to_numpy())
    q = {it["id"]: it["question"] for it in load_items(Path(cfg["items_path"]))}
    pk = {}
    with open(Path(args.pilot_dir) / "packets.jsonl", encoding="utf-8") as f:
        for line in f:
            p = json.loads(line)
            pk[(p["item_id"], p["level"])] = p["evidence"]
    out = Path(args.pilot_dir) / f"sigma_advisory_{args.score_col}.jsonl"
    done = {json.loads(l)["key"] for l in open(out, encoding="utf-8")} if out.exists() else set()
    todo = []
    for r in sig.itertuples(index=False):
        for variant, s in (("sigma_advisory", r.s), ("sigma_placebo", r.s_placebo)):
            key = f"{r.item_id}|{r.level}|{variant}"
            if key in done:
                continue
            adv = ADVISORY_SIGMA.format(s=s, word=_word(s))
            todo.append((key, r.item_id, r.level, variant, float(s), _msgs(P.GENERATOR.format(
                evidence=pk[(r.item_id, r.level)], advisory=adv, question=q[r.item_id]))))
    be = make_backend(cfg)
    bs = cfg["batch_size"]
    with open(out, "a", encoding="utf-8") as f:
        for i in tqdm(range(0, len(todo), bs), desc="sigma_advisory"):
            chunk = todo[i:i + bs]
            outs = be.generate([t[5] for t in chunk], cfg["max_new_tokens_answer"])
            for t, o in zip(chunk, outs):
                f.write(json.dumps({"key": t[0], "item_id": t[1], "level": t[2], "variant": t[3],
                                    "sigma_shown": t[4], "output": o}, ensure_ascii=False) + "\n")
            f.flush()
    print(f"wrote {out}")


def _matched_tau(sigma: np.ndarray, off_answered: np.ndarray, target_rate: float) -> float:
    """Smallest-gap threshold so that mean(off_answered & sigma >= tau) ≈ target_rate."""
    cands = np.unique(np.r_[sigma, np.inf])
    rates = np.array([(off_answered & (sigma >= t)).mean() for t in cands])
    return float(cands[np.argmin(np.abs(rates - target_rate))])


def _sel_risk(df):
    return df["hallucination"].sum() / max(df["answered"].sum(), 1)


def analyze(args):
    from .. import evaluate as E
    from ..judge import load_cache
    E.JUDGED.clear()
    E.JUDGED.update(load_cache())
    gold = {it["id"]: it["answer"] for it in load_items(Path(args.items))}
    ev = pd.read_csv(args.eval_csv)
    off = ev[ev["system"] == "off"][["item_id", "level", "output", "primary", "answer_available"]]
    sig = pd.read_csv(args.sigma)[["item_id", "level", args.score_col]].rename(columns={args.score_col: "sigma"})
    gen = pd.read_json(Path(args.pilot_dir) / f"sigma_advisory_{args.score_col}.jsonl", lines=True)
    wide = gen.pivot_table(index=["item_id", "level"], columns="variant", values="output",
                           aggfunc="first").reset_index()
    d = off.merge(sig, on=["item_id", "level"]).merge(wide, on=["item_id", "level"])
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    md = [f"# Phase 1b — sigma advisory vs authority ({args.score_col})\n"]
    rng = np.random.default_rng(20261005)

    for tag, sub in [("PRIMARY: primary items", d[d["primary"] == 1]), ("all items", d)]:
        sub = sub.reset_index(drop=True)
        lab = lambda col: pd.DataFrame([label(str(o), gold[i], i) for o, i in zip(sub[col], sub["item_id"])])
        L = {"off": lab("output"), "sigma_advisory": lab("sigma_advisory"), "sigma_placebo": lab("sigma_placebo")}
        off_ans = L["off"]["answered"].to_numpy().astype(bool)
        tau_m = _matched_tau(sub["sigma"].to_numpy(), off_ans, L["sigma_advisory"]["answered"].mean())
        for name, tau in (("authority@matched", tau_m), ("authority@0.5", TAU_FIXED)):
            keep = sub["sigma"].to_numpy() >= tau
            L[name] = pd.DataFrame([label(o if k else "INSUFFICIENT EVIDENCE", gold[i], i)
                                    for o, k, i in zip(sub["output"], keep, sub["item_id"])])
        rows = []
        for name, l in L.items():
            rows.append({"system": name, "coverage": l["answered"].mean(), "correct": l["correct"].mean(),
                         "abstain": l["abstain"].mean(), "halluc": l["hallucination"].mean(),
                         "sel_risk": _sel_risk(l),
                         "false_refusal(full)": l.loc[(sub["level"] == "full").to_numpy(), "abstain"].mean()})
        tab = pd.DataFrame(rows)

        # paired item bootstrap for the primary and placebo contrasts
        items = sub["item_id"].to_numpy()
        uniq = np.unique(items)
        rows_of = {i: np.flatnonzero(items == i) for i in uniq}

        def boot(a, b, metric):
            reps = []
            for _ in range(B):
                ix = np.concatenate([rows_of[i] for i in rng.choice(uniq, len(uniq))])
                reps.append(metric(L[b].iloc[ix]) - metric(L[a].iloc[ix]))
            reps = np.array(reps)
            return {"contrast": f"{b} − {a}", "diff": metric(L[b]) - metric(L[a]),
                    "ci_lo": np.percentile(reps, 2.5), "ci_hi": np.percentile(reps, 97.5),
                    "p": float(min(1.0, max(2 * min((reps >= 0).mean(), (reps <= 0).mean()), 1 / B)))}

        con = pd.DataFrame([
            {"id": "P1 (primary)", "metric": "sel_risk", **boot("sigma_advisory", "authority@matched", _sel_risk)},
            {"id": "P1b", "metric": "correct", **boot("sigma_advisory", "authority@matched", lambda x: x["correct"].mean())},
            {"id": "placebo", "metric": "halluc", **boot("sigma_placebo", "sigma_advisory", lambda x: x["hallucination"].mean())},
            {"id": "placebo", "metric": "abstain", **boot("sigma_placebo", "sigma_advisory", lambda x: x["abstain"].mean())},
            {"id": "advisory-use", "metric": "halluc", **boot("off", "sigma_advisory", lambda x: x["hallucination"].mean())},
        ])
        md += [f"\n## {tag} (rows={len(sub)}, tau*={tau_m:.4f})\n",
               "```\n" + tab.round(4).to_string(index=False) + "\n```\n",
               "```\n" + con.round(4).to_string(index=False) + "\n```\n"]
        if tag.startswith("PRIMARY"):
            tab.to_csv(out / f"sigma_authority_{args.score_col}_table.csv", index=False)
            con.to_csv(out / f"sigma_authority_{args.score_col}_contrasts.csv", index=False)
    (out / f"sigma_authority_{args.score_col}.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


def main():
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["generate", "analyze"])
    ap.add_argument("--score-col", default="eag_lc1")
    ap.add_argument("--config", default="configs/pilot_v0.1.yaml")
    ap.add_argument("--sigma", default="07_analysis/eag_phase1/sigma_test.csv")
    ap.add_argument("--pilot-dir", default="05_outputs/pilot_v0.2_qwen2.5-3b")
    ap.add_argument("--items", default="01_data/hotpot_dev_n500_seed20261005.jsonl")
    ap.add_argument("--eval-csv", default="06_evaluation/pilot_v0.2_qwen2.5-3b/eval.csv")
    ap.add_argument("--out", default="07_analysis/eag_phase1")
    args = ap.parse_args()
    generate(args) if args.mode == "generate" else analyze(args)


if __name__ == "__main__":
    main()
