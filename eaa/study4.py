"""Study 4 — the authority ladder: advice vs veto vs intervention (DRAFT prereg: 00_docs/17_...md).

Nothing here touches the test pool until `08_architecture/study4_lock.json` exists. That file is written
by hand when the pre-registration is locked; it fixes the steering direction, layer and strength.

  python -m eaa.study4 sample   [--n 1700]        test pool (excludes pilot + Study 2/3 items)
  python -m eaa.study4 direction --kind within|caa --layer L (--rel r | --alpha a)
                                                  fit the steering vector on ALL dev items -> .pt
  python -m eaa.study4 packets  [--items FILE --out DIR]
  python -m eaa.eag.features --packets DIR/prompts.jsonl --out DIR/features.pt
  python -m eaa.study4 sigma    [--out DIR]
  python -m eaa.study4 generate [--out DIR] [--limit N]    arms: off, advice, placebo, steer, steer_rand
  python -m eaa.judge --config configs/pilot_v0.1.yaml --extra DIR/generations.jsonl
  python -m eaa.study4 k1       [--out DIR]        H4.4: dev-trained probe marks K1 among test hallucinations
  python -m eaa.study4 analyze  [--out DIR]

`--items/--out` exist so the pipeline can be smoke-tested on dev items without touching the test pool.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from . import prompts as P
from .conditions import plan_item, question_class, render_units
from .data import _sha256, _to_item, load_items

SEED = 20261028
RAW = Path("01_data/raw/hotpot_qa_distractor_validation.parquet")
EXCLUDE = [Path("01_data/hotpot_dev_n500_seed20261005.jsonl"), Path("01_data/hotpot_dev_study2_n400_seed20261006.jsonl")]
TEST_ITEMS = Path("01_data/hotpot_dev_study4_n1700_seed20261028.jsonl")
TEST_OUT = Path("05_outputs/study4_qwen2.5-3b")
LOCK = Path("08_architecture/study4_lock.json")
RUNS = Path("08_architecture/eag_runs")
MODEL = "03_models/Qwen2.5-3B-Instruct"
CONDS = [("full", "length"), ("drop_ans", "entity_poor")]
ARMS = ["off", "advice", "placebo", "steer", "steer_rand"]
TAU = 0.5
LAMBDA = 2.0
B = 2000
ADVICE = ("Epistemic module: the estimated probability that the evidence above supports an "
          "answer is {s:.2f} ({word}).\n\n")      # identical wording to phase 1b / Study 3


def _word(s: float) -> str:
    return "high" if s >= 0.67 else "medium" if s >= 0.33 else "low"


def _msgs(user: str) -> list[dict]:
    return [{"role": "system", "content": P.SYSTEM}, {"role": "user", "content": user}]


def sample(n: int):
    excl = {it["id"] for p in EXCLUDE for it in load_items(p)}
    df = pd.read_parquet(RAW)
    items = sorted((_to_item(r) for _, r in df.iterrows()), key=lambda x: x["id"])
    pool = [it for it in items if it["id"] not in excl]
    chosen = random.Random(SEED).sample(pool, n)          # file order = sampled order
    with open(TEST_ITEMS, "w", encoding="utf-8") as f:
        for it in chosen:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    TEST_ITEMS.with_suffix(".manifest.json").write_text(json.dumps({
        "source": str(RAW), "source_sha256": _sha256(RAW), "n": n, "seed": SEED,
        "excludes": [str(p) for p in EXCLUDE], "eligible": len(pool),
        "sampling": "sorted by id, exclusions removed, random.Random(seed).sample; file order = sampled order",
        "purpose": "Study 4 TEST items. Supersedes hotpot_dev_study4_pool600_seed20261017 (never run).",
        "sample_sha256": _sha256(TEST_ITEMS)}, indent=2))
    print(f"{len(pool)} eligible -> {n} -> {TEST_ITEMS}")


def direction(kind: str, layer: int, rel: float | None, alpha: float | None):
    """Fit on ALL dev items (both folds of the pilot) with the method chosen in the pilot."""
    import torch

    from .steer_dev import OUT as DEV, _base

    items, prim, fold, off, lab, pk = _base()
    Hf = torch.load(DEV / "t0_hidden.pt", weights_only=False)["H"]
    li = torch.load(DEV / "t0_hidden.pt", weights_only=False)["layers"].index(layer)
    if kind == "within":
        Hd = torch.load(DEV / "t0_hidden_dropans.pt", weights_only=False)["H"]
        v = torch.stack([Hf[i][li] - Hd[i][li] for i in prim]).mean(0)
    else:
        cor = [i for i in prim if lab[(i, "full", "length")]["correct"] == 1]
        hal = [i for i in prim if lab[(i, "full", "length")]["hallucination"] == 1]
        v = torch.stack([Hf[i][li] for i in cor]).mean(0) - torch.stack([Hf[i][li] for i in hal]).mean(0)
    hn = float(torch.stack([Hf[i][li] for i in prim]).norm(dim=-1).mean())
    vec = v / v.norm() * rel * hn if kind == "within" else alpha * v
    g = torch.Generator().manual_seed(SEED)
    r = torch.randn(vec.shape, generator=g)
    out = Path(f"08_architecture/study4_steer_{kind}_L{layer}.pt")
    torch.save({"vec": vec, "rand": r / r.norm() * vec.norm(), "layer": layer, "kind": kind, "rel": rel,
                "alpha": alpha, "mean_h_norm": hn, "n_dev_items": len(prim)}, out)
    print(f"‖vec‖ = {float(vec.norm()):.2f} (‖h‖ ≈ {hn:.1f}) -> {out}")


def packets(items_path: Path, out: Path):
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(MODEL)
    count = lambda s: len(tok(s, add_special_tokens=False)["input_ids"])
    out.mkdir(parents=True, exist_ok=True)
    n_ok = n_skip = 0
    with open(out / "packets.jsonl", "w", encoding="utf-8") as f, open(out / "prompts.jsonl", "w", encoding="utf-8") as g:
        for it in load_items(items_path):
            plans = {pol: plan_item(it, SEED, 4, count, pol) for pol in ("length", "entity_poor")}
            if any(p is None for p in plans.values()):
                n_skip += 1
                continue
            n_ok += 1
            for lv, pol in CONDS:
                plan = plans[pol]
                units = plan.packet(lv)
                ev = render_units(units)
                f.write(json.dumps({"item_id": it["id"], "level": lv, "policy": pol, "qclass": question_class(it),
                                    "answer_para_defined": plan.answer_para_defined,
                                    "answer_in_packet": plan.answer_in_packet(lv), "evidence": ev,
                                    "gold_flags": [u.gold for u in units]}, ensure_ascii=False) + "\n")
                g.write(json.dumps({"item_id": it["id"], "level": lv, "policy": pol, "split": "test",
                                    "prompt": P.GENERATOR.format(evidence=ev, advisory="", question=it["question"])},
                                   ensure_ascii=False) + "\n")
    print(f"items ok={n_ok} skipped={n_skip} -> {out}")


def sigma(out: Path):
    import torch

    from .eag.model import EpistemicHead
    from .eag.train import predict

    data = torch.load(out / "features.pt", weights_only=False)
    meta, feats = data["meta"], data["feats"]
    runs = [r["name"] for r in json.loads((RUNS / "train_summary.json").read_text()) if r["name"].startswith("eag_lc1_")]
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    cols = []
    for name in runs:
        c = torch.load(RUNS / f"{name}.pt", weights_only=False, map_location="cpu")
        m = EpistemicHead(c["d"], c["n_layers_g"], c["variant"]).to(dev)
        m.load_state_dict(c["state"])
        cols.append(1 / (1 + np.exp(-predict(m, feats, list(range(len(meta))), dev))))
    df = pd.DataFrame([{k: m[k] for k in ("item_id", "level", "policy")} for m in meta])
    df["sigma"] = np.mean(cols, axis=0)
    df["placebo"] = np.random.default_rng(SEED).permutation(df["sigma"].to_numpy())
    df.to_csv(out / "sigma.csv", index=False)
    print(df.groupby("level")[["sigma"]].mean().round(3))


def _with_advice(prompt: str, s: float) -> str:
    i = prompt.rfind("Question: ")
    return prompt[:i] + ADVICE.format(s=s, word=_word(s)) + prompt[i:]


def generate(out: Path, limit: int | None, lock_path: Path, batch_size: int = 4):
    import torch
    from tqdm import tqdm
    from transformers import AutoModelForCausalLM, AutoTokenizer

    lock = json.loads(lock_path.read_text())
    steer = torch.load(lock["steer_file"], weights_only=False)
    L = int(steer["layer"])
    tok = AutoTokenizer.from_pretrained(MODEL, padding_side="left")
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float16, device_map="cuda").eval()
    sig = pd.read_csv(out / "sigma.csv").set_index(["item_id", "level", "policy"])
    rows = [json.loads(l) for l in open(out / "prompts.jsonl", encoding="utf-8")]
    if limit:
        keep = list(dict.fromkeys(r["item_id"] for r in rows))[:limit]
        rows = [r for r in rows if r["item_id"] in keep]
    gen = out / "generations.jsonl"
    done = {json.loads(l)["key"] for l in open(gen, encoding="utf-8")} if gen.exists() else set()
    with open(gen, "a", encoding="utf-8") as f:
        for arm in ARMS:
            todo = []
            for r in rows:
                key = f"{r['item_id']}|{r['level']}|{r['policy']}|{arm}"
                if key in done:
                    continue
                s = sig.loc[(r["item_id"], r["level"], r["policy"])]
                prompt = _with_advice(r["prompt"], float(s.sigma if arm == "advice" else s.placebo)) \
                    if arm in ("advice", "placebo") else r["prompt"]
                todo.append((key, r, prompt))
            if not todo:
                continue
            vec = {"steer": steer["vec"], "steer_rand": steer["rand"]}.get(arm)
            h = None
            if vec is not None:
                delta = vec.to("cuda", torch.float16)

                def hook(mod, inp, o, delta=delta):
                    return (o[0] + delta,) + tuple(o[1:]) if isinstance(o, tuple) else o + delta
                h = model.model.layers[L - 1].register_forward_hook(hook)
            try:
                texts = {t[0]: tok.apply_chat_template(_msgs(t[2]), tokenize=False, add_generation_prompt=True) for t in todo}
                todo.sort(key=lambda t: len(texts[t[0]]))
                for b in tqdm(range(0, len(todo), batch_size), desc=arm):
                    chunk = todo[b:b + batch_size]
                    enc = tok([texts[t[0]] for t in chunk], return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")
                    with torch.inference_mode():
                        g = model.generate(**enc, max_new_tokens=24, do_sample=False, temperature=None, top_p=None,
                                           top_k=None, pad_token_id=tok.pad_token_id)
                    outs = [s.strip() for s in tok.batch_decode(g[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)]
                    for (key, r, _), o in zip(chunk, outs):
                        f.write(json.dumps({"key": key, "item_id": r["item_id"], "level": r["level"], "policy": r["policy"],
                                            "arm": arm, "output": o, "model": MODEL, "lock": lock.get("version")},
                                           ensure_ascii=False) + "\n")
                    f.flush()
            finally:
                if h is not None:
                    h.remove()
    print(f"done -> {gen}")


def k1(out: Path, items_path: Path):
    """H4.4: probe trained on ALL dev candidates (Phase 1b, L27, model-generated only) scores gold vs the
    `off` greedy answer of every test item hallucinated at `off`@full. Writes out/k1.csv (k1 = gold > greedy)."""
    import torch
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from . import evaluate as E
    from .judge import load_cache

    E.JUDGED.clear()
    E.JUDGED.update(load_cache())
    dev = torch.load("07_analysis/diagnosis/probe_candidates.pt", weights_only=False)
    ps = pd.read_csv("07_analysis/diagnosis/probe_scores.csv")          # dev labels (judge-labelled)
    meta = pd.DataFrame(dev["meta"])
    li = dev["layers"].index(27)
    lab = ps.drop_duplicates(["item_id", "cand", "kind"]).set_index(["item_id", "cand", "kind"]).y
    y = np.array([lab.get((i, c, k), np.nan) for i, c, k in zip(meta.item_id, meta.cand, meta.kind)], dtype=float)
    m = meta.kind.isin(["greedy", "sample"]).to_numpy() & ~np.isnan(y)
    clf = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=5000))
    clf.fit(dev["H"][:, li].float().numpy()[m], y[m])

    items = {it["id"]: it for it in load_items(items_path)}
    pk = {(r["item_id"], r["level"], r["policy"]): r["prompt"]
          for r in map(json.loads, open(out / "prompts.jsonl", encoding="utf-8"))}
    gen = [r for r in map(json.loads, open(out / "generations.jsonl", encoding="utf-8"))
           if r["arm"] == "off" and r["level"] == "full"]
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float16, device_map="cuda").eval()
    rows = []
    for r in gen:
        l = E.label(str(r["output"]), items[r["item_id"]]["answer"], r["item_id"])
        if l["hallucination"] != 1:
            continue
        text = tok.apply_chat_template(_msgs(pk[(r["item_id"], "full", "length")]), tokenize=False,
                                       add_generation_prompt=True)
        p_ids = tok(text, add_special_tokens=False)["input_ids"]
        sc = {}
        for name, c in (("gold", items[r["item_id"]]["answer"]), ("greedy", r["output"])):
            ci = tok(c, add_special_tokens=False)["input_ids"]
            with torch.inference_mode():
                hs = model.model(input_ids=torch.tensor([p_ids + ci], device="cuda"),
                                 output_hidden_states=True).hidden_states
            h = hs[27][0, len(p_ids) + len(ci) - 1].float().cpu().numpy()[None]
            sc[name] = float(clf.decision_function(h)[0])
        rows.append({"item_id": r["item_id"], "score_gold": sc["gold"], "score_greedy": sc["greedy"],
                     "k1": int(sc["gold"] > sc["greedy"])})
    pd.DataFrame(rows).to_csv(out / "k1.csv", index=False)
    print(f"k1: {sum(r['k1'] for r in rows)}/{len(rows)} -> {out / 'k1.csv'}")


def analyze(out: Path, items_path: Path):
    from scipy.stats import binomtest

    from . import evaluate as E
    from .analyze import holm
    from .judge import load_cache

    sys.stdout.reconfigure(encoding="utf-8")
    E.JUDGED.clear()
    E.JUDGED.update(load_cache())
    items = {it["id"]: it for it in load_items(items_path)}
    pk = {(r["item_id"], r["level"], r["policy"]): r for r in map(json.loads, open(out / "packets.jsonl", encoding="utf-8"))}
    gen = pd.read_json(out / "generations.jsonl", lines=True)
    sig = pd.read_csv(out / "sigma.csv")
    lab = [E.label(str(o), items[i]["answer"], i) for i, o in zip(gen.item_id, gen.output)]
    for c in ("correct", "hallucination", "abstain", "judge_missing"):
        gen[c] = [l[c] for l in lab]
    W = gen.pivot_table(index=["item_id", "level", "policy"], columns="arm",
                        values=["correct", "hallucination", "abstain"], aggfunc="first")
    s_ = sig.set_index(["item_id", "level", "policy"]).reindex(W.index)
    W[("sigma", "")] = s_["sigma"].to_numpy()
    W[("primary", "")] = [int(pk[k]["qclass"] == "open" and pk[(k[0], "full", "length")]["answer_para_defined"]) for k in W.index]
    gate = (W[("sigma", "")] >= TAU).to_numpy()
    for col in ("correct", "hallucination", "abstain"):     # derived arms
        W[(col, "veto")] = np.where(gate, W[(col, "off")], 1 if col == "abstain" else 0)
        W[(col, "steer_sigma")] = np.where(gate, W[(col, "steer")], W[(col, "off")])
        W[(col, "rand_sigma")] = np.where(gate, W[(col, "steer_rand")], W[(col, "off")])   # same trigger as steer_sigma
    P_ = W[W[("primary", "")] == 1]
    F = P_.xs("full", level="level")
    D = P_.xs("drop_ans", level="level")
    hal = F[("hallucination", "off")] == 1
    cor = F[("correct", "off")] == 1

    def mcnemar(a, b, mask):
        """a, b: arm names; paired 'recovered to correct' on rows in mask. Returns (rate_a, rate_b, b10, b01, p)."""
        x, y = F.loc[mask, ("correct", a)].to_numpy(), F.loc[mask, ("correct", b)].to_numpy()
        n10, n01 = int(((x == 1) & (y == 0)).sum()), int(((x == 0) & (y == 1)).sum())
        p = binomtest(n10, n10 + n01, 0.5).pvalue if n10 + n01 else 1.0
        return x.mean(), y.mean(), n10, n01, p

    rng = np.random.default_rng(SEED)
    ids = F.index.get_level_values(0).to_numpy()

    def boot_U(a, b):
        """U(lambda) per item = mean over its `full` and `drop_ans` rows (as in Study 3: veto pays off mostly
        when evidence is missing), paired item bootstrap."""
        def u(arm):
            x = (P_[("correct", arm)] - LAMBDA * P_[("hallucination", arm)]).astype(float)
            return x.groupby(level="item_id").mean()
        ua, ub = u(a), u(b)
        dif = (ua - ub.reindex(ua.index)).to_numpy()
        reps = [dif[rng.integers(0, len(dif), len(dif))].mean() for _ in range(B)]
        lo, hi = np.percentile(reps, [2.5, 97.5])
        p = float(min(1.0, max(2 * min((np.array(reps) >= 0).mean(), (np.array(reps) <= 0).mean()), 1 / B)))
        return dif.mean(), lo, hi, p

    h1 = mcnemar("steer_sigma", "advice", hal)
    h2 = mcnemar("steer_sigma", "rand_sigma", hal)
    h3 = boot_U("steer_sigma", "veto")
    k1f = out / "k1.csv"                                    # H4.4 (written by `k1` mode)
    k1 = str(k1f) if k1f.exists() else None
    rows = [
        {"id": "H4.1", "uji": "halusinasi→benar: steer_σ vs advice (McNemar)", "a": h1[0], "b": h1[1], "n10": h1[2], "n01": h1[3], "p": h1[4]},
        {"id": "H4.2", "uji": "halusinasi→benar: steer_σ vs steer_rand_σ (McNemar)", "a": h2[0], "b": h2[1], "n10": h2[2], "n01": h2[3], "p": h2[4]},
        {"id": "H4.3", "uji": "U(λ=2) steer_σ − veto, full+drop_ans (bootstrap)", "a": h3[0], "b": np.nan, "lo": h3[1], "hi": h3[2], "p": h3[3]},
    ]
    if k1 and Path(k1).exists():
        from scipy.stats import fisher_exact
        K = pd.read_csv(k1).set_index("item_id").k1
        hal_ids = F.index[hal].get_level_values(0)
        rec = F.loc[hal, ("correct", "steer_sigma")].to_numpy().astype(int)
        kk = K.reindex(hal_ids).fillna(0).to_numpy().astype(int)
        tab4 = [[int(rec[kk == 1].sum()), int((1 - rec[kk == 1]).sum())],
                [int(rec[kk == 0].sum()), int((1 - rec[kk == 0]).sum())]]
        p4 = fisher_exact(tab4, alternative="greater").pvalue
        rows.append({"id": "H4.4", "uji": "halusinasi→benar steer_σ: K1 vs non-K1 (Fisher, satu sisi)",
                     "a": rec[kk == 1].mean() if (kk == 1).any() else np.nan,
                     "b": rec[kk == 0].mean() if (kk == 0).any() else np.nan,
                     "n10": int((kk == 1).sum()), "n01": int((kk == 0).sum()), "p": p4})
    damage = 1 - F.loc[cor, ("correct", "steer_sigma")].mean()
    d_drop = (D[("hallucination", "steer_sigma")] - D[("hallucination", "off")]).to_numpy().astype(float)
    reps = [d_drop[rng.integers(0, len(d_drop), len(d_drop))].mean() for _ in range(B)]
    lo90, hi90 = np.percentile(reps, [5, 95])
    rows.append({"id": "H4.5", "uji": "rusak steer_σ ≤ 0,05 dan Δhalu@drop_ans ≤ +0,02 (TOST 90%)",
                 "a": damage, "b": d_drop.mean(), "lo": lo90, "hi": hi90,
                 "p": np.nan, "verdict": "ok" if damage <= 0.05 and hi90 <= 0.02 else "melampaui"})
    T = pd.DataFrame(rows)
    conf = T.id.isin(["H4.1", "H4.2", "H4.3", "H4.4"])
    T.loc[conf, "p_holm"] = holm(T.loc[conf, "p"].tolist())
    arms = ["off", "advice", "placebo", "veto", "steer", "steer_sigma", "steer_rand", "rand_sigma"]
    tab = pd.DataFrame({a: {"benar@full": F[("correct", a)].mean(), "halu@full": F[("hallucination", a)].mean(),
                            "abstain@full": F[("abstain", a)].mean(), "halu@drop_ans": D[("hallucination", a)].mean(),
                            "halu→benar": F.loc[hal, ("correct", a)].mean()} for a in arms}).T
    md = ["# Studi 4 — tangga otoritas\n", f"Item utama: {len(F)}; halusinasi off@full: {int(hal.sum())}; "
          f"judge_missing: {int(gen.judge_missing.sum())}; k1 file: {k1}\n",
          "```\n" + tab.round(3).to_string() + "\n```\n", "```\n" + T.round(4).to_string(index=False) + "\n```\n"]
    (out / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


def main():
    sys.stdout.reconfigure(encoding="utf-8")   # Windows console (cp1252) cannot print ‖, σ, →
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["sample", "direction", "packets", "sigma", "generate", "k1", "analyze"])
    ap.add_argument("--n", type=int, default=1700)
    ap.add_argument("--items", type=Path, default=TEST_ITEMS)
    ap.add_argument("--out", type=Path, default=TEST_OUT)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--lock", type=Path, default=LOCK)
    ap.add_argument("--kind", choices=["within", "caa"])
    ap.add_argument("--layer", type=int)
    ap.add_argument("--rel", type=float)
    ap.add_argument("--alpha", type=float)
    a = ap.parse_args()
    touches_test = a.out == TEST_OUT or a.items == TEST_ITEMS
    if a.mode in ("generate", "k1", "analyze") and touches_test and not LOCK.exists():
        sys.exit(f"refusing: {LOCK} does not exist (pre-registration not locked). Use --items/--out for a dev smoke test.")
    if a.mode == "sample":
        sample(a.n)
    elif a.mode == "direction":
        direction(a.kind, a.layer, a.rel, a.alpha)
    elif a.mode == "packets":
        packets(a.items, a.out)
    elif a.mode == "sigma":
        sigma(a.out)
    elif a.mode == "generate":
        generate(a.out, a.limit, a.lock)
    elif a.mode == "k1":
        k1(a.out, a.items)
    else:
        analyze(a.out, a.items)


if __name__ == "__main__":
    main()
