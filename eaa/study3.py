"""Study 3 — same signal, advice vs authority, on fresh items (pre-reg: 00_docs/08_...md).

  python -m eaa.study3 packets                  prompts for the 5 Study 2 packets per item
  python -m eaa.eag.features --packets 01_data/study3_packets.jsonl --out 08_architecture/features_study3.pt
  python -m eaa.study3 sigma                    eag_lc1 (3 seeds, frozen from phase 1) -> sigma.csv
  python -m eaa.study3 generate                 advice + placebo arms (Qwen2.5-3B)
  python -m eaa.study3 analyze                  P1-P3 + secondary
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from . import prompts as P
from .data import load_items

ITEMS = Path("01_data/hotpot_dev_study2_n400_seed20261006.jsonl")
S2_DIR = Path("05_outputs/study2_qwen2.5-3b")
PACKETS = Path("01_data/study3_packets.jsonl")
FEATS = Path("08_architecture/features_study3.pt")
RUNS = Path("08_architecture/eag_runs")
REP = Path("07_analysis/study3")
GENERATORS = {"qwen2.5-3b": "hf:03_models/Qwen2.5-3B-Instruct", "gemma4-e4b": "ollama:gemma4:e4b"}


def out_dir(tag: str) -> Path:
    return Path(f"05_outputs/study3_{tag}")
SEED = 20261011
TAU = 0.5
LAMBDA = 2.0
B = 2000
ADVICE = ("Epistemic module: the estimated probability that the evidence above supports an "
          "answer is {s:.2f} ({word}).\n\n")      # identical wording to phase 1b


def _word(s: float) -> str:
    return "high" if s >= 0.67 else "medium" if s >= 0.33 else "low"


def packets():
    q = {it["id"]: it["question"] for it in load_items(ITEMS)}
    with open(S2_DIR / "packets.jsonl", encoding="utf-8") as f, open(PACKETS, "w", encoding="utf-8") as g:
        for line in f:
            p = json.loads(line)
            g.write(json.dumps({"item_id": p["item_id"], "level": p["level"], "policy": p["policy"],
                                "split": "test",
                                "prompt": P.GENERATOR.format(evidence=p["evidence"], advisory="",
                                                             question=q[p["item_id"]])},
                               ensure_ascii=False) + "\n")
    print(f"wrote {PACKETS}")


def sigma():
    import torch

    from .eag.model import EpistemicHead
    from .eag.train import predict

    data = torch.load(FEATS, weights_only=False)
    meta, feats = data["meta"], data["feats"]
    runs = [r["name"] for r in json.loads((RUNS / "train_summary.json").read_text())
            if r["name"].startswith("eag_lc1_")]
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    cols = []
    for name in runs:
        c = torch.load(RUNS / f"{name}.pt", weights_only=False, map_location="cpu")
        m = EpistemicHead(c["d"], c["n_layers_g"], c["variant"]).to(dev)
        m.load_state_dict(c["state"])
        cols.append(1 / (1 + np.exp(-predict(m, feats, list(range(len(meta))), dev))))
    df = pd.DataFrame([{k: m[k] for k in ("item_id", "level", "policy")} for m in meta])
    df["sigma"] = np.mean(cols, axis=0)
    REP.mkdir(parents=True, exist_ok=True)
    df.to_csv(REP / "sigma.csv", index=False)
    print(f"sigma from {runs} -> {REP / 'sigma.csv'}; mean by level:\n",
          df.groupby("level")["sigma"].mean().round(3))


def _with_advice(prompt: str, s: float) -> str:
    i = prompt.rfind("Question: ")
    return prompt[:i] + ADVICE.format(s=s, word=_word(s)) + prompt[i:]


def generate(tag: str, batch_size: int):
    from tqdm import tqdm

    from .backends import HFBackend, OllamaBackend
    from .run import _msgs

    sig = pd.read_csv(REP / "sigma.csv")
    sig["placebo"] = np.random.default_rng(SEED).permutation(sig["sigma"].to_numpy())
    pk = {(r["item_id"], r["level"], r["policy"]): r["prompt"] for r in map(json.loads, open(PACKETS, encoding="utf-8"))}
    OUT = out_dir(tag)
    OUT.mkdir(parents=True, exist_ok=True)
    gen = OUT / "generations.jsonl"
    variants = [("advice", "sigma"), ("placebo", "placebo")]
    if tag != "qwen2.5-3b":          # Qwen's `off` arm = Study 2 extractive outputs (identical prompt)
        variants = [("off", None)] + variants
    done = {json.loads(l)["key"] for l in open(gen, encoding="utf-8")} if gen.exists() else set()
    todo = []
    for r in sig.itertuples(index=False):
        base = pk[(r.item_id, r.level, r.policy)]
        for variant, col in variants:
            key = f"{r.item_id}|{r.level}|{r.policy}|{variant}"
            if key in done:
                continue
            s = float(getattr(r, col)) if col else float("nan")
            prompt = _with_advice(base, s) if col else base
            todo.append((key, r.item_id, r.level, r.policy, variant, s, _msgs(prompt)))
    kind, model = GENERATORS[tag].split(":", 1)
    be = HFBackend(model) if kind == "hf" else OllamaBackend(model)
    todo.sort(key=lambda t: be.prompt_tokens(t[6]))
    with open(gen, "a", encoding="utf-8") as f:
        for i in tqdm(range(0, len(todo), batch_size), desc=f"study3 {tag}"):
            chunk = todo[i:i + batch_size]
            outs = be.generate([t[6] for t in chunk], 24)
            for t, o in zip(chunk, outs):
                f.write(json.dumps({"key": t[0], "item_id": t[1], "level": t[2], "policy": t[3],
                                    "variant": t[4], "sigma_shown": t[5], "output": o, "model": be.name,
                                    "prompt_version": P.PROMPT_VERSION, "ts": time.time()},
                                   ensure_ascii=False) + "\n")
            f.flush()
    print(f"done -> {gen}")


def analyze(tag: str):
    from . import evaluate as E
    from .judge import load_cache

    sys.stdout.reconfigure(encoding="utf-8")
    E.JUDGED.clear()
    E.JUDGED.update(load_cache())
    items = {it["id"]: it for it in load_items(ITEMS)}
    from .conditions import question_class
    s2pk = {(r["item_id"], r["level"], r["policy"]): r for r in map(json.loads, open(S2_DIR / "packets.jsonl", encoding="utf-8"))}
    gen = pd.read_json(out_dir(tag) / "generations.jsonl", lines=True)
    if tag == "qwen2.5-3b":
        off = {(r["item_id"], r["level"], r["policy"]): r["output"]
               for r in map(json.loads, open(S2_DIR / "generations.jsonl", encoding="utf-8")) if r["prompt"] == "extractive"}
    else:
        off = {(r.item_id, r.level, r.policy): r.output for r in gen[gen.variant == "off"].itertuples()}
        gen = gen[gen.variant != "off"]
    wide = gen.pivot_table(index=["item_id", "level", "policy"], columns="variant", values="output", aggfunc="first").reset_index()
    sig = pd.read_csv(REP / "sigma.csv")
    d = wide.merge(sig, on=["item_id", "level", "policy"])
    d["off"] = [off[(i, l, p)] for i, l, p in zip(d.item_id, d.level, d.policy)]
    d["primary"] = [int(question_class(items[i]) == "open" and s2pk[(i, l, p)]["answer_para_defined"])
                    for i, l, p in zip(d.item_id, d.level, d.policy)]
    gated = "INSUFFICIENT EVIDENCE"
    d["authority"] = np.where(d["sigma"] >= TAU, d["off"], gated)
    d["advice_authority"] = np.where(d["sigma"] >= TAU, d["advice"], gated)
    arms = ["off", "advice", "placebo", "authority", "advice_authority"]
    rows = []
    for r in d.itertuples(index=False):
        for a in arms:
            rows.append({"item_id": r.item_id, "level": r.level, "policy": r.policy, "primary": r.primary,
                         "sigma": r.sigma, "arm": a, "output": getattr(r, a),
                         **E.label(str(getattr(r, a)), items[r.item_id]["answer"], r.item_id)})
    L = pd.DataFrame(rows)
    rep = REP / tag
    rep.mkdir(parents=True, exist_ok=True)
    L.to_csv(rep / "eval.csv", index=False)

    md = [f"# Study 3 — advice vs authority (confirmatory) — generator {tag}\n",
          f"judge_missing (unaudited ambiguous): {int(L['judge_missing'].sum())}\n"]
    rng = np.random.default_rng(SEED)
    for tag, sub in [("PRIMARY", L[L.primary == 1]), ("all items", L)]:
        W = {a: sub[sub.arm == a].set_index(["item_id", "level", "policy"]).sort_index() for a in arms}
        idx = W["off"].index
        items_u = idx.get_level_values(0).unique().to_numpy()
        pos = {i: np.flatnonzero(idx.get_level_values(0) == i) for i in items_u}
        boots = [np.concatenate([pos[i] for i in rng.choice(items_u, len(items_u))]) for _ in range(B)]
        full = (idx.get_level_values(1) == "full")

        def arr(a, col):
            return W[a].loc[idx, col].to_numpy().astype(float)

        U = lambda a, lam=LAMBDA: arr(a, "correct") - lam * arr(a, "hallucination")
        tab = pd.DataFrame([{"arm": a, "halluc": arr(a, "hallucination").mean(), "correct": arr(a, "correct").mean(),
                             "abstain": arr(a, "abstain").mean(),
                             "sel_risk": arr(a, "hallucination").sum() / max(arr(a, "answered").sum(), 1),
                             "false_refusal_full": arr(a, "abstain")[full].mean(), "U_lambda2": U(a).mean()}
                            for a in arms])

        def contrast(x, y, alpha=0.05, mask=None):
            """Paired mean difference y − x; item bootstrap over ALL rows (mask restricts rows
            but resampling stays at item level)."""
            dif = (y - x).astype(float)
            if mask is not None:
                dif = np.where(mask, dif, np.nan)
            reps = np.array([np.nanmean(dif[b]) for b in boots])
            lo, hi = np.percentile(reps, [100 * alpha / 2, 100 * (1 - alpha / 2)])
            p = float(min(1.0, max(2 * min((reps >= 0).mean(), (reps <= 0).mean()), 1 / B)))
            return np.nanmean(dif), lo, hi, p

        p1 = contrast(arr("placebo", "hallucination"), arr("advice", "hallucination"), alpha=0.10)
        p2 = contrast(arr("off", "hallucination"), arr("authority", "hallucination"))
        p3 = contrast(U("advice"), U("authority"))
        fr = contrast(arr("off", "abstain"), arr("authority", "abstain"), mask=full)
        from .analyze import holm
        ph = holm([p2[3], p3[3]])
        con = pd.DataFrame([
            {"id": "P1", "contrast": "halluc advice − placebo (90% CI, TOST ±0.02)", "est": p1[0], "lo": p1[1], "hi": p1[2],
             "verdict": "supported" if (p1[1] > -0.02 and p1[2] < 0.02) else "not supported"},
            {"id": "P2", "contrast": "halluc authority − off", "est": p2[0], "lo": p2[1], "hi": p2[2], "p_holm": ph[0],
             "verdict": "supported" if (p2[0] <= -0.05 and p2[2] < 0) else "not supported"},
            {"id": "P3", "contrast": "U(λ=2) authority − advice", "est": p3[0], "lo": p3[1], "hi": p3[2], "p_holm": ph[1],
             "verdict": "supported" if p3[1] > 0 else "not supported"},
            {"id": "cost", "contrast": "false refusal @full authority − off", "est": fr[0], "lo": fr[1], "hi": fr[2],
             "verdict": "ok" if fr[2] <= 0.15 else "exceeds 0.15"},
        ])
        sec = []
        for lam in (1.0, 4.0):
            c = contrast(U("advice", lam), U("authority", lam))
            sec.append({"contrast": f"U(λ={lam:g}) authority − advice", "est": c[0], "lo": c[1], "hi": c[2]})
        c = contrast(arr("off", "hallucination"), arr("advice", "hallucination"))
        sec.append({"contrast": "halluc advice − off", "est": c[0], "lo": c[1], "hi": c[2]})
        lvl = sub.groupby(["arm", "level"])[["hallucination", "correct", "abstain"]].mean().unstack("arm")
        md += [f"\n## {tag} (items={len(items_u)}, rows/arm={len(idx)})\n",
               "```\n" + tab.round(4).to_string(index=False) + "\n```\n",
               "```\n" + con.round(4).to_string(index=False) + "\n```\n",
               "Secondary:\n```\n" + pd.DataFrame(sec).round(4).to_string(index=False) + "\n```\n",
               "Per level (hallucination):\n```\n" + lvl["hallucination"].round(3).to_string() + "\n```\n"]
        if tag == "PRIMARY":
            con.to_csv(rep / "contrasts_primary.csv", index=False)
            tab.to_csv(rep / "arms_primary.csv", index=False)
    (rep / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["packets", "sigma", "generate", "analyze"])
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--tag", default="qwen2.5-3b", choices=list(GENERATORS))
    a = ap.parse_args()
    if a.mode == "packets":
        packets()
    elif a.mode == "sigma":
        sigma()
    elif a.mode == "generate":
        generate(a.tag, a.batch_size)
    else:
        analyze(a.tag)


if __name__ == "__main__":
    main()
