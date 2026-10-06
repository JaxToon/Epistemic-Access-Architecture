"""Study 2 — evidence-anchored confabulation (pre-reg: 00_docs/06_preregistration_study2_confabulation.md).

  python -m eaa.study2 sample  [--n 400]                       fresh dev items (excludes pilot ids)
  python -m eaa.study2 run     --model 03_models/Qwen2.5-3B-Instruct [--limit N]
  python -m eaa.study2 analyze --tag qwen2.5-3b                 (after eaa.judge --extra ...)
"""
from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd

from . import prompts as P
from .conditions import candidate_density, plan_item, question_class, render_units
from .data import _sha256, _to_item, load_items

SEED = 20261006
ITEMS = Path("01_data/hotpot_dev_study2_n400_seed20261006.jsonl")
PILOT_ITEMS = Path("01_data/hotpot_dev_n500_seed20261005.jsonl")
RAW = Path("01_data/raw/hotpot_qa_distractor_validation.parquet")
CONDS = [("full", "length"), ("drop_ans", "entity_rich"), ("drop_ans", "entity_poor"),
         ("drop_all", "entity_rich"), ("drop_all", "entity_poor")]
PROMPTS = {"extractive": P.GENERATOR, "open": P.OPEN}


def sample(n: int):
    pilot = {it["id"] for it in load_items(PILOT_ITEMS)}
    df = pd.read_parquet(RAW)
    pool = sorted(i for i in df["id"] if i not in pilot)
    chosen = set(random.Random(SEED).sample(pool, n))
    rows = [_to_item(r) for _, r in df[df["id"].isin(chosen)].iterrows()]
    rows.sort(key=lambda x: x["id"])
    with open(ITEMS, "w", encoding="utf-8") as f:
        for it in rows:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    (ITEMS.parent / f"{ITEMS.stem}.manifest.json").write_text(json.dumps(
        {"source": str(RAW), "source_sha256": _sha256(RAW), "n": n, "seed": SEED,
         "excludes": str(PILOT_ITEMS), "sample_sha256": _sha256(ITEMS)}, indent=2))
    print(f"wrote {ITEMS} ({len(rows)})")


def run(model: str, tag: str, limit: int | None, batch_size: int, load_in_4bit: bool):
    from tqdm import tqdm

    from .backends import HFBackend, MockBackend
    from .run import _msgs

    items = load_items(ITEMS)[:limit] if limit else load_items(ITEMS)
    be = MockBackend() if model == "mock" else HFBackend(model, load_in_4bit=load_in_4bit)
    out_dir = Path("05_outputs") / f"study2_{tag}"
    out_dir.mkdir(parents=True, exist_ok=True)
    packets, tasks = [], []
    for it in items:
        plans = {pol: plan_item(it, SEED, 4, be.count_tokens, pol)
                 for pol in ("length", "entity_rich", "entity_poor")}
        if any(p is None for p in plans.values()):
            continue
        numeric = any(ch.isdigit() for ch in it["answer"])
        full_tok = be.count_tokens(render_units(plans["length"].packet("full")))
        for lv, pol in CONDS:
            plan = plans[pol]
            units = plan.packet(lv)
            ev = render_units(units)
            rm = plan.removed_paras(lv)
            fill = [plan.filler_for_slot[i] for i, u in enumerate(plan.slots) if u.gold and u.para in rm]
            packets.append({"item_id": it["id"], "level": lv, "policy": pol, "qclass": question_class(it),
                            "answer_para_defined": plan.answer_para_defined,
                            "answer_in_packet": plan.answer_in_packet(lv), "evidence": ev,
                            "gold_flags": [u.gold for u in units],
                            "filler_density": float(np.mean([candidate_density(u.text, numeric) for u in fill])) if fill else None,
                            "len_ratio_vs_full": be.count_tokens(ev) / full_tok})
            for pname, tmpl in PROMPTS.items():
                tasks.append((f"{it['id']}|{lv}|{pol}|{pname}", it["id"], lv, pol, pname,
                              _msgs(tmpl.format(evidence=ev, advisory="", question=it["question"]))))
    with open(out_dir / "packets.jsonl", "w", encoding="utf-8") as f:
        for p in packets:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    gen = out_dir / "generations.jsonl"
    done = {json.loads(l)["key"] for l in open(gen, encoding="utf-8")} if gen.exists() else set()
    todo = [t for t in tasks if t[0] not in done]
    todo.sort(key=lambda t: be.prompt_tokens(t[5]))
    with open(gen, "a", encoding="utf-8") as f:
        for i in tqdm(range(0, len(todo), batch_size), desc=f"study2 {tag}"):
            chunk = todo[i:i + batch_size]
            outs = be.generate([t[5] for t in chunk], 24)
            for t, o in zip(chunk, outs):
                f.write(json.dumps({"key": t[0], "item_id": t[1], "level": t[2], "policy": t[3],
                                    "prompt": t[4], "output": o, "model": model,
                                    "prompt_version": P.PROMPT_VERSION, "ts": time.time()},
                                   ensure_ascii=False) + "\n")
            f.flush()
    print(f"done -> {gen}")


def _source(out_norm: str, evidence: str, flags: list[bool], normalize) -> str:
    if not out_norm:
        return "empty"
    hit = [k for k, line in enumerate(evidence.split("\n")) if f" {out_norm} " in f" {normalize(line)} "]
    if not hit:
        return "not_in_packet"
    return "in_gold_unit" if any(flags[k] for k in hit) else "in_filler_or_distractor"


def analyze(tag: str):
    import sys

    from scipy.stats import binomtest

    from . import evaluate as E
    from .analyze import holm
    from .judge import load_cache

    sys.stdout.reconfigure(encoding="utf-8")
    E.JUDGED.clear()
    E.JUDGED.update(load_cache())
    out_dir = Path("05_outputs") / f"study2_{tag}"
    gold = {it["id"]: it["answer"] for it in load_items(ITEMS)}
    pk = {(r["item_id"], r["level"], r["policy"]): r
          for r in map(json.loads, open(out_dir / "packets.jsonl", encoding="utf-8"))}
    rows = []
    for r in map(json.loads, open(out_dir / "generations.jsonl", encoding="utf-8")):
        p = pk[(r["item_id"], r["level"], r["policy"])]
        lab = E.label(r["output"], gold[r["item_id"]], r["item_id"])
        rows.append({**{k: r[k] for k in ("item_id", "level", "policy", "prompt", "output")},
                     "qclass": p["qclass"], "apd": p["answer_para_defined"],
                     "answer_in_packet": p["answer_in_packet"], "filler_density": p["filler_density"],
                     "len_ratio": p["len_ratio_vs_full"],
                     "source": _source(E.normalize_answer(r["output"]), p["evidence"], p["gold_flags"],
                                       E.normalize_answer) if lab["hallucination"] else None,
                     **lab})
    df = pd.DataFrame(rows)
    ev_dir = Path("06_evaluation") / f"study2_{tag}"
    ev_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(ev_dir / "eval.csv", index=False)
    prim = df[(df["qclass"] == "open") & (df["apd"] == True)]
    rng = np.random.default_rng(SEED)
    md = [f"# Study 2 — evidence-anchored confabulation ({tag})\n",
          f"items: {df['item_id'].nunique()} · primary: {prim['item_id'].nunique()} · "
          f"judge_missing: {int(df['judge_missing'].sum())}\n"]

    chk = prim[prim["prompt"] == "extractive"].groupby(["level", "policy"]).agg(
        filler_density=("filler_density", "mean"), len_ratio=("len_ratio", "mean"),
        answer_in_packet=("answer_in_packet", "mean")).reset_index()
    md += ["## Manipulation check\n", "```\n" + chk.round(3).to_string(index=False) + "\n```\n"]

    tab = prim.groupby(["prompt", "level", "policy"]).agg(
        n=("item_id", "size"), correct=("correct", "mean"), halluc=("hallucination", "mean"),
        abstain=("abstain", "mean"), answered=("answered", "sum"), halluc_n=("hallucination", "sum")).reset_index()
    tab["sel_risk"] = tab["halluc_n"] / tab["answered"].clip(lower=1)
    md += ["## Outcomes (primary)\n", "```\n" + tab.round(3).to_string(index=False) + "\n```\n"]

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
        wa = s.pivot_table(index="item_id", columns="policy", values="abstain").dropna()
        con.append({"id": cid, "prompt": prompt, "level": lv, "n_items": len(a),
                    "halluc_poor": a.mean(), "halluc_rich": b.mean(), "diff": b.mean() - a.mean(),
                    "ci_lo": np.percentile(d, 2.5), "ci_hi": np.percentile(d, 97.5),
                    "poor0_rich1": n01, "poor1_rich0": n10, "p": p,
                    "abstain_poor": wa["entity_poor"].mean(), "abstain_rich": wa["entity_rich"].mean()})
    con = pd.DataFrame(con)
    fam = con["id"].isin(["S2-H1", "S2-H2", "S2-H1(open)"])
    con.loc[fam, "p_holm"] = holm(con.loc[fam, "p"].tolist())
    md += ["## Confirmatory contrasts (rich − poor)\n", "```\n" + con.round(4).to_string(index=False) + "\n```\n"]

    def wilson(k, n, z=1.96):
        if n == 0:
            return (np.nan, np.nan)
        ph = k / n
        c = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / (1 + z * z / n)
        m = (ph + z * z / (2 * n)) / (1 + z * z / n)
        return (m - c, m + c)

    src = []
    for prompt in PROMPTS:
        for lv in ["full", "drop_ans", "drop_all"]:
            h = prim[(prim["prompt"] == prompt) & (prim["level"] == lv) & (prim["hallucination"] == 1)]
            k = int(h["source"].isin(["in_gold_unit", "in_filler_or_distractor"]).sum())
            lo, hi = wilson(k, len(h))
            vc = h["source"].value_counts(normalize=True)
            src.append({"prompt": prompt, "level": lv, "n_halluc": len(h), "copied_from_packet": k / max(len(h), 1),
                        "wilson_lo": lo, "wilson_hi": hi,
                        "from_gold_unit": vc.get("in_gold_unit", 0), "from_filler": vc.get("in_filler_or_distractor", 0),
                        "not_in_packet": vc.get("not_in_packet", 0)})
    src = pd.DataFrame(src)
    md += ["## Source of hallucinated answers (S2-H3 / S2-H4: drop_ans rows)\n",
           "```\n" + src.round(3).to_string(index=False) + "\n```\n"]
    rep = Path("07_analysis") / f"study2_{tag}"
    rep.mkdir(parents=True, exist_ok=True)
    con.to_csv(rep / "contrasts.csv", index=False)
    src.to_csv(rep / "sources.csv", index=False)
    tab.to_csv(rep / "outcomes.csv", index=False)
    (rep / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["sample", "run", "analyze"])
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--model", default="03_models/Qwen2.5-3B-Instruct")
    ap.add_argument("--tag", default="qwen2.5-3b")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--load-in-4bit", action="store_true")
    a = ap.parse_args()
    if a.mode == "sample":
        sample(a.n)
    elif a.mode == "run":
        run(a.model, a.tag, a.limit, a.batch_size, a.load_in_4bit)
    else:
        analyze(a.tag)


if __name__ == "__main__":
    main()
